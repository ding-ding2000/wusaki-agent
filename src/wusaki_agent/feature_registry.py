from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wusaki_agent.json_io import read_json


@dataclass(slots=True)
class FeatureRegistry:
    path: Path

    def load(self) -> dict:
        return read_json(self.path)

    def counts(self) -> dict[str, int]:
        payload = self.load()
        counts: dict[str, int] = {}
        for feature in payload.get("features", []):
            status = feature.get("status", "unknown")
            counts[status] = counts.get(status, 0) + 1
        return counts

