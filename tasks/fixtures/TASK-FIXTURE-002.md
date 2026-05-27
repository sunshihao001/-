# Task Card

task_id: TASK-FIXTURE-002
title: Make fixture matrix executable end-to-end mock pipeline tests
owner_terminal: qa-ci
status: READY

## Input Files
- `fixtures/*.json`
- `skills/*/scripts/run.py`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `tests/test_fixture_e2e_pipeline.py`
- `reports/TASK-FIXTURE-002/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] Fixture scenarios execute through skill functions with mocks or staged outputs
- [ ] Expected gate decisions verified
- [ ] No live GMGN or trading calls

## Dependencies
- rules / fixtures / validators baseline exists.

## Blocked By
- none
