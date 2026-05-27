# Task Card

task_id: TASK-RULE-004
title: Enhance rule_loader for AND/OR/contains/composite conditions
owner_terminal: skill-backend
status: READY

## Input Files
- `rules/gate_rules_v1.json`
- `skills/common/rule_loader.py`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/common/rule_loader.py`
- `tests/test_rule_loader_conditions.py`
- `reports/TASK-RULE-004/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] AND and OR conditions evaluate correctly
- [ ] contains conditions evaluate behavior_signals
- [ ] PAPER_ONLY/NEED_MORE_DATA composite rules are skipped or handled safely
- [ ] Existing tests pass

## Dependencies
- rules / fixtures / validators baseline exists.

## Blocked By
- none
