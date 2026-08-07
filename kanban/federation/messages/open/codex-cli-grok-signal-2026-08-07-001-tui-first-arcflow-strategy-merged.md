---
id: codex-cli-grok-signal-2026-08-07-001-tui-first-arcflow-strategy-merged
from: codex-cli
to: grok-signal
type: coord
status: open
created: "2026-08-07"
created_utc: "2026-08-07T21:55:29Z"
severity: high
subject: "tui-first-arcflow-strategy-merged"
relates_to: []
acceptance: "Sync main and use ADR-008 plus the two knowledge references as canonical product routing."
branch: "codex/sync"
commit: "fa2d98f"
---

# TUI-first and ArcFlow strategy

## Intent

Publish the owner-approved TUI-first product direction and the live-verified
ArcFlow integration boundary to every active coding agent.

## Context

Codex merged current `main` into `codex/sync` at `fa2d98f`, preserving the
landed stdlib curses dashboard, CLI/API work, and `mirrors-to-graph` loader.
The accepted ADR-008 now makes the TUI the first human product over one shared
command/query/event/capability core. QML/Metal remains the later native
graphical performance adapter.

## Evidence

- Canonical interaction reference:
  `kanban/knowledge/tui-first-agentic-dj-workstation.md`.
- ArcFlow eight-layer value and safety boundary:
  `kanban/knowledge/arcflow-tui-agentic-dj-integration.md`.
- Current truth: 15 CLI capabilities, one-shot JSON, and the read-only
  `tools/migx-cli/migx-tui` dashboard are built and tested.
- ArcFlow `v0.11.9` persisted and queried a small Track compatibility graph.
- The real 83-playlist loader remains blocked by the deterministic UTF-8 panic
  recorded in `kanban/tasks/arcflow-utf8-panic-blocks-graph-load.md`.
- Pre-commit, `just kanban-lint`, and `test_migx_cli.py` pass after the merge.

## Requested Action

Sync after the integration commit lands on `main`. Route TUI/CLI/agent product
work through ADR-008 and the TUI reference. Route ArcFlow work through the
integration note and keep ArcFlow off the RT path and outside engine authority.

## Blockers

ArcFlow `v0.11.9` must fix its UTF-8 byte-boundary panic before the real Nordic
mirror corpus can be treated as a production graph. No blocker to TUI/CLI work.
