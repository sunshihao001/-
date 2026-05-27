#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def run_git(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_out(args: list[str], default: str = "") -> str:
    code, out, _err = run_git(args)
    return out if code == 0 else default


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    inside = git_out(["rev-parse", "--is-inside-work-tree"], "false") == "true"
    if not inside:
        print(json.dumps({"is_git_repo": False, "root": str(root)}, ensure_ascii=False, indent=2))
        return 2

    remote_url = git_out(["remote", "get-url", "origin"], "NO_ORIGIN")
    branch = git_out(["branch", "--show-current"], "DETACHED")
    local_head = git_out(["rev-parse", "HEAD"], "UNKNOWN")
    upstream_ref = git_out(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], "NO_UPSTREAM")
    upstream_head = git_out(["rev-parse", "@{u}"], "UNKNOWN") if upstream_ref != "NO_UPSTREAM" else "UNKNOWN"

    ahead_by = 0
    behind_by = 0
    if upstream_ref != "NO_UPSTREAM":
        counts = git_out(["rev-list", "--left-right", "--count", "HEAD...@{u}"], "0\t0")
        try:
            ahead_s, behind_s = counts.split()
            ahead_by = int(ahead_s)
            behind_by = int(behind_s)
        except Exception:
            ahead_by = -1
            behind_by = -1

    porcelain = git_out(["status", "--porcelain"], "")
    dirty_files = [line for line in porcelain.splitlines() if line]
    tracked_dirty = [line for line in dirty_files if not line.startswith("??")]
    untracked = [line for line in dirty_files if line.startswith("??")]

    result = {
        "is_git_repo": True,
        "root": str(root),
        "branch": branch,
        "remote": remote_url,
        "local_head": local_head,
        "upstream_ref": upstream_ref,
        "upstream_head": upstream_head,
        "ahead_by": ahead_by,
        "behind_by": behind_by,
        "working_tree_clean": len(dirty_files) == 0,
        "tracked_dirty_count": len(tracked_dirty),
        "untracked_count": len(untracked),
        "dirty_files": dirty_files,
        "completion_sync_status": "SYNCED_CLEAN" if len(dirty_files) == 0 and ahead_by == 0 and behind_by == 0 else "ATTENTION_REQUIRED",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
