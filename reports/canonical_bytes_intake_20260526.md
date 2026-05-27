# Canonical Bytes Intake Report — 00b-GMGN-Canonical-Bytes

date: 2026-05-26
project_root: /root/sikk-gmgn/
source_document: /root/.hermes/profiles/cangweizhixingbot/cache/documents/doc_732f84d37c37_00b-GMGN-Canonical-Bytes.txt
canonical_project_copy_txt: design/phase1-research/00b-GMGN-Canonical-Bytes.txt
canonical_project_copy_md: design/phase1-research/00b-GMGN-Canonical-Bytes.md
status: INTAKE_CONFIRMED_ALREADY_PRESENT

## 1. What This Document Is

`00b-GMGN-Canonical-Bytes` is the Layer 0 / Canonical Bytes inventory for the Solana meme workflow OS.

It lists GMGN fields that are directly returned by GMGN APIs and therefore should be treated as raw/canonical input bytes, not as derived L1 calculations.

Document claim:

```text
GMGN API directly returns these fields.
They do not require L1 computation.
They are input bytes for L1 features / field combinations.
```

## 2. Project Presence Verification

The uploaded document is already present in the project under:

- `design/phase1-research/00b-GMGN-Canonical-Bytes.txt`
- `design/phase1-research/00b-GMGN-Canonical-Bytes.md`

Verification command executed:

```bash
cmp -s /root/.hermes/profiles/cangweizhixingbot/cache/documents/doc_732f84d37c37_00b-GMGN-Canonical-Bytes.txt /root/sikk-gmgn/design/phase1-research/00b-GMGN-Canonical-Bytes.txt
cmp -s /root/.hermes/profiles/cangweizhixingbot/cache/documents/doc_732f84d37c37_00b-GMGN-Canonical-Bytes.txt /root/sikk-gmgn/design/phase1-research/00b-GMGN-Canonical-Bytes.md
```

Result:

```text
cmp_txt_exit:0
cmp_md_exit:0
```

So this is not a new unregistered document; it is already part of the Phase 1 research assets.

## 3. Field Groups Captured

The document covers 12 canonical byte groups:

1. Price / market cap
2. Volume / transaction count
3. Holders / wallet tag counts
4. Holder concentration
5. Safety / risk
6. Dev / creator
7. Token lifecycle
8. Pool
9. Social / attention
10. Heat / rank
11. Individual holder / trader fields
12. K-line fields

## 4. Correct System Role

This document should be treated as:

```text
GMGN raw byte dictionary
→ input source for S01/S02 field extraction
→ source-field registry for five-forces rules
→ fixture-design basis
→ missing-field policy basis
```

It should not be treated as:

```text
final strategy rule
trade decision
wallet structure conclusion
buy/sell/execute permission
proof that GMGN data is sufficient for all downstream judgments
```

## 5. Impact on Current ai-pro-dev-workflow

Current relevant CR:

- `CR-2026-05-25-002 — GMGN 字段组合五力模型 落地到 S01 候选入口`

Current status:

- CR status is still `DRAFT`
- `TASK-DOC-002` remains `BLOCKED`
- downstream Five-Forces tasks remain `BLOCKED`

Therefore this uploaded document does not unblock implementation by itself. It strengthens the evidence base for the CR, but the workflow still requires human approval before frozen docs are changed or blocked task cards execute.

## 6. How This Document Should Feed the Next Build

Once CR-2026-05-25-002 is human-approved, this document should be referenced as the canonical source-field list for:

### TASK-DOC-002

Update frozen docs to explicitly identify `00b-GMGN-Canonical-Bytes` as the Layer 0 raw-byte source for Five-Forces Gate.

### TASK-RULE-005

When authoring `rules/entry_five_forces_rules_v1.json`, each rule should cite source fields from this document.

Required mapping discipline:

```text
field_group
source_field
raw_or_derived = raw_gmgn_byte
force_target
allowed_use = hint / gate_input / missing_field_check
forbidden_use = final_trade_decision
```

### TASK-SCHEMA-003

Candidate entry schema should preserve enough field provenance to explain which GMGN canonical bytes contributed to:

- `basic_gate`
- `five_forces`
- `gmgn_risk_density`
- `entry_aux_decision`

### TASK-FIXTURE-003 / TASK-QA-003

Fixtures should be built from these canonical byte groups, especially:

- missing `liquidity`
- missing `market_cap`
- `is_wash_trading=true`
- high `bundler_rate`
- high `top_10_holder_rate`
- unrenounced mint/freeze/owner authority

## 7. Minimal Recommended Next Step

Recommended next PM action:

```text
Create a CR evidence addendum that attaches 00b-GMGN-Canonical-Bytes as the Layer 0 raw-byte dictionary for CR-2026-05-25-002.
```

Suggested output path:

```text
reports/cr_20260525_002_canonical_bytes_evidence_addendum.md
```

This keeps the ai-pro-dev-workflow clean:

```text
document intake
→ evidence addendum
→ human CR approval decision
→ freeze record 002
→ task-card execution
```

## 8. Safety / Overclaim Guard

Claims not made:

- not claiming Five-Forces implementation is complete
- not claiming CR-2026-05-25-002 is approved
- not changing frozen docs
- not executing blocked task cards
- not claiming paper/live/production readiness
- not enabling swap/signing/broadcast/private-key behavior

Final intake status:

```text
CANONICAL_BYTES_ALREADY_PRESENT
CR_EVIDENCE_STRENGTHENED
TASK_EXECUTION_STILL_BLOCKED_PENDING_HUMAN_APPROVAL
NO_LIVE_EXECUTION_AUTHORIZED
```
