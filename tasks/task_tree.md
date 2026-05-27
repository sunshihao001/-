# Task Tree — Initial AI Pro Dev Workflow Batch

## Goal
Stabilize `/root/sikk-gmgn/` enough for controlled multi-terminal AI development.

## Current Batch

### Control Plane
- [x] `AGENTS.md`
- [x] `docs/ai_dev_workflow.md`
- [x] `CONTEXT.md`
- [x] `docs/specs.md`
- [x] `docs/acceptance.md`
- [x] `docs/freeze_record.md`

### Backend Contract Fixes
- [ ] `TASK-BE-001` — Fix `meme-token-panel` output and honeypot contract.
- [ ] `TASK-BE-002` — Fix `meme-trade-gate` `gate_decision` output contract.
- [ ] `TASK-BE-003` — Fix wallet roles entrypoint/mock contract mismatch.
- [ ] `TASK-BE-004` — Fix wallet structure risk/concentration output contract.
- [ ] `TASK-BE-005` — Fix evidence chain PASS/WARN/BLOCK semantics.

### QA / Attribution
- [ ] `TASK-QA-001` — Create pytest failure attribution report for current 8 failures.
- [ ] `TASK-QA-002` — Create fixture matrix skeleton covering BLOCK/WATCH/PAPER_ONLY/NEED_MORE_DATA.
- [ ] `TASK-CI-001` — Re-run pytest and record baseline after backend fixes.

### Five-Forces Entry (CR-2026-05-25-002)
状态：CR-2026-05-25-002 已获人类批准；freeze record 002 已写入。按依赖顺序执行；`TASK-RULE-005` 已完成，下一步执行 `TASK-SCHEMA-003`。
- [x] `TASK-DOC-002` — Apply CR-2026-05-25-002 to frozen docs and write freeze record 002.
- [x] `TASK-RULE-005` — Author `rules/entry_five_forces_rules_v1.json`.
- [ ] `TASK-SCHEMA-003` — Extend `meme-candidate-entry` schema for Five-Forces Gate output.
- [ ] `TASK-BE-006` — Implement Five-Forces Gate logic in `meme-candidate-entry`.
- [ ] `TASK-BE-007` — `meme-workflow-controller` honors `basic_gate=FILTERED_OUT` and `entry_aux_decision=SKIP`.
- [ ] `TASK-FIXTURE-003` — Fixtures for entry decisions (PASS/CAUTION/SKIP/FILTERED_OUT/UNKNOWN).
- [ ] `TASK-QA-003` — Pytest for Five-Forces Gate + controller skip behavior.

## Execution Rule
Backend/QA may execute only READY task cards and must write `reports/<task_id>/result.md`.
