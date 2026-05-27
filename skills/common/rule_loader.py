"""
rule_loader.py — 从 rules/*.json 加载门控和降级规则

对应设计文件：design/phase1-skill-06-trade-gate.md 的门控规则表
当 rules/ JSON 不存在时，从内置默认规则回退。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RULES_DIR = Path("/root/sikk-gmgn/rules")


def load_gate_rules(version: str = "v1") -> list[dict]:
    """
    加载门控规则。
    优先从 rules/gate_rules_{version}.json 加载。
    不存在时使用内置默认规则。
    """
    path = RULES_DIR / f"gate_rules_{version}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("rules", [])
    return _default_gate_rules()


def load_downgrade_rules(version: str = "v1") -> list[dict]:
    """
    加载降级规则。
    优先从 rules/downgrade_rules_{version}.json 加载。
    不存在时使用内置默认规则。
    """
    path = RULES_DIR / f"downgrade_rules_{version}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("rules", [])
    return _default_downgrade_rules()


def evaluate_gate_rules(
    rules: list[dict],
    token_panel: dict,
    wallet_roles: dict,
    wallet_structure: dict,
    evidence_chain: dict,
) -> list[dict]:
    """
    评估门控规则，返回触发的规则列表。
    每条规则附带 triggered=True/False 和实际值。
    """
    triggered = []
    sources = {
        "token_panel": token_panel,
        "wallet_roles": wallet_roles,
        "wallet_structure": wallet_structure,
        "evidence_chain": evidence_chain,
    }

    for rule in rules:
        result = _evaluate_single_rule(rule, sources)
        if result["triggered"]:
            triggered.append(result)

    return triggered


def _evaluate_single_rule(rule: dict, sources: dict) -> dict:
    """评估单条规则，支持 AND / OR / contains / comparison。"""
    rule_id = rule.get("rule_id", "")
    result = {
        "rule_id": rule_id,
        "rule_name": rule.get("rule_name", ""),
        "triggered": False,
        "input_value": None,
        "threshold": rule.get("threshold"),
        "contribution": rule.get("action", "").lower(),
    }
    condition = rule.get("condition", "")
    if not condition:
        return result
    result["input_value"] = condition
    result["triggered"] = evaluate_condition(condition, sources)
    return result


def evaluate_condition(condition: str, sources: dict) -> bool:
    """Evaluate a small declarative condition language.

    Supported:
    - `A AND B`
    - `A OR B`
    - `path contains 'VALUE'`
    - `path == value`, `!=`, `>`, `>=`, `<`, `<=`

    Composite natural-language conditions such as PAPER_ONLY are safely skipped
    unless they match the supported grammar.
    """
    condition = (condition or "").strip()
    if not condition:
        return False
    if " OR " in condition:
        return any(evaluate_condition(part, sources) for part in condition.split(" OR "))
    if " AND " in condition:
        return all(evaluate_condition(part, sources) for part in condition.split(" AND "))
    parts = condition.split()
    if len(parts) < 3:
        return False
    field_path, operator = parts[0], parts[1]
    expected_raw = " ".join(parts[2:]).strip().strip("'\"")
    actual_value = _resolve_path(field_path, sources)
    if operator == "contains":
        return _contains_value(actual_value, expected_raw)
    return _compare(actual_value, operator, expected_raw)


def _resolve_path(field_path: str, sources: dict) -> Any:
    path_parts = field_path.split(".")
    if len(path_parts) < 2:
        return None
    obj = sources.get(path_parts[0])
    for key in path_parts[1:]:
        if isinstance(obj, dict):
            obj = obj.get(key)
        elif isinstance(obj, list):
            obj = [item.get(key) for item in obj if isinstance(item, dict)]
        else:
            return None
        if obj is None:
            return None
    return obj


def _contains_value(actual_value: Any, expected: str) -> bool:
    if isinstance(actual_value, list):
        for item in actual_value:
            if isinstance(item, dict):
                if expected in {str(v) for v in item.values()}:
                    return True
            elif str(item) == expected:
                return True
        return False
    if isinstance(actual_value, dict):
        return expected in {str(v) for v in actual_value.values()}
    return expected in str(actual_value)


def _compare(actual_value: Any, operator: str, expected_raw: str) -> bool:
    expected_bool = {"True": True, "False": False, "true": True, "false": False}.get(expected_raw)
    if expected_bool is not None:
        expected: Any = expected_bool
    else:
        expected = expected_raw
    try:
        if operator == "==":
            return actual_value == expected or str(actual_value) == str(expected)
        if operator == "!=":
            return not (actual_value == expected or str(actual_value) == str(expected))
        if operator == ">":
            return float(actual_value) > float(expected_raw)
        if operator == ">=":
            return float(actual_value) >= float(expected_raw)
        if operator == "<":
            return float(actual_value) < float(expected_raw)
        if operator == "<=":
            return float(actual_value) <= float(expected_raw)
    except (ValueError, TypeError):
        return False
    return False


# Backward-compatible helpers retained for older tests/imports.
def _resolve_field(condition: str, sources: dict) -> Any:
    parts = condition.split()
    return _resolve_path(parts[0], sources) if parts else None


def _check_condition(condition: str, actual_value: Any) -> bool:
    parts = condition.split()
    if len(parts) < 3:
        return False
    return _compare(actual_value, parts[1], parts[2].strip("'\""))


# ── 内置默认规则（当 JSON 文件不存在时回退）──

def _default_gate_rules() -> list[dict]:
    """对应 Skill 06 设计文件的门控规则表"""
    return [
        # 一票否决 → BLOCK
        {
            "rule_id": "G01", "rule_name": "Honeypot",
            "category": "block",
            "condition": "token_panel.security.is_honeypot == 'yes'",
            "source_skills": ["token_panel"],
            "action": "BLOCK",
            "rationale": "蜜罐合约无法卖出，100% 归零",
        },
        {
            "rule_id": "G02", "rule_name": "Extreme Rug",
            "category": "block",
            "condition": "token_panel.security.rug_ratio > 0.5",
            "source_skills": ["token_panel"],
            "action": "BLOCK",
            "rationale": "rug_ratio 超过 0.5 表示多数持有人已被收割",
        },
        {
            "rule_id": "G03", "rule_name": "Unrenounced",
            "category": "block",
            "condition": "token_panel.security.renounced_mint == False",
            "source_skills": ["token_panel"],
            "action": "BLOCK",
            "rationale": "mint 和 freeze 均未放弃，发行方保留完全控制权",
        },
        {
            "rule_id": "G04", "rule_name": "High Tax",
            "category": "block",
            "condition": "token_panel.security.buy_tax > 0.10",
            "source_skills": ["token_panel"],
            "action": "BLOCK",
            "rationale": "交易税超过 10%，买卖成本过高",
        },
        {
            "rule_id": "G05", "rule_name": "Wash Trading",
            "category": "block",
            "condition": "token_panel.security.is_wash_trading == True",
            "source_skills": ["token_panel", "evidence_chain"],
            "action": "BLOCK",
            "rationale": "刷量交易被检测且证据链确认",
        },
        {
            "rule_id": "G06", "rule_name": "Critical Structure",
            "category": "block",
            "condition": "wallet_structure.structure_risk.overall_structure_risk == 'critical'",
            "source_skills": ["wallet_structure"],
            "action": "BLOCK",
            "rationale": "钱包结构风险达到 critical 且置信度 >= 0.7",
        },
        # 观察 → WATCH
        {
            "rule_id": "G10", "rule_name": "Dev Holding",
            "category": "watch",
            "condition": "token_panel.security.creator_balance_rate > 0.05",
            "source_skills": ["token_panel"],
            "action": "WATCH",
            "rationale": "Dev 仍持有超过 5% 的 token",
        },
        {
            "rule_id": "G11", "rule_name": "High Concentration",
            "category": "watch",
            "condition": "token_panel.security.top_10_holder_rate > 0.40",
            "source_skills": ["token_panel"],
            "action": "WATCH",
            "rationale": "前 10 持有人占比超过 40%",
        },
        {
            "rule_id": "G12", "rule_name": "No Smart Money",
            "category": "watch",
            "condition": "wallet_roles.wallet_summary.smart_money_count == 0",
            "source_skills": ["token_panel", "wallet_roles"],
            "action": "WATCH",
            "rationale": "无 smart money 参与",
        },
        {
            "rule_id": "G13", "rule_name": "SM Distributing",
            "category": "watch",
            "condition": "wallet_roles.smart_money_behavior.sm_net_direction == 'distributing'",
            "source_skills": ["wallet_roles"],
            "action": "WATCH",
            "rationale": "Smart money 正在出货",
        },
        {
            "rule_id": "G14", "rule_name": "Low Liquidity",
            "category": "watch",
            "condition": "token_panel.basic_info.liquidity < 50000",
            "source_skills": ["token_panel"],
            "action": "WATCH",
            "rationale": "流动性低于 $50k，退出困难",
        },
        {
            "rule_id": "G15", "rule_name": "High Rug Ratio",
            "category": "watch",
            "condition": "token_panel.security.rug_ratio > 0.3",
            "source_skills": ["token_panel"],
            "action": "WATCH",
            "rationale": "rug_ratio 在 0.3-0.5 区间，高风险但未触发 BLOCK",
        },
        {
            "rule_id": "G16", "rule_name": "Structure Risk High",
            "category": "watch",
            "condition": "wallet_structure.structure_risk.overall_structure_risk == 'high'",
            "source_skills": ["wallet_structure"],
            "action": "WATCH",
            "rationale": "钱包结构风险为 high",
        },
        {
            "rule_id": "G17", "rule_name": "Bundler Dominated",
            "category": "watch",
            "condition": "wallet_roles.wallet_summary.bundler_count > 0",
            "source_skills": ["wallet_roles"],
            "action": "WATCH",
            "rationale": "Bundler 数量超过 SM + KOL 总数",
        },
        {
            "rule_id": "G18", "rule_name": "Divergence",
            "category": "watch",
            "condition": "evidence_chain.dominant_behavior == 'DIVERGENCE'",
            "source_skills": ["evidence_chain"],
            "action": "WATCH",
            "rationale": "价格走势与钱包行为出现背离",
        },
        {
            "rule_id": "G19", "rule_name": "Low Confidence",
            "category": "watch",
            "condition": "evidence_chain.confidence_score < 0.5",
            "source_skills": ["evidence_chain"],
            "action": "WATCH",
            "rationale": "证据链置信度低于 0.5",
        },
    ]


def _default_downgrade_rules() -> list[dict]:
    """各 skill 的降级规则汇总"""
    return [
        # Skill 01
        {"skill": "candidate_entry", "condition": "token_age < 600", "action": "Extremely new token, < 10min"},
        {"skill": "candidate_entry", "condition": "no_social_links", "action": "No social links"},
        {"skill": "candidate_entry", "condition": "holder_count < 50", "action": "Very few holders"},
        # Skill 02
        {"skill": "token_panel", "condition": "kline_insufficient", "action": "Insufficient kline data"},
        {"skill": "token_panel", "condition": "no_social", "action": "No social presence"},
        {"skill": "token_panel", "condition": "holder_count < 100", "action": "Low holder count"},
        {"skill": "token_panel", "condition": "liquidity 10000-50000", "action": "Moderate liquidity"},
        {"skill": "token_panel", "condition": "smart_wallets 1-2", "action": "Weak smart money signal"},
        # Skill 03
        {"skill": "wallet_roles", "condition": "holders_api < 10", "action": "Too few holders to analyze"},
        {"skill": "wallet_roles", "condition": "no_smart_degen", "action": "No smart money data"},
        {"skill": "wallet_roles", "condition": "dev_history_fail", "action": "Dev history unavailable"},
        {"skill": "wallet_roles", "condition": "fresh_wallet_ratio > 0.5", "action": "High fresh wallet ratio"},
        # Skill 04
        {"skill": "wallet_structure", "condition": "no_funding_source", "action": "No funding source data"},
        {"skill": "wallet_structure", "condition": "key_wallets < 10", "action": "Too few wallets for structure analysis"},
        {"skill": "wallet_structure", "condition": "no_holding_timestamp", "action": "No holding timestamp data"},
        # Skill 05
        {"skill": "evidence_chain", "condition": "no_structure_data", "action": "No funding source data for structure"},
        {"skill": "evidence_chain", "condition": "no_sm_data", "action": "No smart money data"},
        {"skill": "evidence_chain", "condition": "no_kline", "action": "No price trend data"},
        {"skill": "evidence_chain", "condition": "conflicting_signals", "action": "Conflicting signals"},
        # Skill 06
        {"skill": "trade_gate", "condition": "inherited_downgrade", "action": "Inherited downgrade from upstream"},
        {"skill": "trade_gate", "condition": "confidence < 0.6", "action": "Low confidence, max WATCH"},
        {"skill": "trade_gate", "condition": "structure_data_incomplete", "action": "Structure data incomplete, max score 10"},
    ]
