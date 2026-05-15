# Wusaki Agent Architecture Seed

This repository starts from a phase-one seed architecture rather than a finished implementation.

## Module Map

- `wusaki_agent.cli`
  - local entrypoint
  - workspace initialization
  - feature status inspection
  - skeleton verification hooks
- `wusaki_agent.config`
  - settings loading
  - runtime path resolution
- `wusaki_agent.workspace`
  - workspace bootstrap
  - runtime file and directory contracts
- `wusaki_agent.memory`
  - markdown memory file contracts
  - future vector memory compatibility layer
- `wusaki_agent.proactive`
  - proactive tick model and future orchestration
- `wusaki_agent.drift`
  - SKILL-based idle task discovery
- `wusaki_agent.channels`
  - channel abstraction for QQ and Telegram
- `wusaki_agent.observability`
  - logging and decision trace output

## Immediate Implementation Order

1. Passive reply pipeline and runtime models
2. Markdown memory consolidation and retrieval
3. Proactive tick lifecycle and MCP source abstraction
4. Drift execution contract
5. Channel adapters and deeper CLI workflows

