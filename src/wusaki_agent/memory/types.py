from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MemoryQuery:
    query: str
    limit: int = 5


@dataclass(slots=True)
class MemoryHit:
    memory_id: str
    content: str
    score: float

