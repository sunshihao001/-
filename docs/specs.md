# Specs — Solana Meme Workflow OS

## Source Documents
- `design/README.md`
- `design/phase0-workflow-contract.md`
- `design/phase1-skill-01-candidate-entry.md`
- `design/phase1-skill-02-token-panel.md`
- `design/phase1-skill-03-wallet-roles.md`
- `design/phase1-skill-04-wallet-structure.md`
- `design/phase1-skill-05-evidence-chain.md`
- `design/phase1-skill-06-trade-gate.md`
- `design/phase1-skill-07-workflow-controller.md`
- `design/工程完善计划书.md`

## System Purpose
Build a Hermes-native Solana meme research workflow:

```text
GMGN data → Hermes skill pipeline → evidence-level wallet research → gate decision → paper-only validation → later semi-auto/human-gated phases
```

## Current Phase Scope
Current frozen scope is Phase 1 research pipeline and development control-plane preparation.

Included:
- Skill orchestration for candidate entry through trade gate.
- JSON handoff schema for each skill.
- Phase state tracking.
- Markdown summaries for human review.
- Rule-driven safe gate decisions.
- Testable contracts for skill outputs.
- AI pro development workflow: frozen docs, task cards, result reports, review loop.

Excluded:
- live trading
- wallet signing
- transaction broadcast
- swap execution
- auto deploy
- production readiness claims
- 使用入口层 `SKIP / FILTERED_OUT / CAUTION` 作为最终交易决策。
- 在 `meme-candidate-entry` 内调用任何 GMGN 写入类命令（swap、multi-swap、cooking）。

## Runtime Directory Contract
Expected runtime layout:

```text
/root/sikk-gmgn/
├── design/
├── skills/
├── data/runs/<token_address>/
├── state/
├── rules/
├── fixtures/
├── docs/
├── tasks/
├── reports/
└── templates/
```

## Standard Skill Output Contract
Every skill output must include or preserve equivalent fields:

```json
{
  "schema_version": "1.0",
  "skill_name": "meme-xxx",
  "task_id": "<token_address>_<timestamp>",
  "token_address": "<base58 address>",
  "chain": "sol",
  "timestamp": "<ISO 8601>",
  "status": "PASS | WARN | BLOCK | ERROR | NEED_MORE_DATA",
  "evidence": [],
  "counter_evidence": [],
  "confidence_score": 0.0,
  "downgrade_reasons": [],
  "blocker_reasons": [],
  "missing_fields": [],
  "valid_until": "<ISO 8601>",
  "next_action": "<next skill or STOP>",
  "handoff_to": "<next skill>"
}
```

## S01 Candidate Entry Five-Forces Gate Contract

`meme-candidate-entry` MUST, in addition to the standard output contract, emit the following fields:

```json
{
  "entry_stage": "candidate_entry",
  "basis": "gmgn_field_combination_hint",
  "basic_gate": {
    "decision": "PASS | FILTERED_OUT | UNKNOWN",
    "reasons": []
  },
  "five_forces": {
    "absorption_power":  "weak | normal | strong | unknown",
    "diffusion_power":   "weak | growing | broad | unknown",
    "control_power":     "low | medium | high | unknown",
    "camouflage_power":  "low | medium | high | unknown",
    "exit_power":        "low | medium | high | unknown"
  },
  "gmgn_risk_density": {
    "level":  "low | medium | high | extreme | unknown",
    "score":  0.0,
    "reasons": []
  },
  "entry_aux_decision": "PASS | CAUTION | SKIP | FILTERED_OUT | UNKNOWN",
  "next_action": "RUN_FULL_WORKFLOW | RUN_FULL_WORKFLOW_WITH_CAUTION | STOP"
}
```

Rules:

1. `basis` MUST be the literal string `gmgn_field_combination_hint`. The five-forces output is a hint layer, never a final on-chain conclusion.
2. `entry_aux_decision` is an entry-layer auxiliary signal. It does NOT replace `meme-trade-gate.gate_decision`.
3. `basic_gate.decision == FILTERED_OUT` ⇒ `next_action = STOP`, controller MUST skip S02-S06 for this candidate but MUST still persist the candidate record.
4. `entry_aux_decision == SKIP` ⇒ controller MAY skip S02-S06 only when batch screen is invoked with the explicit `--skip-entry-risk high` flag. Single-token `run` MUST still execute the full workflow with a `CAUTION` flag.
5. Field thresholds and force-classification logic MUST live in machine-loadable `rules/entry_five_forces_rules_v1.json`, not in code constants.

Source-field registry:

- `design/phase1-research/00b-GMGN-Canonical-Bytes.txt`
- `design/phase1-research/00b-GMGN-Canonical-Bytes.md`
- `reports/cr_20260525_002_canonical_bytes_evidence_addendum.md`

These files define Layer 0 GMGN canonical bytes for rule source-field references. They are raw GMGN byte sources, not final trade-decision rules.

## Phase Order

```text
meme-candidate-entry
→ meme-token-panel
→ meme-wallet-roles
→ meme-wallet-structure
→ meme-evidence-chain
→ meme-trade-gate
```

`meme-workflow-controller` owns orchestration and state updates.

## Engineering Requirements
- `meme-candidate-entry` MUST output the Five-Forces Gate Contract defined above.
- `meme-candidate-entry` MUST load thresholds from `rules/entry_five_forces_rules_v1.json`.
- `meme-candidate-entry` MUST NOT use GMGN labels (`smart_degen_count`, `renowned_count`, `bluechip_owner_percentage`, `hot_level`, `is_show_alert`, `rug_ratio`) as hard gates. They may only contribute to `gmgn_risk_density.reasons` or force-level hints.
- `meme-workflow-controller` MUST read S01's `basic_gate.decision` and `entry_aux_decision` to short-circuit batch runs; single-token `run` MUST still go through the full pipeline.
- All skill scripts must be executable from CLI or importable test entrypoints.
- Tests must use deterministic fixtures/mocks, not live token assumptions.
- `rules/gate_rules_v1.json` and `rules/downgrade_rules_v1.json` must be machine-loadable JSON.
- Runtime output must be auditable under `data/runs/<token_address>/`.
- No implementation may silently drop blocker, missing field, or downgrade information.

## AI Development Requirements
- No coding without task card.
- Every execution writes `reports/<task_id>/result.md`.
- PM/review owns task creation and review.
- Backend/QA terminals may write only allowed paths.
- Human final acceptance remains separate from AI internal pass.
