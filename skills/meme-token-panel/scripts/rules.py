"""
rules.py — Skill 02: meme-token-panel 判断 / 降级 / 阻塞规则
"""

from __future__ import annotations


def safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def check_hard_blocks(security: dict) -> list[str]:
    """安全硬停（BLOCK）4 条"""
    blockers = []

    if str(security.get("is_honeypot", "")).lower() == "yes":
        blockers.append("Honeypot detected")

    if safe_float(security.get("rug_ratio")) > 0.5:
        blockers.append("Extreme rug risk")

    if security.get("renounced_mint") is False and security.get("renounced_freeze_account") is False:
        blockers.append("Neither mint nor freeze renounced")

    if safe_float(security.get("buy_tax")) > 0.10 or safe_float(security.get("sell_tax")) > 0.10:
        blockers.append("Tax > 10%")

    return blockers


def check_warnings(security: dict, basic_info: dict, wallet_tags_stat: dict) -> list[str]:
    """安全警告（WARN）7 条"""
    warnings = []

    rug_ratio = safe_float(security.get("rug_ratio"))
    if 0.3 <= rug_ratio <= 0.5:
        warnings.append("High rug ratio")

    if safe_float(security.get("top_10_holder_rate")) > 0.50:
        warnings.append("Top 10 hold > 50%")

    if security.get("creator_token_status") == "creator_hold":
        warnings.append("Dev still holding")

    if safe_int(security.get("sniper_count")) > 20:
        warnings.append("High sniper count")

    if security.get("is_wash_trading") is True:
        warnings.append("Wash trading detected")

    if safe_int(wallet_tags_stat.get("smart_wallets")) == 0:
        warnings.append("No smart money")

    if safe_float(basic_info.get("liquidity")) < 10000:
        warnings.append("Low liquidity < $10k")

    return warnings


def check_pass_conditions(security: dict, basic_info: dict) -> bool:
    """PASS 条件"""
    return (
        security.get("renounced_mint") is True
        and security.get("renounced_freeze_account") is True
        and safe_float(security.get("rug_ratio")) < 0.3
        and safe_float(security.get("top_10_holder_rate")) < 0.50
        and safe_float(basic_info.get("liquidity")) >= 10000
    )


def build_risk_score_card(security: dict) -> dict:
    """risk_score_card 生成规则"""
    rug_ratio = safe_float(security.get("rug_ratio"))
    top10 = safe_float(security.get("top_10_holder_rate"))

    risk = {
        "honeypot": "danger" if str(security.get("is_honeypot", "")).lower() == "yes" else "safe",
        "mint_authority": "safe" if security.get("renounced_mint") is True else "danger",
        "freeze_authority": "safe" if security.get("renounced_freeze_account") is True else "danger",
        "rug_ratio_level": "low" if rug_ratio < 0.10 else ("medium" if rug_ratio <= 0.30 else "high"),
        "concentration_level": "low" if top10 < 0.20 else ("medium" if top10 <= 0.50 else "high"),
        "dev_status": "safe" if security.get("creator_token_status") == "creator_close" else "risk",
        "wash_trading": "detected" if security.get("is_wash_trading") is True else "clean",
        "overall_risk": "low",
    }

    danger_count = sum(1 for key in ["honeypot", "mint_authority", "freeze_authority", "dev_status"] if risk[key] in ("danger", "risk"))
    high_count = sum(1 for key in ["rug_ratio_level", "concentration_level"] if risk[key] == "high")
    medium_count = sum(1 for key in ["rug_ratio_level", "concentration_level"] if risk[key] == "medium")

    if risk["honeypot"] == "danger":
        risk["overall_risk"] = "critical"
    elif danger_count > 0 or high_count > 0:
        risk["overall_risk"] = "high"
    elif medium_count >= 2:
        risk["overall_risk"] = "medium"
    else:
        risk["overall_risk"] = "low"

    return risk


def check_downgrades(basic_info: dict, social: dict, kline_summary: dict | None, wallet_tags_stat: dict) -> list[str]:
    """降级规则 5 条"""
    downgrades = []

    if not kline_summary:
        downgrades.append("Insufficient kline data")

    if not social.get("twitter_username") and not social.get("website") and not social.get("telegram"):
        downgrades.append("No social presence")

    holder_count = safe_int(basic_info.get("holder_count"))
    if holder_count < 100:
        downgrades.append("Low holder count")

    liquidity = safe_float(basic_info.get("liquidity"))
    if 10000 <= liquidity <= 50000:
        downgrades.append("Moderate liquidity")

    smart_wallets = safe_int(wallet_tags_stat.get("smart_wallets"))
    if 1 <= smart_wallets <= 2:
        downgrades.append("Weak smart money signal")

    return downgrades
