from __future__ import annotations

import pytest
from pathlib import Path
import sys

ROOT = Path('/root/sikk-gmgn')
sys.path.insert(0, str(ROOT))


def valid_output():
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    return {
        'schema_version': '1.0', 'skill_name': 'meme-token-panel',
        'task_id': 'So11111111111111111111111111111111_20260525T000000Z',
        'token_address': 'So11111111111111111111111111111111', 'chain': 'sol',
        'timestamp': now.isoformat(), 'status': 'PASS', 'evidence': [], 'counter_evidence': [],
        'confidence_score': 0.8, 'downgrade_reasons': [], 'blocker_reasons': [], 'missing_fields': [],
        'valid_until': (now + timedelta(minutes=30)).isoformat(), 'next_action': 'STOP', 'handoff_to': 'controller'
    }


def test_validate_before_save_rejects_invalid_output(tmp_path):
    from skills.common.validators import save_validated_json
    out = valid_output()
    del out['missing_fields']
    with pytest.raises(AssertionError):
        save_validated_json(out, tmp_path / 'bad.json')
    assert not (tmp_path / 'bad.json').exists()


def test_validate_before_save_allows_valid_output(tmp_path):
    from skills.common.validators import save_validated_json
    p = tmp_path / 'good.json'
    save_validated_json(valid_output(), p)
    assert p.exists()


def test_controller_summary_validator_rejects_missing_forbidden():
    from skills.common.validators import validate_controller_summary
    summary = {
        'schema_version': '1.0', 'skill_name': 'meme-workflow-controller',
        'token_address': 'So11111111111111111111111111111111',
        'timestamp': '2026-05-25T00:00:00+00:00',
        'workflow_status': 'COMPLETED', 'gate_decision': 'PAPER_ONLY',
        'summary_file': '/tmp/x.md', 'next_action': 'COMPLETED'
    }
    errors = validate_controller_summary(summary)
    assert any('forbidden' in e for e in errors)
