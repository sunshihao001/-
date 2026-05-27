"""补充回归测试 — Skill 06 trade-gate 边界与复杂规则。"""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
_RUN_PATH = Path("/root/sikk-gmgn/skills/meme-trade-gate/scripts/run.py")
sys.modules.pop("run", None)
sys.modules.pop("rules", None)
spec = importlib.util.spec_from_file_location("trade_gate_run_more", _RUN_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

from common.file_io import get_run_dir, save_json


def _write_inputs(token, *, token_panel=None, wallet_roles=None, wallet_structure=None, evidence_chain=None):
    rd = get_run_dir(token)
    tp = token_panel or {
        "status": "PASS",
        "basic_info": {"liquidity": 100000},
        "security": {
            "is_honeypot": "no",
            "renounced_mint": True,
            "renounced_freeze_account": True,
            "rug_ratio": 0.05,
            "top_10_holder_rate": 0.15,
            "creator_token_status": "creator_close",
            "is_wash_trading": False,
        },
        "downgrade_reasons": [],
        "missing_fields": [],
    }
    wr = wallet_roles or {
        "status": "PASS",
        "wallet_summary": {"smart_money_count": 3, "kol_count": 1, "bundler_count": 0},
        "smart_money_behavior": {"sm_net_direction": "accumulating", "sm_avg_unrealized_pnl": 10},
        "downgrade_reasons": [],
        "missing_fields": [],
    }
    ws = wallet_structure or {
        "status": "PASS",
        "structure_risk": {"overall_structure_risk": "low"},
        "downgrade_reasons": [],
        "missing_fields": [],
    }
    ev = evidence_chain or {
        "status": "PASS",
        "dominant_behavior": "ACCUMULATION",
        "confidence_score": 0.8,
        "behavior_signals": [],
        "counter_evidence": [],
        "downgrade_reasons": [],
        "missing_fields": [],
    }
    save_json(tp, rd / "token_panel.json")
    save_json(wr, rd / "wallet_roles.json")
    save_json(ws, rd / "wallet_structure.json")
    save_json(ev, rd / "evidence_chain.json")
    return rd


def test_trade_gate_missing_upstream_files_returns_need_more_data_error():
    token = "TestTradeMissing111111111111111111111111111"
    res = mod.run(token)

    assert res["status"] == "ERROR"
    assert res["gate_decision"] == "NEED_MORE_DATA"
    assert any("前置文件缺失" in x for x in res["blocker_reasons"])
    assert (get_run_dir(token) / "trade_gate.json").exists()


def test_trade_gate_token_panel_block_maps_to_gate_block_but_phase_pass():
    token = "TestTradePanelBlock111111111111111111111111"
    _write_inputs(token, token_panel={"status": "BLOCK", "blocker_reasons": ["token risk"]})

    res = mod.run(token)

    assert res["status"] == "PASS"
    assert res["gate_decision"] == "BLOCK"
    assert "token_panel.status = BLOCK" in res["blocker_reasons"]


def test_trade_gate_missing_fields_force_need_more_data():
    token = "TestTradeMissingFields111111111111111111111"
    _write_inputs(token, evidence_chain={
        "status": "PASS",
        "dominant_behavior": "ACCUMULATION",
        "confidence_score": 0.8,
        "behavior_signals": [],
        "counter_evidence": [],
        "downgrade_reasons": [],
        "missing_fields": ["wallet_roles.smart_money_behavior"],
    })

    res = mod.run(token)

    assert res["gate_decision"] == "NEED_MORE_DATA"
    assert "wallet_roles.smart_money_behavior" in res["missing_fields"]
    assert res["phase_permission"]["paper_allowed"] is False


def test_trade_gate_complex_unrenounced_rule_requires_both_mint_and_freeze_false():
    token = "TestTradeG03BothFalse111111111111111111111"
    _write_inputs(token, token_panel={
        "status": "PASS",
        "basic_info": {"liquidity": 100000},
        "security": {
            "is_honeypot": "no",
            "renounced_mint": False,
            "renounced_freeze_account": False,
            "rug_ratio": 0.05,
            "top_10_holder_rate": 0.15,
            "creator_token_status": "creator_close",
            "is_wash_trading": False,
        },
        "downgrade_reasons": [],
        "missing_fields": [],
    })

    res = mod.run(token)

    assert res["gate_decision"] == "BLOCK"
    assert any(r["rule_id"] == "G03" for r in res["decision_reasons"])


def test_trade_gate_bundler_dominated_adds_g17_watch_rule():
    token = "TestTradeG17Bundler11111111111111111111111"
    _write_inputs(token, wallet_roles={
        "status": "PASS",
        "wallet_summary": {"smart_money_count": 1, "kol_count": 0, "bundler_count": 3},
        "smart_money_behavior": {"sm_net_direction": "neutral", "sm_avg_unrealized_pnl": 0},
        "downgrade_reasons": [],
        "missing_fields": [],
    })

    res = mod.run(token)

    assert any(r["rule_id"] == "G17" for r in res["decision_reasons"])
    assert res["gate_decision"] in {"WATCH", "PAPER_ONLY", "NEED_MORE_DATA", "BLOCK"}


def test_trade_gate_wash_rule_requires_wash_behavior_too():
    token = "TestTradeG05Wash111111111111111111111111111"
    _write_inputs(token, token_panel={
        "status": "PASS",
        "basic_info": {"liquidity": 100000},
        "security": {
            "is_honeypot": "no",
            "renounced_mint": True,
            "renounced_freeze_account": True,
            "rug_ratio": 0.05,
            "top_10_holder_rate": 0.15,
            "creator_token_status": "creator_close",
            "is_wash_trading": True,
        },
        "downgrade_reasons": [],
        "missing_fields": [],
    }, evidence_chain={
        "status": "PASS",
        "dominant_behavior": "ACCUMULATION",
        "confidence_score": 0.8,
        "behavior_signals": [],
        "counter_evidence": [],
        "downgrade_reasons": [],
        "missing_fields": [],
    })

    res = mod.run(token)

    assert not any(r["rule_id"] == "G05" for r in res["decision_reasons"])
