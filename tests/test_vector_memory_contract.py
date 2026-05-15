from __future__ import annotations

from wusaki_agent.memory.types import ForgetRequest, MemoryQuery, RememberRequest
from wusaki_agent.memory.vector import StubVectorMemory


def test_stub_vector_memory_remember_retrieve_forget_contract() -> None:
    memory = StubVectorMemory()

    remember = memory.remember(
        RememberRequest(content="用户喜欢清晰的任务拆解", source="turn:demo")
    )
    assert remember.record.memory_id.startswith("stub-memory-")
    assert remember.record.source == "turn:demo"

    hits = memory.retrieve(MemoryQuery(query="任务拆解", limit=5))
    assert len(hits) == 1
    assert hits[0].memory_id == remember.record.memory_id
    assert "任务拆解" in hits[0].content

    forget = memory.forget(ForgetRequest(memory_id=remember.record.memory_id))
    assert forget.forgotten is True
    assert memory.retrieve(MemoryQuery(query="任务拆解", limit=5)) == []


def test_stub_vector_memory_forget_missing_id_is_safe() -> None:
    memory = StubVectorMemory()
    result = memory.forget(ForgetRequest(memory_id="missing-id"))
    assert result.forgotten is False
