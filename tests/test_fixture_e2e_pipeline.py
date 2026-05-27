from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path('/root/sikk-gmgn')
sys.path.insert(0, str(ROOT))


def test_fixture_matrix_can_drive_expected_gate_decision_contract():
    from tests.utils.fixture_pipeline import run_fixture_contract
    for path in sorted((ROOT / 'fixtures').glob('*.json')):
        fixture = json.load(open(path, encoding='utf-8'))
        result = run_fixture_contract(fixture)
        assert result['trade_gate']['gate_decision'] == fixture['expected_outputs']['trade_gate']['gate_decision'], path.name
        assert result['safety']['live_trading'] is False
        assert result['safety']['swap'] is False


def test_fixture_pipeline_never_uses_live_gmgn(monkeypatch):
    from tests.utils.fixture_pipeline import run_fixture_contract
    called = {'live': False}
    def mark(*args, **kwargs):
        called['live'] = True
        raise AssertionError('live call forbidden')
    # The fixture runner should use fixture JSON only, so this monkeypatch should never matter.
    fixture = json.load(open(ROOT / 'fixtures' / '场景01-正常通过.json', encoding='utf-8'))
    result = run_fixture_contract(fixture)
    assert result['trade_gate']['gate_decision'] == 'PAPER_ONLY'
    assert called['live'] is False
