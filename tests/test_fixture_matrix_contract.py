from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('/root/sikk-gmgn')
FIXTURES = ROOT / 'fixtures'

REQUIRED_MOCK_INPUTS = {
    'candidate_entry_input',
    'gmgn_token_info_response',
    'gmgn_token_security_response',
    'gmgn_token_pool_response',
    'gmgn_market_kline_response',
    'gmgn_token_holders_response',
    'gmgn_portfolio_stats_response',
    'gmgn_created_tokens_response',
}
REQUIRED_EXPECTED_OUTPUTS = {
    'candidate_entry',
    'token_panel',
    'wallet_roles',
    'wallet_structure',
    'evidence_chain',
    'trade_gate',
}


def fixture_files():
    return sorted(FIXTURES.glob('*.json'))


def test_fixture_matrix_has_five_parseable_scenarios():
    files = fixture_files()
    assert len(files) >= 5
    for path in files:
        data = json.load(open(path, encoding='utf-8'))
        assert data['fixture_id']
        assert data['description']


def test_each_fixture_has_full_mock_inputs_and_expected_outputs():
    for path in fixture_files():
        data = json.load(open(path, encoding='utf-8'))
        assert REQUIRED_MOCK_INPUTS <= set(data['mock_inputs']), path.name
        assert REQUIRED_EXPECTED_OUTPUTS <= set(data['expected_outputs']), path.name


def test_fixture_gate_decision_coverage():
    decisions = set()
    has_downgrade = False
    has_missing = False
    for path in fixture_files():
        data = json.load(open(path, encoding='utf-8'))
        decisions.add(data['expected_outputs']['trade_gate']['gate_decision'])
        blob = json.dumps(data, ensure_ascii=False)
        has_downgrade |= 'downgrade_reasons' in blob
        has_missing |= 'missing_fields' in blob
    assert {'BLOCK', 'WATCH', 'PAPER_ONLY', 'NEED_MORE_DATA'} <= decisions
    assert has_downgrade
    assert has_missing
