from __future__ import annotations

from wusaki_agent.channels.base import ChannelAdapter, ChannelMessage


class QqChannelAdapter(ChannelAdapter):
    name = "qq"

    def send(self, message: ChannelMessage) -> str:
        return f"[qq-placeholder] {message.user_id}: {message.text}"

