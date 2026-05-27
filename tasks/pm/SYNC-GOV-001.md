# Task Card

task_id: SYNC-GOV-001
title: Repo 同步与完成态治理落地
owner_terminal: pm-review
status: READY

## Mission

把 `/root/sikk-gmgn` 的本地执行状态、GitHub repo 提交状态、GitHub issue 管理状态用一个可检查协议连接起来，避免“GitHub 做完但 Hermes 本地没有”或“本地写完但 GitHub 没有”的状态混乱。

## Input Files

- `AGENTS.md`
- `docs/ai_dev_workflow.md`
- `templates/result.template.md`
- `templates/review.template.md`

## Allowed Write Paths

- `tasks/pm/SYNC-GOV-001.md`
- `docs/repo_sync_completion_protocol.md`
- `templates/result.template.md`
- `templates/review.template.md`
- `scripts/check_repo_sync_state.py`
- `reports/SYNC-GOV-001/result.md`

## Forbidden

- Modify `docs/specs.md`, `docs/acceptance.md`, `CONTEXT.md`, or `docs/freeze_record.md`
- Modify skill runtime logic
- Modify unrelated task packages
- Commit/push pre-existing unrelated dirty files as part of this governance task
- Print or store GitHub tokens/private credentials
- Trigger live trading, wallet signing, transaction broadcast, GMGN swap/cooking, or auto deploy

## Acceptance Criteria

- [ ] A repo sync/completion protocol document exists.
- [ ] Result template includes machine-readable `done_state` fields.
- [ ] Review template requires PM/review to inspect result.md, diff, tests, commit, push, and issue-comment evidence.
- [ ] A script can report local/remote git sync state without exposing secrets.
- [ ] The script passes `py_compile` and runs successfully.
- [ ] `reports/SYNC-GOV-001/result.md` records commands, outputs, files changed, pre-existing dirty files, and commit/push status.
- [ ] Only governance files are committed/pushed; unrelated dirty files remain unstaged/uncommitted unless separately approved.
