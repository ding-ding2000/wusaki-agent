from __future__ import annotations

from pathlib import Path

from wusaki_agent.json_io import write_json
from wusaki_agent.models import CheckResult, InitSummary
from wusaki_agent.workspace.templates import DIRECTORIES, JSON_TEMPLATES, TEXT_TEMPLATES


def init_workspace(workspace: Path) -> InitSummary:
    summary = InitSummary(workspace=workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    for rel_path in DIRECTORIES:
        target = workspace / rel_path
        existed = target.exists()
        target.mkdir(parents=True, exist_ok=True)
        (summary.skipped if existed else summary.created).append(target)

    for rel_path, content in TEXT_TEMPLATES.items():
        target = workspace / rel_path
        if target.exists():
            summary.skipped.append(target)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        summary.created.append(target)

    for rel_path, payload in JSON_TEMPLATES.items():
        target = workspace / rel_path
        if target.exists():
            summary.skipped.append(target)
            continue
        write_json(target, payload)
        summary.created.append(target)

    return summary


def verify_workspace(workspace: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []
    required_paths = [
        workspace / "memory" / "MEMORY.md",
        workspace / "memory" / "SELF.md",
        workspace / "memory" / "HISTORY.md",
        workspace / "memory" / "RECENT_CONTEXT.md",
        workspace / "memory" / "PENDING.md",
        workspace / "drift" / "skills",
        workspace / "PROACTIVE_CONTEXT.md",
        workspace / "state" / "runtime.json",
    ]

    for path in required_paths:
        checks.append(
            CheckResult(
                name=str(path.relative_to(workspace)),
                ok=path.exists(),
                detail="present" if path.exists() else "missing",
            )
        )

    return checks

