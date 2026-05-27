"""test_candidate_pool.py — S01 候选池生成测试"""
import sys, json
from pathlib import Path
sys.path.insert(0, "/root/sikk-gmgn/skills")
sys.path.insert(0, "/root/sikk-gmgn/skills/meme-candidate-entry/scripts")

from run import build_candidate_pool


class MockGmgn:
    def market_trending(self, chain="sol", interval="1h", order_by="volume", limit=50):
        return {"code":0,"data":{"rank":[
            {"address":"A11111111111111111111111111111111","symbol":"AAA","name":"Token A","volume":1000,"rank":1,"liquidity":100000,"market_cap":120000},
            {"address":"B11111111111111111111111111111111","symbol":"BBB","name":"Token B","volume":900,"rank":2,"liquidity":10000,"market_cap":120000},
            {"address":"A11111111111111111111111111111111","symbol":"AAA","name":"Token A","volume":1000,"rank":1,"liquidity":100000,"market_cap":120000},
        ]}}


def test_build_candidate_pool_trending_dedupes_and_writes_files():
    result = build_candidate_pool(source="trending", limit=3, gmgn=MockGmgn())
    assert result["source"] == "trending"
    assert len(result["candidates"]) == 1
    assert result["filtered_out_count"] == 1
    assert result["candidates"][0]["entry_source"] == "gmgn_trending"
    assert result["candidates"][0]["entry_liquidity_marketcap_gate"] == "PASS"
    assert result["filtered_out"][0]["entry_liquidity_marketcap_gate"] == "FILTERED_OUT"
    assert "GMGN trending" in result["candidates"][0]["entry_reason"]
    assert Path(result["candidate_pool_file"]).exists()
    assert Path(result["candidate_pool_report"]).exists()
