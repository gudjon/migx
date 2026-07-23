---
id: codex-cli-2026-07-23-001-knowledge-governance-ssot-charter
owner: codex-cli
status: closed
created: "2026-07-23"
created_utc: "2026-07-23T08:21:17Z"
expires_utc: "2026-07-23T20:21:17Z"
subject: "knowledge-governance-ssot-charter"
paths: "kanban/knowledge/AGENTS.md, kanban/AGENTS.md, .claude/rules/single-source-of-truth.md"
branch: "main"
commit: "b8f95d3"
---

# knowledge-governance-ssot-charter

## Intent
Make this active lane visible before another agent edits the same surface.

## Scope
- `kanban/knowledge/AGENTS.md`
- `kanban/AGENTS.md`
- `.claude/rules/single-source-of-truth.md`

## Release
Run `./kanban/scripts/migx-fed release --id codex-cli-2026-07-23-001-knowledge-governance-ssot-charter --by codex-cli --resolution "..."` when the lane is done.

## Resolution
Released by codex-cli at 2026-07-23T08:30:47Z.

Added kanban/knowledge/AGENTS.md as the technical/product research SSoT charter; updated kanban/AGENTS.md and .claude/rules/single-source-of-truth.md routing tables. Verified with just kanban-lint and migx-fed audit --strict.
