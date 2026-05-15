from __future__ import annotations

from wusaki_agent.runtime.models import TurnEnvelope


def describe_passive_turn_contract(turn: TurnEnvelope) -> str:
    return (
        f"Passive turn placeholder: channel={turn.channel}, "
        f"user_id={turn.user_id}, message_length={len(turn.message)}"
    )

