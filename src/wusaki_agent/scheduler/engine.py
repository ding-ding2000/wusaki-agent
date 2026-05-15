from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SchedulerState:
    proactive_enabled: bool
    drift_enabled: bool

