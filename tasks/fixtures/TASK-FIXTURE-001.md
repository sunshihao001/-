# Task Card

task_id: TASK-FIXTURE-001
title: Expand fixture matrix into full GMGN mock input / expected output contract
owner_terminal: qa-ci
status: READY

## Input Files
- `fixtures/*.json`
- `design/工程完善计划书.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `fixtures/*.json`
- `fixtures/README.md`
- `tests/test_fixture_matrix_contract.py`
- `reports/TASK-FIXTURE-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Acceptance Criteria
- [ ] All five fixtures include full mock_inputs categories
- [ ] All five fixtures include expected_outputs for six skills
- [ ] Coverage includes BLOCK/WATCH/PAPER_ONLY/NEED_MORE_DATA
- [ ] JSON parse tests pass

## Dependencies
- Frozen docs exist.

## Blocked By
- none
