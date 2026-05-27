# Task Card

task_id: TASK-SCHEMA-001
title: Add common skill output validator
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/common/schema_base.py`
- `docs/specs.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/common/validators.py`
- `reports/TASK-SCHEMA-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] Validator checks standard handoff fields
- [ ] Validator checks statuses and list field types
- [ ] Trade gate validator checks gate fields
- [ ] No dependency on live data

## Dependencies
- Frozen docs exist.

## Blocked By
- none
