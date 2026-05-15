from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from wusaki_agent.mcp.sources import ProactiveSource, SourceItem
from wusaki_agent.runtime.models import TickDecision


@dataclass(slots=True)
class TickState:
    now: datetime
    last_sent_at: datetime | None = None
    sent_in_last_hour: int = 0


def choose_item(items: list[SourceItem]) -> SourceItem | None:
    if not items:
        return None
    # Keep deterministic ordering by highest importance, then oldest item id.
    sorted_items = sorted(items, key=lambda x: (-x.importance, x.item_id))
    return sorted_items[0]


def dry_run_tick(
    sources: list[ProactiveSource],
    state: TickState,
    cooldown_minutes: int,
    max_per_hour: int,
) -> TickDecision:
    if cooldown_minutes < 0:
        raise ValueError("cooldown_minutes must be >= 0")
    if max_per_hour <= 0:
        raise ValueError("max_per_hour must be > 0")

    if state.last_sent_at is not None:
        cooldown_until = state.last_sent_at + timedelta(minutes=cooldown_minutes)
        if state.now < cooldown_until:
            return TickDecision(
                decision="skip",
                reason="skip: cooldown window is still active.",
            )
    if state.sent_in_last_hour >= max_per_hour:
        return TickDecision(
            decision="skip",
            reason="skip: hourly frequency limit reached.",
        )

    for source in sources:
        candidate = choose_item(source.pull())
        if candidate is None:
            continue
        return TickDecision(
            decision="send",
            reason=f"send: selected {candidate.kind} item from source {source.source_id}.",
            selected_source_id=source.source_id,
            selected_item_id=candidate.item_id,
        )

    return TickDecision(
        decision="skip",
        reason="skip: no eligible items from MCP sources, switch to drift.",
        should_trigger_drift=True,
    )
