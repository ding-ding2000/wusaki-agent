from __future__ import annotations

from pathlib import Path

import pytest
import typer

from wusaki_agent import cli
from wusaki_agent.json_io import read_json, write_json


@pytest.fixture()
def temp_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    project = tmp_path / "repo"
    project.mkdir(parents=True, exist_ok=True)
    handoff_dir = project / "handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    (handoff_dir / "HANDOFF.md").write_text("# Handoff\n", encoding="utf-8")

    write_json(
        project / "progress_journal.json",
        {
            "schema_version": "1.0",
            "project": "wusaki-agent",
            "active_round": None,
            "rounds": [],
        },
    )
    write_json(
        project / "feature_list.json",
        {
            "execution_policy": {"mode": "single_task_relay"},
            "features": [],
        },
    )
    monkeypatch.setattr(cli, "project_root", lambda: project)
    return project


def test_round_start_and_finish_and_commit_flow(temp_project: Path) -> None:
    cli.round_start(round_id="R100", task_id="F007", summary="test")

    state = read_json(temp_project / "progress_journal.json")
    assert state["active_round"] == "R100"
    assert state["rounds"][0]["status"] == "in_progress"

    cli.round_finish(
        verification=[".venv/bin/ruff check .", ".venv/bin/pytest"],
        completed_on="2026-05-15",
        commit="abc1234",
    )
    state = read_json(temp_project / "progress_journal.json")
    assert state["active_round"] is None
    assert state["rounds"][0]["status"] == "done"
    assert state["rounds"][0]["commit"] == "abc1234"

    cli.round_commit(round_id="R100", commit="def5678")
    state = read_json(temp_project / "progress_journal.json")
    assert state["rounds"][0]["commit"] == "def5678"


def test_round_start_rejects_duplicate_id(temp_project: Path) -> None:
    cli.round_start(round_id="R200", task_id="F007", summary="first")
    cli.round_finish(verification=[".venv/bin/pytest"], completed_on="2026-05-15", commit=None)

    with pytest.raises(typer.BadParameter):
        cli.round_start(round_id="R200", task_id="F007", summary="duplicate")


def test_round_finish_requires_active_round(temp_project: Path) -> None:
    with pytest.raises(typer.BadParameter):
        cli.round_finish(verification=[".venv/bin/pytest"], completed_on="2026-05-15", commit=None)


def test_round_commit_requires_done_round(temp_project: Path) -> None:
    cli.round_start(round_id="R300", task_id="F007", summary="in progress")
    with pytest.raises(typer.BadParameter):
        cli.round_commit(round_id="R300", commit="abc")
