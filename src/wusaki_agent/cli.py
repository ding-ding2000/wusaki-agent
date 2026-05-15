from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from wusaki_agent.agent.passive import run_passive_turn
from wusaki_agent.config import Settings, ensure_default_settings
from wusaki_agent.drift.skills import discover_skills
from wusaki_agent.feature_registry import FeatureRegistry
from wusaki_agent.json_io import read_json, write_json
from wusaki_agent.observability.logging import configure_logging
from wusaki_agent.paths import default_workspace_path, feature_list_path, project_root
from wusaki_agent.proactive.tick import dry_run_tick
from wusaki_agent.runtime.models import TurnEnvelope
from wusaki_agent.workspace.bootstrap import init_workspace, verify_workspace

app = typer.Typer(help="Wusaki agent bootstrap CLI")
console = Console()
DEFAULT_WORKSPACE = default_workspace_path()
DEFAULT_SETTINGS_PATH = project_root() / "config" / "settings.local.toml"


def main() -> None:
    app()


@app.command("show-features")
def show_features() -> None:
    registry = FeatureRegistry(feature_list_path())
    payload = registry.load()

    table = Table(title="Wusaki Feature List")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Milestone")
    table.add_column("Priority")
    for feature in payload.get("features", []):
        table.add_row(
            feature["id"],
            feature["title"],
            feature["status"],
            feature["milestone"],
            feature["priority"],
        )
    console.print(table)


@app.command("round-status")
def round_status() -> None:
    project = project_root()
    feature_state = read_json(project / "feature_list.json")
    progress_state = read_json(project / "progress_journal.json")
    handoff_path = project / "handoff" / "HANDOFF.md"

    table = Table(title="Relay Round Status")
    table.add_column("Key")
    table.add_column("Value")
    table.add_row("Mode", feature_state.get("execution_policy", {}).get("mode", "unknown"))
    table.add_row("Active Round", str(progress_state.get("active_round")))
    table.add_row("Rounds Logged", str(len(progress_state.get("rounds", []))))
    table.add_row("Handoff Log", str(handoff_path))
    console.print(table)


@app.command("round-start")
def round_start(
    round_id: str = typer.Option(..., "--round-id", help="Round id, e.g. R003."),
    task_id: str = typer.Option(..., "--task-id", help="Feature task id, e.g. F007."),
    summary: str = typer.Option(..., "--summary", help="Short summary for this round."),
) -> None:
    project = project_root()
    progress_path = project / "progress_journal.json"
    progress_state = read_json(progress_path)

    if progress_state.get("active_round"):
        raise typer.BadParameter(
            "An active round already exists. Finish it before starting a new one."
        )

    rounds = progress_state.setdefault("rounds", [])
    existing_ids = {item.get("round_id") for item in rounds}
    if round_id in existing_ids:
        raise typer.BadParameter(f"Round id already exists: {round_id}")

    round_entry: dict[str, Any] = {
        "round_id": round_id,
        "task_id": task_id,
        "status": "in_progress",
        "summary": summary,
        "verification": [],
        "commit": None,
        "completed_on": None,
    }

    progress_state["active_round"] = round_id
    rounds.append(round_entry)
    write_json(progress_path, progress_state)
    console.print(f"Started round: {round_id} ({task_id})")


@app.command("round-finish")
def round_finish(
    verification: list[str] = typer.Option(  # noqa: B008
        ...,
        "--verification",
        help="Deterministic verification command. Pass multiple times if needed.",
    ),
    completed_on: str = typer.Option(
        ...,
        "--completed-on",
        help="Completion date, e.g. 2026-05-15.",
    ),
    commit: str | None = typer.Option(
        None,
        "--commit",
        help="Optional commit hash to attach while finishing the round.",
    ),
) -> None:
    project = project_root()
    progress_path = project / "progress_journal.json"
    progress_state = read_json(progress_path)

    active_round = progress_state.get("active_round")
    if not active_round:
        raise typer.BadParameter("No active round found. Start one with `round-start` first.")
    if not verification:
        raise typer.BadParameter("At least one deterministic verification command is required.")

    rounds = progress_state.get("rounds", [])
    target = None
    for item in rounds:
        if item.get("round_id") == active_round:
            target = item
            break
    if target is None:
        raise typer.BadParameter(f"Active round id not found in rounds: {active_round}")

    target["status"] = "done"
    target["verification"] = verification
    target["completed_on"] = completed_on
    if commit is not None:
        commit_hash = commit.strip()
        if not commit_hash:
            raise typer.BadParameter("Commit hash must not be empty when provided.")
        target["commit"] = commit_hash
    progress_state["active_round"] = None
    write_json(progress_path, progress_state)
    console.print(f"Finished round: {active_round}")


@app.command("round-commit")
def round_commit(
    round_id: str = typer.Option(..., "--round-id", help="Round id, e.g. R004."),
    commit: str = typer.Option(..., "--commit", help="Commit hash, e.g. 3169b45."),
) -> None:
    project = project_root()
    progress_path = project / "progress_journal.json"
    progress_state = read_json(progress_path)

    commit_hash = commit.strip()
    if not commit_hash:
        raise typer.BadParameter("Commit hash must not be empty.")

    rounds = progress_state.get("rounds", [])
    target = None
    for item in rounds:
        if item.get("round_id") == round_id:
            target = item
            break
    if target is None:
        raise typer.BadParameter(f"Round id not found: {round_id}")
    if target.get("status") != "done":
        raise typer.BadParameter(f"Round must be done before writing commit: {round_id}")

    target["commit"] = commit_hash
    write_json(progress_path, progress_state)
    console.print(f"Attached commit for round: {round_id}")


@app.command("init-workspace")
def init_workspace_cmd(
    workspace: Path = typer.Option(DEFAULT_WORKSPACE, help="Workspace directory."),  # noqa: B008
) -> None:
    summary = init_workspace(workspace)
    console.print(f"Initialized workspace: {summary.workspace}")
    console.print(f"Created: {len(summary.created)}")
    console.print(f"Skipped: {len(summary.skipped)}")


@app.command("status")
def status(
    settings_path: Path = typer.Option(  # noqa: B008
        DEFAULT_SETTINGS_PATH,
        help="Path to the local settings file.",
    ),
) -> None:
    ensure_default_settings(settings_path)
    settings = Settings.from_file(settings_path)
    workspace = settings.workspace_path
    registry = FeatureRegistry(feature_list_path())

    table = Table(title="Wusaki Status")
    table.add_column("Key")
    table.add_column("Value")
    table.add_row("Project Root", str(project_root()))
    table.add_row("Workspace", str(workspace))
    table.add_row("Feature Counts", str(registry.counts()))
    table.add_row("Proactive Enabled", str(settings.proactive.enabled))
    table.add_row("Drift Enabled", str(settings.drift.enabled))
    console.print(table)


@app.command("verify-skeleton")
def verify_skeleton(
    workspace: Path = typer.Option(DEFAULT_WORKSPACE, help="Workspace directory."),  # noqa: B008
) -> None:
    results = verify_workspace(workspace)
    failed = [item for item in results if not item.ok]
    table = Table(title="Skeleton Verification")
    table.add_column("Path")
    table.add_column("Status")
    table.add_column("Detail")
    for item in results:
        table.add_row(item.name, "ok" if item.ok else "missing", item.detail)
    console.print(table)
    if failed:
        raise typer.Exit(code=1)


@app.command("drift-scan")
def drift_scan(
    workspace: Path = typer.Option(DEFAULT_WORKSPACE, help="Workspace directory."),  # noqa: B008
) -> None:
    skills = discover_skills(workspace / "drift" / "skills")
    table = Table(title="Drift Skills")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Path")
    for skill in skills:
        table.add_row(skill.name, skill.description, str(skill.path))
    console.print(table)


@app.command("proactive-tick")
def proactive_tick(dry_run: bool = typer.Option(True, help="Run in dry-run mode.")) -> None:
    if not dry_run:
        raise typer.BadParameter("Only dry-run mode is available in the current scaffold.")
    decision = dry_run_tick()
    console.print(f"Decision: {decision.decision}")
    console.print(f"Reason: {decision.reason}")


@app.command("passive-turn")
def passive_turn(
    channel: str = typer.Option(..., "--channel", help="Channel name, e.g. cli."),
    user: str = typer.Option(..., "--user", help="User id."),
    message: str = typer.Option(..., "--message", help="Incoming message text."),
    workspace: Path = typer.Option(DEFAULT_WORKSPACE, help="Workspace directory."),  # noqa: B008
    dry_run: bool = typer.Option(False, "--dry-run", help="Run without writing turn files."),
) -> None:
    turn = TurnEnvelope(
        channel=channel,
        user_id=user,
        message=message,
        created_at=datetime.utcnow(),
    )
    result = run_passive_turn(turn, workspace, persist=not dry_run)
    console.print(f"Response: {result.response}")
    if dry_run:
        console.print("Mode: dry-run (no files written)")
    else:
        console.print(f"Turn log: {workspace / 'state' / 'turns.log'}")


@app.callback()
def common(log_level: str = typer.Option("INFO", help="Log level.")) -> None:
    configure_logging(log_level)
