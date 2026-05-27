"""
schema_base.py — 公共 Handoff Schema 定义

所有 skill 输出必须包含这些公共字段。
对应设计文件：design/phase0-workflow-contract.md
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any


@dataclass
class Evidence:
    """单条证据"""
    claim: str
    source: str
    value: Any
    weight: str  # "high" | "medium" | "low"


@dataclass
class CounterEvidence:
    """单条反面证据"""
    claim: str
    source: str
    value: Any


@dataclass
class BaseSkillOutput:
    """
    所有 skill 输出的公共基类。
    对应 phase0-workflow-contract.md 的 Standard Handoff Schema。
    """
    schema_version: str = "1.0"
    skill_name: str = ""
    task_id: str = ""
    token_address: str = ""
    chain: str = "sol"
    timestamp: str = ""
    status: str = ""  # PASS | WARN | BLOCK | ERROR | NEED_MORE_DATA

    evidence: list[dict] = field(default_factory=list)
    counter_evidence: list[dict] = field(default_factory=list)
    confidence_score: float = 0.0
    downgrade_reasons: list[str] = field(default_factory=list)
    blocker_reasons: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    valid_until: str = ""
    next_action: str = ""
    handoff_to: str = ""

    def set_timestamp(self) -> None:
        """设置当前 UTC 时间"""
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def set_valid_until(self, minutes: int = 30) -> None:
        """设置过期时间"""
        expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        self.valid_until = expires.isoformat()

    def set_task_id(self, token_address: str) -> None:
        """生成 task_id: <token_address>_<timestamp>"""
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.task_id = f"{token_address}_{ts}"
        self.token_address = token_address

    def add_evidence(self, claim: str, source: str, value: Any, weight: str = "medium") -> None:
        self.evidence.append({
            "claim": claim,
            "source": source,
            "value": value,
            "weight": weight,
        })

    def add_counter_evidence(self, claim: str, source: str, value: Any) -> None:
        self.counter_evidence.append({
            "claim": claim,
            "source": source,
            "value": value,
        })

    def add_downgrade(self, reason: str) -> None:
        if reason not in self.downgrade_reasons:
            self.downgrade_reasons.append(reason)

    def add_blocker(self, reason: str) -> None:
        if reason not in self.blocker_reasons:
            self.blocker_reasons.append(reason)

    def add_missing_field(self, field_name: str) -> None:
        if field_name not in self.missing_fields:
            self.missing_fields.append(field_name)

    def block(self, reason: str) -> None:
        """标记为 BLOCK 并记录原因"""
        self.status = "BLOCK"
        self.add_blocker(reason)
        self.next_action = "STOP"
        self.handoff_to = ""

    def error(self, reason: str) -> None:
        """标记为 ERROR 并记录原因"""
        self.status = "ERROR"
        self.add_blocker(reason)
        self.next_action = "STOP"
        self.handoff_to = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def save(self, path: str) -> str:
        """保存 JSON 到文件，自动创建目录"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        return path

    @classmethod
    def load(cls, path: str) -> dict:
        """从 JSON 文件加载（返回 dict，子类自行解析）"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
