# Task Card

task_id: TASK-DOC-001
title: Update 工程完善计划书 current status
owner_terminal: docs-a
status: READY

## Input Files
- `design/工程完善计划书.md`
- `reports/*.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `design/工程完善计划书.md`
- `reports/TASK-DOC-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] Outdated asset status corrected
- [ ] New rule/fixture/schema/data deepening status reflected
- [ ] No frozen docs modified

## Dependencies
- Frozen docs exist.

## Blocked By
- none
