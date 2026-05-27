#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
READY_STATUSES = {"READY", "READY_FOR_EXEC"}
FORBIDDEN_COMMAND_TERMS = {
    "gmgn-cli swap",
    "gmgn-cli multi-swap",
    "gmgn-cli cooking",
    "private key",
    "private_key",
    "wallet signing",
    "sign transaction",
    "transaction broadcast",
    "broadcast transaction",
    "live trading",
    "auto deploy",
}


@dataclass
class LongrunPackage:
    path: Path
    task_id: str
    title: str
    owner_terminal: str
    status: str
    allowed_write_paths: list[str]
    forbidden_items: list[str]
    acceptance_checks: list[str]
    shell_check_commands: list[str]
    result_path: str


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except Exception:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_scalar(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else ""


def extract_section(text: str, heading_pattern: str) -> str:
    pattern = re.compile(rf"(?ms)^##\s+(?:{heading_pattern})\s*\n(?P<body>.*?)(?=^##\s+|\Z)")
    match = pattern.search(text)
    return match.group("body").strip() if match else ""


def extract_bullets(section: str) -> list[str]:
    items: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("- [x]"):
            item = stripped[5:].strip()
        elif stripped.startswith("-"):
            item = stripped[1:].strip()
        else:
            continue
        if item:
            items.append(item.strip("`"))
    return items


def extract_fenced_shell_commands(text: str) -> list[str]:
    commands: list[str] = []
    for match in re.finditer(r"(?ms)```(?P<lang>[A-Za-z0-9_-]*)\s*\n(?P<body>.*?)\n```", text):
        lang = match.group("lang").strip().lower()
        block = match.group("body").strip()
        if not block or lang not in {"", "bash", "sh"}:
            continue
        if looks_like_shell_block(block):
            commands.append(block)
    return commands


def looks_like_shell_block(block: str) -> bool:
    shell_markers = ("python", "pytest", "test ", "git ", "echo ", "mkdir ", "cp ", "mv ")
    first = next((line.strip() for line in block.splitlines() if line.strip()), "")
    if first.startswith("{") or first.startswith("["):
        return False
    if first.startswith("def ") or first.startswith("from ") or first.startswith("import "):
        return False
    return first.startswith(shell_markers) or "\n" in block and any(line.strip().startswith(shell_markers) for line in block.splitlines())


def forbidden_command_hits(command: str) -> list[str]:
    lowered = command.lower()
    return sorted(term for term in FORBIDDEN_COMMAND_TERMS if term in lowered)


def parse_package(package_path: Path) -> LongrunPackage:
    text = read_text(package_path)
    task_id = parse_scalar(text, "task_id")
    title = parse_scalar(text, "title")
    owner_terminal = parse_scalar(text, "owner_terminal")
    status = parse_scalar(text, "status")

    allowed_section = extract_section(text, r"(?:\d+\.\s*)?Allowed Write Scope|Allowed Write Paths")
    forbidden_section = extract_section(text, r"(?:\d+\.\s*)?Forbidden Scope|Forbidden")
    acceptance_section = extract_section(text, r"(?:\d+\.\s*)?Final Acceptance Criteria|Acceptance Criteria")

    allowed_write_paths = extract_bullets(allowed_section)
    forbidden_items = extract_bullets(forbidden_section)
    acceptance_checks = extract_bullets(acceptance_section)
    shell_check_commands = extract_fenced_shell_commands(text)

    result_path = f"reports/{task_id}/result.md" if task_id else "reports/UNKNOWN/result.md"
    for item in allowed_write_paths:
        if item.startswith("reports/") and item.endswith("result.md"):
            result_path = item
            break

    return LongrunPackage(
        path=package_path,
        task_id=task_id,
        title=title,
        owner_terminal=owner_terminal,
        status=status,
        allowed_write_paths=allowed_write_paths,
        forbidden_items=forbidden_items,
        acceptance_checks=acceptance_checks,
        shell_check_commands=shell_check_commands,
        result_path=result_path,
    )


def repo_sync_state() -> dict[str, Any]:
    script = REPO_ROOT / "scripts" / "check_repo_sync_state.py"
    if not script.exists():
        return {"available": False, "error": "scripts/check_repo_sync_state.py missing"}
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return {"available": False, "returncode": proc.returncode, "stderr": proc.stderr.strip()}
    try:
        data = json.loads(proc.stdout)
    except Exception as exc:
        return {"available": False, "error": f"invalid json: {exc}", "stdout": proc.stdout[:1000]}
    data["available"] = True
    return data


def to_report(pkg: LongrunPackage) -> dict[str, Any]:
    command_safety = [
        {"command": command, "forbidden_hits": forbidden_command_hits(command), "allowed_to_execute": not forbidden_command_hits(command)}
        for command in pkg.shell_check_commands
    ]
    return {
        "runner": "SIKK_LONGRUN_EXECUTION_RUNNER_V0_1",
        "inspected_at": datetime.now(timezone.utc).isoformat(),
        "package_path": repo_relative(pkg.path),
        "task_id": pkg.task_id,
        "title": pkg.title,
        "owner_terminal": pkg.owner_terminal,
        "status": pkg.status,
        "status_ready": pkg.status in READY_STATUSES,
        "allowed_write_paths": pkg.allowed_write_paths,
        "forbidden_items": pkg.forbidden_items,
        "acceptance_checks": pkg.acceptance_checks,
        "shell_check_commands": pkg.shell_check_commands,
        "command_safety": command_safety,
        "result_path": pkg.result_path,
        "repo_sync_state": repo_sync_state(),
        "safety_envelope": {
            "auto_business_code_generation": False,
            "execute_checks_requires_flag": True,
            "live_trading": False,
            "private_key_handling": False,
            "wallet_signing": False,
            "transaction_broadcast": False,
            "gmgn_swap_or_cooking": False,
            "auto_deploy": False,
        },
    }


def write_result_skeleton(pkg: LongrunPackage, report: dict[str, Any]) -> Path:
    result_path = REPO_ROOT / pkg.result_path
    result_path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# Result

task_id: {pkg.task_id}
status: RUNNER_SKELETON_CREATED

## Summary

Longrun runner created this result skeleton from `{repo_relative(pkg.path)}`. This is not business implementation completion.

## Files Changed
- {pkg.result_path}

## Commands Run
- python scripts/run_longrun_task.py {repo_relative(pkg.path)} --inspect-only
- python scripts/run_longrun_task.py {repo_relative(pkg.path)} --write-result-skeleton

## Validation

Runner inspection JSON was generated. Business implementation/tests are still owned by the executing agent following the longrun package.

## Evidence

```json
{json.dumps(report, ensure_ascii=False, indent=2)}
```

## Done State

```yaml
done_state:
  local_files_written: true
  tests_passed: false
  result_md_written: true
  git_committed: false
  git_commit: "NOT_COMMITTED"
  git_pushed: false
  github_issue_commented: false
  github_issue_comment_url: "NOT_APPLICABLE"
  hermes_local_synced_with_remote: false
```

## Deviations
- Result skeleton only; target longrun implementation not executed by this flag.

## Known Gaps
- Business code execution requires an AI execution session to follow the package, or future runner extensions.

## Needs PM Clarification
- None for runner skeleton generation.
"""
    result_path.write_text(content, encoding="utf-8")
    return result_path


def execute_checks(pkg: LongrunPackage) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for command in pkg.shell_check_commands:
        hits = forbidden_command_hits(command)
        if hits:
            results.append({"command": command, "skipped": True, "forbidden_hits": hits})
            continue
        proc = subprocess.run(command, cwd=REPO_ROOT, text=True, shell=True, capture_output=True, check=False)
        results.append(
            {
                "command": command,
                "skipped": False,
                "returncode": proc.returncode,
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-4000:],
            }
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect and scaffold execution for SIKK longrun packages.")
    parser.add_argument("package", nargs="?", help="Path to tasks/longrun/<TASK_ID>.md")
    parser.add_argument("--inspect-only", action="store_true", help="Print package inspection JSON and exit.")
    parser.add_argument("--allow-draft", action="store_true", help="Allow DRAFT/non-ready packages.")
    parser.add_argument("--write-result-skeleton", action="store_true", help="Write reports/<task_id>/result.md skeleton.")
    parser.add_argument("--execute-checks", action="store_true", help="Execute safe fenced shell check commands from the package.")
    args = parser.parse_args(argv)

    if not args.package:
        parser.print_help(sys.stderr)
        return 2

    package_path = (REPO_ROOT / args.package).resolve() if not Path(args.package).is_absolute() else Path(args.package).resolve()
    if not package_path.exists():
        print(json.dumps({"error": "package_not_found", "package": str(package_path)}, ensure_ascii=False), file=sys.stderr)
        return 2
    if REPO_ROOT not in package_path.parents and package_path != REPO_ROOT:
        print(json.dumps({"error": "package_outside_repo", "package": str(package_path)}, ensure_ascii=False), file=sys.stderr)
        return 2

    pkg = parse_package(package_path)
    report = to_report(pkg)

    if pkg.status not in READY_STATUSES and not args.allow_draft:
        report["error"] = "package_not_ready"
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 3

    if args.write_result_skeleton:
        result_path = write_result_skeleton(pkg, report)
        report["result_skeleton_written"] = repo_relative(result_path)

    if args.execute_checks:
        report["executed_checks"] = execute_checks(pkg)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
