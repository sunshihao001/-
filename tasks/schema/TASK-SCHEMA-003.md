# Task Card

task_id: TASK-SCHEMA-003
title: Extend meme-candidate-entry schema for Five-Forces Gate output
owner_terminal: skill-backend
status: READY

## Input Files
- `skills/meme-candidate-entry/scripts/schema.py`
- `docs/proposed/CR-2026-05-25-002-docs-patch.md`
- `rules/entry_five_forces_rules_v1.json` (after TASK-RULE-005)

## Read-Only Context
- `docs/specs.md` (after TASK-DOC-002)
- `docs/acceptance.md` (after TASK-DOC-002)
- `CONTEXT.md` (after TASK-DOC-002)
- `docs/freeze_record.md` (entry 002)

## Allowed Write Paths
- `skills/meme-candidate-entry/scripts/schema.py`
- `reports/TASK-SCHEMA-003/result.md`

## Forbidden
- Modify `skills/meme-candidate-entry/scripts/run.py` in this card
- Modify `skills/meme-candidate-entry/scripts/rules.py` in this card
- Touch any other skill folder
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `schema.py` defines a `FiveForces` dataclass with the five force fields and explicit Literal/Enum values.
- [ ] `schema.py` defines a `BasicGate` dataclass with `decision`, `reasons`, plus numeric snapshot fields (`liquidity`, `market_cap`, `volume`, `holder_count`, `swaps`).
- [ ] `schema.py` defines a `GmgnRiskDensity` dataclass with `level`, `score`, `reasons`.
- [ ] `CandidateEntryOutput` is extended with `entry_stage`, `basis`, `basic_gate`, `five_forces`, `gmgn_risk_density`, `entry_aux_decision`, `next_action`.
- [ ] `basis` default is the literal `"gmgn_field_combination_hint"`.
- [ ] All previous schema fields remain present; no breaking removal.
- [ ] `python3 -m py_compile skills/meme-candidate-entry/scripts/schema.py` passes.
- [ ] `reports/TASK-SCHEMA-003/result.md` includes the diff and a JSON sample.

## Dependencies
- TASK-RULE-005 must be `INTERNAL_PASS`.

## Blocked By
- none.

## Unblocked By
- TASK-RULE-005 INTERNAL_PASS and `rules/entry_five_forces_rules_v1.json`.
