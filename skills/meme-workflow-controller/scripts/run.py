"""run.py — Skill 07: meme-workflow-controller 主入口

功能：按顺序调度 Skill 01-06，管理 phase_state，生成 workflow_summary.md。
Phase 1：paper-only / research-only。禁止交易 API。
"""
from __future__ import annotations

import sys, json, importlib.util
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, "/root/sikk-gmgn/skills")
from common.file_io import get_run_dir, save_json, save_markdown, load_active_runs, save_active_runs, load_completed_runs, save_completed_runs
from common.validators import validate_controller_summary
from common.phase_state import create_phase_state, load_phase_state, resolve_resume_phase, get_stale_phases, PHASE_ORDER

PROJECT_ROOT = Path("/root/sikk-gmgn")
SKILLS_ROOT = PROJECT_ROOT / "skills"

SKILL_RUNNERS = {
    "candidate_entry": SKILLS_ROOT / "meme-candidate-entry" / "scripts" / "run.py",
    "token_panel": SKILLS_ROOT / "meme-token-panel" / "scripts" / "run.py",
    "wallet_roles": SKILLS_ROOT / "meme-wallet-roles" / "scripts" / "run.py",
    "wallet_structure": SKILLS_ROOT / "meme-wallet-structure" / "scripts" / "run.py",
    "evidence_chain": SKILLS_ROOT / "meme-evidence-chain" / "scripts" / "run.py",
    "trade_gate": SKILLS_ROOT / "meme-trade-gate" / "scripts" / "run.py",
}

STOP_STATUSES = {"BLOCK", "ERROR"}


# ── Walking Skeleton mock fixtures ──
# 依据：freeze_record 003 — Walking Skeleton freeze
# 目的：让 7 个 skill 在不接真实数据的情况下端到端跑通，
# 验证总控编排 + 状态机 + 容错 + 交接物落盘 + 断点续跑这一层。
# 数据真实性不在本阶段验证范围内。
SKELETON_MOCKS = {
    "candidate_entry": {
        "schema_version": "1.0",
        "skill_name": "meme-candidate-entry",
        "status": "PASS",
        "gate_decision": "PASS",
        "basic_gate": "PASS",
        "entry_aux_decision": "PASS",
        "blocker_reasons": [],
        "_skeleton_mock": True,
    },
    "token_panel": {
        "schema_version": "1.0",
        "skill_name": "meme-token-panel",
        "status": "PASS",
        "basic_info": {"symbol": "SKELETON", "name": "Skeleton Mock Token"},
        "risk_score_card": {"overall_risk": "low"},
        "_skeleton_mock": True,
    },
    "wallet_roles": {
        "schema_version": "1.0",
        "skill_name": "meme-wallet-roles",
        "status": "PASS",
        "wallet_summary": {"smart_money_count": 0},
        "smart_money_behavior": {"sm_net_direction": "neutral"},
        "_skeleton_mock": True,
    },
    "wallet_structure": {
        "schema_version": "1.0",
        "skill_name": "meme-wallet-structure",
        "status": "PASS",
        "structure_risk": {"overall_structure_risk": "low"},
        "_skeleton_mock": True,
    },
    "evidence_chain": {
        "schema_version": "1.0",
        "skill_name": "meme-evidence-chain",
        "status": "PASS",
        "confidence_score": 0,
        "narrative": {"one_line": "Walking Skeleton mock evidence — not a real judgment."},
        "risk_factors": [],
        "positive_signals": [],
        "_skeleton_mock": True,
    },
    "trade_gate": {
        "schema_version": "1.0",
        "skill_name": "meme-trade-gate",
        "status": "PASS",
        "gate_decision": "NEED_MORE_DATA",
        "gate_score": {"total_score": 0},
        "confidence_score": 0,
        "next_action": "SKELETON_COMPLETE",
        "_skeleton_mock": True,
    },
}

# phase → 该 phase 落盘的文件名（与各 skill 实际写入保持一致）
SKELETON_OUTPUT_FILES = {
    "candidate_entry": "candidate_entry.json",
    "token_panel": "token_panel.json",
    "wallet_roles": "wallet_roles.json",
    "wallet_structure": "wallet_structure.json",
    "evidence_chain": "evidence_chain.json",
    "trade_gate": "trade_gate.json",
}


def is_skeleton_mode() -> bool:
    """Walking Skeleton 模式开关。由 --skeleton CLI flag 或 SIKK_SKELETON_MODE=1 触发。"""
    import os
    return os.environ.get("SIKK_SKELETON_MODE") == "1"


def _run_phase_skeleton(phase: str, token_address: str) -> dict:
    """骨架模式下的 phase 短路：写 mock JSON，推进状态机，不调真实 skill。"""
    from common.phase_state import complete_phase
    mock = dict(SKELETON_MOCKS[phase])
    mock["token_address"] = token_address
    mock["timestamp"] = datetime.now(timezone.utc).isoformat()
    run_dir = get_run_dir(token_address)
    save_json(mock, run_dir / SKELETON_OUTPUT_FILES[phase])
    complete_phase(token_address, phase, "PASS")
    return mock


def run(token_address: str, chain: str = "sol", resume_from: str | None = None, force_refresh: bool = False) -> dict:
    """执行完整工作流。"""
    _mark_active(token_address)
    try:
        state_info = _prepare_start_state(token_address, resume_from=resume_from, force_refresh=force_refresh)
        state = state_info["state"]
        start_phase = state_info["start_phase"]
        start_idx = PHASE_ORDER.index(start_phase)

        results = {}
        for phase in PHASE_ORDER[start_idx:]:
            result = _run_phase(phase, token_address, chain)
            results[phase] = result
            status = result.get("status")
            if status in STOP_STATUSES:
                summary = _build_block_summary(token_address, phase, result)
                _write_workflow_summary(token_address, summary)
                return summary
            # trade_gate 用 gate_decision 控制最终状态
            if phase == "trade_gate":
                summary = _build_complete_summary(token_address, results)
                _write_workflow_summary(token_address, summary)
                _mark_completed(token_address, summary)
                return summary

        summary = _build_complete_summary(token_address, results)
        _write_workflow_summary(token_address, summary)
        _mark_completed(token_address, summary)
        return summary
    finally:
        _unmark_active(token_address)


def status(token_address: str) -> dict:
    """查看单个 token 状态。"""
    state = load_phase_state(token_address)
    if not state:
        return {"token_address": token_address, "status": "NOT_FOUND"}
    stale = get_stale_phases(token_address)
    details = _stale_phase_details(token_address, stale)
    return {"token_address": token_address, "status": "FOUND", "phase_state": state, "stale_phases": stale, "stale_phase_details": details}


def list_runs() -> dict:
    """查看 active/completed 索引。"""
    return {"active_runs": load_active_runs(), "completed_runs": load_completed_runs()}


def _prepare_start_state(token_address: str, resume_from: str | None = None, force_refresh: bool = False) -> dict:
    state = load_phase_state(token_address) or create_phase_state(token_address)
    start_phase = resolve_resume_phase(token_address, resume_from) if resume_from else state.get("current_phase", "candidate_entry")
    if force_refresh:
        state = create_phase_state(token_address)
        state["reset_reason"] = "force_refresh"
        state["resume_from"] = None
        from common.phase_state import save_phase_state
        save_phase_state(token_address, state)
        start_phase = "candidate_entry"
    elif start_phase in ("COMPLETED", "BLOCKED", "ERROR"):
        start_phase = "candidate_entry"
    if start_phase not in PHASE_ORDER:
        start_phase = "candidate_entry"
    return {"state": state, "start_phase": start_phase}


def _stale_phase_details(token_address: str, stale: list[str]) -> list[dict]:
    from common.phase_state import OUTPUT_FILES, TTL_MAP
    import time
    rd = get_run_dir(token_address)
    details = []
    for phase in stale:
        path = rd / OUTPUT_FILES.get(phase, f"{phase}.json")
        details.append({
            "phase": phase,
            "output_file": str(path),
            "ttl_seconds": TTL_MAP.get(phase),
            "age_seconds": int(time.time() - path.stat().st_mtime) if path.exists() else None,
        })
    return details


def _run_phase(phase: str, token_address: str, chain: str) -> dict:
    # Walking Skeleton 模式：短路，不调真实 skill。
    if is_skeleton_mode():
        return _run_phase_skeleton(phase, token_address)
    path = SKILL_RUNNERS[phase]
    mod = _load_module(path, f"sikk_{phase}_runner")
    if phase == "candidate_entry":
        return mod.run(token_address=token_address, chain=chain, entry_source="manual_ca", entry_reason="workflow_controller")
    return mod.run(token_address=token_address, chain=chain)


def _load_module(path: Path, module_name: str):
    # 每个 skill 都有 scripts/rules.py / schema.py。动态加载时必须清理同名模块，避免串包。
    for name in ("rules", "schema"):
        if name in sys.modules:
            del sys.modules[name]
    script_dir = str(path.parent)
    if script_dir in sys.path:
        sys.path.remove(script_dir)
    sys.path.insert(0, script_dir)

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build_block_summary(token_address: str, phase: str, result: dict) -> dict:
    return {
        "schema_version": "1.0",
        "skill_name": "meme-workflow-controller",
        "token_address": token_address,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workflow_status": "BLOCKED" if result.get("status") == "BLOCK" else "ERROR",
        "blocked_at": phase,
        "blocker_reasons": result.get("blocker_reasons", []),
        "gate_decision": "BLOCK" if result.get("status") == "BLOCK" else "NEED_MORE_DATA",
        "summary_file": str(get_run_dir(token_address) / "workflow_summary.md"),
        "next_action": "STOP",
        "forbidden": ["live_trading", "swap", "private_key", "signing", "broadcast"],
    }


def _build_complete_summary(token_address: str, results: dict) -> dict:
    rd = get_run_dir(token_address)
    def load(name):
        p = rd / name
        return json.load(open(p, encoding="utf-8")) if p.exists() else {}
    token_panel = load("token_panel.json")
    wallet_roles = load("wallet_roles.json")
    wallet_structure = load("wallet_structure.json")
    evidence_chain = load("evidence_chain.json")
    trade_gate = load("trade_gate.json")
    symbol = token_panel.get("basic_info", {}).get("symbol", token_address[:8])
    return {
        "schema_version": "1.0",
        "skill_name": "meme-workflow-controller",
        "token_address": token_address,
        "symbol": symbol,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "workflow_status": "COMPLETED",
        "gate_decision": trade_gate.get("gate_decision", "NEED_MORE_DATA"),
        "gate_score": trade_gate.get("gate_score", {}).get("total_score", 0),
        "confidence_score": trade_gate.get("confidence_score", evidence_chain.get("confidence_score", 0)),
        "key_findings": {
            "narrative": evidence_chain.get("narrative", {}).get("one_line", ""),
            "smart_money_count": wallet_roles.get("wallet_summary", {}).get("smart_money_count", 0),
            "sm_direction": wallet_roles.get("smart_money_behavior", {}).get("sm_net_direction", "unknown"),
            "structure_risk": wallet_structure.get("structure_risk", {}).get("overall_structure_risk", "unknown"),
            "security_risk": token_panel.get("risk_score_card", {}).get("overall_risk", "unknown"),
        },
        "risk_factors": evidence_chain.get("risk_factors", []),
        "positive_signals": evidence_chain.get("positive_signals", []),
        "next_action": trade_gate.get("next_action", "COMPLETED"),
        "summary_file": str(rd / "workflow_summary.md"),
        "forbidden": ["live_trading", "swap", "private_key", "signing", "broadcast"],
    }


def _write_workflow_summary(token_address: str, summary: dict) -> None:
    rd = get_run_dir(token_address)
    gd = summary.get("gate_decision", "")
    md = f"""# Workflow Summary: {summary.get('symbol', token_address[:8])}

**Token:** {token_address}
**Chain:** SOL
**Analyzed at:** {summary.get('timestamp')}
**Workflow Status:** {summary.get('workflow_status')}
**Gate Decision:** {gd}
**Gate Score:** {summary.get('gate_score', 0)}/100
**Confidence:** {summary.get('confidence_score', 0)}

---

## Key Findings
- Narrative: {summary.get('key_findings', {}).get('narrative', '')}
- Smart Money: {summary.get('key_findings', {}).get('smart_money_count', 0)}, {summary.get('key_findings', {}).get('sm_direction', 'unknown')}
- Structure Risk: {summary.get('key_findings', {}).get('structure_risk', 'unknown')}
- Security Risk: {summary.get('key_findings', {}).get('security_risk', 'unknown')}

## Risk Factors
{_list_md(summary.get('risk_factors', []))}

## Positive Signals
{_list_md(summary.get('positive_signals', []))}

## Blockers
{_list_md(summary.get('blocker_reasons', []))}

## Safety Boundary
- 禁止 live trading
- 禁止 swap
- 禁止 private key
- 禁止 signing
- 禁止 broadcast
- 当前输出只用于 research / paper-only 判断

## Next
{summary.get('next_action')}
"""
    errors = validate_controller_summary(summary)
    if errors:
        raise AssertionError('; '.join(errors))
    save_markdown(md, rd / "workflow_summary.md")
    save_json(summary, rd / "workflow_summary.json")
    if summary.get("workflow_status") in ("BLOCKED", "ERROR"):
        blocker_md = f"""# Blocker Report: {token_address}

Blocked at: {summary.get('blocked_at')}
Status: {summary.get('workflow_status')}
Gate Decision: {summary.get('gate_decision')}

## Blocker Reasons
{_list_md(summary.get('blocker_reasons', []))}

## Safety Boundary
- no live trading
- no swap
- no private key
- no signing
- no broadcast
"""
        save_markdown(blocker_md, rd / "blocker_report.md")


def _list_md(items) -> str:
    if not items:
        return "- 无"
    out = []
    for x in items:
        if isinstance(x, dict):
            out.append("- " + json.dumps(x, ensure_ascii=False))
        else:
            out.append(f"- {x}")
    return "\n".join(out)


def _mark_active(token_address: str) -> None:
    data = load_active_runs()
    active = data.setdefault("active", [])
    if token_address not in active:
        active.append(token_address)
    save_active_runs(data)


def _unmark_active(token_address: str) -> None:
    data = load_active_runs()
    data["active"] = [x for x in data.get("active", []) if x != token_address]
    save_active_runs(data)


def _mark_completed(token_address: str, summary: dict) -> None:
    data = load_completed_runs()
    completed = [x for x in data.get("completed", []) if x.get("token_address") != token_address]
    completed.append({"token_address": token_address, "completed_at": summary.get("timestamp"), "gate_decision": summary.get("gate_decision"), "summary_file": summary.get("summary_file")})
    data["completed"] = completed
    save_completed_runs(data)


def screen_candidate_pool(candidate_pool: dict, chain: str = "sol", runner=None) -> dict:
    """批量调度候选池。候选发现由 S01 完成；这里只负责逐个跑完整工作流并汇总。"""
    if runner is None:
        runner = run
    now = datetime.now(timezone.utc)
    batch_id = now.strftime("%Y%m%dT%H%M%SZ")
    batch_dir = PROJECT_ROOT / "data" / "runs" / "batches" / batch_id
    batch_dir.mkdir(parents=True, exist_ok=True)

    candidates = candidate_pool.get("candidates", [])
    results = []
    for c in candidates:
        token = c.get("token_address")
        if not token:
            continue
        try:
            summary = runner(token, chain=chain, force_refresh=True)
            results.append({
                "token_address": token,
                "symbol": summary.get("symbol", c.get("symbol", "")),
                "entry_source": c.get("entry_source", ""),
                "entry_reason": c.get("entry_reason", ""),
                "workflow_status": summary.get("workflow_status"),
                "gate_decision": summary.get("gate_decision"),
                "gate_score": summary.get("gate_score"),
                "confidence_score": summary.get("confidence_score"),
                "summary_file": summary.get("summary_file"),
            })
        except Exception as e:
            results.append({
                "token_address": token,
                "symbol": c.get("symbol", ""),
                "entry_source": c.get("entry_source", ""),
                "entry_reason": c.get("entry_reason", ""),
                "workflow_status": "ERROR",
                "gate_decision": "NEED_MORE_DATA",
                "error": str(e),
            })

    result = {
        "schema_version": "1.0",
        "batch_id": batch_id,
        "source": candidate_pool.get("source", ""),
        "generated_at": now.isoformat(),
        "candidate_count": len(candidates),
        "filtered_out_count": candidate_pool.get("filtered_out_count", 0),
        "completed_count": len(results),
        "results": results,
        "筛选结果文件": str(batch_dir / "筛选结果.json"),
        "筛选报告文件": str(batch_dir / "筛选报告.md"),
    }
    save_json(candidate_pool, batch_dir / "候选池.json")
    save_json(result, batch_dir / "筛选结果.json")
    save_markdown(_screen_report(result), batch_dir / "筛选报告.md")
    return result


def screen(source: str = "trending", limit: int = 10, chain: str = "sol", min_liquidity: float = 50000, min_market_cap: float = 50000) -> dict:
    """一步式筛选：调用 S01 生成候选池，再批量跑工作流。"""
    s01 = _load_module(SKILL_RUNNERS["candidate_entry"], "sikk_candidate_entry_for_screen")
    candidate_pool = s01.build_candidate_pool(source=source, limit=limit, chain=chain, min_liquidity=min_liquidity, min_market_cap=min_market_cap)
    return screen_candidate_pool(candidate_pool, chain=chain)


def _screen_report(result: dict) -> str:
    lines = [
        "# 筛选报告",
        "",
        f"- Batch ID: {result['batch_id']}",
        f"- Source: {result['source']}",
        f"- Generated At: {result['generated_at']}",
        f"- Candidate Count: {result['candidate_count']}",
        f"- Filtered Out Count: {result.get('filtered_out_count', 0)}",
        f"- Completed Count: {result['completed_count']}",
        "",
        "## Results",
    ]
    for r in result["results"]:
        lines.append(f"- {r.get('symbol','')} | {r['token_address']} | {r.get('gate_decision')} | score={r.get('gate_score')} | {r.get('workflow_status')}")
    lines += [
        "",
        "## Safety Boundary",
        "- 筛选结果只表示研究门控状态，不表示交易许可",
        "- 禁止 live trading / swap / private key / signing / broadcast",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Skill 07: meme-workflow-controller")
    sub = p.add_subparsers(dest="command")
    r = sub.add_parser("run"); r.add_argument("token_address"); r.add_argument("--chain", default="sol"); r.add_argument("--from", dest="resume_from"); r.add_argument("--force-refresh", action="store_true"); r.add_argument("--skeleton", action="store_true", help="Walking Skeleton mode: mock all skills, isolate to data/runs/_skeleton_/")
    s = sub.add_parser("status"); s.add_argument("token_address")
    sc = sub.add_parser("screen"); sc.add_argument("--source", default="trending", choices=["trending", "trenches", "signal", "mixed"]); sc.add_argument("--limit", type=int, default=10); sc.add_argument("--chain", default="sol"); sc.add_argument("--min-liquidity", type=float, default=50000); sc.add_argument("--min-market-cap", type=float, default=50000)
    sub.add_parser("list")
    a = p.parse_args()
    if a.command == "run":
        if getattr(a, "skeleton", False):
            import os
            os.environ["SIKK_SKELETON_MODE"] = "1"
        print(json.dumps(run(a.token_address, a.chain, a.resume_from, a.force_refresh), ensure_ascii=False, indent=2))
    elif a.command == "status": print(json.dumps(status(a.token_address), ensure_ascii=False, indent=2))
    elif a.command == "screen": print(json.dumps(screen(a.source, a.limit, a.chain, a.min_liquidity, a.min_market_cap), ensure_ascii=False, indent=2))
    elif a.command == "list": print(json.dumps(list_runs(), ensure_ascii=False, indent=2))
    else: p.print_help()
