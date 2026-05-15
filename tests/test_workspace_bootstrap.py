from pathlib import Path

from wusaki_agent.drift.skills import discover_skills
from wusaki_agent.workspace.bootstrap import init_workspace, verify_workspace


def test_workspace_init_and_verify(tmp_path: Path) -> None:
    workspace = tmp_path / ".wusaki"

    summary = init_workspace(workspace)
    checks = verify_workspace(workspace)
    skills = discover_skills(workspace / "drift" / "skills")

    assert summary.created
    assert all(item.ok for item in checks)
    assert len(skills) == 3
