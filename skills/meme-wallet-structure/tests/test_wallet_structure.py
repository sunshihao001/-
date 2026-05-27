"""test_wallet_structure.py — Skill 04 基础测试"""

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
spec = importlib.util.spec_from_file_location("wallet_structure_run", _RUN_PATH)
_run_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_run_module)
run = _run_module.run
from common.file_io import get_run_dir, save_json


def test_wallet_structure_high_risk():
    token = "So11111111111111111111111111111111"
    wallets = []
    for i in range(12):
        wallets.append({
            "address": f"W{i}",
            "amount_percentage": 0.08 if i < 3 else 0.01,
            "usd_value": 1000,
            "native_transfer_from": "FUNDER1" if i < 3 else f"F{i}",
            "start_holding_at": 60 if i < 3 else 600 + i * 60,
            "sell_amount_percentage": 0.0,
        })
    save_json({"status": "PASS", "key_wallets": wallets}, get_run_dir(token) / "wallet_roles.json")
    result = run(token)
    assert result["status"] == "WARN"
    assert len(result["same_source_groups"]) == 1
    assert result["structure_risk"]["overall_structure_risk"] in ("high", "critical")
    assert result["next_action"] == "meme-evidence-chain"
