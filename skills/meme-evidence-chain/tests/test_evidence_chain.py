"""test_evidence_chain.py — Skill 05 基础测试"""
import sys
sys.path.insert(0,"/root/sikk-gmgn/skills")
sys.path.insert(0,"/root/sikk-gmgn/skills/meme-evidence-chain/scripts")
import importlib.util
_RUN_PATH = Path("/root/sikk-gmgn/skills/meme-evidence-chain/scripts/run.py") if 'Path' in globals() else None
if _RUN_PATH is None:
    from pathlib import Path
    _RUN_PATH = Path("/root/sikk-gmgn/skills/meme-evidence-chain/scripts/run.py")
sys.modules.pop("run", None)
sys.modules.pop("rules", None)
sys.path.insert(0, str(_RUN_PATH.parent))
spec = importlib.util.spec_from_file_location("evidence_chain_run", _RUN_PATH)
_run_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_run_module)
run = _run_module.run
from common.file_io import get_run_dir, save_json


def test_evidence_chain_accumulation():
    token="So11111111111111111111111111111111"
    rd=get_run_dir(token)
    save_json({"status":"PASS","basic_info":{"symbol":"MOCK"},"security":{"is_wash_trading":False},"kline_summary":{"trend":"up"},"downgrade_reasons":[],"missing_fields":[]}, rd/"token_panel.json")
    save_json({"status":"PASS","smart_money_behavior":{"sm_net_direction":"accumulating"},"wallet_summary":{"fresh_wallet_count":1,"total_holders_sampled":20,"smart_money_count":3},"dev_profile":{"creator_token_status":"creator_close"},"downgrade_reasons":[],"missing_fields":[]}, rd/"wallet_roles.json")
    save_json({"status":"PASS","same_source_groups":[],"structure_risk":{"has_same_source_groups":False,"same_source_combined_pct":0,"overall_structure_risk":"low"},"downgrade_reasons":[],"missing_fields":[]}, rd/"wallet_structure.json")
    res=run(token)
    assert res["status"] in ("PASS","WARN")
    assert res["dominant_behavior"] == "ACCUMULATION"
    assert res["next_action"] == "meme-trade-gate"
    assert "一定会涨" not in res["narrative"]["paragraph"]
