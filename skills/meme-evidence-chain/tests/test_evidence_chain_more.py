"""补充回归测试 — Skill 05 evidence-chain 边界路径。"""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
_RUN_PATH = Path("/root/sikk-gmgn/skills/meme-evidence-chain/scripts/run.py")
sys.modules.pop("run", None)
sys.modules.pop("rules", None)
spec = importlib.util.spec_from_file_location("evidence_chain_run_more", _RUN_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

from common.file_io import get_run_dir, save_json


def test_evidence_chain_missing_upstream_files_returns_error():
    token = "TestEvidenceMissing11111111111111111111111111"
    res = mod.run(token)

    assert res["status"] == "ERROR"
    assert res["dominant_behavior"] == "UNKNOWN"
    assert res["gate_decision"] if "gate_decision" in res else True
    assert any("前置文件缺失或解析失败" in x for x in res["blocker_reasons"])
    assert (get_run_dir(token) / "evidence_chain.json").exists()


def test_evidence_chain_propagates_token_panel_block():
    token = "TestEvidenceBlock111111111111111111111111111"
    rd = get_run_dir(token)
    save_json({"status": "BLOCK", "blocker_reasons": ["security block"]}, rd / "token_panel.json")
    save_json({"status": "PASS"}, rd / "wallet_roles.json")
    save_json({"status": "PASS"}, rd / "wallet_structure.json")

    res = mod.run(token)

    assert res["status"] == "BLOCK"
    assert "token_panel.status = BLOCK" in res["blocker_reasons"]
    assert (rd / "evidence_chain.json").exists()


def test_evidence_chain_distribution_divergence_becomes_need_more_data():
    token = "TestEvidenceDivergence1111111111111111111111"
    rd = get_run_dir(token)
    save_json(
        {
            "status": "PASS",
            "basic_info": {"symbol": "DIV"},
            "security": {"is_wash_trading": False},
            "kline_summary": {"trend": "up"},
            "downgrade_reasons": [],
            "missing_fields": [],
        },
        rd / "token_panel.json",
    )
    save_json(
        {
            "status": "PASS",
            "smart_money_behavior": {"sm_net_direction": "distributing"},
            "wallet_summary": {"fresh_wallet_count": 0, "total_holders_sampled": 20, "smart_money_count": 2},
            "dev_profile": {"creator_token_status": "creator_hold", "creator_balance_rate": 0.01},
            "downgrade_reasons": [],
            "missing_fields": [],
        },
        rd / "wallet_roles.json",
    )
    save_json(
        {
            "status": "PASS",
            "same_source_groups": [{"group": "mock"}],
            "structure_risk": {
                "has_same_source_groups": False,
                "same_source_combined_pct": 0,
                "overall_structure_risk": "low",
            },
            "downgrade_reasons": [],
            "missing_fields": [],
        },
        rd / "wallet_structure.json",
    )

    res = mod.run(token)

    behaviors = {s["behavior"] for s in res["behavior_signals"]}
    assert {"DISTRIBUTION", "DIVERGENCE"}.issubset(behaviors)
    assert res["dominant_behavior"] == "UNKNOWN"
    assert res["status"] == "NEED_MORE_DATA"
    assert any(r["factor"] == "DIVERGENCE" for r in res["risk_factors"])
    assert "一定会涨" not in res["narrative"]["paragraph"]
