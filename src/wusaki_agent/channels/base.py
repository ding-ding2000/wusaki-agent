from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ChannelMessage:
    channel: str
    user_id: str
    text: str


class ChannelAdapter:
    name: str = "base"

    def send(self, message: ChannelMessage) -> str:
        raise NotImplementedError

