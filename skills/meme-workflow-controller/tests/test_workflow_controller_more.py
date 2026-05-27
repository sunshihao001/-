"""补充回归测试 — Skill 07 workflow controller 骨架与短路行为。"""
import importlib.util
import os
import sys
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")

_CONTROLLER_PATH = Path("/root/sikk-gmgn/skills/meme-workflow-controller/scripts/run.py")
_SPEC = importlib.util.spec_from_file_location("workflow_controller_run_more", _CONTROLLER_PATH)
_controller = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_controller)

from common.file_io import get_run_dir, load_active_runs, load_completed_runs
from common.phase_state import create_phase_state, load_phase_state, PHASE_ORDER


def test_controller_skeleton_run_completes_and_isolates_output_dir():
    token = "So33333333333333333333333333333333333333333"
    os.environ["SIKK_SKELETON_MODE"] = "1"
    try:
        res = _controller.run(token, force_refresh=True)
    finally:
        os.environ.pop("SIKK_SKELETON_MODE", None)

    assert res["workflow_status"] == "COMPLETED"
    assert res["summary_file"].startswith("/root/sikk-gmgn/data/runs/_skeleton_/")
    assert Path(res["summary_file"]).exists()
    assert Path(res["summary_file"]).parent.name == token


def test_controller_status_reports_phase_state_and_stale_details():
    token = "TestControllerStatus1111111111111111111111111"
    create_phase_state(token)
    rd = get_run_dir(token)
    (rd / "token_panel.json").write_text("{}", encoding="utf-8")
    st = _controller.status(token)

    assert st["status"] == "FOUND"
    assert "phase_state" in st
    assert "stale_phases" in st
    assert "stale_phase_details" in st


def test_controller_list_runs_exposes_active_and_completed_index():
    token = "So44444444444444444444444444444444444444444"
    os.environ["SIKK_SKELETON_MODE"] = "1"
    try:
        _controller.run(token, force_refresh=True)
    finally:
        os.environ.pop("SIKK_SKELETON_MODE", None)
    lr = _controller.list_runs()

    assert "active_runs" in lr
    assert "completed_runs" in lr
    assert isinstance(lr["active_runs"].get("active", []), list)
    assert isinstance(lr["completed_runs"].get("completed", []), list)


def test_controller_block_summary_marks_blocked_and_stop():
    token = "TestControllerBlock11111111111111111111111111"
    summary = _controller._build_block_summary(token, "candidate_entry", {"status": "BLOCK", "blocker_reasons": ["no pool"]})

    assert summary["workflow_status"] == "BLOCKED"
    assert summary["blocked_at"] == "candidate_entry"
    assert summary["gate_decision"] == "BLOCK"
    assert summary["next_action"] == "STOP"


def test_controller_prepare_start_state_force_refresh_resets_to_candidate_entry():
    token = "TestControllerReset1111111111111111111111111"
    state = create_phase_state(token)
    state["current_phase"] = "trade_gate"
    from common.phase_state import save_phase_state
    save_phase_state(token, state)

    prepared = _controller._prepare_start_state(token, force_refresh=True)

    assert prepared["start_phase"] == "candidate_entry"
    assert prepared["state"]["reset_reason"] == "force_refresh"
    assert prepared["state"]["resume_from"] is None
