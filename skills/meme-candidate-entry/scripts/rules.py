"""
rules.py — Skill 01 判断 / 降级 / 阻塞规则

对应设计文件：design/phase1-skill-01-candidate-entry.md
"""

from __future__ import annotations

from typing import Any


def check_judgment_rules(token_info: dict, validation: dict) -> list[dict]:
    """
    判断规则表（5 条）。
    返回触发的规则列表。
    """
    triggered = []

    # 1. 地址格式 — 已在 schema.validate() 中检查，这里跳过

    # 2. token 存在
    if not validation.get("token_exists"):
        triggered.append({
            "rule": "token_exists",
            "action": "BLOCK",
            "reason": "Token not found",
        })

    # 3. 有交易池
    if not validation.get("has_pool"):
        triggered.append({
            "rule": "has_pool",
            "action": "BLOCK",
            "reason": "No pool found",
        })

    # 4. 有流动性
    if not validation.get("has_liquidity"):
        triggered.append({
            "rule": "has_liquidity",
            "action": "BLOCK",
            "reason": "Zero liquidity",
        })

    # 5. 未在 bonding curve 上
    if validation.get("is_on_curve"):
        triggered.append({
            "rule": "is_on_curve",
            "action": "WARN",
            "reason": "Still on bonding curve",
        })

    return triggered


def check_downgrade_rules(token_info: dict) -> list[str]:
    """
    降级规则（3 条）。
    返回触发的降级原因列表。
    """
    downgrades = []

    # 1. token 创建时间 < 10 分钟
    import time
    creation_ts = token_info.get("creation_timestamp") or token_info.get("open_timestamp")
    if creation_ts:
        try:
            age = time.time() - float(creation_ts)
            if age < 600:  # 10 min
                downgrades.append(f"Extremely new token, < 10min (age={int(age)}s)")
        except (ValueError, TypeError):
            pass

    # 2. 无社交链接
    social = token_info.get("social_links") or {}
    link = token_info.get("link") or {}
    twitter = token_info.get("twitter_username") or social.get("twitter") or link.get("twitter_username") or ""
    website = token_info.get("website") or social.get("website") or link.get("website") or ""
    telegram = token_info.get("telegram") or social.get("telegram") or link.get("telegram") or ""
    if not twitter and not website and not telegram:
        downgrades.append("No social links")

    # 3. holder_count < 50
    holder_count = token_info.get("holder_count", 0)
    try:
        if int(holder_count) < 50:
            downgrades.append(f"Very few holders ({holder_count})")
    except (ValueError, TypeError):
        pass

    return downgrades


def check_blocker_rules(validation: dict) -> list[str]:
    """
    阻塞规则（4 条）。
    返回阻塞原因列表。任何一条触发 → BLOCK + 停止。
    """
    blockers = []

    if not validation.get("address_valid"):
        blockers.append("Invalid address")

    if not validation.get("token_exists"):
        blockers.append("Token not found")

    if not validation.get("has_pool"):
        blockers.append("No pool found")

    if not validation.get("has_liquidity"):
        blockers.append("Zero liquidity")

    return blockers
