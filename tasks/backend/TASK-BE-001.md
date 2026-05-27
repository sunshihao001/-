# Task Card

task_id: TASK-BE-001
title: Fix meme-token-panel output and honeypot contract
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/meme-token-panel/scripts/run.py`
- `skills/meme-token-panel/tests/test_token_panel.py`
- `docs/specs.md`
- `docs/acceptance.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/meme-token-panel/scripts/run.py`
- `skills/meme-token-panel/scripts/*.py`
- `reports/TASK-BE-001/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `pytest -q skills/meme-token-panel/tests/test_token_panel.py` passes
- [ ] PASS case includes `risk_score_card.overall_risk == low` or test/spec is coherently updated
- [ ] honeypot mock returns `status == BLOCK`
- [ ] result.md written with commands and evidence

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Current failures:
- `test_token_panel_pass`: `KeyError: risk_score_card`
- `test_token_panel_honeypot_block`: expected `BLOCK`, got `PASS`
Do not change frozen docs. If tests are outdated, document exact contract mismatch in result.md and mark PATCH_REQUIRED.

