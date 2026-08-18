---
id: grok-signal-2026-08-18-001-domain-vs-engine-partition
owner: grok-signal
status: closed
created: "2026-08-18"
created_utc: "2026-08-18T18:43:04Z"
expires_utc: "2026-08-19T06:43:04Z"
subject: "domain-vs-engine-partition"
paths: "kanban/architecture/decisions, kanban/architecture/ddd/boundaries, kanban/architecture/ddd/context-map.md, kanban/architecture/README.md, kanban/architecture/ddd/bounded-contexts/arch-engine-realtime.md, kanban/architecture/ddd/bounded-contexts/arch-mixer-decks.md, kanban/architecture/decisions/ADR-009-cli-tui-implementation-language.md"
branch: "main"
commit: "32333df"
---

# domain-vs-engine-partition

## Intent
Make this active lane visible before another agent edits the same surface.

## Scope
- `kanban/architecture/decisions`
- `kanban/architecture/ddd/boundaries`
- `kanban/architecture/ddd/context-map.md`
- `kanban/architecture/README.md`
- `kanban/architecture/ddd/bounded-contexts/arch-engine-realtime.md`
- `kanban/architecture/ddd/bounded-contexts/arch-mixer-decks.md`
- `kanban/architecture/decisions/ADR-009-cli-tui-implementation-language.md`

## Release
Run `./kanban/scripts/migx-fed release --id grok-signal-2026-08-18-001-domain-vs-engine-partition --by grok-signal --resolution "..."` when the lane is done.

## Resolution
Released by grok-signal at 2026-08-18T18:45:01Z.

ADR-010 + domain-to-engine seam landed on main
