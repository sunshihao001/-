# Task Card

task_id: TASK-DATA-001
title: Define missing_fields / downgrade taxonomy
owner_terminal: docs-a
status: READY

## Input Files
- `docs/specs.md`
- `design/phase0-workflow-contract.md`
- `rules/downgrade_rules_v1.json`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `docs/missing_data_policy.md`
- `reports/TASK-DATA-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] Defines missing field severity taxonomy
- [ ] Defines retry/refresh/recover semantics
- [ ] Maps taxonomy to downgrade_rules
- [ ] No runtime/live permission added

## Dependencies
- Frozen docs exist.

## Blocked By
- none
