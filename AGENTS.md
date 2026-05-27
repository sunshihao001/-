# Project Agent Rules — Solana Meme Workflow OS

## Project Root
`/root/sikk-gmgn/`

## Default Mode
This project uses the `ai-pro-dev-workflow` control plane in 3-terminal preparation mode until PM/review upgrades it.

## Role Split

### PM/Docs / PM-review
Owns management, requirement freezing, task cards, review, CI attribution, dispatch, project status, and human handoff.

May write:
- `AGENTS.md`
- `CONTEXT.md`
- `docs/**`
- `tasks/**`
- `reports/review.md`
- `reports/final_acceptance.md`
- `templates/**`

### Skill Backend
Executes approved backend task cards only.

May write only paths listed in the task card, typically:
- `skills/**`
- `rules/**`
- `reports/<task_id>/result.md`

### QA/CI
Executes approved QA or CI task cards only.

May write only paths listed in the task card, typically:
- `fixtures/**`
- `skills/**/tests/**`
- `reports/<task_id>/result.md`
- `reports/<task_id>/fix_result.md`

### Docs A
Maintains current status/changelog/result summaries after PM approval.

## Required Before Coding
Read:
- `CONTEXT.md`
- `docs/specs.md`
- `docs/acceptance.md`
- `docs/freeze_record.md`
- relevant `tasks/<category>/<task_id>.md`

## Hard Rules
- No task card, no coding.
- Do not code from chat summaries.
- Do not modify `docs/specs.md`, `docs/acceptance.md`, or `CONTEXT.md` without PM/review approval and a new freeze record.
- Do not change unrelated files.
- Do not invent requirements.
- Do not skip validation.
- Do not claim final acceptance.
- PM/review may grant only `INTERNAL_PASS`; human grants `HUMAN_ACCEPTED` or `HUMAN_REJECTED`.

## Solana Meme Safety Boundary
Phase 1 is read-only research / paper-only gating.

Forbidden for all terminals unless a future human-approved phase explicitly changes this:
- real orders
- private key access
- wallet signing
- transaction broadcast
- `gmgn-cli swap`
- `gmgn-cli multi-swap`
- `gmgn-cli cooking create`
- auto deploy
- claims such as “确定庄家”, “确定内幕”, or “一定会涨”

## Completion Contract
Every execution task must write:
- `reports/<task_id>/result.md`

CI fix tasks write:
- `reports/<task_id>/fix_result.md`
