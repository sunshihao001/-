"""test_workflow_screen.py — S07 批量筛选测试"""
import sys, json, importlib.util
from pathlib import Path
sys.path.insert(0, "/root/sikk-gmgn/skills")

controller_path = Path("/root/sikk-gmgn/skills/meme-workflow-controller/scripts/run.py")
spec = importlib.util.spec_from_file_location("workflow_controller_run_screen", controller_path)
controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controller)


def test_screen_candidate_pool_with_runner_writes_batch_files():
    candidate_pool = {
        "source": "trending",
        "candidates": [
            {"token_address": "A11111111111111111111111111111111", "symbol": "AAA", "entry_source": "gmgn_trending", "entry_reason": "test A"},
            {"token_address": "B11111111111111111111111111111111", "symbol": "BBB", "entry_source": "gmgn_trending", "entry_reason": "test B"},
        ]
    }

    def fake_runner(token_address, chain="sol", resume_from=None, force_refresh=False):
        return {"token_address": token_address, "symbol": token_address[0], "workflow_status": "COMPLETED", "gate_decision": "WATCH", "gate_score": 42, "confidence_score": 0.5, "summary_file": f"/tmp/{token_address}.md"}

    result = controller.screen_candidate_pool(candidate_pool, runner=fake_runner)
    assert result["candidate_count"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["gate_decision"] == "WATCH"
    assert Path(result["筛选结果文件"]).exists()
    assert Path(result["筛选报告文件"]).exists()
