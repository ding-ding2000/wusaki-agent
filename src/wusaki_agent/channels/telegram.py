from __future__ import annotations

from wusaki_agent.channels.base import ChannelAdapter, ChannelMessage


class TelegramChannelAdapter(ChannelAdapter):
    name = "telegram"

    def send(self, message: ChannelMessage) -> str:
        return f"[telegram-placeholder] {message.user_id}: {message.text}"

