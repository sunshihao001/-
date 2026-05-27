"""
test_token_panel.py — Skill 02 基础测试
"""

import sys
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
sys.path.insert(0, "/root/sikk-gmgn/skills/meme-token-panel/scripts")

import importlib.util
_RUN_PATH = Path("/root/sikk-gmgn/skills/meme-token-panel/scripts/run.py") if 'Path' in globals() else None
if _RUN_PATH is None:
    from pathlib import Path
    _RUN_PATH = Path("/root/sikk-gmgn/skills/meme-token-panel/scripts/run.py")
sys.modules.pop("run", None)
sys.modules.pop("rules", None)
sys.path.insert(0, str(_RUN_PATH.parent))
spec = importlib.util.spec_from_file_location("token_panel_run", _RUN_PATH)
_run_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_run_module)
run = _run_module.run


class MockGmgnClient:
    def token_info(self, token_address: str, chain: str = "sol"):
        return {"data": {
            "address": token_address,
            "symbol": "MOCK",
            "name": "Mock Token",
            "price": 0.01,
            "market_cap": 1000000,
            "liquidity": 100000,
            "holder_count": 500,
            "total_supply": 1000000000,
            "pair_age_seconds": 3600,
            "launchpad": "pump.fun",
            "launchpad_status": 2,
            "biggest_pool_address": "POOL1111111111111111111111111111111",
            "pool_exchange": "Raydium",
            "ath_price": 0.02,
            "twitter_username": "mock",
            "smart_degen_count": 3,
            "creator_address": "CREATOR11111111111111111111111111111",
        }}

    def token_security(self, token_address: str, chain: str = "sol"):
        return {"data": {
            "is_honeypot": "no",
            "renounced_mint": True,
            "renounced_freeze_account": True,
            "buy_tax": 0.0,
            "sell_tax": 0.0,
            "rug_ratio": 0.05,
            "top_10_holder_rate": 0.15,
            "creator_token_status": "creator_close",
            "creator_balance_rate": 0.0,
            "is_wash_trading": False,
            "sniper_count": 2,
        }}

    def token_pool(self, token_address: str, chain: str = "sol"):
        return {"data": {"exchange": "Raydium", "liquidity": 100000}}

    def market_kline(self, token_address: str, chain: str = "sol", resolution: str = "5m", from_ts: str = "", to_ts: str = ""):
        return {"data": {"candles": [
            {"open": 0.01, "high": 0.011, "low": 0.009, "close": 0.0105, "volume": 1000},
            {"open": 0.0105, "high": 0.012, "low": 0.010, "close": 0.011, "volume": 2000},
        ]}}


class MockHoneypotGmgnClient(MockGmgnClient):
    def token_security(self, token_address: str, chain: str = "sol"):
        data = super().token_security(token_address, chain)["data"]
        data["is_honeypot"] = "yes"
        return {"data": data}


def test_token_panel_pass():
    token_address = "So11111111111111111111111111111111"
    result = run(token_address, gmgn=MockGmgnClient())
    assert result["status"] == "PASS"
    assert result["risk_score_card"]["overall_risk"] == "low"
    assert result["next_action"] == "meme-wallet-roles"


def test_token_panel_honeypot_block():
    token_address = "So11111111111111111111111111111111"
    result = run(token_address, gmgn=MockHoneypotGmgnClient())
    assert result["status"] == "BLOCK"
    assert "Honeypot detected" in result["blocker_reasons"]
    assert result["next_action"] == "STOP"
