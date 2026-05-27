from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path('/root/sikk-gmgn')
sys.path.insert(0, str(ROOT))


def base_output(skill_name='meme-test'):
    now = datetime.now(timezone.utc)
    return {
        'schema_version': '1.0',
        'skill_name': skill_name,
        'task_id': 'So11111111111111111111111111111111_20260525T000000Z',
        'token_address': 'So11111111111111111111111111111111',
        'chain': 'sol',
        'timestamp': now.isoformat(),
        'status': 'PASS',
        'evidence': [],
        'counter_evidence': [],
        'confidence_score': 0.8,
        'downgrade_reasons': [],
        'blocker_reasons': [],
        'missing_fields': [],
        'valid_until': (now + timedelta(minutes=30)).isoformat(),
        'next_action': 'STOP',
        'handoff_to': 'controller',
    }


def test_common_validator_accepts_standard_output():
    from skills.common.validators import validate_skill_output
    errors = validate_skill_output(base_output('meme-token-panel'))
    assert errors == []


def test_common_validator_rejects_missing_required_field():
    from skills.common.validators import validate_skill_output
    out = base_output('meme-token-panel')
    del out['missing_fields']
    errors = validate_skill_output(out)
    assert any('missing_fields' in e for e in errors)


def test_trade_gate_validator_requires_phase1_gate_fields():
    from skills.common.validators import validate_trade_gate_output
    out = base_output('meme-trade-gate')
    out.update({
        'gate_decision': 'PAPER_ONLY',
        'decision_reasons': [],
        'gate_score': {'total_score': 80, 'max_possible': 100},
        'phase_permission': {'research_allowed': True, 'paper_allowed': True, 'semi_auto_allowed': False, 'auto_allowed': False},
        'next_review_conditions': [],
    })
    assert validate_trade_gate_output(out) == []
    out['gate_decision'] = 'AUTO_READY'
    assert any('gate_decision' in e for e in validate_trade_gate_output(out))
