# Task Card

task_id: TASK-BE-004
title: Fix wallet structure risk and concentration output contract
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/meme-wallet-structure/scripts/run.py`
- `skills/meme-wallet-structure/tests/test_wallet_structure.py`
- `skills/meme-wallet-structure/tests/test_wallet_structure_exclusions.py`
- `docs/specs.md`
- `docs/acceptance.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/meme-wallet-structure/scripts/run.py`
- `skills/meme-wallet-structure/scripts/*.py`
- `reports/TASK-BE-004/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `pytest -q skills/meme-wallet-structure/tests` passes
- [ ] high same-source structure risk produces WARN rather than unintended BLOCK unless blocker criteria clearly apply
- [ ] output includes `concentration.top5_holder_pct`
- [ ] pool/exchange addresses are excluded from concentration where applicable
- [ ] result.md written

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Current failures:
- expected WARN got BLOCK for high-risk same-source scenario
- missing `concentration` key in pool exclusion test

