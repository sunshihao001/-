# Task Card

task_id: TASK-FIXTURE-003
title: Fixtures for Five-Forces Gate decisions (PASS/CAUTION/SKIP/FILTERED_OUT/UNKNOWN)
owner_terminal: qa-ci
status: BLOCKED

## Input Files
- `skills/meme-candidate-entry/scripts/run.py` (after TASK-BE-006)
- `rules/entry_five_forces_rules_v1.json` (after TASK-RULE-005)
- `learning/GMGN字段组合五力模型理论总结.txt`

## Read-Only Context
- `docs/specs.md` (after TASK-DOC-002)
- `docs/acceptance.md` (after TASK-DOC-002)
- `CONTEXT.md` (after TASK-DOC-002)
- `docs/freeze_record.md` (entry 002)

## Allowed Write Paths
- `fixtures/entry_five_forces/pass_normal.json`
- `fixtures/entry_five_forces/caution_high_camouflage.json`
- `fixtures/entry_five_forces/skip_high_risk_density.json`
- `fixtures/entry_five_forces/filtered_out_thin_pool.json`
- `fixtures/entry_five_forces/unknown_missing_fields.json`
- `fixtures/entry_five_forces/README.md`
- `reports/TASK-FIXTURE-003/result.md`

## Forbidden
- Modify skill code
- Use live GMGN data (use only deterministic mocked GMGN responses)
- Add credentials or any private key in fixtures
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] Five fixture JSON files exist, each representing one S01 entry decision.
- [ ] Each fixture contains a `mock_token_info` block matching GMGN field names actually used by `meme-candidate-entry`.
- [ ] At least one fixture exhibits each pitfall: low liquidity, low market cap, `is_wash_trading=true`, high `bundler_rate`, high `top_10_holder_rate`, missing `renounced_mint`/`renounced_freeze_account`.
- [ ] `fixtures/entry_five_forces/README.md` documents each fixture's purpose, expected `basic_gate.decision`, expected `entry_aux_decision`, and any active forces.
- [ ] `reports/TASK-FIXTURE-003/result.md` lists the fixture files and their expected outputs.

## Dependencies
- TASK-BE-006 must be `INTERNAL_PASS`.

## Blocked By
- TASK-BE-006.
