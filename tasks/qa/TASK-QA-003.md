# Task Card

task_id: TASK-QA-003
title: Pytest for Five-Forces Gate + controller skip behavior
owner_terminal: qa-ci
status: BLOCKED

## Input Files
- `skills/meme-candidate-entry/scripts/run.py` (after TASK-BE-006)
- `skills/meme-workflow-controller/scripts/run.py` (after TASK-BE-007)
- `fixtures/entry_five_forces/*.json` (after TASK-FIXTURE-003)

## Read-Only Context
- `docs/specs.md` (after TASK-DOC-002)
- `docs/acceptance.md` (after TASK-DOC-002)
- `CONTEXT.md` (after TASK-DOC-002)
- `docs/freeze_record.md` (entry 002)

## Allowed Write Paths
- `skills/meme-candidate-entry/tests/test_five_forces.py`
- `skills/meme-workflow-controller/tests/test_workflow_skip.py`
- `reports/TASK-QA-003/result.md`
- `reports/TASK-QA-003/fix_result.md`

## Forbidden
- Modify skill `run.py`
- Modify fixtures themselves (only consume them)
- Use live GMGN data
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `test_five_forces.py` covers all five fixtures and asserts `entry_aux_decision`, `basic_gate.decision`, `gmgn_risk_density.level`, plus at least one assertion per force value.
- [ ] `test_workflow_skip.py` includes:
  - one test where S01 returns `FILTERED_OUT` and controller short-circuits with `workflow_status == "FILTERED_OUT"`.
  - one test where `screen(--skip-entry-risk high)` actually skips a `SKIP + high` candidate and the result lists it in `skipped`.
  - one test where `screen(--skip-entry-risk none)` runs the same candidate end-to-end.
- [ ] `pytest -q skills/meme-candidate-entry/tests/test_five_forces.py` passes.
- [ ] `pytest -q skills/meme-workflow-controller/tests/test_workflow_skip.py` passes.
- [ ] Aggregate `pytest -q skills/meme-candidate-entry/tests skills/meme-workflow-controller/tests` passes per isolated-process baseline previously recorded in `reports/pytest_baseline_after_fixes.md`.
- [ ] `reports/TASK-QA-003/result.md` records exact commands, runtime, and pass count.

## Dependencies
- TASK-BE-006, TASK-BE-007, TASK-FIXTURE-003 must be `INTERNAL_PASS`.

## Blocked By
- TASK-FIXTURE-003.
