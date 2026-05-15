from __future__ import annotations

import json
from pathlib import Path

from wusaki_agent.json_io import write_json
from wusaki_agent.runtime.models import TurnEnvelope


def describe_passive_turn_contract(turn: TurnEnvelope) -> str:
    return (
        f"Passive turn placeholder: channel={turn.channel}, "
        f"user_id={turn.user_id}, message_length={len(turn.message)}"
    )


def run_passive_turn(turn: TurnEnvelope, workspace: Path) -> dict:
    """Run one deterministic passive turn and persist minimal turn logs."""
    response_text = f"收到消息：{turn.message}"
    record = {
        "channel": turn.channel,
        "user_id": turn.user_id,
        "message": turn.message,
        "created_at": turn.created_at.isoformat(),
        "response": response_text,
    }
    append_turn_log(workspace, record)
    return record


def append_turn_log(workspace: Path, record: dict) -> None:
    state_dir = workspace / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    log_path = state_dir / "turns.log"
    with log_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")

    latest_path = state_dir / "latest_turn.json"
    write_json(latest_path, record)
