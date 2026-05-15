from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from wusaki_agent.json_io import read_json, write_json


@dataclass(slots=True)
class DriftSkill:
    name: str
    description: str
    path: Path
    work_files: list[str]
    max_messages: int


@dataclass(slots=True)
class DriftRunResult:
    skill_name: str
    status: str
    actions: list[str]
    message_sent: bool
    message_preview: str | None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover_skills(skills_dir: Path) -> list[DriftSkill]:
    found: list[DriftSkill] = []
    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        payload, body = _parse_skill_doc(skill_file)
        found.append(
            DriftSkill(
                name=payload.get("name", skill_file.parent.name),
                description=payload.get("description", ""),
                path=skill_file,
                work_files=_extract_work_files(body),
                max_messages=_detect_max_messages(body),
            )
        )
    return found


def _parse_skill_doc(path: Path) -> tuple[dict[str, Any], str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}, content
    _, front_matter, body = content.split("---\n", 2)
    payload = yaml.safe_load(front_matter) or {}
    parsed = payload if isinstance(payload, dict) else {}
    return parsed, body


def _extract_work_files(body: str) -> list[str]:
    work_files: list[str] = []
    for line in body.splitlines():
        raw = line.strip()
        if raw.startswith("- `") and raw.endswith("`"):
            rel = raw[3:-1].strip()
            if rel:
                work_files.append(rel)
    return work_files


def _detect_max_messages(body: str) -> int:
    lowered = body.lower()
    if "最多发一条消息" in body or "at most one message" in lowered:
        return 1
    if "静默" in body or "without messaging" in lowered:
        return 0
    return 1


def run_drift_round(workspace: Path, skill_name: str | None = None) -> DriftRunResult:
    skills_dir = workspace / "drift" / "skills"
    skills = discover_skills(skills_dir)
    if not skills:
        raise ValueError(f"No drift skills found under: {skills_dir}")

    selected = skills[0]
    if skill_name is not None:
        matched = [skill for skill in skills if skill.name == skill_name]
        if not matched:
            raise ValueError(f"Drift skill not found: {skill_name}")
        selected = matched[0]

    actions = [f"loaded skill: {selected.name}"]
    for rel_path in selected.work_files:
        target = workspace / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text("", encoding="utf-8")
        actions.append(f"checked work file: {rel_path}")

    message_sent = selected.max_messages > 0
    message_preview = f"[drift:{selected.name}] ping" if message_sent else None
    actions.append("completed round")

    drift_path = workspace / "drift" / "drift.json"
    drift_state = (
        read_json(drift_path)
        if drift_path.exists()
        else {
            "recent_runs": [],
        }
    )
    recent_runs = drift_state.setdefault("recent_runs", [])
    recent_runs.append(
        {
            "skill": selected.name,
            "status": "completed",
            "actions": actions,
            "message_sent": message_sent,
            "message_preview": message_preview,
            "completed_at": _now_iso(),
        }
    )
    write_json(drift_path, drift_state)

    return DriftRunResult(
        skill_name=selected.name,
        status="completed",
        actions=actions,
        message_sent=message_sent,
        message_preview=message_preview,
    )
