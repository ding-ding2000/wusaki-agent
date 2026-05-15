from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(slots=True)
class MemoryQuery:
    query: str
    limit: int = 5


@dataclass(slots=True)
class MemoryHit:
    memory_id: str
    content: str
    score: float


@dataclass(slots=True)
class MemoryRecord:
    memory_id: str
    content: str
    source: str
    created_at: str


@dataclass(slots=True)
class RememberRequest:
    content: str
    source: str
    memory_id: str | None = None


@dataclass(slots=True)
class ForgetRequest:
    memory_id: str


@dataclass(slots=True)
class RememberResult:
    record: MemoryRecord


@dataclass(slots=True)
class ForgetResult:
    forgotten: bool


def now_iso() -> str:
    return datetime.now(UTC).isoformat()
