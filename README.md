# wusaki-agent

`wusaki-agent` is a phase-one implementation scaffold for a companion agent that supports:

- passive reply turns
- markdown and vector memory
- proactive polling and push decisions
- drift idle tasks
- multi-channel delivery
- local CLI-driven development

The current repository is intentionally initialized as a delivery-oriented skeleton:

- `docs/PRD.md` keeps the product baseline
- `feature_list.json` tracks coarse-grained executable features
- `src/wusaki_agent/` contains the application skeleton
- `tests/` contains bootstrap verification tests
- `.wusaki/` is the default local runtime workspace created by the CLI

## Quickstart

```bash
uv sync
uv run wusaki-agent init-workspace
uv run wusaki-agent status
uv run pytest
```

## First Commands

```bash
uv run wusaki-agent show-features
uv run wusaki-agent init-workspace --workspace .wusaki
uv run wusaki-agent verify-skeleton
```

## Current Scope

This initialization focuses on:

- defining the phase-one feature backlog
- creating a verifiable project skeleton
- standardizing workspace and runtime conventions
- preparing the repository for iterative implementation loops

