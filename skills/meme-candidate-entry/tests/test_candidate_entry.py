"""
test_candidate_entry.py — Skill 01 基础测试
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, "/root/sikk-gmgn/skills")
sys.path.insert(0, "/root/sikk-gmgn/skills/meme-candidate-entry/scripts")

from run import run


class MockGmgnClient:
    def __init__(self, response):
        self.response = response

    def token_info(self, token_address: str, chain: str = "sol"):
        return self.response


def test_candidate_entry_pass():
    token_address = "So11111111111111111111111111111111"
    mock = MockGmgnClient({
        "data": {
            "address": token_address,
            "symbol": "MOCK",
            "name": "Mock Token",
            "creation_timestamp": str(time.time() - 3600),
            "launchpad": "pump.fun",
            "launchpad_status": 2,
            "biggest_pool_address": "POOL1111111111111111111111111111111",
            "liquidity": 100000,
            "holder_count": 200,
            "twitter_username": "mock",
        }
    })

    result = run(
        token_address=token_address,
        entry_source="manual_ca",
        entry_reason="test",
        gmgn=mock,
    )

    assert result["status"] == "PASS"
    assert result["initial_validation"]["address_valid"] is True
    assert result["initial_validation"]["token_exists"] is True
    assert result["initial_validation"]["has_pool"] is True
    assert result["initial_validation"]["has_liquidity"] is True
    assert result["next_action"] == "meme-token-panel"


def test_candidate_entry_block_no_pool():
    token_address = "So11111111111111111111111111111111"
    mock = MockGmgnClient({
        "data": {
            "address": token_address,
            "symbol": "MOCK",
            "name": "Mock Token",
            "liquidity": 100000,
            "holder_count": 200,
        }
    })

    result = run(
        token_address=token_address,
        entry_source="manual_ca",
        entry_reason="test",
        gmgn=mock,
    )

    assert result["status"] == "BLOCK"
    assert "No pool found" in result["blocker_reasons"]
    assert result["next_action"] == "STOP"
