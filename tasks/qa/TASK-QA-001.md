# Task Card

task_id: TASK-QA-001
title: Create pytest failure attribution report for current 8 failures
owner_terminal: qa-ci
status: READY

## Input Files
- `pytest output from current baseline`
- `docs/acceptance.md`
- `tasks/task_tree.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `reports/TASK-QA-001/result.md`
- `reports/pytest_failure_attribution.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] report maps each failing test to a backend task card
- [ ] report distinguishes implementation bug vs stale test vs entrypoint mismatch
- [ ] no production/live actions
- [ ] result.md written

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Use the known baseline: 8 failed, 5 passed. Re-run pytest if needed, then write attribution.

