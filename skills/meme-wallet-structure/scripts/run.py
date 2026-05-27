"""run.py — Skill 04: meme-wallet-structure 主入口"""

from __future__ import annotations

import sys, json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, "/root/sikk-gmgn/skills")
from common.file_io import get_run_dir, save_json, save_markdown
from common.validators import save_validated_json
from common.phase_state import complete_phase, block_phase


def sf(v, d=0.0):
    try: return float(v)
    except Exception: return d


def run(token_address: str, chain: str = "sol") -> dict:
    run_dir = get_run_dir(token_address)
    now = datetime.now(timezone.utc)
    output = _base(token_address, chain, now)

    path = run_dir / "wallet_roles.json"
    if not path.exists():
        output["status"] = "ERROR"
        output["blocker_reasons"].append("wallet_roles.json 不存在或解析失败")
        _save(token_address, output, "ERROR")
        return output

    wallet_roles = json.load(open(path, "r", encoding="utf-8"))
    if wallet_roles.get("status") == "BLOCK":
        output["status"] = "BLOCK"
        output["blocker_reasons"].append("wallet_roles.status = BLOCK")
        _save(token_address, output, "BLOCK")
        return output

    key_wallets = wallet_roles.get("key_wallets", [])
    if len(key_wallets) < 10:
        output["downgrade_reasons"].append("Too few wallets for structure analysis")

    output["same_source_groups"] = _same_source_groups(key_wallets)
    output["coordinated_buy_groups"] = _coordinated_buy_groups(key_wallets)
    output["distribution_groups"] = _distribution_groups(key_wallets)
    output["concentration"] = _concentration(key_wallets)
    output["suspected_controller_wallets"] = _suspected_controllers(key_wallets, output)
    output["structure_risk"] = _structure_risk(output)

    if not any(w.get("native_transfer_from") for w in key_wallets):
        output["downgrade_reasons"].append("No funding source data")
    if not any(w.get("start_holding_at") for w in key_wallets):
        output["downgrade_reasons"].append("No holding timestamp data")

    output["confidence_score"] = max(0.1, min(1.0, 0.8 - len(output["downgrade_reasons"]) * 0.1))
    risk = output["structure_risk"]["overall_structure_risk"]
    output["status"] = "WARN" if risk in ("high", "critical") or output["downgrade_reasons"] else "PASS"

    _save(token_address, output, output["status"])
    _save_md(token_address, output)
    return output


def _is_system_wallet(w):
    """识别 AMM / pool / CEX / 系统地址。系统地址只保留 raw，不参与结构风险计算。"""
    tags = set(w.get("maker_token_tags", []) or []) | set(w.get("tags", []) or [])
    exchange = w.get("exchange") or ""
    addr_type = w.get("addr_type")
    role = w.get("role") or ""
    if addr_type == 2:
        return True
    if exchange:
        return True
    if role in ("pool", "cex", "amm"):
        return True
    if "pool" in tags or "amm" in tags or "cex" in tags:
        return True
    return False


def _analysis_wallets(wallets):
    return [w for w in wallets if not _is_system_wallet(w)]


def _same_source_groups(wallets):
    wallets = _analysis_wallets(wallets)
    groups = defaultdict(list)
    for w in wallets:
        f = w.get("native_transfer_from")
        if f:
            groups[f].append(w)
    out = []
    for funder, ws in groups.items():
        if len(ws) >= 2:
            out.append({
                "funding_source": funder,
                "wallets": [w.get("address") for w in ws],
                "wallet_count": len(ws),
                "combined_holding_pct": sum(sf(w.get("amount_percentage")) for w in ws),
                "combined_usd_value": sum(sf(w.get("usd_value")) for w in ws),
                "group_type": "same_funder",
            })
    return out


def _coordinated_buy_groups(wallets):
    wallets = _analysis_wallets(wallets)
    clusters = defaultdict(list)
    for w in wallets:
        ts = int(w.get("start_holding_at") or 0)
        if ts:
            clusters[ts // 300].append(w)
    out = []
    for bucket, ws in clusters.items():
        if len(ws) >= 3:
            start = bucket * 300
            out.append({
                "time_window_start": start,
                "time_window_end": start + 300,
                "wallets": [w.get("address") for w in ws],
                "wallet_count": len(ws),
                "combined_holding_pct": sum(sf(w.get("amount_percentage")) for w in ws),
            })
    return out


def _distribution_groups(wallets):
    wallets = _analysis_wallets(wallets)
    sellers = [w for w in wallets if sf(w.get("sell_amount_percentage")) > 0.5]
    if len(sellers) < 2:
        return []
    sellers.sort(key=lambda w: sf(w.get("sell_amount_percentage")))
    group = sellers
    return [{
        "pattern": "similar_sell_ratio",
        "wallets": [w.get("address") for w in group],
        "sell_ratio_range": [sf(group[0].get("sell_amount_percentage")), sf(group[-1].get("sell_amount_percentage"))],
        "combined_sold_pct": sum(sf(w.get("sell_amount_percentage")) for w in group),
    }]


def _concentration(wallets):
    wallets = _analysis_wallets(wallets)
    sorted_ws = sorted(wallets, key=lambda w: -sf(w.get("amount_percentage")))
    top5 = sum(sf(w.get("amount_percentage")) for w in sorted_ws[:5])
    top10 = sum(sf(w.get("amount_percentage")) for w in sorted_ws[:10])
    top20 = sum(sf(w.get("amount_percentage")) for w in sorted_ws[:20])
    if top10 > 0.6:
        level = "extreme"
    elif top10 > 0.4:
        level = "high"
    elif top10 > 0.2:
        level = "medium"
    else:
        level = "low"
    return {
        "top5_holder_pct": top5,
        "top10_holder_pct": top10,
        "top20_holder_pct": top20,
        "excluding_pools_and_cex": True,
        "concentration_level": level,
    }


def _suspected_controllers(wallets, output):
    wallets = _analysis_wallets(wallets)
    controllers = []
    addr_to_wallet = {w.get("address"): w for w in wallets}
    for g in output["same_source_groups"]:
        if g["wallet_count"] >= 3:
            controllers.append({
                "address": g["funding_source"],
                "reason": "funding_source_of_multiple",
                "evidence_strength": "strong" if g["combined_holding_pct"] > 0.05 else "moderate",
                "holding_pct": g["combined_holding_pct"],
            })
    sorted_ws = sorted(wallets, key=lambda w: (-sf(w.get("amount_percentage")), int(w.get("start_holding_at") or 999999999)))
    if sorted_ws:
        w = sorted_ws[0]
        if sf(w.get("amount_percentage")) > 0.05:
            controllers.append({
                "address": w.get("address"),
                "reason": "largest_holder_and_early",
                "evidence_strength": "moderate",
                "holding_pct": sf(w.get("amount_percentage")),
            })
    return controllers


def _structure_risk(o):
    same_pct = max([g["combined_holding_pct"] for g in o["same_source_groups"]] or [0])
    coord_pct = max([g["combined_holding_pct"] for g in o["coordinated_buy_groups"]] or [0])
    conc = o["concentration"]["concentration_level"]
    controllers = o["suspected_controller_wallets"]

    if same_pct > 0.4 or any(c["holding_pct"] > 0.3 for c in controllers):
        overall = "critical"
    elif same_pct > 0.2 or len(o["coordinated_buy_groups"]) > 1 or conc in ("high", "extreme"):
        overall = "high"
    elif same_pct > 0 or o["coordinated_buy_groups"] or conc == "medium":
        overall = "medium"
    else:
        overall = "low"

    return {
        "has_same_source_groups": bool(o["same_source_groups"]),
        "same_source_combined_pct": same_pct,
        "has_coordinated_buys": bool(o["coordinated_buy_groups"]),
        "coordinated_buy_combined_pct": coord_pct,
        "has_distribution_pattern": bool(o["distribution_groups"]),
        "concentration_level": conc,
        "overall_structure_risk": overall,
    }


def _base(token_address, chain, now):
    return {
        "schema_version": "1.0", "skill_name": "meme-wallet-structure",
        "task_id": f"{token_address}_{now.strftime('%Y%m%dT%H%M%SZ')}",
        "token_address": token_address, "chain": chain, "timestamp": now.isoformat(), "status": "",
        "same_source_groups": [], "coordinated_buy_groups": [], "distribution_groups": [], "concentration": {},
        "suspected_controller_wallets": [], "structure_risk": {},
        "evidence": [], "counter_evidence": [], "confidence_score": 0.0,
        "downgrade_reasons": [], "blocker_reasons": [], "missing_fields": [],
        "valid_until": (now + timedelta(minutes=60)).isoformat(),
        "next_action": "meme-evidence-chain", "handoff_to": "meme-evidence-chain",
    }


def _save(token_address, output, status):
    save_validated_json(output, get_run_dir(token_address) / "wallet_structure.json")
    if status in ("BLOCK", "ERROR"):
        block_phase(token_address, "wallet_structure", output.get("blocker_reasons", []))
    else:
        complete_phase(token_address, "wallet_structure", status)


def _save_md(token_address, output):
    r = output["structure_risk"]
    md = f"""# Wallet Structure: {token_address}

- Same-source groups: {len(output['same_source_groups'])}
- Coordinated buys: {len(output['coordinated_buy_groups'])}
- Distribution groups: {len(output['distribution_groups'])}
- Concentration: {output['concentration'].get('concentration_level')}
- Overall structure risk: {r.get('overall_structure_risk')}

Status: {output.get('status')}
Next: {output.get('next_action')}
"""
    save_markdown(md, get_run_dir(token_address) / "wallet_structure.md")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("token_address")
    p.add_argument("--chain", default="sol")
    a = p.parse_args()
    print(json.dumps(run(a.token_address, a.chain), ensure_ascii=False, indent=2))
