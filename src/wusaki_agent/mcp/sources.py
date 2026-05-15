from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

SourceKind = Literal["alert", "content", "context"]


@dataclass(slots=True)
class SourceItem:
    item_id: str
    kind: SourceKind
    title: str
    body: str
    created_at: datetime
    importance: int = 0

@dataclass(slots=True)
class ProactiveSource:
    source_id: str
    server: str
    channel: str
    kind: SourceKind
    sample_items: list[SourceItem]
    enabled: bool = True

    def pull(self) -> list[SourceItem]:
        if not self.enabled:
            return []
        return list(self.sample_items)
