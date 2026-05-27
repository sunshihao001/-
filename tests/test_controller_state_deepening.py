from __future__ import annotations

import json
from pathlib import Path
import importlib.util


def load_controller():
    path = Path('/root/sikk-gmgn/skills/meme-workflow-controller/scripts/run.py')
    spec = importlib.util.spec_from_file_location('controller_state_deepening_run', path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_blocker_report_written_for_block_summary(tmp_path, monkeypatch):
    controller = load_controller()

    token = 'StateDeepening1111111111111111111111111111'
    summary = controller._build_block_summary(token, 'token_panel', {'status': 'BLOCK', 'blocker_reasons': ['x']})
    controller._write_workflow_summary(token, summary)
    report = Path('/root/sikk-gmgn/data/runs') / token / 'blocker_report.md'
    assert report.exists()
    assert 'token_panel' in report.read_text()


def test_force_refresh_records_reset_reason():
    import sys
    sys.path.insert(0, '/root/sikk-gmgn/skills')
    from common.phase_state import create_phase_state, load_phase_state
    controller = load_controller()

    token = 'StateRefresh111111111111111111111111111111'
    create_phase_state(token)
    state = controller._prepare_start_state(token, resume_from=None, force_refresh=True)
    loaded = load_phase_state(token)
    assert loaded['reset_reason'] == 'force_refresh'
    assert state['start_phase'] == 'candidate_entry'


def test_status_exposes_stale_phase_metadata():
    controller = load_controller()
    token = 'So11111111111111111111111111111111'
    s = controller.status(token)
    assert 'stale_phase_details' in s
    assert isinstance(s['stale_phase_details'], list)
