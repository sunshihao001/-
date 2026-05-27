# Task Card

task_id: TASK-RULE-005
title: Author rules/entry_five_forces_rules_v1.json (Five-Forces + risk density thresholds)
owner_terminal: skill-backend
status: INTERNAL_PASS

## Input Files
- `learning/GMGN字段组合五力模型理论总结.txt`
- `learning/15-GMGN字段组合地基.md`
- `docs/proposed/CR-2026-05-25-002-docs-patch.md`

## Read-Only Context
- `docs/specs.md` (after TASK-DOC-002)
- `docs/acceptance.md` (after TASK-DOC-002)
- `CONTEXT.md` (after TASK-DOC-002)
- `docs/freeze_record.md` (entry 002)
- `rules/gate_rules_v1.json`
- `rules/downgrade_rules_v1.json`

## Allowed Write Paths
- `rules/entry_five_forces_rules_v1.json`
- `reports/TASK-RULE-005/result.md`

## Forbidden
- Modify any other rules JSON
- Embed thresholds directly in skill code
- Treat GMGN labels (smart_degen_count, hot_level, is_show_alert, rug_ratio) as hard gates
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] File exists at `rules/entry_five_forces_rules_v1.json`.
- [ ] JSON is machine-loadable (parses with `json.load`).
- [ ] Contains keys: `schema_version`, `basic_gate`, `forces`, `risk_density`, `entry_aux_decision`, `safety`.
- [ ] `basic_gate` defines numeric thresholds for `min_liquidity`, `min_market_cap`, `min_volume`, `min_holder_count`, `min_swaps`.
- [ ] `forces` defines classification thresholds for each of: `absorption_power`, `diffusion_power`, `control_power`, `camouflage_power`, `exit_power`, each with explicit source fields and bin edges.
- [ ] `risk_density` defines weighted contributions, level edges (`low/medium/high/extreme`), and reason labels.
- [ ] `entry_aux_decision` defines deterministic mapping from `(basic_gate, forces, risk_density)` to `PASS / CAUTION / SKIP / FILTERED_OUT / UNKNOWN`.
- [ ] `safety` block reaffirms paper-only; explicitly forbids using these thresholds as final trade decisions.
- [ ] `reports/TASK-RULE-005/result.md` includes the rule JSON path, a one-page rationale per threshold, and `pytest` not required for this card.

## Dependencies
- TASK-DOC-002 must be `INTERNAL_PASS`.

## Blocked By
- none.

## Unblocked By
- TASK-DOC-002 INTERNAL_PASS and freeze record `sol-ai-pro-dev-workflow-freeze-20260525-002`.
