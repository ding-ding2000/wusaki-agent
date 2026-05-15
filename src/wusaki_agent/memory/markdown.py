from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MARKDOWN_MEMORY_FILES: tuple[str, ...] = (
    "MEMORY.md",
    "SELF.md",
    "HISTORY.md",
    "RECENT_CONTEXT.md",
    "PENDING.md",
)


def memory_file_paths(memory_dir: Path) -> list[Path]:
    return [memory_dir / name for name in MARKDOWN_MEMORY_FILES]


@dataclass(slots=True)
class ConsolidationResult:
    processed: int
    skipped: int
    history_appended: int
    pending_appended: int
    recent_context_updated: bool


def run_consolidation(workspace: Path, limit: int | None = None) -> ConsolidationResult:
    state_dir = workspace / "state"
    memory_dir = workspace / "memory"
    queue_path = state_dir / "postprocess_queue.jsonl"

    _ensure_memory_files(memory_dir)
    index = _load_index(state_dir / "consolidation_index.json")
    queue_items = _load_queue(queue_path)

    processed = 0
    skipped = 0
    history_appended = 0
    pending_appended = 0
    recent_context_updated = False
    used = 0

    for item in queue_items:
        if item.get("status") != "pending":
            continue
        turn_id = str(item.get("turn_id", "")).strip()
        if not turn_id:
            item["status"] = "skipped"
            skipped += 1
            continue
        if turn_id in index["processed_turn_ids"]:
            item["status"] = "done"
            skipped += 1
            continue

        artifact_path = workspace / "state" / item.get("artifact", "")
        if not artifact_path.exists():
            item["status"] = "skipped"
            skipped += 1
            continue
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        turn = artifact.get("turn", {})
        response = artifact.get("response", {})
        source_tag = f"source:{turn_id}"

        if _append_unique_line(
            memory_dir / "HISTORY.md",
            (
                f"- [{turn.get('created_at', '')}] 用户: {turn.get('message', '')} "
                f"| 回复: {response.get('text', '')} [{source_tag}]"
            ),
            marker=f"[{source_tag}]",
        ):
            history_appended += 1

        if _append_unique_line(
            memory_dir / "PENDING.md",
            f"- [requested_memory] 最近一轮用户消息: {turn.get('message', '')} [{source_tag}]",
            marker=f"[{source_tag}]",
        ):
            pending_appended += 1

        _update_recent_context(memory_dir / "RECENT_CONTEXT.md", turn, response)
        recent_context_updated = True
        index["processed_turn_ids"].append(turn_id)
        item["status"] = "done"
        processed += 1
        used += 1
        if limit is not None and used >= limit:
            break

    _save_index(state_dir / "consolidation_index.json", index)
    _save_queue(queue_path, queue_items)
    return ConsolidationResult(
        processed=processed,
        skipped=skipped,
        history_appended=history_appended,
        pending_appended=pending_appended,
        recent_context_updated=recent_context_updated,
    )


def _ensure_memory_files(memory_dir: Path) -> None:
    memory_dir.mkdir(parents=True, exist_ok=True)
    defaults = {
        "MEMORY.md": "# Long-term Memory\n",
        "SELF.md": "# Self Model\n",
        "HISTORY.md": "# Timeline History\n",
        "RECENT_CONTEXT.md": (
            "# Recent Context\n\n## Compression\n\n## Ongoing Threads\n\n## Recent Turns\n"
        ),
        "PENDING.md": "# Pending Facts\n",
    }
    for filename, content in defaults.items():
        path = memory_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _load_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"processed_turn_ids": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "processed_turn_ids" not in payload or not isinstance(payload["processed_turn_ids"], list):
        payload["processed_turn_ids"] = []
    return payload


def _save_index(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_queue(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    items: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        items.append(json.loads(text))
    return items


def _save_queue(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        for item in items:
            fp.write(json.dumps(item, ensure_ascii=False) + "\n")


def _append_unique_line(path: Path, line: str, marker: str) -> bool:
    content = path.read_text(encoding="utf-8")
    if marker in content:
        return False
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content + line + "\n", encoding="utf-8")
    return True


def _update_recent_context(path: Path, turn: dict[str, Any], response: dict[str, Any]) -> None:
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_line = f"- user: {turn.get('message', '')} | assistant: {response.get('text', '')}"
    if new_line in lines:
        return
    lines.append(new_line)
    # Keep only a small tail of recent turns to avoid unbounded growth.
    header: list[str] = []
    recent: list[str] = []
    for line in lines:
        if line.startswith("- user: "):
            recent.append(line)
        else:
            header.append(line)
    recent = recent[-10:]
    merged = header + recent
    path.write_text("\n".join(merged).rstrip() + "\n", encoding="utf-8")
