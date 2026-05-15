from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


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

