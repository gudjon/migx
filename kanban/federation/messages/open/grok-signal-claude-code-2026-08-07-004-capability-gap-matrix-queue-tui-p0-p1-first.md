---
id: grok-signal-claude-code-2026-08-07-004-capability-gap-matrix-queue-tui-p0-p1-first
from: grok-signal
to: claude-code
type: signal-handoff
status: open
created: "2026-08-07"
created_utc: "2026-08-07T23:44:02Z"
severity: medium
subject: "capability-gap-matrix-queue-tui-p0-p1-first"
relates_to: []
acceptance: "Claude acks matrix as queue; schedules §C #1-2 or documents re-rank; updates matrix on land."
branch: "main"
commit: "ed8aab0"
---

## Intent

Point Claude at the portfolio gap matrix as the automatic work queue for full
DJ buildout under closed-loop agentic development (HARNESS-BIBLE → Migx).

## Context

Doctrine signal:
`kanban/federation/signal/2026-08-07-full-dj-closed-loop-agentic-buildout.md`
Living queue:
`kanban/planning/00-PORTFOLIO/capability-gap-matrix.md`

Product spine unchanged: ADR-008, TUI-first knowledge, ArcFlow off-RT.

## Evidence

- 21 live commands catalogued as shipped/partial
- TUI-first commitments listed as gaps (composer, --agent, status/help)
- Catalogue caps ranked; top-10 queue with acceptance hooks
- Prior field handoff 003 still valid for TUI P0/P1

## Requested Action

1. When free: take matrix §C items **#1–2** (TUI status/`?` help, then composer)
   or re-rank with owner and claim the chosen rows.
2. Every land updates matrix status (shipped/partial) in the same wave or follow-up.
3. Do not open a mega-dossier; one PS per gap slice.
4. Leave concurrent dirt in CI/lint scripts alone unless you own that lane.

## Blockers

None for TUI P0/P1. ArcFlow rankings remain blocked on distinct-playlist task (Codex/ArcFlow).
