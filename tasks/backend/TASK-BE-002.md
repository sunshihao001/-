# Task Card

task_id: TASK-BE-002
title: Fix meme-trade-gate gate_decision output contract
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/meme-trade-gate/scripts/run.py`
- `skills/meme-trade-gate/tests/test_trade_gate.py`
- `docs/specs.md`
- `docs/acceptance.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`

## Allowed Write Paths
- `skills/meme-trade-gate/scripts/run.py`
- `skills/meme-trade-gate/scripts/*.py`
- `reports/TASK-BE-002/result.md`

## Forbidden
- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Change unrelated files
- Expand scope
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `pytest -q skills/meme-trade-gate/tests/test_trade_gate.py` passes
- [ ] trade gate output always includes `gate_decision` when execution reaches gate logic
- [ ] honeypot evidence maps to `BLOCK`
- [ ] valid low-risk evidence maps to `PAPER_ONLY` within Phase 1
- [ ] result.md written

## Dependencies
- none

## Blocked By
- none

## Failure / Work Details
Current failures:
- `test_trade_gate_paper_only`: `KeyError: gate_decision`
- `test_trade_gate_honeypot_block`: `KeyError: gate_decision`

