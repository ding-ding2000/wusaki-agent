from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class TurnEnvelope:
    channel: str
    user_id: str
    message: str
    created_at: datetime


@dataclass(slots=True)
class TickDecision:
    decision: str
    reason: str
    should_trigger_drift: bool = False
    selected_source_id: str | None = None
    selected_item_id: str | None = None


@dataclass(slots=True)
class PassiveTurnOutput:
    channel: str
    user_id: str
    message: str
    created_at: str
    response: str
    context_used: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "user_id": self.user_id,
            "message": self.message,
            "created_at": self.created_at,
            "response": self.response,
            "context_used": self.context_used,
        }
