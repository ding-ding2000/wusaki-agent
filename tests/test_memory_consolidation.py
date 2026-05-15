from __future__ import annotations

from datetime import datetime
from pathlib import Path

from wusaki_agent.agent.passive import run_passive_turn
from wusaki_agent.memory.markdown import run_consolidation
from wusaki_agent.runtime.models import TurnEnvelope
from wusaki_agent.workspace.bootstrap import init_workspace


def _prepare_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / ".wusaki"
    init_workspace(workspace)
    return workspace


def test_consolidation_writes_history_pending_and_recent_context(tmp_path: Path) -> None:
    workspace = _prepare_workspace(tmp_path)
    turn = TurnEnvelope(
        channel="cli",
        user_id="demo",
        message="记住我今天在做F003",
        created_at=datetime(2026, 5, 15, 10, 0, 0),
    )
    run_passive_turn(turn, workspace, persist=True)

    result = run_consolidation(workspace)

    assert result.processed == 1
    assert result.history_appended == 1
    assert result.pending_appended == 1
    assert result.recent_context_updated is True

    history = (workspace / "memory" / "HISTORY.md").read_text(encoding="utf-8")
    pending = (workspace / "memory" / "PENDING.md").read_text(encoding="utf-8")
    recent = (workspace / "memory" / "RECENT_CONTEXT.md").read_text(encoding="utf-8")
    queue = (workspace / "state" / "postprocess_queue.jsonl").read_text(encoding="utf-8")

    assert "记住我今天在做F003" in history
    assert "requested_memory" in pending
    assert "user: 记住我今天在做F003" in recent
    assert '"status": "done"' in queue


def test_consolidation_is_idempotent_for_same_turn(tmp_path: Path) -> None:
    workspace = _prepare_workspace(tmp_path)
    turn = TurnEnvelope(
        channel="cli",
        user_id="demo",
        message="同一条消息不要重复写入",
        created_at=datetime(2026, 5, 15, 10, 0, 0),
    )
    run_passive_turn(turn, workspace, persist=True)

    first = run_consolidation(workspace)
    second = run_consolidation(workspace)

    assert first.processed == 1
    assert second.processed == 0
    assert second.skipped == 0

    history_lines = (workspace / "memory" / "HISTORY.md").read_text(encoding="utf-8").splitlines()
    matched = [line for line in history_lines if "同一条消息不要重复写入" in line]
    assert len(matched) == 1
