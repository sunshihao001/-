from __future__ import annotations

import sys
from pathlib import Path
ROOT = Path('/root/sikk-gmgn')
sys.path.insert(0, str(ROOT))

def sources():
    return {
        'token_panel': {
            'security': {'is_honeypot': 'no', 'rug_ratio': 0.05, 'buy_tax': 0.0, 'sell_tax': 0.0},
            'basic_info': {'liquidity': 100000},
        },
        'wallet_roles': {'wallet_summary': {'smart_money_count': 3, 'kol_count': 1, 'bundler_count': 5}},
        'wallet_structure': {'structure_risk': {'overall_structure_risk': 'high'}},
        'evidence_chain': {'confidence_score': 0.8, 'dominant_behavior': 'ACCUMULATION', 'behavior_signals': [{'behavior': 'DIVERGENCE'}]},
    }


def test_and_condition_requires_all_parts():
    from skills.common.rule_loader import evaluate_condition
    s = sources()
    assert evaluate_condition("token_panel.security.is_honeypot == 'no' AND evidence_chain.confidence_score >= 0.7", s) is True
    assert evaluate_condition("token_panel.security.is_honeypot == 'yes' AND evidence_chain.confidence_score >= 0.7", s) is False


def test_or_condition_accepts_either_part():
    from skills.common.rule_loader import evaluate_condition
    s = sources()
    assert evaluate_condition("token_panel.security.buy_tax > 0.10 OR token_panel.security.sell_tax > 0.10", s) is False
    s['token_panel']['security']['sell_tax'] = 0.2
    assert evaluate_condition("token_panel.security.buy_tax > 0.10 OR token_panel.security.sell_tax > 0.10", s) is True


def test_contains_condition_checks_nested_list_dicts():
    from skills.common.rule_loader import evaluate_condition
    assert evaluate_condition("evidence_chain.behavior_signals contains 'DIVERGENCE'", sources()) is True
    assert evaluate_condition("evidence_chain.behavior_signals contains 'WASH'", sources()) is False


def test_composite_rules_do_not_crash_evaluator():
    from skills.common.rule_loader import load_gate_rules, evaluate_gate_rules
    s = sources()
    triggered = evaluate_gate_rules(load_gate_rules(), s['token_panel'], s['wallet_roles'], s['wallet_structure'], s['evidence_chain'])
    assert isinstance(triggered, list)
    assert any(r['rule_id'] == 'G16' for r in triggered)
