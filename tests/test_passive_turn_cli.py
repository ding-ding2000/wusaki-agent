from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from wusaki_agent.agent.passive import run_passive_turn
from wusaki_agent.runtime.models import TurnEnvelope


def test_run_passive_turn_persists_logs(tmp_path: Path) -> None:
    workspace = tmp_path / ".wusaki"
    turn = TurnEnvelope(
        channel="cli",
        user_id="demo",
        message="你好",
        created_at=datetime(2026, 5, 15, 12, 0, 0),
    )

    result = run_passive_turn(turn, workspace)

    assert result["response"] == "收到消息：你好"

    latest_path = workspace / "state" / "latest_turn.json"
    assert latest_path.exists()
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    assert latest["channel"] == "cli"
    assert latest["user_id"] == "demo"

    turns_log = workspace / "state" / "turns.log"
    assert turns_log.exists()
    lines = turns_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    line_obj = json.loads(lines[0])
    assert line_obj["message"] == "你好"
