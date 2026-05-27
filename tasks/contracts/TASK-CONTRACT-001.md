# Task Card

task_id: TASK-CONTRACT-001
title: Wire validators before each skill save or controller summary
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/common/validators.py`
- `skills/*/scripts/run.py`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/common/validators.py`
- `skills/*/scripts/run.py`
- `tests/test_validator_integration.py`
- `reports/TASK-CONTRACT-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] Invalid skill output raises before save
- [ ] Controller summary validates through summary validator
- [ ] Full pytest passes

## Dependencies
- rules / fixtures / validators baseline exists.

## Blocked By
- none
