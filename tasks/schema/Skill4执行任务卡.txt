# Task Card

task_id: TASK-SCHEMA-004
title: meme-chip-control skill design + schema + integration
owner_terminal: PM/docs
status: READY

## Input Files

- `design/phase1-skill-08-chip-control.md`
- `design/chip_control_output_schema.json`
- `知识库/学习课题/Skill4-筹码控制权/meme-chip-control-skill-spec-v1.md`

## Read-Only Context

- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `design/phase0-workflow-contract.md`
- `design/README.md`
- `design/phase1-skill-05-evidence-chain.md`
- `design/phase1-skill-03-wallet-roles.md`

## Allowed Write Paths

- `skills/chip_control/__init__.py`
- `skills/chip_control/chip_control.py`
- `skills/chip_control/ooda.py`
- `skills/chip_control/entity_weights.py`
- `skills/chip_control/reflexive_guard.py`
- `skills/chip_control/projection_scores.py`
- `skills/chip_control/state_machine.py`
- `skills/chip_control/bayesian_update.py`
- `reports/TASK-SCHEMA-004/result.md`

## Forbidden

- Modify `docs/specs.md`
- Modify `docs/acceptance.md`
- Modify `CONTEXT.md`
- Modify existing phase1-skill design files (except phase1-skill-05-evidence-chain.md which must have chip_control extraction noted)
- Change unrelated files
- Expand scope beyond this task card
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, cooking, or auto deploy

## Key Implementation Requirements

### 1. chip_control.py (main entry)

Implement the 8-step formula bus:

```python
# evaluate_chip_control(inputs, previous_state):
#   Step 0: input alignment check -> UNKNOWN / INPUT_NOT_ALIGNED
#   Step 1: OODA hard gate -> UNKNOWN / STALE_OODA_LOOP
#   Step 2: control stock floor -> COLLAPSED or UNKNOWN / NO_VALID_ACTIVE_CONTROL_ENTITY
#   Step 3: main channel (net_control_flow, control_raw)
#   Step 4: per_entity_control_weight = base * source * timing * flow * reflexive * ooda
#   Step 5: noise correction (reflexive / camouflage / data_quality)
#   Step 6: bayesian_update(state_probs, likelihood, base_rate)
#   Step 7: state machine -> check allowed_transitions
#   Step 8: build output JSON
```

### 2. ooda.py

- Compute `remaining_validity_sec`, `market_half_life_sec`, `ooda_status`
- Implement hard gate: `if remaining_validity_sec <= 0: return UNKNOWN`

### 3. entity_weights.py

- `compute_raw_entity_weight(entity, context)` — base × source × timing × flow × reflexive × ooda
- `normalize_entity_weights(raw_weights)` — return (normalized, control_stock_score)
- Exclusion: filter POOL/CEX/SYSTEM/BURN/dust
- UNVERIFIED: keep with lowered weight_confidence

### 4. reflexive_guard.py

- `reflexive_disguise_risk` from backflow, cooldown, behavior similarity
- `camouflage_cost_score` from cost estimates
- `reflexive_confidence_modifier`
- `backflow_strength`

### 5. projection_scores.py

Implement four score formulas:

```python
retention_score = clamp(0.45*stock + 0.25*same_source + 0.15*concentration + 0.10*ooda + 0.05*(1-disguise), 0, 1)
exit_intensity = clamp(0.35*outflow + 0.25*sell_pressure + 0.15*sync_exit + 0.15*exit_done + 0.10*(1-backflow), 0, 1)
counterparty = clamp(0.30*new_holder + 0.25*new_whale + 0.20*receiver + 0.15*external + 0.10*price_impact, 0, 1)
distribution = clamp(0.30*sold_ratio + 0.20*receiver + 0.20*decline + 0.15*recycle + 0.15*continuity, 0, 1)
```

### 6. state_machine.py

```python
ALLOWED_TRANSITIONS = {
    "UNKNOWN": {"ESTABLISHING", "ESTABLISHED", "MAINTAINED", "LOOSENING", "TRANSFERRING", "COLLAPSED"},
    "ESTABLISHING": {"ESTABLISHED", "MAINTAINED", "COLLAPSED", "UNKNOWN"},
    "ESTABLISHED": {"MAINTAINED", "LOOSENING", "TRANSFERRING", "COLLAPSED", "UNKNOWN"},
    "MAINTAINED": {"ESTABLISHED", "LOOSENING", "TRANSFERRING", "COLLAPSED", "UNKNOWN"},
    "LOOSENING": {"MAINTAINED", "TRANSFERRING", "COLLAPSED", "UNKNOWN"},
    "TRANSFERRING": {"MAINTAINED", "LOOSENING", "COLLAPSED", "UNKNOWN"},
    "COLLAPSED": {"UNKNOWN", "ESTABLISHING"},
}
# COLLAPSED -> ESTABLISHING requires new_structure_evidence
```

### 7. bayesian_update.py

```python
def bayesian_update(previous_state_probs, evidence, base_rate):
    # likelihood(evidence | state) from evidence scores
    # P(state | evidence) ∝ P(evidence | state) × P(state | context)
    # normalize, ensure ooda_fresh bayes only
```

## Acceptance Criteria

- [ ] Output contains `chip_control_status`, `status_confidence`, `state_probabilities`
- [ ] Output contains `control_stock_score` + `per_entity_control_weight[]`
- [ ] Output contains `valid_until` / `ooda_status` / `remaining_validity_sec`
- [ ] UNKNOWN always includes `unknown_reason`
- [ ] Cleared entity raw_weight = 0
- [ ] CEX / POOL / SYSTEM / BURN raw_weight = 0
- [ ] normalized weights sum to 1 when `control_stock_score > floor`
- [ ] OODA expired triggers `UNKNOWN / STALE_OODA_LOOP`
- [ ] Transition violations fallback to `UNKNOWN / ILLEGAL_STATE_TRANSITION`
- [ ] `entity_control_veto_evidence` does not trigger final BLOCK
- [ ] No output contains `BUY / SELL / BLOCK / PAPER_READY`
- [ ] All 14 forbidden output values are blocked

## Dependencies

- Frozen docs exist.
- `core/rules/allowed_transitions.py` (part of state machine).
- `core/models/chip_control_schema.py` or common validator.

## Blocked By

- none
