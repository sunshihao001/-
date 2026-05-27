"""
run.py — Skill 03: meme-wallet-roles 主入口
"""

from __future__ import annotations

import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
_script_dir = Path(__file__).parent
sys.path.insert(0, str(_script_dir))

from common.gmgn_client import GmgnClient
from common.file_io import get_run_dir, save_json, save_markdown
from common.validators import save_validated_json
from common.phase_state import complete_phase, block_phase
from rules import classify_role, classify_sm_behavior, classify_dev_profile


def run(token_address: str, chain: str = "sol", gmgn: GmgnClient | None = None) -> dict:
    if gmgn is None:
        gmgn = GmgnClient()

    run_dir = get_run_dir(token_address)
    now = datetime.now(timezone.utc)
    output = _base_output(token_address, chain, now)

    # 读取 token_panel
    token_panel_path = run_dir / "token_panel.json"
    if not token_panel_path.exists():
        output["status"] = "ERROR"
        output["blocker_reasons"].append("Missing token_panel.json")
        _save(token_address, output, "ERROR")
        return output

    token_panel = json.load(open(token_panel_path, "r", encoding="utf-8"))

    # 查询 holders / traders / dev
    holders = []
    raw_holders = {}
    try:
        raw_holders = gmgn.token_holders(token_address, chain, limit=50)
    except Exception as e:
        output["status"] = "ERROR"
        output["blocker_reasons"].append(f"holders API failed: {e}")
        _save(token_address, output, "ERROR")
        return output

    data = raw_holders.get("data", raw_holders)
    if isinstance(data, list):
        holders = data
    elif isinstance(data, dict):
        holders = data.get("items", data.get("holders", data.get("list", [])))
    else:
        holders = []

    if len(holders) < 10:
        output["downgrade_reasons"].append("Too few holders to analyze")

    # 角色分类
    key_wallets = [classify_role(w) for w in holders]
    output["key_wallets"] = key_wallets

    # 汇总
    summary = {
        "total_holders_sampled": len(key_wallets),
        "smart_money_count": 0,
        "smart_money_total_pct": 0.0,
        "kol_count": 0,
        "kol_total_pct": 0.0,
        "sniper_count": 0,
        "bundler_count": 0,
        "rat_trader_count": 0,
        "fresh_wallet_count": 0,
        "dev_wallet_count": 0,
    }
    for w in key_wallets:
        role = w["role"]
        pct = w["amount_percentage"]
        if role == "smart_money":
            summary["smart_money_count"] += 1
            summary["smart_money_total_pct"] += pct
        elif role == "kol":
            summary["kol_count"] += 1
            summary["kol_total_pct"] += pct
        elif role == "sniper":
            summary["sniper_count"] += 1
        elif role == "bundler":
            summary["bundler_count"] += 1
        elif role == "rat_trader":
            summary["rat_trader_count"] += 1
        elif role == "fresh_wallet":
            summary["fresh_wallet_count"] += 1
        elif role == "dev":
            summary["dev_wallet_count"] += 1
    output["wallet_summary"] = summary

    # SM 行为
    output["smart_money_behavior"] = classify_sm_behavior(key_wallets)

    # Dev profile
    creator = token_panel.get("dev_info", {}).get("creator_address", "")
    dev_wallet = None
    if creator:
        try:
            created = gmgn.portfolio_created_tokens(creator, chain)
            stats = gmgn.portfolio_stats(creator, chain, period="30d")
            dev_wallet = _merge_dev_data(creator, token_panel, created, stats)
        except Exception:
            output["downgrade_reasons"].append("Dev history unavailable")
            dev_wallet = None
    output["dev_profile"] = classify_dev_profile(token_panel, dev_wallet)

    # 早期买家分析
    output["early_buyer_analysis"] = _build_early_buyer_analysis(key_wallets)

    # Missing + downgrade
    if summary["smart_money_count"] == 0:
        output["downgrade_reasons"].append("No smart money data")
    if summary["fresh_wallet_count"] / max(summary["total_holders_sampled"], 1) > 0.5:
        output["downgrade_reasons"].append("High fresh wallet ratio")

    # 状态
    if output["blocker_reasons"]:
        output["status"] = "BLOCK"
    elif output["downgrade_reasons"]:
        output["status"] = "WARN"
    else:
        output["status"] = "PASS"

    output["confidence_score"] = max(0.1, min(1.0, 1.0 - len(output["downgrade_reasons"]) * 0.08 - len(output["missing_fields"]) * 0.05))

    _save(token_address, output, output["status"])
    _save_markdown(token_address, output)
    return output


def _base_output(token_address: str, chain: str, now: datetime) -> dict:
    return {
        "schema_version": "1.0",
        "skill_name": "meme-wallet-roles",
        "task_id": f"{token_address}_{now.strftime('%Y%m%dT%H%M%SZ')}",
        "token_address": token_address,
        "chain": chain,
        "timestamp": now.isoformat(),
        "status": "",
        "wallet_summary": {},
        "key_wallets": [],
        "dev_profile": {},
        "smart_money_behavior": {},
        "early_buyer_analysis": {},
        "evidence": [],
        "counter_evidence": [],
        "confidence_score": 0.0,
        "downgrade_reasons": [],
        "blocker_reasons": [],
        "missing_fields": [],
        "valid_until": (now + timedelta(minutes=60)).isoformat(),
        "next_action": "meme-wallet-structure",
        "handoff_to": "meme-wallet-structure",
    }


def _merge_dev_data(creator: str, token_panel: dict, created: dict, stats: dict) -> dict:
    created_data = created.get("data", created)
    stats_data = stats.get("data", stats)
    if isinstance(created_data, dict):
        items = created_data.get("items", created_data.get("tokens", []))
    else:
        items = created_data if isinstance(created_data, list) else []
    best_mc = 0.0
    best_symbol = ""
    graduated_count = 0
    total_tokens = len(items)
    for t in items:
        mc = float(t.get("token_ath_mc", t.get("ath_mc", 0)) or 0)
        if mc > best_mc:
            best_mc = mc
            best_symbol = t.get("symbol", "")
        if t.get("status") in ("graduated", "success"):
            graduated_count += 1
    return {
        "creator_address": creator,
        "creator_token_status": token_panel.get("security", {}).get("creator_token_status", ""),
        "total_tokens_created": total_tokens,
        "graduated_count": graduated_count,
        "graduation_ratio": graduated_count / total_tokens if total_tokens else 0.0,
        "best_token_ath_mc": best_mc,
        "best_token_symbol": best_symbol,
        "dev_30d_winrate": float(stats_data.get("winrate", 0) or 0),
        "dev_30d_pnl": float(stats_data.get("pnl", 0) or 0),
        "fund_from_address": token_panel.get("dev_info", {}).get("fund_from", ""),
    }


def _build_early_buyer_analysis(wallets: list[dict]) -> dict:
    earliest = None
    for w in wallets:
        if earliest is None or (w.get("start_holding_at", 0) and w.get("start_holding_at", 0) < earliest.get("start_holding_at", 0)):
            earliest = w
    if not earliest:
        return {
            "earliest_buyer_address": "",
            "earliest_buyer_tags": [],
            "earliest_buyer_still_holding": False,
            "earliest_buyer_profit": 0.0,
            "top5_early_buyers_funding_sources": [],
        }
    return {
        "earliest_buyer_address": earliest.get("address", ""),
        "earliest_buyer_tags": earliest.get("gmgn_hint", []),
        "earliest_buyer_still_holding": not earliest.get("is_selling", False),
        "earliest_buyer_profit": float(earliest.get("unrealized_profit", 0.0)),
        "top5_early_buyers_funding_sources": [w.get("native_transfer_from", "") for w in wallets[:5] if w.get("native_transfer_from")],
    }


def _save(token_address: str, output: dict, status: str) -> None:
    run_dir = get_run_dir(token_address)
    save_json(output, run_dir / "wallet_roles.json")
    if status == "BLOCK":
        block_phase(token_address, "wallet_roles", output.get("blocker_reasons", []))
    else:
        complete_phase(token_address, "wallet_roles", status)


def _save_markdown(token_address: str, output: dict) -> None:
    summary = output["wallet_summary"]
    sm = output["smart_money_behavior"]
    dev = output["dev_profile"]
    md = f"""# Wallet Roles: {token_address}

## 概览
- Holders Sampled: {summary.get('total_holders_sampled')}
- Smart Money: {summary.get('smart_money_count')} ({summary.get('smart_money_total_pct'):.2%})
- KOL: {summary.get('kol_count')} ({summary.get('kol_total_pct'):.2%})
- Sniper: {summary.get('sniper_count')}
- Bundler: {summary.get('bundler_count')}
- Rat Trader: {summary.get('rat_trader_count')}
- Fresh Wallet: {summary.get('fresh_wallet_count')}
- Dev Wallet: {summary.get('dev_wallet_count')}

## SM 行为
- Direction: {sm.get('sm_net_direction')}
- Avg PnL: {sm.get('sm_avg_unrealized_pnl')}

## Dev
- Creator: {dev.get('creator_address')}
- Status: {dev.get('dev_status')}
- Graduation Ratio: {dev.get('graduation_ratio'):.2%}
- Best Token ATH MC: {dev.get('best_token_ath_mc')}

## 判定
Status: {output.get('status')}
Next: {output.get('next_action')}
"""
    save_markdown(md, get_run_dir(token_address) / "wallet_roles.md")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skill 03: meme-wallet-roles")
    parser.add_argument("token_address")
    parser.add_argument("--chain", default="sol")
    args = parser.parse_args()
    print(json.dumps(run(args.token_address, args.chain), ensure_ascii=False, indent=2))
