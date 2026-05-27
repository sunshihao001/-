"""
run.py — Skill 01: meme-candidate-entry 主入口

流程：地址验证 → token info 调用 → 池子/流动性检查 → 输出 candidate_entry.json
对应设计文件：design/phase1-skill-01-candidate-entry.md
"""

from __future__ import annotations

import sys
import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone, timedelta

# 添加 skills 目录到路径
sys.path.insert(0, "/root/sikk-gmgn/skills")

from common.gmgn_client import GmgnClient, GmgnError
from common.file_io import get_run_dir, save_json
from common.validators import save_validated_json
from common.phase_state import create_phase_state, complete_phase, block_phase
# Schema 和 rules 在同目录下
_script_dir = __import__("pathlib").Path(__file__).parent
sys.path.insert(0, str(_script_dir))
from schema import CandidateEntryInput, CandidateEntryOutput, InitialValidation, SOLANA_ADDRESS_RE
from rules import check_judgment_rules, check_downgrade_rules, check_blocker_rules

logger = logging.getLogger(__name__)


def run(
    token_address: str,
    chain: str = "sol",
    entry_source: str = "manual_ca",
    entry_reason: str = "",
    gmgn: GmgnClient | None = None,
) -> dict:
    """
    执行 Skill 01：meme-candidate-entry

    返回 candidate_entry 输出 dict。
    同时写入 data/runs/<token_address>/candidate_entry.json
    """

    if gmgn is None:
        gmgn = GmgnClient()

    # ── 1. 输入验证 ──
    input_data = CandidateEntryInput(
        mode="manual",
        token_address=token_address,
        chain=chain,
        entry_source=entry_source,
        entry_reason=entry_reason,
    )
    errors = input_data.validate()

    # 构建输出
    output = _build_output(token_address, entry_source, entry_reason)
    validation = InitialValidation()

    if errors:
        output["status"] = "ERROR"
        output["blocker_reasons"] = errors
        output["next_action"] = "STOP"
        output["handoff_to"] = ""
        _save_output(token_address, output, phase_status="ERROR")
        return output

    # 地址格式有效
    validation.address_valid = True

    # ── 2. 调用 token info ──
    token_info = {}
    try:
        token_info = gmgn.token_info(token_address, chain)
    except GmgnError as e:
        output["status"] = "ERROR"
        output["blocker_reasons"] = [f"GMGN token info failed: {e}"]
        output["next_action"] = "STOP"
        output["handoff_to"] = ""
        output["initial_validation"] = asdict(validation)
        _save_output(token_address, output, phase_status="ERROR")
        return output

    # ── 3. 解析 token info ──
    # GMGN 返回格式可能嵌套在 data 字段里
    data = token_info.get("data", token_info)
    if isinstance(data, dict) and "token" in data:
        data = data["token"]

    # 提取字段
    output["token_symbol"] = data.get("symbol", "")
    output["token_name"] = data.get("name", "")
    output["creation_timestamp"] = str(data.get("creation_timestamp", data.get("open_timestamp", "")))
    output["launchpad"] = data.get("launchpad", "")

    # ── 4. 验证检查 ──
    # token 存在
    if data.get("symbol") or data.get("address") or data.get("name"):
        validation.token_exists = True

    # 有交易池
    pool_addr = data.get("biggest_pool_address", "") or data.get("pool_address", "")
    if pool_addr:
        validation.has_pool = True

    # 有流动性
    liquidity = _safe_float(data.get("liquidity", 0))
    if liquidity > 0:
        validation.has_liquidity = True

    # 是否在 bonding curve 上
    # 实测 GMGN token info：无 launchpad 时 launchpad='' 且 launchpad_status=0。
    # 这种情况不能误判为 on_curve。只有存在 launchpad / launchpad_platform 且状态未完成时才视为 on_curve。
    launchpad_status = data.get("launchpad_status")
    launchpad_name = data.get("launchpad") or data.get("launchpad_platform") or ""
    if launchpad_name and launchpad_status is not None and int(launchpad_status) != 2:
        validation.is_on_curve = True
    # 也检查 is_on_curve 字段（如果 GMGN 直接给）
    if data.get("is_on_curve"):
        validation.is_on_curve = True

    output["initial_validation"] = asdict(validation)

    # ── 5. 判断规则 ──
    judgment = check_judgment_rules(data, asdict(validation))
    blockers_from_judgment = [j for j in judgment if j["action"] == "BLOCK"]
    warns_from_judgment = [j for j in judgment if j["action"] == "WARN"]

    # ── 6. 阻塞规则 ──
    blockers = check_blocker_rules(asdict(validation))

    if blockers:
        output["status"] = "BLOCK"
        output["blocker_reasons"] = blockers
        output["next_action"] = "STOP"
        output["handoff_to"] = ""
        for b in blockers:
            output["evidence"].append({
                "claim": b,
                "source": "gmgn token info",
                "value": None,
                "weight": "high",
            })
        _save_output(token_address, output, phase_status="BLOCK", blockers=blockers)
        return output

    # ── 7. 降级规则 ──
    downgrades = check_downgrade_rules(data)
    output["downgrade_reasons"] = downgrades

    # ── 8. 检查 WARN ──
    for w in warns_from_judgment:
        output["evidence"].append({
            "claim": w["reason"],
            "source": "gmgn token info",
            "value": w["rule"],
            "weight": "medium",
        })
        if w["reason"] not in output["downgrade_reasons"]:
            output["downgrade_reasons"].append(w["reason"])

    # ── 9. 缺失字段检查 ──
    missing = []
    if not output["token_symbol"]:
        missing.append("token_symbol")
    if not output["creation_timestamp"]:
        missing.append("creation_timestamp")
    if not output["launchpad"]:
        missing.append("launchpad")
    output["missing_fields"] = missing

    # ── 10. 最终状态 ──
    if downgrades or warns_from_judgment:
        output["status"] = "WARN" if not downgrades else "PASS"
        # 有 warn 但无 block → 仍然 PASS，只记录
    if not output["status"]:
        output["status"] = "PASS"

    output["confidence_score"] = 1.0 - (len(downgrades) * 0.1) - (len(missing) * 0.05)
    output["confidence_score"] = max(0.1, min(1.0, output["confidence_score"]))

    # ── 11. 保存 ──
    _save_output(token_address, output, phase_status=output["status"])
    return output


def _build_output(token_address: str, entry_source: str, entry_reason: str) -> dict:
    """构建初始输出 dict"""
    now = datetime.now(timezone.utc)
    return {
        "schema_version": "1.0",
        "skill_name": "meme-candidate-entry",
        "task_id": f"{token_address}_{now.strftime('%Y%m%dT%H%M%SZ')}",
        "token_address": token_address,
        "chain": "sol",
        "timestamp": now.isoformat(),
        "status": "",
        "entry_source": entry_source,
        "entry_reason": entry_reason,
        "token_symbol": "",
        "token_name": "",
        "creation_timestamp": "",
        "launchpad": "",
        "initial_validation": {},
        "evidence": [],
        "counter_evidence": [],
        "confidence_score": 1.0,
        "downgrade_reasons": [],
        "blocker_reasons": [],
        "missing_fields": [],
        "valid_until": (now + timedelta(minutes=30)).isoformat(),
        "next_action": "meme-token-panel",
        "handoff_to": "meme-token-panel",
    }


def _save_output(
    token_address: str,
    output: dict,
    phase_status: str,
    blockers: list[str] | None = None,
) -> None:
    """保存输出文件并更新 phase_state"""
    run_dir = get_run_dir(token_address)
    save_validated_json(output, run_dir / "candidate_entry.json")

    if phase_status in ("BLOCK", "ERROR"):
        block_phase(token_address, "candidate_entry", blockers or output.get("blocker_reasons", []))
    else:
        complete_phase(token_address, "candidate_entry", phase_status)


def _safe_float(val) -> float:
    """安全转 float"""
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


# ── 候选池生成 ──

def build_candidate_pool(
    source: str = "trending",
    limit: int = 10,
    chain: str = "sol",
    gmgn: GmgnClient | None = None,
    min_liquidity: float = 50000,
    min_market_cap: float = 50000,
) -> dict:
    """
    生成候选池。只负责候选发现，不跑 S02-S06。

    输出：data/runs/candidate_pools/<timestamp>/候选池.json + 候选池报告.md
    """
    if gmgn is None:
        gmgn = GmgnClient()

    now = datetime.now(timezone.utc)
    batch_id = now.strftime("%Y%m%dT%H%M%SZ")
    pool_dir = __import__("pathlib").Path("/root/sikk-gmgn/data/runs/candidate_pools") / batch_id
    pool_dir.mkdir(parents=True, exist_ok=True)

    raw_items = _fetch_candidate_items(source, limit, chain, gmgn)
    candidates = []
    filtered_out = []
    seen = set()

    for idx, item in enumerate(raw_items, start=1):
        address = item.get("address") or item.get("token_address") or ""
        if not address or address in seen:
            continue
        seen.add(address)
        liquidity = _safe_float(item.get("liquidity", item.get("pool_liquidity", 0)))
        market_cap = _safe_float(item.get("market_cap", item.get("fdv", item.get("fully_diluted_valuation", 0))))
        liquidity_ok = liquidity >= min_liquidity
        market_cap_ok = market_cap >= min_market_cap
        gate = "PASS" if liquidity_ok and market_cap_ok else "FILTERED_OUT"
        filter_reasons = []
        if not liquidity_ok:
            filter_reasons.append(f"liquidity_below_min:{liquidity}<{min_liquidity}")
        if not market_cap_ok:
            filter_reasons.append(f"market_cap_below_min:{market_cap}<{min_market_cap}")
        candidate = {
            "token_address": address,
            "symbol": item.get("symbol", ""),
            "name": item.get("name", ""),
            "entry_source": _entry_source_for(source),
            "entry_reason": _entry_reason_for(source, idx, item),
            "rank": item.get("rank", idx),
            "liquidity": liquidity,
            "market_cap": market_cap,
            "entry_liquidity_marketcap_gate": gate,
            "entry_filter_reasons": filter_reasons,
            "raw": item,
        }
        if gate == "FILTERED_OUT":
            filtered_out.append(candidate)
            continue
        candidates.append(candidate)

    result = {
        "schema_version": "1.0",
        "source": source,
        "chain": chain,
        "limit": limit,
        "min_liquidity": min_liquidity,
        "min_market_cap": min_market_cap,
        "generated_at": now.isoformat(),
        "raw_candidate_count": len(raw_items),
        "candidate_count": len(candidates),
        "filtered_out_count": len(filtered_out),
        "candidates": candidates,
        "filtered_out": filtered_out,
        "candidate_pool_file": str(pool_dir / "候选池.json"),
        "candidate_pool_report": str(pool_dir / "候选池报告.md"),
    }

    with open(pool_dir / "候选池.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    report = _candidate_pool_report(result)
    with open(pool_dir / "候选池报告.md", "w", encoding="utf-8") as f:
        f.write(report)

    return result


def _fetch_candidate_items(source: str, limit: int, chain: str, gmgn: GmgnClient) -> list[dict]:
    if source == "trending":
        raw = gmgn.market_trending(chain=chain, interval="1h", order_by="volume", limit=limit)
        data = raw.get("data", raw)
        return data.get("rank", data.get("list", [])) if isinstance(data, dict) else data
    if source == "trenches":
        raw = gmgn.market_trenches(chain=chain, type_="completed", filter_preset="strict", sort_by="smart_degen_count")
        data = raw.get("data", raw)
        items = data.get("list", data.get("rank", data.get("items", []))) if isinstance(data, dict) else data
        return items[:limit]
    if source == "signal":
        raw = gmgn.market_signal(chain=chain, signal_type=12)
        data = raw.get("data", raw)
        items = data.get("list", data.get("rank", data.get("items", []))) if isinstance(data, dict) else data
        return items[:limit]
    if source == "mixed":
        items = []
        for s in ["trending", "trenches", "signal"]:
            try:
                items.extend(_fetch_candidate_items(s, limit, chain, gmgn))
            except Exception:
                pass
        return items[:limit]
    raise ValueError(f"Unsupported source: {source}")


def _entry_source_for(source: str) -> str:
    return {
        "trending": "gmgn_trending",
        "trenches": "gmgn_trenches",
        "signal": "gmgn_signal",
        "mixed": "gmgn_mixed",
    }.get(source, source)


def _entry_reason_for(source: str, idx: int, item: dict) -> str:
    if source == "trending":
        return f"GMGN trending 1h volume rank #{item.get('rank', idx)}"
    if source == "trenches":
        return f"GMGN trenches completed strict candidate #{idx}"
    if source == "signal":
        return f"GMGN smart money signal candidate #{idx}"
    if source == "mixed":
        return f"GMGN mixed candidate #{idx}"
    return f"GMGN candidate #{idx}"


def _candidate_pool_report(result: dict) -> str:
    lines = [
        "# 候选池报告",
        "",
        f"- Source: {result['source']}",
        f"- Chain: {result['chain']}",
        f"- Generated At: {result['generated_at']}",
        f"- Candidate Count: {result['candidate_count']}",
        f"- Filtered Out Count: {result.get('filtered_out_count', 0)}",
        f"- Min Liquidity: {result.get('min_liquidity')}",
        f"- Min Market Cap: {result.get('min_market_cap')}",
        "",
        "## Candidates",
    ]
    for c in result["candidates"]:
        lines.append(f"- {c.get('symbol','')} | {c['token_address']} | liq={c.get('liquidity')} | mcap={c.get('market_cap')} | {c['entry_reason']}")
    if result.get("filtered_out"):
        lines += ["", "## Filtered Out"]
        for c in result["filtered_out"]:
            lines.append(f"- {c.get('symbol','')} | {c['token_address']} | liq={c.get('liquidity')} | mcap={c.get('market_cap')} | {', '.join(c.get('entry_filter_reasons', []))}")
    lines += [
        "",
        "## Safety Boundary",
        "- 候选池只表示进入研究，不表示可以买",
        "- 禁止 live trading / swap / private key / signing / broadcast",
    ]
    return "\n".join(lines) + "\n"


# ── CLI 入口 ──

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Skill 01: meme-candidate-entry")
    parser.add_argument("token_address", help="Solana token CA")
    parser.add_argument("--chain", default="sol")
    parser.add_argument("--source", default="manual_ca")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    result = run(
        token_address=args.token_address,
        chain=args.chain,
        entry_source=args.source,
        entry_reason=args.reason,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
