from __future__ import annotations

from pathlib import Path

TEXT_TEMPLATES: dict[str, str] = {
    "memory/MEMORY.md": "# Long-term Memory\n",
    "memory/SELF.md": "# Self Model\n\n- The agent is a long-term companion assistant.\n",
    "memory/HISTORY.md": "# Timeline History\n",
    "memory/RECENT_CONTEXT.md": (
        "# Recent Context\n\n## Compression\n\n## Ongoing Threads\n\n## Recent Turns\n"
    ),
    "memory/PENDING.md": "# Pending Facts\n",
    "PROACTIVE_CONTEXT.md": (
        "# Proactive Context\n\n## Rules\n\n"
        "- Add allowlist, blocklist and routing rules here.\n"
    ),
    "drift/drift_note.md": "# Drift Notes\n",
    "drift/skills/memory-audit/SKILL.md": """---
name: memory-audit
description: Audit one memory candidate and record the result.
---

## 目标
抽检一条长期记忆候选并更新审计记录。

## 工作文件
- `drift/skills/memory-audit/state.json`
- `drift/skills/memory-audit/audited.md`

## 工作流程
1. 读取 `audited.md` 和 `state.json`。
2. 选择下一条待审计记忆。
3. 如果存在高置信问题，允许最多发一条消息；否则静默结束。
4. 写回状态并结束本轮。
""",
    "drift/skills/profile-gap/SKILL.md": """---
name: profile-gap
description: Maintain a lightweight queue of profile questions.
---

## 目标
补足用户画像中的轻量生活化空白。

## 工作文件
- `drift/skills/profile-gap/state.json`
- `drift/skills/profile-gap/queue.md`

## 工作流程
1. 读取 `queue.md`。
2. 如果队列为空，补充 5 个自然问题候选。
3. 如需触达用户，最多发一条消息。
4. 更新状态并结束本轮。
""",
    "drift/skills/backlog-tidy/SKILL.md": """---
name: backlog-tidy
description: Keep the execution backlog tidy without messaging the user.
---

## 目标
整理执行 backlog 并记录阶段停滞点。

## 工作文件
- `drift/skills/backlog-tidy/state.json`
- `drift/skills/backlog-tidy/backlog.md`

## 工作流程
1. 读取 backlog 相关文件。
2. 归并重复事项，标出阻塞项。
3. 静默写回结果并结束本轮。
""",
    "drift/skills/memory-audit/audited.md": "# Audited Memory IDs\n",
    "drift/skills/profile-gap/queue.md": "# Question Queue\n",
    "drift/skills/backlog-tidy/backlog.md": "# Drift Backlog\n",
}

JSON_TEMPLATES: dict[str, object] = {
    "drift/drift.json": {"recent_runs": []},
    "proactive_sources.json": {"sources": []},
    "mcp_servers.json": {"servers": {}},
    "schedules.json": [],
    "state/runtime.json": {"last_bootstrap_at": None},
    "drift/skills/memory-audit/state.json": {"last_run_at": None, "last_result": None},
    "drift/skills/profile-gap/state.json": {"last_run_at": None, "last_result": None},
    "drift/skills/backlog-tidy/state.json": {"last_run_at": None, "last_result": None},
}

DIRECTORIES: tuple[str, ...] = (
    "logs",
    "state",
    "memory",
    "channels",
    "drift",
    "drift/skills",
    "mcp",
)


def template_paths() -> list[Path]:
    return [Path(path) for path in [*TEXT_TEMPLATES.keys(), *JSON_TEMPLATES.keys(), *DIRECTORIES]]
