"""test_wallet_structure_exclusions.py — Skill 04 池子/交易所地址排除测试"""
import sys
sys.path.insert(0, "/root/sikk-gmgn/skills")
sys.path.insert(0, "/root/sikk-gmgn/skills/meme-wallet-structure/scripts")

import importlib.util
_RUN_PATH = Path("/root/sikk-gmgn/skills/meme-wallet-structure/scripts/run.py") if 'Path' in globals() else None
if _RUN_PATH is None:
    from pathlib import Path
    _RUN_PATH = Path("/root/sikk-gmgn/skills/meme-wallet-structure/scripts/run.py")
sys.modules.pop("run", None)
sys.modules.pop("rules", None)
sys.path.insert(0, str(_RUN_PATH.parent))
spec = importlib.util.spec_from_file_location("wallet_structure_run_exclusions", _RUN_PATH)
_run_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_run_module)
run = _run_module.run
from common.file_io import get_run_dir, save_json


def test_wallet_structure_excludes_pool_address_from_concentration():
    token = "So11111111111111111111111111111114"
    wallets = [
        {
            "address": "POOL_ADDRESS",
            "addr_type": 2,
            "exchange": "pump_amm",
            "maker_token_tags": ["top_holder"],
            "amount_percentage": 0.80,
            "usd_value": 80000,
            "native_transfer_from": "",
            "start_holding_at": 100,
            "sell_amount_percentage": 0.0,
        }
    ]
    for i in range(20):
        wallets.append({
            "address": f"W{i}",
            "addr_type": 0,
            "exchange": "",
            "maker_token_tags": [],
            "amount_percentage": 0.005,
            "usd_value": 500,
            "native_transfer_from": f"F{i}",
            "start_holding_at": 600 + i * 60,
            "sell_amount_percentage": 0.0,
        })

    save_json({"status": "PASS", "key_wallets": wallets}, get_run_dir(token) / "wallet_roles.json")
    result = run(token)

    assert result["concentration"]["top5_holder_pct"] < 0.80
    assert result["concentration"]["concentration_level"] != "extreme"
    assert result["structure_risk"]["overall_structure_risk"] != "critical"
