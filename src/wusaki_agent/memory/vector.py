from __future__ import annotations

from typing import Protocol

from wusaki_agent.memory.types import (
    ForgetRequest,
    ForgetResult,
    MemoryHit,
    MemoryQuery,
    MemoryRecord,
    RememberRequest,
    RememberResult,
    now_iso,
)


class VectorMemory(Protocol):
    def retrieve(self, query: MemoryQuery) -> list[MemoryHit]:
        ...

    def remember(self, request: RememberRequest) -> RememberResult:
        ...

    def forget(self, request: ForgetRequest) -> ForgetResult:
        ...


class StubVectorMemory:
    """Deterministic in-memory compatibility layer for vector memory contracts."""

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._counter = 0

    def retrieve(self, query: MemoryQuery) -> list[MemoryHit]:
        needle = query.query.strip().lower()
        if not needle:
            return []

        hits: list[MemoryHit] = []
        for record in self._records.values():
            text = record.content.lower()
            if needle in text:
                score = min(1.0, len(needle) / max(len(text), 1))
                hits.append(
                    MemoryHit(memory_id=record.memory_id, content=record.content, score=score)
                )
        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[: query.limit]

    def remember(self, request: RememberRequest) -> RememberResult:
        memory_id = request.memory_id or self._next_memory_id()
        record = MemoryRecord(
            memory_id=memory_id,
            content=request.content,
            source=request.source,
            created_at=now_iso(),
        )
        self._records[memory_id] = record
        return RememberResult(record=record)

    def forget(self, request: ForgetRequest) -> ForgetResult:
        existed = request.memory_id in self._records
        self._records.pop(request.memory_id, None)
        return ForgetResult(forgotten=existed)

    def _next_memory_id(self) -> str:
        self._counter += 1
        return f"stub-memory-{self._counter:04d}"
