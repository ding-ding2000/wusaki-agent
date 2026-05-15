from __future__ import annotations

from wusaki_agent.channels.base import ChannelAdapter, ChannelMessage


class TelegramChannelAdapter(ChannelAdapter):
    name = "telegram"

    def normalize_user_id(self, raw_user_id: str) -> str:
        cleaned = raw_user_id.strip()
        return cleaned.removeprefix("tg:")

    def send(self, message: ChannelMessage) -> str:
        user_id = self.normalize_user_id(message.user_id)
        if message.kind == "passive":
            return f"[telegram-placeholder] {user_id}: {message.text}"
        return f"[telegram-placeholder:{message.kind}] {user_id}: {message.text}"
