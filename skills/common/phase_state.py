"""
phase_state.py — phase_state.json 读写与状态管理

对应设计文件：design/phase0-workflow-contract.md Phase State Schema
                design/phase1-skill-07-workflow-controller.md
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .file_io import get_run_dir, save_json, load_json


# Skill 执行顺序
PHASE_ORDER = [
    "candidate_entry",
    "token_panel",
    "wallet_roles",
    "wallet_structure",
    "evidence_chain",
    "trade_gate",
]

# 数据过期时间（秒）
TTL_MAP = {
    "candidate_entry": 1800,    # 30 min
    "token_panel": 1800,        # 30 min
    "wallet_roles": 3600,       # 60 min
    "wallet_structure": 3600,   # 60 min
    "evidence_chain": 1800,     # 30 min
    "trade_gate": 900,          # 15 min
}

# Phase → 输出文件名
OUTPUT_FILES = {
    "candidate_entry": "candidate_entry.json",
    "token_panel": "token_panel.json",
    "wallet_roles": "wallet_roles.json",
    "wallet_structure": "wallet_structure.json",
    "evidence_chain": "evidence_chain.json",
    "trade_gate": "trade_gate.json",
}


def create_phase_state(token_address: str) -> dict:
    """创建新的 phase_state"""
    now = datetime.now(timezone.utc).isoformat()
    state = {
        "task_id": f"{token_address}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "token_address": token_address,
        "chain": "sol",
        "created_at": now,
        "updated_at": now,
        "current_phase": "candidate_entry",
        "completed_phases": [],
        "blocked_at": None,
        "blocker_phase": None,
        "blocker_reasons": [],
        "gate_decision": None,
        "resume_from": None,
    }
    save_phase_state(token_address, state)
    return state


def load_phase_state(token_address: str) -> dict | None:
    """加载 phase_state，不存在返回 None"""
    path = get_run_dir(token_address) / "phase_state.json"
    if not path.exists():
        return None
    return load_json(path)


def save_phase_state(token_address: str, state: dict) -> str:
    """保存 phase_state"""
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    path = get_run_dir(token_address) / "phase_state.json"
    return save_json(state, path)


def complete_phase(token_address: str, phase: str, status: str) -> dict:
    """标记某个 phase 完成"""
    state = load_phase_state(token_address)
    if state is None:
        state = create_phase_state(token_address)

    now = datetime.now(timezone.utc).isoformat()
    completed = {
        "phase": phase,
        "status": status,
        "completed_at": now,
        "output_file": OUTPUT_FILES.get(phase, f"{phase}.json"),
    }

    # 去重：如果已有同名 phase，替换
    state["completed_phases"] = [
        p for p in state["completed_phases"] if p["phase"] != phase
    ]
    state["completed_phases"].append(completed)

    # 更新 current_phase
    if status in ("BLOCK", "ERROR"):
        state["current_phase"] = "BLOCKED" if status == "BLOCK" else "ERROR"
        state["blocked_at"] = now
        state["blocker_phase"] = phase
    else:
        # 找下一个 phase
        idx = PHASE_ORDER.index(phase) if phase in PHASE_ORDER else -1
        if idx < len(PHASE_ORDER) - 1:
            state["current_phase"] = PHASE_ORDER[idx + 1]
        else:
            state["current_phase"] = "COMPLETED"

    save_phase_state(token_address, state)
    return state


def block_phase(token_address: str, phase: str, reasons: list[str]) -> dict:
    """标记某个 phase 为 BLOCK"""
    state = load_phase_state(token_address)
    if state is None:
        state = create_phase_state(token_address)

    now = datetime.now(timezone.utc).isoformat()
    state["current_phase"] = "BLOCKED"
    state["blocked_at"] = now
    state["blocker_phase"] = phase
    state["blocker_reasons"] = reasons

    save_phase_state(token_address, state)
    return state


def set_gate_decision(token_address: str, decision: str) -> dict:
    """设置最终 gate decision"""
    state = load_phase_state(token_address)
    if state is None:
        state = create_phase_state(token_address)

    state["gate_decision"] = decision
    state["current_phase"] = "COMPLETED"

    save_phase_state(token_address, state)
    return state


def resolve_resume_phase(token_address: str, resume_phase: str) -> str:
    """
    确定实际应该从哪个 phase 恢复。
    如果 resume_phase 之前的 phase 没完成，从缺失处重跑。
    """
    state = load_phase_state(token_address)
    if state is None:
        return PHASE_ORDER[0]

    completed = {p["phase"] for p in state.get("completed_phases", [])}
    resume_idx = PHASE_ORDER.index(resume_phase) if resume_phase in PHASE_ORDER else 0

    for i in range(resume_idx):
        if PHASE_ORDER[i] not in completed:
            return PHASE_ORDER[i]

    return resume_phase


def get_stale_phases(token_address: str) -> list[str]:
    """检查哪些 phase 的数据已过期"""
    import time

    run_dir = get_run_dir(token_address)
    stale = []

    for phase, ttl in TTL_MAP.items():
        output_file = run_dir / OUTPUT_FILES.get(phase, f"{phase}.json")
        if output_file.exists():
            age = time.time() - output_file.stat().st_mtime
            if age > ttl:
                stale.append(phase)

    return stale
