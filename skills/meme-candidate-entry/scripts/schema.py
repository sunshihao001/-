"""
schema.py — Skill 01: meme-candidate-entry 输入输出 schema

对应设计文件：design/phase1-skill-01-candidate-entry.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Solana base58 地址正则（32-44 字符）
SOLANA_ADDRESS_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")

VALID_ENTRY_SOURCES = {
    "manual_ca",
    "gmgn_trending",
    "gmgn_trenches",
    "gmgn_signal",
    "smartmoney_cluster",
    "telegram",
}


@dataclass
class CandidateEntryInput:
    """Skill 01 输入"""
    mode: str = "manual"  # "manual" | "auto"
    token_address: str = ""
    chain: str = "sol"
    entry_source: str = "manual_ca"
    entry_reason: str = ""

    def validate(self) -> list[str]:
        errors = []
        if self.mode not in ("manual", "auto"):
            errors.append(f"Invalid mode: {self.mode}")
        if self.mode == "manual":
            if not self.token_address:
                errors.append("token_address is required in manual mode")
            elif not SOLANA_ADDRESS_RE.match(self.token_address):
                errors.append(f"Invalid Solana address format: {self.token_address}")
        if self.entry_source not in VALID_ENTRY_SOURCES:
            errors.append(f"Invalid entry_source: {self.entry_source}")
        return errors


@dataclass
class InitialValidation:
    """候选入口初始验证结果"""
    address_valid: bool = False
    token_exists: bool = False
    has_pool: bool = False
    has_liquidity: bool = False
    is_on_curve: bool = False


@dataclass
class CandidateEntryOutput:
    """Skill 01 完整输出（扩展 BaseSkillOutput）"""
    # 公共字段
    schema_version: str = "1.0"
    skill_name: str = "meme-candidate-entry"
    task_id: str = ""
    token_address: str = ""
    chain: str = "sol"
    timestamp: str = ""
    status: str = ""

    # Skill 01 专属字段
    entry_source: str = ""
    entry_reason: str = ""
    token_symbol: str = ""
    token_name: str = ""
    creation_timestamp: str = ""
    launchpad: str = ""
    initial_validation: dict = field(default_factory=dict)

    # 公共字段续
    evidence: list[dict] = field(default_factory=list)
    counter_evidence: list[dict] = field(default_factory=list)
    confidence_score: float = 1.0
    downgrade_reasons: list[str] = field(default_factory=list)
    blocker_reasons: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    valid_until: str = ""
    next_action: str = "meme-token-panel"
    handoff_to: str = "meme-token-panel"
