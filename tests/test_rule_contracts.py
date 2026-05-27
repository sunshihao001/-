from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('/root/sikk-gmgn')


def load_json(rel: str):
    return json.load(open(ROOT / rel, encoding='utf-8'))


def test_gate_rules_v1_contract_and_coverage():
    data = load_json('rules/gate_rules_v1.json')
    assert data['schema_version'] == '1.0'
    assert data['rule_set'] == 'gate_rules_v1'
    rules = data['rules']
    ids = {r['rule_id'] for r in rules}
    assert {f'G{i:02d}' for i in range(1, 7)} <= ids
    assert {f'G{i}' for i in range(10, 20)} <= ids
    assert 'PAPER_ONLY' in ids
    assert 'NEED_MORE_DATA' in ids
    for rule in rules:
        for key in ['rule_id', 'rule_name', 'category', 'condition', 'source_skills', 'source_fields', 'action', 'rationale', 'version']:
            assert key in rule, f'{rule.get("rule_id")} missing {key}'
        assert rule['action'] in {'BLOCK', 'WATCH', 'PAPER_ONLY', 'NEED_MORE_DATA'}
        assert isinstance(rule['source_skills'], list)
        assert isinstance(rule['source_fields'], list)
        assert rule['rationale']


def test_downgrade_rules_cover_all_skills():
    data = load_json('rules/downgrade_rules_v1.json')
    assert data['schema_version'] == '1.0'
    assert data['rule_set'] == 'downgrade_rules_v1'
    rules = data['rules']
    covered = set()
    for rule in rules:
        for key in ['rule_id', 'skill_name', 'condition', 'downgrade_reason', 'severity', 'missing_fields', 'recovery_action', 'version']:
            assert key in rule, f'{rule.get("rule_id")} missing {key}'
        covered.add(rule['skill_name'])
    assert {
        'meme-candidate-entry',
        'meme-token-panel',
        'meme-wallet-roles',
        'meme-wallet-structure',
        'meme-evidence-chain',
        'meme-trade-gate',
        'meme-workflow-controller',
    } <= covered


def test_rule_loader_prefers_json_rules():
    import sys
    sys.path.insert(0, str(ROOT / 'skills'))
    from common.rule_loader import load_gate_rules, load_downgrade_rules

    gate = load_gate_rules()
    down = load_downgrade_rules()
    assert any(r['rule_id'] == 'PAPER_ONLY' for r in gate)
    assert any(r['rule_id'] == 'NEED_MORE_DATA' for r in gate)
    assert any(r['skill_name'] == 'meme-workflow-controller' for r in down)
