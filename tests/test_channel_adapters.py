from __future__ import annotations

from wusaki_agent.channels.base import ChannelMessage, build_channel_adapters


def test_channel_registry_contains_qq_telegram_and_cli() -> None:
    adapters = build_channel_adapters()
    assert set(adapters.keys()) == {"qq", "telegram", "cli"}


def test_qq_and_telegram_share_same_message_contract() -> None:
    adapters = build_channel_adapters()
    qq = adapters["qq"]
    tg = adapters["telegram"]

    qq_text = qq.send(ChannelMessage(channel="qq", user_id="qq:1001", text="hello", kind="passive"))
    tg_text = tg.send(
        ChannelMessage(channel="telegram", user_id="tg:2002", text="hello", kind="passive")
    )

    assert qq_text == "[qq-placeholder] 1001: hello"
    assert tg_text == "[telegram-placeholder] 2002: hello"


def test_adapters_support_proactive_and_drift_message_paths() -> None:
    adapters = build_channel_adapters()
    qq = adapters["qq"]
    tg = adapters["telegram"]
    cli = adapters["cli"]

    qq_proactive = qq.send(
        ChannelMessage(channel="qq", user_id="qq:1001", text="proactive ping", kind="proactive")
    )
    tg_drift = tg.send(
        ChannelMessage(channel="telegram", user_id="tg:2002", text="drift ping", kind="drift")
    )
    cli_proactive = cli.send(
        ChannelMessage(channel="cli", user_id="dev", text="local ping", kind="proactive")
    )

    assert qq_proactive == "[qq-placeholder:proactive] 1001: proactive ping"
    assert tg_drift == "[telegram-placeholder:drift] 2002: drift ping"
    assert cli_proactive == "[cli-placeholder:proactive] dev: local ping"
