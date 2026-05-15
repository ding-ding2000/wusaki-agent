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
    recent_context = load_recent_context(workspace)
    response_text = f"收到消息：{turn.message}"
    record = {
        "channel": turn.channel,
        "user_id": turn.user_id,
        "message": turn.message,
        "created_at": turn.created_at.isoformat(),
        "context_used": {
            "recent_context_preview": recent_context[:200],
        },
        "response": response_text,
    }
    append_turn_log(workspace, record, recent_context=recent_context)
    return record


def load_recent_context(workspace: Path) -> str:
    path = workspace / "memory" / "RECENT_CONTEXT.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def append_turn_log(workspace: Path, record: dict, recent_context: str) -> None:
    state_dir = workspace / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    log_path = state_dir / "turns.log"
    with log_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")

    latest_path = state_dir / "latest_turn.json"
    write_json(latest_path, record)

    # Structured artifact for downstream consolidation and audits.
    artifact = {
        "turn": {
            "channel": record["channel"],
            "user_id": record["user_id"],
            "message": record["message"],
            "created_at": record["created_at"],
        },
        "context": {"recent_context": recent_context},
        "response": {"text": record["response"]},
    }
    artifact_name = f"turn_{record['created_at'].replace(':', '-').replace('.', '-')}.json"
    artifact_path = state_dir / "turn_artifacts" / artifact_name
    write_json(artifact_path, artifact)
