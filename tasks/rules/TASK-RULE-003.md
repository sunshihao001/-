# Task Card

task_id: TASK-RULE-003
title: Add rule contract tests
owner_terminal: qa-ci
status: READY

## Input Files
- `rules/gate_rules_v1.json`
- `rules/downgrade_rules_v1.json`
- `skills/common/rule_loader.py`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `tests/test_rule_contracts.py`
- `reports/TASK-RULE-003/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] Tests fail before JSON exists or required fields missing
- [ ] Tests verify loader uses JSON files
- [ ] Tests pass

## Dependencies
- Frozen docs exist.

## Blocked By
- none
