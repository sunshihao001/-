"""test_workflow_controller.py — Skill 07 基础测试（从 trade_gate 已有文件汇总）"""
import sys, json, importlib.util
from pathlib import Path
sys.path.insert(0,"/root/sikk-gmgn/skills")

_controller_path = Path("/root/sikk-gmgn/skills/meme-workflow-controller/scripts/run.py")
_spec = importlib.util.spec_from_file_location("workflow_controller_run", _controller_path)
_controller = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_controller)
status = _controller.status
list_runs = _controller.list_runs
_build_complete_summary = _controller._build_complete_summary
_write_workflow_summary = _controller._write_workflow_summary

from common.file_io import get_run_dir, save_json
from common.phase_state import create_phase_state


def test_controller_summary_status():
    token="So11111111111111111111111111111113"
    rd=get_run_dir(token)
    create_phase_state(token)
    save_json({"basic_info":{"symbol":"MOCK"},"risk_score_card":{"overall_risk":"low"}}, rd/"token_panel.json")
    save_json({"wallet_summary":{"smart_money_count":3},"smart_money_behavior":{"sm_net_direction":"accumulating"}}, rd/"wallet_roles.json")
    save_json({"structure_risk":{"overall_structure_risk":"low"}}, rd/"wallet_structure.json")
    save_json({"confidence_score":0.8,"narrative":{"one_line":"MOCK: ACCUMULATION"},"risk_factors":[],"positive_signals":[]}, rd/"evidence_chain.json")
    save_json({"gate_decision":"PAPER_ONLY","gate_score":{"total_score":80},"confidence_score":0.8,"next_action":"COMPLETED"}, rd/"trade_gate.json")
    summary=_build_complete_summary(token,{})
    assert summary["gate_decision"]=="PAPER_ONLY"
    _write_workflow_summary(token, summary)
    assert (rd/"workflow_summary.md").exists()
    st=status(token)
    assert st["status"]=="FOUND"
    lr=list_runs()
    assert "active_runs" in lr
