# Task Card

task_id: TASK-RULE-002
title: Create rules/downgrade_rules_v1.json covering all 7 skills
owner_terminal: skill-backend
status: READY

## Input Files
- `design/phase0-workflow-contract.md`
- `design/phase1-skill-*.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `rules/downgrade_rules_v1.json`
- `rules/README.md`
- `tests/test_rule_contracts.py`
- `reports/TASK-RULE-002/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] downgrade rules cover all seven meme skills
- [ ] Each rule has missing_fields impact where applicable
- [ ] JSON parses
- [ ] contract tests pass

## Dependencies
- Frozen docs exist.

## Blocked By
- none
