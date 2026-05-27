"""
rules.py — Skill 03: meme-wallet-roles 角色规则

注：当前为工程可运行版，后续需要按理论补 basis / gmgn_hint / unverified。
"""

from __future__ import annotations

from typing import Any


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


def classify_role(wallet: dict) -> dict:
    """返回角色判定与 basis（临时版）"""
    tags = set(wallet.get("tags", []) or [])
    amount_pct = safe_float(wallet.get("amount_percentage"))
    start_holding_at = safe_int(wallet.get("start_holding_at"))
    is_new = bool(wallet.get("is_new", False))

    role = "wallet"
    basis = "unverified"

    if "smart_degen" in tags:
        role = "smart_money"
        basis = "gmgn_hint"
    elif "renowned" in tags or "kol" in tags:
        role = "kol"
        basis = "gmgn_hint"
    elif "sniper" in tags:
        role = "sniper"
        basis = "gmgn_hint"
    elif "bundler" in tags:
        role = "bundler"
        basis = "gmgn_hint"
    elif "rat_trader" in tags:
        role = "rat_trader"
        basis = "gmgn_hint"
    elif "dev" in tags:
        role = "dev"
        basis = "gmgn_hint"
    elif amount_pct > 0.02 and not tags:
        role = "whale"
        basis = "behavior_rule"
    elif start_holding_at > 0 and start_holding_at < 300 and "sniper" not in tags:
        role = "early_buyer"
        basis = "behavior_rule"
    elif is_new or "fresh_wallet" in tags:
        role = "fresh_wallet"
        basis = "gmgn_hint"

    native_transfer = wallet.get("native_transfer") or {}
    native_transfer_from = wallet.get("native_transfer_from", "")
    if not native_transfer_from and isinstance(native_transfer, dict):
        native_transfer_from = native_transfer.get("from_address") or native_transfer.get("address") or ""

    return {
        "address": wallet.get("address", ""),
        "role": role,
        "basis": basis,
        "gmgn_hint": list(tags),
        "amount_percentage": amount_pct,
        "usd_value": safe_float(wallet.get("usd_value")),
        "avg_cost": safe_float(wallet.get("avg_cost")),
        "realized_profit": safe_float(wallet.get("realized_profit")),
        "unrealized_profit": safe_float(wallet.get("unrealized_profit")),
        "buy_volume_cur": safe_float(wallet.get("buy_volume_cur")),
        "sell_volume_cur": safe_float(wallet.get("sell_volume_cur")),
        "sell_amount_percentage": safe_float(wallet.get("sell_amount_percentage")),
        "buy_tx_count": safe_int(wallet.get("buy_tx_count")),
        "sell_tx_count": safe_int(wallet.get("sell_tx_count")),
        "start_holding_at": start_holding_at,
        "is_selling": bool(wallet.get("is_selling", False)),
        "native_transfer_from": native_transfer_from,
        "twitter_username": wallet.get("twitter_username", ""),
        "name": wallet.get("name", ""),
        "addr_type": safe_int(wallet.get("addr_type")),
        "exchange": wallet.get("exchange", ""),
        "maker_token_tags": wallet.get("maker_token_tags", []) or [],
    }


def classify_sm_behavior(wallets: list[dict]) -> dict:
    """SM 行为判断"""
    smart_money = [w for w in wallets if w.get("role") == "smart_money"]
    if not smart_money:
        return {
            "sm_buying": False,
            "sm_selling": False,
            "sm_net_direction": "no_sm",
            "sm_avg_unrealized_pnl": 0.0,
            "sm_with_profit_count": 0,
            "sm_with_loss_count": 0,
        }

    avg_sell = sum(safe_float(w.get("sell_amount_percentage")) for w in smart_money) / max(len(smart_money), 1)
    avg_pnl = sum(safe_float(w.get("unrealized_profit")) for w in smart_money) / max(len(smart_money), 1)
    with_profit = sum(1 for w in smart_money if safe_float(w.get("unrealized_profit")) > 0)
    with_loss = sum(1 for w in smart_money if safe_float(w.get("unrealized_profit")) < 0)

    if avg_sell < 0.2:
        direction = "accumulating"
    elif avg_sell > 0.7:
        direction = "distributing"
    else:
        direction = "neutral"

    return {
        "sm_buying": direction == "accumulating",
        "sm_selling": direction == "distributing",
        "sm_net_direction": direction,
        "sm_avg_unrealized_pnl": avg_pnl,
        "sm_with_profit_count": with_profit,
        "sm_with_loss_count": with_loss,
    }


def classify_dev_profile(token_panel: dict, dev_wallet: dict | None) -> dict:
    """Dev 信誉判断"""
    if not dev_wallet:
        return {
            "creator_address": token_panel.get("dev_info", {}).get("creator_address", ""),
            "creator_token_status": token_panel.get("security", {}).get("creator_token_status", ""),
            "total_tokens_created": 0,
            "graduated_count": 0,
            "graduation_ratio": 0.0,
            "best_token_ath_mc": 0.0,
            "best_token_symbol": "",
            "dev_30d_winrate": 0.0,
            "dev_30d_pnl": 0.0,
            "fund_from_address": token_panel.get("dev_info", {}).get("fund_from", ""),
            "dev_status": "unverified",
        }

    total = safe_int(dev_wallet.get("total_tokens_created"))
    graduated = safe_int(dev_wallet.get("graduated_count"))
    ratio = graduated / total if total > 0 else 0.0
    best_mc = safe_float(dev_wallet.get("best_token_ath_mc"))

    if ratio > 0.3 and best_mc > 100000:
        status = "has_success"
    elif ratio < 0.1:
        status = "high_risk"
    elif total > 50 and ratio < 0.05:
        status = "batch_risk"
    else:
        status = "mixed"

    return {
        "creator_address": dev_wallet.get("creator_address", ""),
        "creator_token_status": dev_wallet.get("creator_token_status", token_panel.get("security", {}).get("creator_token_status", "")),
        "total_tokens_created": total,
        "graduated_count": graduated,
        "graduation_ratio": ratio,
        "best_token_ath_mc": best_mc,
        "best_token_symbol": dev_wallet.get("best_token_symbol", ""),
        "dev_30d_winrate": safe_float(dev_wallet.get("dev_30d_winrate")),
        "dev_30d_pnl": safe_float(dev_wallet.get("dev_30d_pnl")),
        "fund_from_address": dev_wallet.get("fund_from_address", token_panel.get("dev_info", {}).get("fund_from", "")),
        "dev_status": status,
    }
