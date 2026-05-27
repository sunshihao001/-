# Task Card

task_id: TASK-RULE-001
title: Create rules/gate_rules_v1.json from Skill 06 design
owner_terminal: skill-backend
status: READY

## Input Files
- `design/phase1-skill-06-trade-gate.md`
- `skills/common/rule_loader.py`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `rules/gate_rules_v1.json`
- `rules/README.md`
- `tests/test_rule_contracts.py`
- `reports/TASK-RULE-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] G01-G06 and G10-G19 exist
- [ ] PAPER_ONLY and NEED_MORE_DATA meta conditions exist
- [ ] Each rule has rationale/source_fields/action/category
- [ ] JSON parses
- [ ] contract tests pass

## Dependencies
- Frozen docs exist.

## Blocked By
- none
