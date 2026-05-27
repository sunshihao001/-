# Task Card

task_id: TASK-DOC-002
title: Apply CR-2026-05-25-002 to frozen docs and write freeze record 002
owner_terminal: pm-review
status: INTERNAL_PASS

## Input Files
- `docs/docs_change_request.md`
- `docs/proposed/CR-2026-05-25-002-docs-patch.md`
- `learning/GMGN字段组合五力模型理论总结.txt`
- `learning/15-GMGN字段组合地基.md`

## Read-Only Context
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`
- `AGENTS.md`
- `docs/ai_dev_workflow.md`

## Allowed Write Paths
- `docs/specs.md`
- `docs/acceptance.md`
- `CONTEXT.md`
- `docs/freeze_record.md`
- `tasks/task_tree.md`
- `reports/TASK-DOC-002/result.md`

## Forbidden
- Modify task cards owned by skill-backend or qa-ci
- Change unrelated docs
- Expand scope beyond CR-2026-05-25-002
- Trigger live trading, wallet signing, transaction broadcast, gmgn swap, or auto deploy

## Acceptance Criteria
- [ ] `docs/specs.md` contains the new `S01 Candidate Entry Five-Forces Gate Contract` section verbatim from proposed patch §1.1.
- [ ] `docs/specs.md` Engineering Requirements include patch §1.2 bullets.
- [ ] `docs/specs.md` Excluded list includes patch §1.3 bullets.
- [ ] `docs/acceptance.md` Skill Contract Gates include patch §2.1 bullets.
- [ ] `docs/acceptance.md` Test Gates include patch §2.2 bullets.
- [ ] `CONTEXT.md` contains the `Five-Forces Entry Terms` block.
- [ ] `docs/freeze_record.md` has a new entry with `freeze_id: sol-ai-pro-dev-workflow-freeze-20260525-002`.
- [ ] `tasks/task_tree.md` adds a `Five-Forces Entry` batch listing TASK-RULE-005, TASK-SCHEMA-003, TASK-BE-006, TASK-BE-007, TASK-FIXTURE-003, TASK-QA-003.
- [ ] `reports/TASK-DOC-002/result.md` written with the diff summary and the new freeze_id.

## Dependencies
- Human approval of CR-2026-05-25-002.

## Blocked By
- CR-2026-05-25-002 (status DRAFT → must be APPROVED).
