"""test_trade_gate.py — Skill 06 基础测试"""
import sys
sys.path.insert(0,"/root/sikk-gmgn/skills")
sys.path.insert(0,"/root/sikk-gmgn/skills/meme-trade-gate/scripts")
import importlib.util
_RUN_PATH = Path("/root/sikk-gmgn/skills/meme-trade-gate/scripts/run.py") if 'Path' in globals() else None
if _RUN_PATH is None:
    from pathlib import Path
    _RUN_PATH = Path("/root/sikk-gmgn/skills/meme-trade-gate/scripts/run.py")
sys.modules.pop("run", None)
sys.modules.pop("rules", None)
sys.path.insert(0, str(_RUN_PATH.parent))
spec = importlib.util.spec_from_file_location("trade_gate_run", _RUN_PATH)
_run_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_run_module)
run = _run_module.run
from common.file_io import get_run_dir, save_json


def test_trade_gate_paper_only():
    token="So11111111111111111111111111111111"; rd=get_run_dir(token)
    save_json({"status":"PASS","basic_info":{"liquidity":100000},"security":{"is_honeypot":"no","renounced_mint":True,"renounced_freeze_account":True,"rug_ratio":0.05,"top_10_holder_rate":0.15,"creator_token_status":"creator_close"},"downgrade_reasons":[],"missing_fields":[]},rd/"token_panel.json")
    save_json({"status":"PASS","wallet_summary":{"smart_money_count":3,"kol_count":1,"bundler_count":0},"smart_money_behavior":{"sm_net_direction":"accumulating","sm_avg_unrealized_pnl":100},"downgrade_reasons":[],"missing_fields":[]},rd/"wallet_roles.json")
    save_json({"status":"PASS","structure_risk":{"overall_structure_risk":"low"},"downgrade_reasons":[],"missing_fields":[]},rd/"wallet_structure.json")
    save_json({"status":"PASS","dominant_behavior":"ACCUMULATION","confidence_score":0.8,"downgrade_reasons":[],"missing_fields":[],"behavior_signals":[]},rd/"evidence_chain.json")
    res=run(token)
    assert res["gate_decision"]=="PAPER_ONLY"
    assert res["phase_permission"]["paper_allowed"] is True


def test_trade_gate_honeypot_block():
    token="So11111111111111111111111111111112"; rd=get_run_dir(token)
    save_json({"status":"PASS","basic_info":{"liquidity":100000},"security":{"is_honeypot":"yes","renounced_mint":True,"renounced_freeze_account":True,"rug_ratio":0.05,"top_10_holder_rate":0.15},"downgrade_reasons":[],"missing_fields":[]},rd/"token_panel.json")
    save_json({"status":"PASS","wallet_summary":{"smart_money_count":3,"kol_count":1,"bundler_count":0},"smart_money_behavior":{"sm_net_direction":"accumulating"},"downgrade_reasons":[],"missing_fields":[]},rd/"wallet_roles.json")
    save_json({"status":"PASS","structure_risk":{"overall_structure_risk":"low"},"downgrade_reasons":[],"missing_fields":[]},rd/"wallet_structure.json")
    save_json({"status":"PASS","dominant_behavior":"ACCUMULATION","confidence_score":0.8,"downgrade_reasons":[],"missing_fields":[],"behavior_signals":[]},rd/"evidence_chain.json")
    res=run(token)
    assert res["gate_decision"]=="BLOCK"
