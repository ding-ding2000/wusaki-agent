from __future__ import annotations

from wusaki_agent.memory.types import MemoryHit, MemoryQuery


class StubVectorMemory:
    """Temporary compatibility layer until a real vector backend lands."""

    def retrieve(self, query: MemoryQuery) -> list[MemoryHit]:
        return [
            MemoryHit(
                memory_id="stub-memory",
                content=f"Vector memory backend is not implemented yet for query: {query.query}",
                score=0.0,
            )
        ]

