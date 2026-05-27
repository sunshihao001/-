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
## Five-Forces Entry Terms

- `Five-Forces Gate`: S01 entry-layer auxiliary judgment built from GMGN field combinations.
- `Absorption Power`: market depth and value-pricing capacity.
- `Diffusion Power`: distribution growth of participants.
- `Control Power`: concentration of supply, sniper/bundler/dev influence.
- `Camouflage Power`: forgeability of volume, social, narrative.
- `Exit Power`: ability and incentive of early actors to exit on others.
- `Entry Aux Decision`: PASS | CAUTION | SKIP | FILTERED_OUT | UNKNOWN.
- `GMGN Risk Density`: aggregated GMGN risk-hint level, never a final on-chain conclusion.
- `Basis`: `gmgn_field_combination_hint`, fixed string identifying the layer of the judgment.

