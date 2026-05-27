"""
file_io.py — JSON 读写 + data/runs/ 目录管理

对应设计文件：design/phase0-workflow-contract.md 目录结构
"""

from __future__ import annotations

import os
import json
import time
from pathlib import Path
from typing import Any

# 项目根目录
PROJECT_ROOT = Path("/root/sikk-gmgn")
DATA_RUNS = PROJECT_ROOT / "data" / "runs"
STATE_DIR = PROJECT_ROOT / "state"


def get_run_dir(token_address: str) -> Path:
    """获取 token 的运行目录，自动创建。

    Walking Skeleton 模式（SIKK_SKELETON_MODE=1）：
    所有 run 写到 data/runs/_skeleton_/<token>/，与正式 run 物理隔离，
    避免骨架阶段的 mock 数据污染真实运行历史。
    依据：freeze_record 003 — Walking Skeleton freeze。
    """
    if os.environ.get("SIKK_SKELETON_MODE") == "1":
        run_dir = DATA_RUNS / "_skeleton_" / token_address
    else:
        run_dir = DATA_RUNS / token_address
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_json(data: dict | list, path: str | Path) -> str:
    """保存 JSON 到文件，自动创建目录"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(path)


def load_json(path: str | Path) -> dict | list:
    """从 JSON 文件加载"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_markdown(content: str, path: str | Path) -> str:
    """保存 Markdown 到文件"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(path)


def file_age_seconds(path: str | Path) -> float | None:
    """返回文件距今的秒数，文件不存在返回 None"""
    path = Path(path)
    if not path.exists():
        return None
    return time.time() - path.stat().st_mtime


def is_stale(path: str | Path, ttl_seconds: int) -> bool:
    """检查文件是否过期"""
    age = file_age_seconds(path)
    if age is None:
        return True  # 文件不存在视为过期
    return age > ttl_seconds


# ── 全局状态管理 ──

def load_active_runs() -> dict:
    """加载当前活跃的分析任务"""
    path = STATE_DIR / "active_runs.json"
    if path.exists():
        return load_json(path)
    return {"active": []}


def save_active_runs(data: dict) -> str:
    return save_json(data, STATE_DIR / "active_runs.json")


def load_completed_runs() -> dict:
    """加载已完成的分析索引"""
    path = STATE_DIR / "completed_runs.json"
    if path.exists():
        return load_json(path)
    return {"completed": []}


def save_completed_runs(data: dict) -> str:
    return save_json(data, STATE_DIR / "completed_runs.json")
