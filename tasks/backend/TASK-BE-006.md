# Task Card

task_id: TASK-BE-006
title: Implement Five-Forces Gate logic in meme-candidate-entry
owner_terminal: skill-backend
status: BLOCKED

## Input Files
- `skills/meme-candidate-entry/scripts/run.py`
- `skills/meme-candidate-entry/scripts/rules.py`
- `skills/meme-candidate-entry/scripts/schema.py` (after TASK-SCHEMA-003)
- `rules/entry_five_forces_rules_v1.json` (after TASK-RULE-005)
- `skills/common/rule_loader.py`

## Read-Only Context
- `docs/specs.md` (after TASK-DOC-002)
- `docs/acceptance.md` (after TASK-DOC-002)
- `CONTEXT.md` (after TASK-DOC-002)
- `docs/freeze_record.md` (entry 002)
- `learning/GMGN字段组合五力模型理论总结.txt`

## Allowed Write Paths
- `skills/meme-candidate-entry/scripts/run.py`
- `skills/meme-candidate-entry/scripts/rules.py`
- `skills/meme-candidate-entry/scripts/five_forces.py`
- `reports/TASK-BE-006/result.md`

## Forbidden
- Hard-code thresholds in Python source (must read `rules/entry_five_forces_rules_v1.json`)
- Treat GMGN labels (smart_degen_count, hot_level, is_show_alert, rug_ratio) as hard gates
- Change `meme-candidate-entry` output to drop any pre-existing field
- Touch other skill folders
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `run.py` populates `entry_stage`, `basis="gmgn_field_combination_hint"`, `basic_gate`, `five_forces`, `gmgn_risk_density`, `entry_aux_decision`, `next_action`.
- [ ] Logic lives in `five_forces.py` and `rules.py`, not inline in `run.py` ad-hoc.
- [ ] `basic_gate.decision == FILTERED_OUT` ⇒ `next_action == "STOP"`, candidate still written to `candidate_entry.json`.
- [ ] `entry_aux_decision == SKIP` does not change `next_action` for the single-token `run` path; it only annotates downstream behavior in batch.
- [ ] `build_candidate_pool` already passes liquidity/market-cap min thresholds — keep them as compatibility shim, but new logic must come from rules JSON.
- [ ] All pre-existing tests in `skills/meme-candidate-entry/tests/` still pass.
- [ ] `python3 -m py_compile $(find skills/meme-candidate-entry -name '*.py')` passes.
- [ ] `reports/TASK-BE-006/result.md` includes one sample input + one sample output for each of: PASS, CAUTION, SKIP, FILTERED_OUT, UNKNOWN.

## Dependencies
- TASK-SCHEMA-003 must be `INTERNAL_PASS`.

## Blocked By
- TASK-SCHEMA-003.
