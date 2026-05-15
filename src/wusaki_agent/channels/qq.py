from __future__ import annotations

from wusaki_agent.channels.base import ChannelAdapter, ChannelMessage


class QqChannelAdapter(ChannelAdapter):
    name = "qq"

    def normalize_user_id(self, raw_user_id: str) -> str:
        cleaned = raw_user_id.strip()
        return cleaned.removeprefix("qq:")

    def send(self, message: ChannelMessage) -> str:
        user_id = self.normalize_user_id(message.user_id)
        if message.kind == "passive":
            return f"[qq-placeholder] {user_id}: {message.text}"
        return f"[qq-placeholder:{message.kind}] {user_id}: {message.text}"
