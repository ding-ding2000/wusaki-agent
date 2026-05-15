from __future__ import annotations

from wusaki_agent.runtime.models import TickDecision


def dry_run_tick() -> TickDecision:
    return TickDecision(
        decision="skip",
        reason="No MCP sources are configured yet, so proactive delivery remains in dry-run mode.",
    )

