from __future__ import annotations

from pathlib import Path

MARKDOWN_MEMORY_FILES: tuple[str, ...] = (
    "MEMORY.md",
    "SELF.md",
    "HISTORY.md",
    "RECENT_CONTEXT.md",
    "PENDING.md",
)


def memory_file_paths(memory_dir: Path) -> list[Path]:
    return [memory_dir / name for name in MARKDOWN_MEMORY_FILES]

