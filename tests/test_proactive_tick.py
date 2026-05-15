from __future__ import annotations

from datetime import datetime, timedelta

from wusaki_agent.mcp.sources import ProactiveSource, SourceItem, SourceKind
from wusaki_agent.proactive.tick import TickState, dry_run_tick


def make_source(source_id: str, kind: SourceKind, has_item: bool) -> ProactiveSource:
    now = datetime(2026, 5, 15, 12, 0, 0)
    items = (
        [
                SourceItem(
                    item_id=f"{source_id}-001",
                kind=kind,
                title=f"{kind} title",
                body="body",
                created_at=now,
                importance=5,
            )
        ]
        if has_item
        else []
    )
    return ProactiveSource(
        source_id=source_id,
        server="mcp.test",
        channel="demo",
        kind=kind,
        sample_items=items,
    )


def test_tick_sends_when_eligible_item_exists() -> None:
    state = TickState(now=datetime(2026, 5, 15, 12, 0, 0))
    sources = [
        make_source("src-alert", "alert", True),
        make_source("src-content", "content", False),
        make_source("src-context", "context", False),
    ]

    decision = dry_run_tick(sources=sources, state=state, cooldown_minutes=30, max_per_hour=2)

    assert decision.decision == "send"
    assert decision.selected_source_id == "src-alert"
    assert decision.selected_item_id == "src-alert-001"
    assert decision.should_trigger_drift is False


def test_tick_skips_when_cooldown_active() -> None:
    now = datetime(2026, 5, 15, 12, 0, 0)
    state = TickState(now=now, last_sent_at=now - timedelta(minutes=5), sent_in_last_hour=0)
    sources = [make_source("src-alert", "alert", True)]

    decision = dry_run_tick(sources=sources, state=state, cooldown_minutes=30, max_per_hour=3)

    assert decision.decision == "skip"
    assert "cooldown" in decision.reason


def test_tick_skips_when_rate_limit_hit() -> None:
    state = TickState(
        now=datetime(2026, 5, 15, 12, 0, 0),
        last_sent_at=datetime(2026, 5, 15, 10, 0, 0),
        sent_in_last_hour=2,
    )
    sources = [make_source("src-alert", "alert", True)]

    decision = dry_run_tick(sources=sources, state=state, cooldown_minutes=30, max_per_hour=2)

    assert decision.decision == "skip"
    assert "frequency" in decision.reason


def test_tick_falls_back_to_drift_when_no_items() -> None:
    state = TickState(now=datetime(2026, 5, 15, 12, 0, 0))
    sources = [
        make_source("src-alert", "alert", False),
        make_source("src-content", "content", False),
        make_source("src-context", "context", False),
    ]

    decision = dry_run_tick(sources=sources, state=state, cooldown_minutes=30, max_per_hour=2)

    assert decision.decision == "skip"
    assert decision.should_trigger_drift is True
    assert "drift" in decision.reason
