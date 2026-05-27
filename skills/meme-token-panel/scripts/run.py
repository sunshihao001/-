"""
run.py — Skill 02: meme-token-panel 主入口

流程：token info + security + pool + kline → 组装面板 → risk_score_card → 输出 token_panel.json + token_panel.md
"""

from __future__ import annotations

import sys
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
_script_dir = Path(__file__).parent
sys.path.insert(0, str(_script_dir))

from common.gmgn_client import GmgnClient, GmgnError
from common.file_io import get_run_dir, save_json, save_markdown, load_json
from common.validators import save_validated_json
from common.phase_state import complete_phase, block_phase
from rules import (
    safe_float, safe_int,
    check_hard_blocks, check_warnings, check_pass_conditions,
    build_risk_score_card, check_downgrades,
)


def run(token_address: str, chain: str = "sol", gmgn: GmgnClient | None = None) -> dict:
    if gmgn is None:
        gmgn = GmgnClient()

    now = datetime.now(timezone.utc)
    output = _base_output(token_address, chain, now)

    # 读取前置 candidate_entry（存在则读取，不存在则记录 missing）
    run_dir = get_run_dir(token_address)
    candidate_path = run_dir / "candidate_entry.json"
    if not candidate_path.exists():
        output["missing_fields"].append("candidate_entry.json")
        output["downgrade_reasons"].append("Missing candidate_entry.json")

    # 调用 4 个 GMGN 命令；失败则降级或错误
    try:
        token_info_raw = gmgn.token_info(token_address, chain)
    except Exception as e:
        output["status"] = "ERROR"
        output["blocker_reasons"].append(f"token info failed: {e}")
        _save(token_address, output, "ERROR")
        return output

    try:
        token_security_raw = gmgn.token_security(token_address, chain)
    except Exception as e:
        output["status"] = "ERROR"
        output["blocker_reasons"].append(f"token security failed: {e}")
        _save(token_address, output, "ERROR")
        return output

    try:
        token_pool_raw = gmgn.token_pool(token_address, chain)
    except Exception as e:
        token_pool_raw = {}
        output["downgrade_reasons"].append(f"token pool unavailable: {e}")
        output["missing_fields"].append("pool")

    try:
        to_ts = str(int(time.time()))
        from_ts = str(int(time.time()) - 3600)
        kline_raw = gmgn.market_kline(token_address, chain, "5m", from_ts, to_ts)
    except Exception as e:
        kline_raw = {}
        output["downgrade_reasons"].append(f"kline unavailable: {e}")
        output["missing_fields"].append("kline")

    # 解析响应
    info = _unwrap(token_info_raw)
    security = _unwrap(token_security_raw)
    pool = _unwrap(token_pool_raw)
    kline = _unwrap(kline_raw)

    output["basic_info"] = _build_basic_info(info, pool)
    output["security"] = _build_security(security, info)
    output["wallet_tags_stat"] = _build_wallet_tags_stat(info, security)
    output["dev_info"] = _build_dev_info(info, security)
    output["social"] = _build_social(info)
    output["kline_summary"] = _build_kline_summary(kline)

    # 风险卡
    output["risk_score_card"] = build_risk_score_card(output["security"])

    # BLOCK / WARN / PASS
    blockers = check_hard_blocks(output["security"])
    if blockers:
        output["status"] = "BLOCK"
        output["blocker_reasons"] = blockers
        output["next_action"] = "STOP"
        output["handoff_to"] = ""
        for b in blockers:
            output["evidence"].append({"claim": b, "source": "gmgn token security", "value": None, "weight": "high"})
        _save(token_address, output, "BLOCK")
        return output

    warnings = check_warnings(output["security"], output["basic_info"], output["wallet_tags_stat"])
    for w in warnings:
        output["downgrade_reasons"].append(w)
        output["evidence"].append({"claim": w, "source": "token_panel rules", "value": None, "weight": "medium"})

    # 降级
    output["downgrade_reasons"].extend(
        d for d in check_downgrades(output["basic_info"], output["social"], output["kline_summary"], output["wallet_tags_stat"])
        if d not in output["downgrade_reasons"]
    )

    # 缺失字段
    _collect_missing(output)

    if check_pass_conditions(output["security"], output["basic_info"]) and not warnings:
        output["status"] = "PASS"
    else:
        output["status"] = "WARN" if warnings or output["downgrade_reasons"] else "PASS"

    output["confidence_score"] = max(0.1, min(1.0, 1.0 - len(output["downgrade_reasons"]) * 0.08 - len(output["missing_fields"]) * 0.05))

    _save(token_address, output, output["status"])
    _save_markdown_report(token_address, output)
    return output


def _base_output(token_address: str, chain: str, now: datetime) -> dict:
    return {
        "schema_version": "1.0",
        "skill_name": "meme-token-panel",
        "task_id": f"{token_address}_{now.strftime('%Y%m%dT%H%M%SZ')}",
        "token_address": token_address,
        "chain": chain,
        "timestamp": now.isoformat(),
        "status": "",
        "basic_info": {},
        "security": {},
        "wallet_tags_stat": {},
        "dev_info": {},
        "social": {},
        "kline_summary": None,
        "risk_score_card": {},
        "evidence": [],
        "counter_evidence": [],
        "confidence_score": 0.0,
        "downgrade_reasons": [],
        "blocker_reasons": [],
        "missing_fields": [],
        "valid_until": (now + timedelta(minutes=30)).isoformat(),
        "next_action": "meme-wallet-roles",
        "handoff_to": "meme-wallet-roles",
    }


def _unwrap(raw: dict) -> dict:
    if not isinstance(raw, dict):
        return {}
    data = raw.get("data", raw)
    if isinstance(data, dict) and "token" in data:
        data = data["token"]
    return data if isinstance(data, dict) else {}


def _build_basic_info(info: dict, pool: dict) -> dict:
    price_val = safe_float((info.get("price") or {}).get("price") if isinstance(info.get("price"), dict) else info.get("price"))
    total_supply_val = safe_float(info.get("total_supply"))
    market_cap_val = safe_float(info.get("market_cap", info.get("fdv", info.get("migration_market_cap"))))
    if market_cap_val == 0 and price_val > 0 and total_supply_val > 0:
        market_cap_val = price_val * total_supply_val
    return {
        "symbol": info.get("symbol", ""),
        "name": info.get("name", ""),
        "price": price_val,
        "market_cap": market_cap_val,
        "liquidity": safe_float(info.get("liquidity", pool.get("liquidity"))),
        "holder_count": safe_int(info.get("holder_count", (info.get("stat") or {}).get("holder_count"))),
        "total_supply": total_supply_val,
        "pair_age_seconds": safe_int(info.get("pair_age_seconds", info.get("age_seconds"))),
        "launchpad": info.get("launchpad", ""),
        "launchpad_status": safe_int(info.get("launchpad_status")),
        "pool_address": info.get("biggest_pool_address", info.get("pool_address", pool.get("address", ""))),
        "pool_exchange": pool.get("exchange", info.get("pool_exchange", "")),
        "ath_price": safe_float(info.get("ath_price")),
    }


def _build_security(security: dict, info: dict) -> dict:
    dev = info.get("dev") or {}
    stat = info.get("stat") or {}
    return {
        "is_honeypot": security.get("is_honeypot", info.get("is_honeypot", "")),
        "renounced_mint": bool(security.get("renounced_mint", info.get("renounced_mint", security.get("mint_authority_renounced", False)))),
        "renounced_freeze_account": bool(security.get("renounced_freeze_account", info.get("renounced_freeze_account", security.get("freeze_authority_renounced", False)))),
        "open_source": security.get("open_source", info.get("is_open_source", "")),
        "owner_renounced": security.get("owner_renounced", info.get("is_renounced", "")),
        "buy_tax": safe_float(security.get("buy_tax", info.get("buy_tax"))),
        "sell_tax": safe_float(security.get("sell_tax", info.get("sell_tax"))),
        "rug_ratio": safe_float(security.get("rug_ratio", info.get("rug_ratio"))),
        "top_10_holder_rate": safe_float(security.get("top_10_holder_rate", info.get("top_10_holder_rate", dev.get("top_10_holder_rate", stat.get("top_10_holder_rate"))))),
        "creator_token_status": security.get("creator_token_status", info.get("creator_token_status", dev.get("creator_token_status", ""))),
        "creator_balance_rate": safe_float(security.get("creator_balance_rate", info.get("creator_balance_rate", stat.get("creator_hold_rate")))),
        "dev_team_hold_rate": safe_float(security.get("dev_team_hold_rate", info.get("dev_team_hold_rate", stat.get("dev_team_hold_rate")))),
        "suspected_insider_hold_rate": safe_float(security.get("suspected_insider_hold_rate")),
        "is_wash_trading": bool(security.get("is_wash_trading", False)),
        "rat_trader_amount_rate": safe_float(security.get("rat_trader_amount_rate")),
        "bundler_trader_amount_rate": safe_float(security.get("bundler_trader_amount_rate")),
        "sniper_count": safe_int(security.get("sniper_count")),
        "burn_status": security.get("burn_status", ""),
    }


def _build_wallet_tags_stat(info: dict, security: dict) -> dict:
    stat = info.get("wallet_tags_stat", security.get("wallet_tags_stat", {})) or {}
    return {
        "smart_wallets": safe_int(stat.get("smart_wallets", info.get("smart_degen_count"))),
        "renowned_wallets": safe_int(stat.get("renowned_wallets", info.get("renowned_count"))),
        "sniper_wallets": safe_int(stat.get("sniper_wallets", security.get("sniper_count"))),
        "rat_trader_wallets": safe_int(stat.get("rat_trader_wallets", security.get("rat_trader_count"))),
        "bundler_wallets": safe_int(stat.get("bundler_wallets", security.get("bundler_count"))),
        "whale_wallets": safe_int(stat.get("whale_wallets")),
        "fresh_wallets": safe_int(stat.get("fresh_wallets", security.get("fresh_wallet_count"))),
    }


def _build_dev_info(info: dict, security: dict) -> dict:
    dev = info.get("dev") or {}
    return {
        "creator_address": info.get("creator_address", security.get("creator_address", dev.get("creator_address", ""))),
        "creator_token_balance": str(security.get("creator_token_balance", dev.get("creator_token_balance", ""))),
        "creator_open_count": safe_int(info.get("creator_open_count", security.get("creator_open_count", dev.get("creator_open_count")))),
        "fund_from": info.get("fund_from", security.get("fund_from", dev.get("fund_from", ""))),
        "cto_flag": safe_int(info.get("cto_flag")),
        "dexscr_ad": safe_int(info.get("dexscr_ad")),
        "dexscr_update_link": safe_int(info.get("dexscr_update_link")),
    }


def _build_social(info: dict) -> dict:
    link = info.get("link") or {}
    return {
        "twitter_username": info.get("twitter_username", link.get("twitter_username", "")),
        "website": info.get("website", link.get("website", "")),
        "telegram": info.get("telegram", link.get("telegram", "")),
    }


def _build_kline_summary(kline: dict) -> dict | None:
    candles = kline.get("candles") or kline.get("list") or kline.get("items") or []
    if not candles:
        return None

    def cget(c, key, idx=None):
        if isinstance(c, dict):
            return c.get(key, 0)
        if isinstance(c, (list, tuple)) and idx is not None and len(c) > idx:
            return c[idx]
        return 0

    first = candles[0]
    last = candles[-1]
    opens = safe_float(cget(first, "open", 1))
    close = safe_float(cget(last, "close", 4))
    highs = [safe_float(cget(c, "high", 2)) for c in candles]
    lows = [safe_float(cget(c, "low", 3)) for c in candles]
    volumes = [safe_float(cget(c, "volume", 5)) for c in candles]

    trend = "sideways"
    if close > opens * 1.05:
        trend = "up"
    elif close < opens * 0.95:
        trend = "down"
    elif max(highs or [0]) > max(opens, close) * 1.2:
        trend = "volatile"

    return {
        "resolution": "5m",
        "period": "1h",
        "open": opens,
        "close": close,
        "high": max(highs) if highs else 0.0,
        "low": min(lows) if lows else 0.0,
        "total_volume_usd": sum(volumes),
        "trend": trend,
    }


def _collect_missing(output: dict) -> None:
    if not output["basic_info"].get("symbol"):
        output["missing_fields"].append("basic_info.symbol")
    if output["basic_info"].get("liquidity", 0) == 0:
        output["missing_fields"].append("basic_info.liquidity")
    if output["security"].get("is_honeypot", "") == "":
        output["missing_fields"].append("security.is_honeypot")
    if output["security"].get("creator_token_status", "") == "":
        output["missing_fields"].append("security.creator_token_status")


def _save(token_address: str, output: dict, status: str) -> None:
    run_dir = get_run_dir(token_address)
    save_validated_json(output, run_dir / "token_panel.json")
    if status in ("BLOCK", "ERROR"):
        block_phase(token_address, "token_panel", output.get("blocker_reasons", []))
    else:
        complete_phase(token_address, "token_panel", status)


def _save_markdown_report(token_address: str, output: dict) -> None:
    basic = output["basic_info"]
    risk = output["risk_score_card"]
    dev = output["dev_info"]
    kline = output["kline_summary"] or {}

    md = f"""# Token Panel: {basic.get('symbol')} ({basic.get('name')})

## 基础信息
- Price: ${basic.get('price')}
- Market Cap: ${basic.get('market_cap')}
- Liquidity: ${basic.get('liquidity')}
- Holders: {basic.get('holder_count')}
- Pool: {basic.get('pool_exchange')}
- Age: {basic.get('pair_age_seconds')}s

## 安全评分
- Honeypot: {risk.get('honeypot')}
- Mint Authority: {risk.get('mint_authority')}
- Freeze Authority: {risk.get('freeze_authority')}
- Rug Ratio Level: {risk.get('rug_ratio_level')}
- Concentration: {risk.get('concentration_level')}
- Dev Status: {risk.get('dev_status')}
- Wash Trading: {risk.get('wash_trading')}
- Overall Risk: {risk.get('overall_risk')}

## Smart Money
- Smart Money Holders: {output['wallet_tags_stat'].get('smart_wallets')}
- KOL Holders: {output['wallet_tags_stat'].get('renowned_wallets')}

## Dev 信息
- Creator: {dev.get('creator_address')}
- Status: {output['security'].get('creator_token_status')}
- 历史发币数: {dev.get('creator_open_count')}

## 1h K线
- Open → Close: ${kline.get('open')} → ${kline.get('close')}
- Range: ${kline.get('low')} - ${kline.get('high')}
- Volume: ${kline.get('total_volume_usd')}
- Trend: {kline.get('trend')}

## 风险警告
{chr(10).join('- ' + x for x in output.get('blocker_reasons', []) + output.get('downgrade_reasons', []))}

## 判定
Status: {output.get('status')}
Next: {output.get('next_action')}
"""
    save_markdown(md, get_run_dir(token_address) / "token_panel.md")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skill 02: meme-token-panel")
    parser.add_argument("token_address")
    parser.add_argument("--chain", default="sol")
    args = parser.parse_args()
    print(json.dumps(run(args.token_address, args.chain), ensure_ascii=False, indent=2))
