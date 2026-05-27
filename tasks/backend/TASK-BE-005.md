# Task Card

task_id: TASK-BE-005
title: Fix evidence-chain PASS/WARN/BLOCK semantics
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/meme-evidence-chain/scripts/run.py`
- `skills/meme-evidence-chain/tests/test_evidence_chain.py`
- `docs/specs.md`
- `docs/acceptance.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/meme-evidence-chain/scripts/run.py`
- `skills/meme-evidence-chain/scripts/*.py`
- `reports/TASK-BE-005/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `pytest -q skills/meme-evidence-chain/tests/test_evidence_chain.py` passes
- [ ] accumulation fixture with low structure risk does not produce unintended BLOCK
- [ ] conflicting/missing evidence remains represented in output
- [ ] result.md written

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Current failure:
- `test_evidence_chain_accumulation`: expected PASS/WARN, got BLOCK

