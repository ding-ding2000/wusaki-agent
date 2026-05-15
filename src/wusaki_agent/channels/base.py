from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MessageKind = Literal["passive", "proactive", "drift"]

@dataclass(slots=True)
class ChannelMessage:
    channel: str
    user_id: str
    text: str
    kind: MessageKind = "passive"


class ChannelAdapter:
    name: str = "base"

    def normalize_user_id(self, raw_user_id: str) -> str:
        return raw_user_id.strip()

    def send(self, message: ChannelMessage) -> str:
        raise NotImplementedError


class CliChannelAdapter(ChannelAdapter):
    name = "cli"

    def send(self, message: ChannelMessage) -> str:
        user_id = self.normalize_user_id(message.user_id)
        if message.kind == "passive":
            return f"[cli-placeholder] {user_id}: 收到消息：{message.text}"
        return f"[cli-placeholder:{message.kind}] {user_id}: {message.text}"


def build_channel_adapters() -> dict[str, ChannelAdapter]:
    from wusaki_agent.channels.qq import QqChannelAdapter
    from wusaki_agent.channels.telegram import TelegramChannelAdapter

    return {
        "qq": QqChannelAdapter(),
        "telegram": TelegramChannelAdapter(),
        "cli": CliChannelAdapter(),
    }
