# Task Card

task_id: TASK-BE-007
title: meme-workflow-controller honors basic_gate FILTERED_OUT and entry_aux_decision SKIP
owner_terminal: skill-backend
status: BLOCKED

## Input Files
- `skills/meme-workflow-controller/scripts/run.py`
- `skills/meme-candidate-entry/scripts/run.py` (after TASK-BE-006)

## Read-Only Context
- `docs/specs.md` (after TASK-DOC-002)
- `docs/acceptance.md` (after TASK-DOC-002)
- `CONTEXT.md` (after TASK-DOC-002)
- `docs/freeze_record.md` (entry 002)

## Allowed Write Paths
- `skills/meme-workflow-controller/scripts/run.py`
- `reports/TASK-BE-007/result.md`

## Forbidden
- Modify any other skill folder
- Modify `meme-trade-gate` decision semantics
- Add new gate decision values
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] In `screen_candidate_pool`, candidates with `basic_gate.decision == "FILTERED_OUT"` from S01 are NOT run through S02-S06; they are recorded in a new `skipped` list with `skipped_reason == "basic_gate_filtered_out"` and `entry_aux_decision`.
- [ ] In `screen` CLI, new flag `--skip-entry-risk {none,high,extreme}` (default `none`):
  - `none`: only `FILTERED_OUT` is skipped.
  - `high`: also skip `entry_aux_decision == SKIP` with `gmgn_risk_density.level in {"high","extreme"}`.
  - `extreme`: only skip when `gmgn_risk_density.level == "extreme"`.
- [ ] Single-token `run(...)` path is unchanged for normal candidates; if S01 returns `basic_gate.decision == FILTERED_OUT`, controller writes a `workflow_summary.json` with `workflow_status == "FILTERED_OUT"` and stops, without invoking S02-S06.
- [ ] `筛选结果.json` includes `filtered_out_count`, `skipped_count`, `completed_count`, `total_count` and a `skipped` array carrying each skipped candidate's reason.
- [ ] `筛选报告.md` lists Skipped section under a clear Chinese heading `## 入口跳过`.
- [ ] All pre-existing controller tests pass; one new test covers `FILTERED_OUT` short-circuit; one new test covers `--skip-entry-risk high`.
- [ ] `python3 -m py_compile skills/meme-workflow-controller/scripts/run.py` passes.
- [ ] `reports/TASK-BE-007/result.md` records CLI examples and one batch sample output.

## Dependencies
- TASK-BE-006 must be `INTERNAL_PASS`.

## Blocked By
- TASK-BE-006.
