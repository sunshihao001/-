"""test_wallet_roles.py — Skill 03 基础测试"""

import sys
import json
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
sys.path.insert(0, "/root/sikk-gmgn/skills/meme-wallet-roles/scripts")

import importlib.util
_RUN_PATH = Path("/root/sikk-gmgn/skills/meme-wallet-roles/scripts/run.py") if 'Path' in globals() else None
if _RUN_PATH is None:
    from pathlib import Path
    _RUN_PATH = Path("/root/sikk-gmgn/skills/meme-wallet-roles/scripts/run.py")
sys.modules.pop("run", None)
sys.modules.pop("rules", None)
sys.path.insert(0, str(_RUN_PATH.parent))
spec = importlib.util.spec_from_file_location("wallet_roles_run", _RUN_PATH)
_run_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_run_module)
run = _run_module.run
from common.file_io import get_run_dir, save_json


class MockGmgnClient:
    def token_holders(self, token_address: str, chain: str = "sol", limit: int = 50, tag=None, order_by="amount_percentage", direction="desc"):
        holders = []
        for i in range(12):
            tags = []
            if i < 3:
                tags = ["smart_degen"]
            elif i == 3:
                tags = ["sniper"]
            elif i == 4:
                tags = ["bundler"]
            holders.append({
                "address": f"WALLET{i:02d}",
                "tags": tags,
                "amount_percentage": 0.01 + i * 0.001,
                "usd_value": 1000,
                "unrealized_profit": 100 if i < 3 else -10,
                "sell_amount_percentage": 0.1 if i < 3 else 0.0,
                "start_holding_at": i * 60,
                "native_transfer_from": "FUNDER1" if i < 2 else f"FUNDER{i}",
            })
        return {"data": holders}

    def portfolio_created_tokens(self, wallet: str, chain: str = "sol", order_by="token_ath_mc", direction="desc"):
        return {"data": {"items": [
            {"symbol": "A", "token_ath_mc": 200000, "status": "graduated"},
            {"symbol": "B", "token_ath_mc": 50000, "status": "failed"},
        ]}}

    def portfolio_stats(self, wallet: str, chain: str = "sol", period: str = "30d"):
        return {"data": {"winrate": 0.5, "pnl": 1000}}


def test_wallet_roles_pass():
    token_address = "So11111111111111111111111111111111"
    run_dir = get_run_dir(token_address)
    save_json({
        "security": {"creator_token_status": "creator_close"},
        "dev_info": {"creator_address": "CREATOR1", "fund_from": "FUNDERX"},
    }, run_dir / "token_panel.json")

    result = run(token_address, gmgn=MockGmgnClient())
    assert result["status"] in ("PASS", "WARN")
    assert result["wallet_summary"]["smart_money_count"] == 3
    assert result["smart_money_behavior"]["sm_net_direction"] == "accumulating"
    assert result["key_wallets"][0]["basis"] == "gmgn_hint"
    assert result["next_action"] == "meme-wallet-structure"
