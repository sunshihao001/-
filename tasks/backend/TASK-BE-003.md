# Task Card

task_id: TASK-BE-003
title: Fix wallet roles entrypoint and mock contract mismatch
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/meme-wallet-roles/scripts/run.py`
- `skills/meme-wallet-roles/tests/test_wallet_roles.py`
- `skills/meme-candidate-entry/scripts/run.py`
- `docs/specs.md`
- `docs/acceptance.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/meme-wallet-roles/scripts/run.py`
- `skills/meme-wallet-roles/scripts/*.py`
- `skills/meme-wallet-roles/tests/test_wallet_roles.py`
- `reports/TASK-BE-003/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `pytest -q skills/meme-wallet-roles/tests/test_wallet_roles.py` passes or result documents test imports wrong module
- [ ] wallet_roles task does not accidentally execute candidate_entry logic
- [ ] mock GMGN client contract is explicit
- [ ] result.md written

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Current failure shows `skills/meme-candidate-entry/scripts/run.py` executing inside wallet_roles test and mock lacks `token_info`. Diagnose import/path/entrypoint issue before changing logic.

