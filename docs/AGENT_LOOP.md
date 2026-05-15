# Coding Agent Relay Loop

This project uses a strict relay loop for implementation rounds.

## Inputs Allowed Per Round

Each coding agent must only read:

1. `feature_list.json`
2. `progress_journal.json`
3. `handoff/HANDOFF.md`
4. repository code and tests

No hidden context is assumed across rounds.

## One-Round Rules

1. Pick exactly one explicit small task.
2. Implement only that task.
3. Run deterministic verification (`pytest`, `ruff check`, or type checks).
4. Only if verification passes:
   - update `feature_list.json` status fields
   - append one handoff record
   - commit code
5. End the round; next agent continues from files only.

## Required Handoff Record

Each round must append one entry to `handoff/HANDOFF.md` containing:

- round id
- task id
- what changed
- exact verification commands
- pass/fail result
- next suggested task

## Deterministic Verification

Preferred commands:

```bash
uv run ruff check .
uv run pytest
```

If a task has narrower scope, a smaller deterministic check is allowed, but the command must be recorded.

