# Cross-Skill Handoff Contract — Solana Meme Workflow OS

Version: 2026-05-26-p3
Status: ENGINEERING_HANDOFF_CONTRACT
Scope: Phase 1 research / paper-only workflow
Project root: `/root/sikk-gmgn/`

---

## 0. Purpose

This document defines how the seven workflow components hand data to each other:

```text
S01 meme-candidate-entry
  → S02 meme-token-panel
  → S03 meme-wallet-roles
  → S04 meme-wallet-structure
  → S05 meme-evidence-chain
  → S06 meme-trade-gate
  → S07 meme-workflow-controller summary
```

It answers the engineering question:

> Which files does each skill produce, which downstream skill consumes them, which fields are required for the next step, and what must never be interpreted as a trading instruction?

This is not a trading strategy document. It is a handoff contract for code, tests, QA, and future agents.

---

## 1. Safety Boundary

Phase 1 is read-only research / paper-only gating.

Forbidden for every skill and downstream consumer:

- real orders
- private key access
- wallet signing
- transaction broadcast
- `gmgn-cli swap`
- `gmgn-cli multi-swap`
- `gmgn-cli cooking create`
- auto deploy
- claims such as `确定庄家`, `确定内幕`, `一定会涨`, `一定会跌`
- using any Phase 1 output as direct buy/sell/size/entry/exit instruction

`meme-trade-gate.gate_decision` is a research gate label, not a trading command.

---

## 2. Runtime Directory Contract

Default runtime directory:

```text
data/runs/<token_address>/
```

Walking Skeleton / mock mode runtime directory:

```text
data/runs/_skeleton_/<token_address>/
```

Required per-token files in a completed normal run:

```text
candidate_entry.json
phase_state.json
token_panel.json
token_panel.md
wallet_roles.json
wallet_roles.md
wallet_structure.json
wallet_structure.md
evidence_chain.json
evidence_chain.md
trade_gate.json
trade_gate.md
workflow_summary.json
workflow_summary.md
```

BLOCK / ERROR early stop runs may produce only the files up to the blocking phase plus:

```text
workflow_summary.json
workflow_summary.md
blocker_report.md   # when controller writes a blocking report
```

---

## 3. Universal Skill Output Fields

Every business skill output must preserve the standard contract enforced by `skills/common/validators.py`:

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

Rules:

1. `missing_fields` must record unavailable inputs. Do not silently substitute unknown values.
2. `downgrade_reasons` must record reduced confidence. Do not hide degraded evidence.
3. `blocker_reasons` must record why the pipeline stopped.
4. `counter_evidence` must preserve conflicting evidence; it must not be deleted for narrative neatness.
5. `confidence_score` must be numeric and between `0.0` and `1.0`.

---

## 4. Status and Decision Vocabulary

### 4.1 Skill `status`

Allowed by `validators.py`:

- `PASS`: phase completed and can hand off
- `WARN`: phase completed with downgrade reasons
- `BLOCK`: phase must stop due to business/risk blocker
- `ERROR`: execution failure or invalid/missing upstream file
- `NEED_MORE_DATA`: phase cannot judge safely from available data

### 4.2 Trade gate `gate_decision`

Allowed Phase 1 gate decisions:

- `BLOCK`
- `WATCH`
- `PAPER_ONLY`
- `NEED_MORE_DATA`

Forbidden in Phase 1:

- `BUY`
- `SELL`
- `HOLD`
- `SEMI_AUTO_READY`
- `AUTO_READY`
- any size / entry / exit / take-profit / stop-loss field

### 4.3 Controller `workflow_status`

Controller-level status is separate from phase-level `status`:

- `COMPLETED`: controller reached trade_gate and wrote summary
- `BLOCKED`: controller stopped because a phase returned `BLOCK`
- `ERROR`: controller stopped because a phase returned `ERROR`

Do not confuse phase `BLOCK` with workflow `BLOCKED`.

---

## 5. Phase-by-Phase Handoff Matrix

### S01 — `meme-candidate-entry`

Producer:

```text
skills/meme-candidate-entry/scripts/run.py
```

Output file:

```text
data/runs/<token>/candidate_entry.json
```

Consumes:

- external `gmgn-cli` token / pool / liquidity data
- input token address
- optional injected `GmgnClient` in tests

Required downstream fields:

- `status`
- `entry_source`
- `entry_reason`
- `token_symbol`
- `token_name`
- `initial_validation.address_valid`
- `initial_validation.token_exists`
- `initial_validation.has_pool`
- `initial_validation.has_liquidity`
- `confidence_score`
- `downgrade_reasons`
- `blocker_reasons`
- `missing_fields`
- `next_action`

Declared but currently under paused Five-Forces workstream:

- `entry_stage`
- `basis = gmgn_field_combination_hint`
- `basic_gate.decision`
- `five_forces`
- `gmgn_risk_density`
- `entry_aux_decision`

Important boundary:

- S01 is an entry filter, not a final trade gate.
- `entry_aux_decision` must never replace `meme-trade-gate.gate_decision`.
- Existing Five-Forces tasks are paused by freeze 003 until higher-priority stabilization is complete.

Downstream consumers:

- S07 controller reads `status` and may stop on `BLOCK` / `ERROR`.
- S02 may run after S01 PASS/WARN depending on controller policy.

---

### S02 — `meme-token-panel`

Producer:

```text
skills/meme-token-panel/scripts/run.py
```

Output files:

```text
data/runs/<token>/token_panel.json
data/runs/<token>/token_panel.md
```

Consumes:

- external `gmgn-cli` token info
- external `gmgn-cli` security
- external `gmgn-cli` pool
- external `gmgn-cli` kline
- optional injected `GmgnClient` in tests

Required downstream fields:

- `status`
- `basic_info.symbol`
- `basic_info.name`
- `basic_info.liquidity` or equivalent liquidity source
- `security.is_honeypot`
- `security.renounced_mint`
- `security.renounced_freeze_account`
- `security.rug_ratio`
- `security.top_10_holder_rate`
- `security.creator_token_status`
- `security.is_wash_trading`
- `risk_score_card.overall_risk`
- `kline_summary.trend`
- `downgrade_reasons`
- `missing_fields`

Downstream consumers:

- S03 wallet-roles may read creator / token context.
- S05 evidence-chain reads `basic_info`, `security`, `kline_summary`, `downgrade_reasons`, `missing_fields`.
- S06 trade-gate reads `basic_info`, `security`, `downgrade_reasons`, `missing_fields`.

Failure semantics:

- `status=BLOCK` must be propagated by S05/S06 and/or controller as a blocking condition.
- Missing security or liquidity fields must be listed in `missing_fields` rather than guessed.

---

### S03 — `meme-wallet-roles`

Producer:

```text
skills/meme-wallet-roles/scripts/run.py
```

Output files:

```text
data/runs/<token>/wallet_roles.json
data/runs/<token>/wallet_roles.md
```

Consumes:

- external `gmgn-cli` wallet / trader / smart money / dev information
- upstream `token_panel.json` when available

Required downstream fields:

- `status`
- `wallet_summary.smart_money_count`
- `wallet_summary.kol_count`
- `wallet_summary.bundler_count`
- `wallet_summary.fresh_wallet_count`
- `wallet_summary.total_holders_sampled`
- `smart_money_behavior.sm_net_direction`
- `smart_money_behavior.sm_avg_unrealized_pnl`
- `dev_profile.creator_token_status`
- `dev_profile.creator_balance_rate`
- `downgrade_reasons`
- `missing_fields`

Downstream consumers:

- S05 evidence-chain reads `smart_money_behavior`, `wallet_summary`, `dev_profile`.
- S06 trade-gate reads `wallet_summary`, `smart_money_behavior`, `downgrade_reasons`, `missing_fields`.

Important boundary:

- GMGN labels are hints, not final role classification.
- This skill must not claim a wallet is definitely `庄家`, `内幕`, or `dev 小号`.
- It does not execute follow-trading.

---

### S04 — `meme-wallet-structure`

Producer:

```text
skills/meme-wallet-structure/scripts/run.py
```

Output files:

```text
data/runs/<token>/wallet_structure.json
data/runs/<token>/wallet_structure.md
```

Consumes:

- external `gmgn-cli` holders / wallet stats
- optional upstream `wallet_roles.json`

Required downstream fields:

- `status`
- `same_source_groups`
- `structure_risk.has_same_source_groups`
- `structure_risk.same_source_combined_pct`
- `structure_risk.overall_structure_risk`
- `downgrade_reasons`
- `missing_fields`

Downstream consumers:

- S05 evidence-chain reads same-source fields and overall structure risk.
- S06 trade-gate reads `structure_risk.overall_structure_risk`, `downgrade_reasons`, `missing_fields`.

Important boundary:

- Pool / exchange / system addresses must not be counted as ordinary holder concentration when identifiable.
- Structure risk is not proof of manipulation. It is a risk signal.

---

### S05 — `meme-evidence-chain`

Producer:

```text
skills/meme-evidence-chain/scripts/run.py
```

Output files:

```text
data/runs/<token>/evidence_chain.json
data/runs/<token>/evidence_chain.md
```

Consumes:

```text
token_panel.json
wallet_roles.json
wallet_structure.json
```

Required upstream fields:

From `token_panel.json`:

- `status`
- `basic_info.symbol`
- `security.is_wash_trading`
- `kline_summary.trend`
- `downgrade_reasons`
- `missing_fields`

From `wallet_roles.json`:

- `smart_money_behavior.sm_net_direction`
- `wallet_summary.fresh_wallet_count`
- `wallet_summary.total_holders_sampled`
- `wallet_summary.smart_money_count`
- `dev_profile.creator_token_status`
- `dev_profile.creator_balance_rate`
- `downgrade_reasons`
- `missing_fields`

From `wallet_structure.json`:

- `same_source_groups`
- `structure_risk.has_same_source_groups`
- `structure_risk.same_source_combined_pct`
- `structure_risk.overall_structure_risk`
- `downgrade_reasons`
- `missing_fields`

Produces downstream fields:

- `status`
- `dominant_behavior`
- `behavior_signals[]`
- `risk_factors[]`
- `positive_signals[]`
- `evidence_summary`
- `narrative.one_line`
- `narrative.paragraph`
- `confidence_score`
- `downgrade_reasons`
- `missing_fields`
- `counter_evidence`

Dominant behavior values currently used by code:

- `ACCUMULATION`
- `DISTRIBUTION`
- `CONTROLLED`
- `WASH`
- `EARLY_STAGE`
- `UNKNOWN`

Failure semantics:

- Missing or invalid upstream JSON → `status=ERROR`, write blocker reason.
- `token_panel.status=BLOCK` → `status=BLOCK`, propagate blocker.
- `confidence_score < 0.4` or `dominant_behavior=UNKNOWN` → `status=NEED_MORE_DATA`.
- `0.4 <= confidence_score < 0.6` → `status=WARN`.
- otherwise → `status=PASS`.

Important boundary:

- Evidence-chain must preserve conflicting evidence.
- Narrative must not contain forbidden certainty / trading terms.

---

### S06 — `meme-trade-gate`

Producer:

```text
skills/meme-trade-gate/scripts/run.py
```

Output files:

```text
data/runs/<token>/trade_gate.json
data/runs/<token>/trade_gate.md
```

Consumes:

```text
token_panel.json
wallet_roles.json
wallet_structure.json
evidence_chain.json
```

Required upstream fields:

From `token_panel.json`:

- `status`
- `basic_info.liquidity`
- `security.is_honeypot`
- `security.renounced_mint`
- `security.renounced_freeze_account`
- `security.rug_ratio`
- `security.top_10_holder_rate`
- `security.creator_token_status`
- `security.is_wash_trading`
- `downgrade_reasons`
- `missing_fields`

From `wallet_roles.json`:

- `wallet_summary.smart_money_count`
- `wallet_summary.kol_count`
- `wallet_summary.bundler_count`
- `smart_money_behavior.sm_net_direction`
- `smart_money_behavior.sm_avg_unrealized_pnl`
- `downgrade_reasons`
- `missing_fields`

From `wallet_structure.json`:

- `structure_risk.overall_structure_risk`
- `downgrade_reasons`
- `missing_fields`

From `evidence_chain.json`:

- `status`
- `dominant_behavior`
- `confidence_score`
- `behavior_signals`
- `counter_evidence`
- `downgrade_reasons`
- `missing_fields`

Produces downstream fields:

- `status`
- `gate_decision`
- `decision_reasons[]`
- `gate_score.security_score`
- `gate_score.smart_money_score`
- `gate_score.structure_score`
- `gate_score.behavior_score`
- `gate_score.total_score`
- `phase_permission.research_allowed`
- `phase_permission.paper_allowed`
- `phase_permission.semi_auto_allowed = false`
- `phase_permission.auto_allowed = false`
- `next_review_conditions[]`
- `confidence_score`
- `missing_fields`
- `downgrade_reasons`

Decision rules summary:

- Any triggered block rule (`G01`-`G06` or contribution `block`) ⇒ `gate_decision=BLOCK`.
- `evidence_chain.status=NEED_MORE_DATA` or any `missing_fields` or upstream `ERROR` ⇒ `NEED_MORE_DATA`.
- If watch conditions are limited, confidence is sufficient, dominant behavior is `ACCUMULATION`/`EARLY_STAGE`, smart money exists, liquidity is sufficient, rug ratio is acceptable, and score ≥ 66 ⇒ `PAPER_ONLY`.
- Low score ≤ 20 ⇒ `BLOCK` if rules triggered else `WATCH`.
- Otherwise ⇒ `WATCH`.

Important boundary:

- `PAPER_ONLY` allows paper observation only.
- No `gate_decision` authorizes real orders.
- `phase_permission.semi_auto_allowed` and `phase_permission.auto_allowed` must be false in Phase 1.

---

### S07 — `meme-workflow-controller`

Producer:

```text
skills/meme-workflow-controller/scripts/run.py
```

Output files:

```text
data/runs/<token>/workflow_summary.json
data/runs/<token>/workflow_summary.md
state/active_runs.json
state/completed_runs.json
```

Consumes:

- S01-S06 output JSON files
- `phase_state.json`
- `PHASE_ORDER` from `skills/common/phase_state.py`

Responsibilities:

1. Start or resume a token run.
2. Execute phases in order.
3. Stop when a phase returns `BLOCK` or `ERROR`.
4. Build BLOCK/ERROR summary when stopped early.
5. Build completed workflow summary after S06.
6. Maintain active/completed indexes.
7. Support skeleton mode through `SIKK_SKELETON_MODE=1` or CLI `--skeleton`.

Controller summary fields:

- `workflow_status`
- `blocked_at` when stopped early
- `blocker_reasons`
- `gate_decision`
- `gate_score`
- `confidence_score`
- `key_findings`
- `risk_factors`
- `positive_signals`
- `next_action`
- `summary_file`
- `forbidden`

Important boundary:

- Controller does not interpret wallets or prices.
- Controller does not trade.
- Controller should not mutate business skill outputs except by reading and summarizing them.

---

## 6. Downstream Consumption Rules

### 6.1 Missing data

If a downstream skill requires a field that is absent:

1. Add the exact path to `missing_fields`.
2. Reduce confidence or return `NEED_MORE_DATA` where appropriate.
3. Do not silently set optimistic defaults.
4. Do not infer a field from unrelated fields unless the rule explicitly documents it.

### 6.2 Downgrades

If evidence exists but quality is weak:

1. Record a human-readable reason in `downgrade_reasons`.
2. Preserve the original evidence.
3. Continue only if the status semantics allow it (`WARN` or `NEED_MORE_DATA`).

### 6.3 Blockers

If a phase cannot safely continue:

1. Set `status=BLOCK` for business/risk blockers or `status=ERROR` for execution failures.
2. Add one or more `blocker_reasons`.
3. Controller must stop downstream phases.
4. Downstream JSON files after the blocking phase must not be created by that run.

### 6.4 Counter-evidence

Counter-evidence is not noise. It is part of the contract.

- Evidence-chain must preserve it.
- Trade-gate must carry it forward.
- Reports must not delete it to make a stronger story.

---

## 7. Known Gaps / Priority Follow-ups

These are intentionally not solved by this document, but should be handled by future task cards:

1. **Five-Forces S01 freeze mismatch**
   - `docs/specs.md` declares Five-Forces fields as required.
   - freeze 003 paused the remaining Five-Forces implementation tasks.
   - Engineering should treat these fields as declared target contract but not stable until the paused tasks are resumed.

2. **Status vocabulary still needs formal cleanup**
   - `BLOCK` is phase-level.
   - `BLOCKED` is workflow-level.
   - `TIMEOUT` / `SKIPPED` are mentioned in Walking Skeleton acceptance but are not fully modeled in `validators.py`.

3. **Schema coverage is uneven**
   - `meme-candidate-entry` has explicit schema classes.
   - Other skills rely mostly on generic validators and tests.
   - Future work should add machine-checkable schemas per skill if field drift becomes painful.

4. **Controller exception handling is still shallow**
   - Phase output `BLOCK` / `ERROR` is handled.
   - Uncaught Python exceptions from `_run_phase` are not yet fully converted into controller summaries.

5. **Batch-mode skeleton contract is not fully implemented**
   - Single-token `--skeleton` works.
   - `screen --skeleton` is mentioned in acceptance but not yet fully implemented.

---

## 8. Validation Commands

Current expected command:

```bash
cd /root/sikk-gmgn
python3 -m pytest skills/ -q
```

At the time this document was created, the full skill test suite passed:

```text
27 passed
```

For a single skeleton smoke run:

```bash
python3 skills/meme-workflow-controller/scripts/run.py run <token_address> --skeleton
```

Expected:

```json
{
  "workflow_status": "COMPLETED",
  "summary_file": "/root/sikk-gmgn/data/runs/_skeleton_/<token_address>/workflow_summary.md"
}
```

---

## 9. Engineering Handoff Checklist

Before modifying any skill in this pipeline:

- [ ] Read this document.
- [ ] Read `docs/specs.md`.
- [ ] Read `docs/acceptance.md`.
- [ ] Read `docs/freeze_record.md`.
- [ ] Identify the exact upstream files consumed.
- [ ] Identify the exact downstream files affected.
- [ ] Add or update tests for the affected handoff fields.
- [ ] Run `python3 -m pytest skills/ -q`.
- [ ] Do not add trading-action fields.
- [ ] Do not remove `missing_fields`, `downgrade_reasons`, `blocker_reasons`, or `counter_evidence`.

---

## 10. One-Sentence Contract

The pipeline is allowed to move a token from raw GMGN data to a paper-only research gate label, but every step must preserve evidence, uncertainty, blockers, and safety boundaries so that no downstream consumer can mistake research output for an execution instruction.
