# Task Card

task_id: TASK-SCHEMA-002
title: Add per-skill output contract tests
owner_terminal: qa-ci
status: READY

## Input Files
- `skills/*/tests/*.py`
- `skills/common/validators.py`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `tests/test_skill_output_contracts.py`
- `reports/TASK-SCHEMA-002/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] Each skill targeted mock output validates
- [ ] Trade gate output validates extra contract
- [ ] Full pytest passes

## Dependencies
- Frozen docs exist.

## Blocked By
- none
