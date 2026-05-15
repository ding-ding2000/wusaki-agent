from __future__ import annotations

from pathlib import Path

from wusaki_agent.drift.skills import discover_skills, run_drift_round
from wusaki_agent.json_io import read_json
from wusaki_agent.workspace.bootstrap import init_workspace


def test_discover_skills_parses_work_files_and_message_limit(tmp_path: Path) -> None:
    workspace = tmp_path / ".wusaki"
    init_workspace(workspace)

    skills = discover_skills(workspace / "drift" / "skills")
    assert len(skills) == 3
    assert any(skill.work_files for skill in skills)
    assert all(skill.max_messages in {0, 1} for skill in skills)


def test_drift_round_runs_and_records_result(tmp_path: Path) -> None:
    workspace = tmp_path / ".wusaki"
    init_workspace(workspace)

    result = run_drift_round(workspace, skill_name="memory-audit")
    assert result.skill_name == "memory-audit"
    assert result.status == "completed"
    assert result.message_sent is True
    assert result.message_preview is not None

    drift_state = read_json(workspace / "drift" / "drift.json")
    recent_runs = drift_state["recent_runs"]
    assert len(recent_runs) == 1
    assert recent_runs[0]["skill"] == "memory-audit"
    assert recent_runs[0]["status"] == "completed"
    assert recent_runs[0]["message_sent"] is True


def test_drift_round_silent_skill_respects_no_message(tmp_path: Path) -> None:
    workspace = tmp_path / ".wusaki"
    init_workspace(workspace)

    result = run_drift_round(workspace, skill_name="backlog-tidy")
    assert result.skill_name == "backlog-tidy"
    assert result.message_sent is False
    assert result.message_preview is None
