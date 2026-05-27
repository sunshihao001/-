"""run.py — Skill 05: meme-evidence-chain 主入口"""

from __future__ import annotations

import sys, json
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
from common.file_io import get_run_dir, save_json, save_markdown
from common.validators import save_validated_json
from common.phase_state import complete_phase, block_phase

FORBIDDEN_TERMS = ["确定庄家", "确定内幕", "一定会涨", "一定会跌", "买入建议", "卖出建议"]


def sf(v, d=0.0):
    try: return float(v)
    except Exception: return d


def run(token_address: str, chain: str = "sol") -> dict:
    run_dir = get_run_dir(token_address)
    now = datetime.now(timezone.utc)
    output = _base(token_address, chain, now)

    try:
        token_panel = json.load(open(run_dir / "token_panel.json", "r", encoding="utf-8"))
        wallet_roles = json.load(open(run_dir / "wallet_roles.json", "r", encoding="utf-8"))
        wallet_structure = json.load(open(run_dir / "wallet_structure.json", "r", encoding="utf-8"))
    except Exception as e:
        output["status"] = "ERROR"
        output["blocker_reasons"].append(f"前置文件缺失或解析失败: {e}")
        _save(token_address, output, "ERROR")
        return output

    if token_panel.get("status") == "BLOCK":
        output["status"] = "BLOCK"
        output["blocker_reasons"].append("token_panel.status = BLOCK")
        _save(token_address, output, "BLOCK")
        return output

    signals = infer_behavior(token_panel, wallet_roles, wallet_structure)
    output["behavior_signals"] = signals
    output["dominant_behavior"] = classify_behavior(signals)
    output["confidence_score"] = calculate_confidence(
        signals,
        len(token_panel.get("downgrade_reasons", [])) + len(wallet_roles.get("downgrade_reasons", [])) + len(wallet_structure.get("downgrade_reasons", [])),
        len(token_panel.get("missing_fields", [])) + len(wallet_roles.get("missing_fields", [])) + len(wallet_structure.get("missing_fields", [])),
    )
    output["risk_factors"] = build_risk_factors(signals, token_panel, wallet_structure)
    output["positive_signals"] = build_positive_signals(signals, wallet_roles, wallet_structure)
    output["evidence_summary"] = {
        "total_evidence_count": len(signals),
        "high_weight_count": sum(1 for s in signals if s["weight"] == "high"),
        "medium_weight_count": sum(1 for s in signals if s["weight"] == "medium"),
        "low_weight_count": sum(1 for s in signals if s["weight"] == "low"),
        "counter_evidence_count": 0,
    }
    output["narrative"] = build_narrative(output, token_panel, wallet_roles, wallet_structure)

    # 禁止措辞过滤
    text = json.dumps(output["narrative"], ensure_ascii=False)
    for term in FORBIDDEN_TERMS:
        if term in text:
            output["narrative"]["paragraph"] = output["narrative"]["paragraph"].replace(term, "疑似结构")

    # 降级
    if not wallet_structure.get("same_source_groups"):
        output["downgrade_reasons"].append("No funding source data for structure")
    if wallet_roles.get("wallet_summary", {}).get("smart_money_count", 0) == 0:
        output["downgrade_reasons"].append("No smart money data")
    if not token_panel.get("kline_summary"):
        output["downgrade_reasons"].append("No price trend data")
    if has_conflict(signals):
        output["downgrade_reasons"].append("Conflicting signals")

    if output["dominant_behavior"] == "UNKNOWN" or output["confidence_score"] < 0.4:
        output["status"] = "NEED_MORE_DATA"
    elif output["confidence_score"] < 0.6:
        output["status"] = "WARN"
    else:
        output["status"] = "PASS"

    _save(token_address, output, output["status"])
    _save_md(token_address, output)
    return output


def infer_behavior(token_panel, wallet_roles, wallet_structure):
    signals = []
    sm = wallet_roles.get("smart_money_behavior", {})
    if sm.get("sm_net_direction") == "accumulating":
        signals.append(sig("ACCUMULATION", "high", "Smart money accumulating", "wallet_roles", "smart_money_behavior.sm_net_direction"))
    elif sm.get("sm_net_direction") == "distributing":
        signals.append(sig("DISTRIBUTION", "high", "Smart money distributing", "wallet_roles", "smart_money_behavior.sm_net_direction"))

    struct = wallet_structure.get("structure_risk", {})
    if struct.get("has_same_source_groups") and sf(struct.get("same_source_combined_pct")) > 0.2:
        signals.append(sig("CONTROLLED", "medium", f"Same-source groups hold {sf(struct.get('same_source_combined_pct')):.0%}", "wallet_structure", "structure_risk.same_source_combined_pct"))

    dev = wallet_roles.get("dev_profile", {})
    if dev.get("creator_token_status") == "creator_hold" and sf(dev.get("creator_balance_rate")) > 0.05:
        signals.append(sig("DEV_RISK", "medium", "Dev holding significant position", "wallet_roles", "dev_profile.creator_token_status"))
    elif dev.get("creator_token_status") == "creator_close":
        signals.append(sig("DEV_EXITED", "low", "Dev has exited", "wallet_roles", "dev_profile.creator_token_status"))

    if token_panel.get("security", {}).get("is_wash_trading"):
        signals.append(sig("WASH_TRADING", "high", "Wash trading detected", "token_panel", "security.is_wash_trading"))

    if token_panel.get("kline_summary", {}).get("trend") == "up" and sm.get("sm_net_direction") == "distributing":
        signals.append(sig("DIVERGENCE", "high", "Price up but SM distributing", "token_panel+wallet_roles", "kline_summary.trend+sm_net_direction"))

    summary = wallet_roles.get("wallet_summary", {})
    if summary.get("fresh_wallet_count", 0) / max(summary.get("total_holders_sampled", 1), 1) > 0.5:
        signals.append(sig("ARTIFICIAL", "medium", "Majority fresh wallets", "wallet_roles", "wallet_summary.fresh_wallet_count"))

    return signals


def sig(behavior, weight, reason, source_skill, source_field):
    return {"behavior": behavior, "weight": weight, "reason": reason, "source_skill": source_skill, "source_field": source_field}


def calculate_confidence(signals, downgrade_count, missing_count):
    base = 0.8
    for s in signals:
        if s["weight"] == "high": base += 0.05
        elif s["weight"] == "medium": base += 0.03
    base -= downgrade_count * 0.1
    base -= missing_count * 0.05
    return max(0.1, min(1.0, base))


def classify_behavior(signals):
    behaviors = [s["behavior"] for s in signals]
    if "WASH_TRADING" in behaviors: return "WASH"
    if "DIVERGENCE" in behaviors: return "UNKNOWN"
    if "DISTRIBUTION" in behaviors: return "DISTRIBUTION"
    if "CONTROLLED" in behaviors: return "CONTROLLED"
    if "ACCUMULATION" in behaviors and "CONTROLLED" not in behaviors: return "ACCUMULATION"
    if "DEV_EXITED" in behaviors and "ACCUMULATION" in behaviors: return "EARLY_STAGE"
    return "UNKNOWN"


def has_conflict(signals):
    bs = {s["behavior"] for s in signals}
    return ("ACCUMULATION" in bs and "CONTROLLED" in bs) or ("ACCUMULATION" in bs and "DISTRIBUTION" in bs)


def build_risk_factors(signals, token_panel, wallet_structure):
    out = []
    for s in signals:
        if s["behavior"] in ("DISTRIBUTION", "WASH_TRADING", "CONTROLLED", "DIVERGENCE", "ARTIFICIAL", "DEV_RISK"):
            out.append({"factor": s["behavior"], "severity": "high" if s["weight"] == "high" else "medium", "source": s["source_skill"]})
    return out


def build_positive_signals(signals, wallet_roles, wallet_structure):
    out = []
    for s in signals:
        if s["behavior"] in ("ACCUMULATION", "DEV_EXITED"):
            out.append({"signal": s["behavior"], "strength": "strong" if s["weight"] == "high" else "moderate", "source": s["source_skill"]})
    return out


def build_narrative(output, token_panel, wallet_roles, wallet_structure):
    symbol = token_panel.get("basic_info", {}).get("symbol", output["token_address"][:8])
    sm = wallet_roles.get("smart_money_behavior", {}).get("sm_net_direction", "unknown")
    level = wallet_structure.get("structure_risk", {}).get("overall_structure_risk", "unknown")
    dev = wallet_roles.get("dev_profile", {}).get("creator_token_status", "unknown")
    one = f"{symbol}: {output['dominant_behavior']}. SM {sm}, structure risk {level}, dev {dev}. Confidence {output['confidence_score']:.2f}."
    reasons = "；".join(s["reason"] for s in output["behavior_signals"][:3]) or "证据不足"
    risks = ", ".join(r["factor"] for r in output["risk_factors"]) or "无明显风险因子"
    para = f"{symbol} 当前主导行为判断为 {output['dominant_behavior']}。证据：{reasons}。风险因素：{risks}。置信度 {output['confidence_score']:.2f}，降级原因：{output['downgrade_reasons'] or '无'}。"
    return {"one_line": one, "paragraph": para}


def _base(token_address, chain, now):
    return {"schema_version":"1.0","skill_name":"meme-evidence-chain","task_id":f"{token_address}_{now.strftime('%Y%m%dT%H%M%SZ')}","token_address":token_address,"chain":chain,"timestamp":now.isoformat(),"status":"","dominant_behavior":"UNKNOWN","behavior_signals":[],"narrative":{},"evidence_summary":{},"risk_factors":[],"positive_signals":[],"evidence":[],"counter_evidence":[],"confidence_score":0.0,"downgrade_reasons":[],"blocker_reasons":[],"missing_fields":[],"valid_until":(now+timedelta(minutes=30)).isoformat(),"next_action":"meme-trade-gate","handoff_to":"meme-trade-gate"}


def _save(token_address, output, status):
    save_validated_json(output, get_run_dir(token_address) / "evidence_chain.json")
    if status in ("BLOCK", "ERROR"):
        block_phase(token_address, "evidence_chain", output.get("blocker_reasons", []))
    else:
        complete_phase(token_address, "evidence_chain", status)


def _save_md(token_address, output):
    md = f"# Evidence Chain: {token_address}\n\n{output['narrative'].get('paragraph','')}\n\nStatus: {output['status']}\nNext: {output['next_action']}\n"
    save_markdown(md, get_run_dir(token_address) / "evidence_chain.md")

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("token_address"); p.add_argument("--chain",default="sol"); a=p.parse_args()
    print(json.dumps(run(a.token_address,a.chain), ensure_ascii=False, indent=2))
