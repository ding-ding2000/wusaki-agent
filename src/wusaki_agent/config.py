from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from wusaki_agent.paths import default_settings_template_path, default_workspace_path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


class AppSection(BaseModel):
    name: str = "wusaki-agent"
    workspace_dir: str = ".wusaki"
    log_level: str = "INFO"


class LlmSection(BaseModel):
    provider: str = "openai"
    model: str = "gpt-5.4-mini"
    api_key: str = ""


class MemorySection(BaseModel):
    enabled: bool = True
    vector_backend: str = "stub"


class QqChannelSection(BaseModel):
    enabled: bool = False
    bot_token: str = ""


class TelegramChannelSection(BaseModel):
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""


class ChannelsSection(BaseModel):
    qq: QqChannelSection = Field(default_factory=QqChannelSection)
    telegram: TelegramChannelSection = Field(default_factory=TelegramChannelSection)


class ProactiveSection(BaseModel):
    enabled: bool = False
    profile: Literal["daily", "quiet", "dev_verify"] = "daily"
    cooldown_minutes: int = 120
    max_messages_per_hour: int = 1


class DriftSection(BaseModel):
    enabled: bool = True
    min_interval_minutes: int = 60


class Settings(BaseModel):
    app: AppSection = Field(default_factory=AppSection)
    llm: LlmSection = Field(default_factory=LlmSection)
    memory: MemorySection = Field(default_factory=MemorySection)
    channels: ChannelsSection = Field(default_factory=ChannelsSection)
    proactive: ProactiveSection = Field(default_factory=ProactiveSection)
    drift: DriftSection = Field(default_factory=DriftSection)

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
        return cls.model_validate(payload)

    @property
    def workspace_path(self) -> Path:
        raw = Path(self.app.workspace_dir)
        if raw.is_absolute():
            return raw
        return default_workspace_path() if raw == Path(".wusaki") else Path.cwd() / raw


def ensure_default_settings(path: Path) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_settings_template_path().read_text(encoding="utf-8"), encoding="utf-8")
    return path
