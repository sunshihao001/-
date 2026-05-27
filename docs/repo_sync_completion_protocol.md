# Repo Sync & Completion Protocol

protocol_id: SIKK_REPO_SYNC_COMPLETION_PROTOCOL_V0_1
status: ACTIVE
scope: `/root/sikk-gmgn` local workspace ↔ GitHub repo `sunshihao001/-` ↔ GitHub Issues

## Purpose

This protocol prevents ambiguous completion claims such as:

- "GitHub is done" when only an issue/comment exists.
- "Hermes is done" when files exist locally but were not committed or pushed.
- "Code is done" when the remote repo changed but the local Hermes workspace has not pulled it.

## Three Separate State Layers

```yaml
state_layers:
  github_issues:
    meaning: task / discussion / review management
    not_equal_to: code committed or local workspace updated
  github_repo:
    meaning: committed and pushed shared source state
    not_equal_to: current Hermes local files unless fetched/pulled
  hermes_local_workspace:
    path: /root/sikk-gmgn
    meaning: execution workspace and uncommitted work area
    not_equal_to: GitHub repo until committed and pushed
```

## Required Done State

Every execution `reports/<task_id>/result.md` must include:

```yaml
done_state:
  local_files_written: true | false
  tests_passed: true | false
  result_md_written: true | false
  git_committed: true | false
  git_commit: "<sha | NOT_COMMITTED>"
  git_pushed: true | false
  github_issue_commented: true | false
  github_issue_comment_url: "<url | NOT_APPLICABLE | NOT_DONE>"
  hermes_local_synced_with_remote: true | false
```

## Required Pre-Execution Sync Check

Before non-trivial execution, run:

```bash
python scripts/check_repo_sync_state.py
```

The executor must inspect:

- current branch
- remote URL
- local HEAD
- upstream HEAD
- ahead/behind counts
- dirty tracked files
- untracked files
- whether the working tree is clean

If the remote is ahead, pull only when the local tree is clean or after PM/review decides how to handle dirty files.

## Required Post-Execution Completion Check

Before claiming completion, run:

```bash
python scripts/check_repo_sync_state.py
```

A final task can be called "done" only with an explicit done-state classification:

```yaml
completion_levels:
  LOCAL_DONE:
    requirements:
      - local_files_written: true
      - result_md_written: true
    limitation: not shared until commit/push
  VERIFIED_LOCAL_DONE:
    requirements:
      - LOCAL_DONE
      - tests_passed: true
    limitation: still not shared until commit/push
  GITHUB_SHARED_DONE:
    requirements:
      - VERIFIED_LOCAL_DONE
      - git_committed: true
      - git_pushed: true
    limitation: issue may still need comment/review
  ISSUE_LINKED_DONE:
    requirements:
      - GITHUB_SHARED_DONE
      - github_issue_commented: true
    limitation: PM/review or human may still reject
```

## PM/Review Checklist

PM/review must inspect:

- task card or longrun package
- `reports/<task_id>/result.md`
- git diff / changed files
- test command outputs
- `done_state`
- commit SHA if committed
- push status
- issue comment URL if applicable
- safety boundary confirmation

PM/review may grant only `INTERNAL_PASS`; human acceptance remains separate.

## Dirty Workspace Rule

If pre-existing dirty files are present before a governance or implementation task, the executor must:

1. record them in result.md;
2. avoid staging/committing unrelated files;
3. commit only files owned by the current task scope;
4. leave unrelated dirty files untouched unless a task card explicitly includes them.

## Forbidden Scope

This protocol does not authorize:

- live trading
- private key handling
- wallet signing
- transaction broadcast
- GMGN swap / multi-swap / cooking
- auto deploy
- production readiness claims
- strategy approval
- paper-ready or auto-ready claims
