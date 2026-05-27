# Task Card

task_id: TASK-CI-001
title: Re-run pytest and record baseline after fixes
owner_terminal: qa-ci
status: READY

## Input Files
- `tasks/backend/*.md`
- `tasks/qa/*.md`
- `docs/acceptance.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `reports/TASK-CI-001/result.md`
- `reports/pytest_baseline_after_fixes.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `pytest -q` is executed
- [ ] baseline result recorded with pass/fail counts
- [ ] remaining failures, if any, are mapped to task cards or marked BLOCKED
- [ ] result.md written

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Run after backend tasks are implemented, not before unless used as interim attribution.

