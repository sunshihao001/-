# AI Pro Dev Workflow — Solana Meme Workflow OS

## Core Chain

```text
user direction
→ PM/review clarification
→ docs/specs.md + docs/acceptance.md + CONTEXT.md
→ docs/freeze_record.md
→ tasks/task_tree.md + task cards
→ task-card-bound execution
→ reports/<task_id>/result.md
→ PM/review: INTERNAL_PASS | PATCH_REQUIRED | BLOCKED
→ CI failure attribution + fix task card
→ human final acceptance
```

## Current Role Mode
Default 3-terminal mode:

1. `PM/Docs` — freeze requirements, create tasks, review, dispatch.
2. `Skill Backend` — implement `skills/**`, `rules/**`, and backend contracts only from task cards.
3. `QA/CI` — maintain tests, fixtures, CI commands, and failure attribution only from task cards.

Upgrade to 5+ terminals only after pytest baseline is clean or all failures are explicitly attributed.

## Frozen Core Docs
After this freeze, these are frozen inputs:
- `CONTEXT.md`
- `docs/specs.md`
- `docs/acceptance.md`

Any change requires:
- `docs/docs_change_request.md` entry or task-specific change request
- PM/review approval
- new `docs/freeze_record.md` entry

## Execution Protocol
- No task card, no coding.
- Execution terminals must read frozen docs and their task card.
- Execution terminals may write only `allowed_write_paths`.
- Execution terminals must write `reports/<task_id>/result.md`.
- Execution terminals must mark `BLOCKED` instead of guessing when scope or data is unclear.

## CI Failure Protocol

```text
pytest/CI failed
→ QA/CI writes failure attribution
→ PM/review checks whether failure belongs to current task
→ if yes: create fix task card
→ if no: create separate task or mark BLOCKED
→ executor writes fix_result.md
→ PM/review rechecks
```

## Human Acceptance
`INTERNAL_PASS` is not final acceptance. Only the human can set:
- `HUMAN_ACCEPTED`
- `HUMAN_REJECTED`

## Safety Mode
This project remains Phase 1 safe-mode unless a later frozen doc explicitly changes phase. No live trading, private key access, signing, broadcast, or swap commands.
