# CONTEXT — Solana Meme Workflow OS Glossary

This file is glossary/domain-language only. It does not define implementation tasks, progress, or acceptance gates.

## System Terms

- `Solana Meme Workflow OS`: GMGN-entry + wallet-intel + Hermes-stateful Solana meme research workflow.
- `Phase 1`: research pipeline only; no live trading.
- `Safe Mode`: execution boundary that forbids real orders, private key access, signing, transaction broadcast, swap, and auto deploy.
- `Evidence Pipeline`: every decision must preserve evidence, counter-evidence, missing fields, confidence, downgrade reasons, and blockers.
- `Phase State`: JSON state file under `data/runs/<token_address>/phase_state.json` used for interrupt/resume/audit.

## Skill Terms

- `meme-candidate-entry`: validates candidate token address and creates initial run state.
- `meme-token-panel`: collects token info, security, pool, and K-line summary.
- `meme-wallet-roles`: classifies wallet behavior using behavior rules; GMGN labels are hints, not final classification.
- `meme-wallet-structure`: analyzes holder concentration, same-source funding, coordinated timing, and structure risk.
- `meme-evidence-chain`: combines token, wallet role, and wallet structure evidence into a narrative evidence chain.
- `meme-trade-gate`: produces gate decision from evidence and rules.
- `meme-workflow-controller`: orchestrates skill order, phase state, active/completed runs, and summary output.

## Status Terms

- `PASS`: phase can hand off to next skill.
- `WARN`: phase can continue with downgrade reasons.
- `BLOCK`: phase must stop and write blocker reasons.
- `ERROR`: execution failure; may retry after attribution.
- `NEED_MORE_DATA`: data insufficient; missing fields must be recorded.

## Gate Decision Terms

- `BLOCK`: do not continue.
- `WATCH`: observe only.
- `PAPER_ONLY`: paper trading/research only.
- `NEED_MORE_DATA`: cannot judge safely from available data.
- `SEMI_AUTO_READY`: future phase, forbidden in Phase 1.
- `AUTO_READY`: future phase, forbidden in Phase 1.

## AI Dev Workflow Terms

- `PM/review`: role that freezes docs, creates task cards, reviews results, and attributes CI failures.
- `Task Card`: only valid entrypoint for Backend/QA/CI execution.
- `INTERNAL_PASS`: AI review pass; not human final acceptance.
- `HUMAN_ACCEPTED`: final human approval.

## v2 新增术语（V2-FREEZE-001 freeze）
依据：`CONTEXT.freeze_candidate.md`，PM/review INTERNAL_PASS

### System Terms (v2)

- `Solana Meme Workflow OS v2`: GMGN-entry + wallet-intel + evidence-chain + gated paper-only Solana meme research workflow built on Hermes stateful orchestration.
- `v2 Research Pipeline`: The 10-business-skill research pipeline used to convert token candidates into evidence-backed state outputs.
- `Paper-only Research`: A safety boundary where the workflow may produce BLOCK / WATCH / PAPER_ONLY / NEED_MORE_DATA states but never authorizes live trading.
- `v1 Legacy`: The earlier workflow baseline. Existing front-layer artifacts may be recognized as legacy-compatible, but v2 schemas must be refrozen.
- `Legacy-compatible`: A compatibility label meaning an old artifact can be identified and mapped to a v2 layer. It does not mean the artifact satisfies v2 schema.

### Skill Terms (v2)

- `meme-structure-evidence`: The structure evidence skill that converts wallet relationships into auditable structural evidence such as same-source groups, timing clusters, concentration clusters, distribution patterns, backflow edges, and wash activity candidates.
- `meme-chip-control`: The chip control skill that estimates probabilistic chip-control status from structural evidence and preserves counter-evidence, missing fields, downgrade reasons, and validity windows.
- `meme-lifecycle-classifier`: The lifecycle skill that classifies the current token or dominant-side lifecycle stage using evidence-chain and chip-control context.
- `meme-negative-gate`: The negative gate skill that applies veto and hard-blocking conditions to the positive gate result. It may maintain or downgrade the result but cannot upgrade it.
- `meme-paper-validation-and-attribution`: The paper validation skill that evaluates paper-only outcomes after the fact, attributes which assumptions worked or failed, and proposes rule revision candidates without authorizing live trading.

### State Terms (v2)

- `gate_sequence`: The ordered record of entry gate, positive gate, and negative gate decisions and their evidence references.
- `artifact_manifest`: The record of workflow artifacts, their producer skill, path, schema version, status, validity window, missing fields, and downgrade reasons.
- `resume_point`: The point from which a workflow run may continue after interruption or recoverable error.
- `final_state`: The final workflow state after positive gate and negative gate have both been applied.

### Gate Terms (v2)

- `entry_gate`: The gate produced by meme-candidate-entry. It determines whether a token enters the research workflow.
- `positive_gate`: The gate produced by meme-trade-gate. It determines the maximum allowed research state.
- `negative_gate`: The gate produced by meme-negative-gate. It applies veto or downgrade conditions after positive gate.
- `DEGRADED_CONTINUE`: A controller state indicating the workflow may continue while preserving downgrade reasons.
- `UNKNOWN+expired`: A stale unknown state that should not be treated as usable evidence by downstream skills.

### Evidence Terms (v2)

- `conflict_evidence`: Evidence showing unresolved conflict between competing interpretations.
- `dominant_behavior`: A derived summary from evidence-chain, used for downstream structured consumption. It is not a buy/sell signal.

### Safety Terms (v2)

- `Human Acceptance`: The only approval that may advance a future workflow beyond internal AI review. INTERNAL_PASS is not human acceptance.
- `Production Readiness Claim`: A forbidden claim in current v2 research context. The workflow may produce candidates, evidence, gates, and paper-only states, not production authorization.

### v2 待冻结问题

1. `UNKNOWN+expired` 是否需要拆成 `UNKNOWN` + `expired_reason` 两个术语？
2. `DEGRADED_CONTINUE` 是 controller state 还是 skill status？
3. `PAPER_ONLY` 是否只在 gate 层出现，还是 paper-validation 也可使用？

- `Five-Forces Gate`: S01 entry-layer auxiliary judgment built from GMGN field combinations.
- `Absorption Power`: market depth and value-pricing capacity.
- `Diffusion Power`: distribution growth of participants.
- `Control Power`: concentration of supply, sniper/bundler/dev influence.
- `Camouflage Power`: forgeability of volume, social, narrative.
- `Exit Power`: ability and incentive of early actors to exit on others.
- `Entry Aux Decision`: PASS | CAUTION | SKIP | FILTERED_OUT | UNKNOWN.
- `GMGN Risk Density`: aggregated GMGN risk-hint level, never a final on-chain conclusion.
- `Basis`: `gmgn_field_combination_hint`, fixed string identifying the layer of the judgment.

