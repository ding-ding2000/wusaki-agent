from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class DriftSkill:
    name: str
    description: str
    path: Path


def discover_skills(skills_dir: Path) -> list[DriftSkill]:
    found: list[DriftSkill] = []
    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        payload = _parse_front_matter(skill_file)
        found.append(
            DriftSkill(
                name=payload.get("name", skill_file.parent.name),
                description=payload.get("description", ""),
                path=skill_file,
            )
        )
    return found


def _parse_front_matter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    _, front_matter, _rest = content.split("---\n", 2)
    payload = yaml.safe_load(front_matter) or {}
    return payload if isinstance(payload, dict) else {}

