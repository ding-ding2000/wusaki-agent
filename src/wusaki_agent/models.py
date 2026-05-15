from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class InitSummary:
    workspace: Path
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


@dataclass(slots=True)
class CheckResult:
    name: str
    ok: bool
    detail: str

