# Task Card

task_id: TASK-EXEC-RUNNER-001
title: 工程执行端 Longrun Runner 最小可用入口
owner_terminal: exec
status: READY

## Mission

实现工程执行端 longrun runner：

```bash
python scripts/run_longrun_task.py tasks/longrun/<TASK_ID>.md
```

该 runner 作为代码执行端的任务包读取、边界检查、阶段/命令提取、结果骨架生成入口。当前任务只做安全的最小可用控制器，不自动让 AI 写业务代码，不绕过 PM/review，不执行交易/钱包/GMGN 写入动作。

## Input Files

- `docs/repo_sync_completion_protocol.md`
- `scripts/check_repo_sync_state.py`
- `templates/result.template.md`
- `tasks/longrun/TASK-SCHEMA-004.md` as fixture-like real package

## Allowed Write Paths

- `tasks/pm/TASK-EXEC-RUNNER-001.md`
- `scripts/run_longrun_task.py`
- `reports/TASK-EXEC-RUNNER-001/result.md`

## Forbidden

- Modify `docs/specs.md`, `docs/acceptance.md`, `CONTEXT.md`, `docs/freeze_record.md`
- Modify existing longrun packages
- Modify skill runtime code
- Auto-commit unrelated dirty files
- Execute arbitrary shell commands from a package unless explicitly using `--execute-checks`
- Execute commands containing forbidden runtime/trading/wallet/swap/signing/broadcast/cooking/private-key terms
- Claim business implementation completion for the target longrun package

## Acceptance Criteria

- [ ] `scripts/run_longrun_task.py` exists and imports with py_compile.
- [ ] Running without args prints CLI help or exits cleanly with usage.
- [ ] `--inspect-only` on `tasks/longrun/TASK-SCHEMA-004.md` outputs parseable JSON.
- [ ] JSON includes task_id, title, status, owner_terminal, allowed_write_paths, forbidden_items, acceptance_checks, shell_check_commands, result_path, repo_sync_state.
- [ ] Runner refuses packages whose status is not `READY` or `READY_FOR_EXEC` unless `--allow-draft` is provided.
- [ ] Runner can write `reports/<task_id>/result.md` skeleton only when `--write-result-skeleton` is provided.
- [ ] Runner does not modify target package or skill code.
- [ ] Forbidden command detector blocks live/wallet/swap/signing/broadcast/cooking/private-key command candidates.
- [ ] `reports/TASK-EXEC-RUNNER-001/result.md` records validation commands and outputs.
