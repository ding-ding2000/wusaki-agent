from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_workspace_path() -> Path:
    return project_root() / ".wusaki"


def feature_list_path() -> Path:
    return project_root() / "feature_list.json"


def default_settings_template_path() -> Path:
    return project_root() / "config" / "settings.example.toml"

