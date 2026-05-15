from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProactiveSource:
    server: str
    channel: str
    enabled: bool = True

