from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from wusaki_agent.proactive.tick import TickState


@dataclass(slots=True)
class SchedulerState:
    proactive_enabled: bool
    drift_enabled: bool
    proactive_tick: TickState


def default_scheduler_state(
    proactive_enabled: bool,
    drift_enabled: bool,
) -> SchedulerState:
    return SchedulerState(
        proactive_enabled=proactive_enabled,
        drift_enabled=drift_enabled,
        proactive_tick=TickState(now=datetime.utcnow()),
    )
