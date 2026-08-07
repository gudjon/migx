---
id: grok-signal-claude-code-2026-08-07-003-tui-first-field-deltas-p0-status-help-p1-compose
from: grok-signal
to: claude-code
type: signal-handoff
status: open
created: "2026-08-07"
created_utc: "2026-08-07T22:58:34Z"
severity: medium
subject: "tui-first-field-deltas-p0-status-help-p1-compose"
relates_to: []
acceptance: "Claude acks and either schedules P0 status+help (then P1 composer/stage) or defers with reason; does not add gesture code to curses."
branch: "feat/migx-cli-spotify-mirror"
commit: "ec9b182"
---

## Intent

Hand Claude a field-validated backlog for the next `migx-tui` waves after the
current Deck/KEYMAP dirt lands — without Grok editing `tui.py`.

## Context

Codex TUI-first routing + Claude shipping modes (Library/Arrange/Prep/Track/Deck).
Trackpad design is closed (native host only). New field brief:
`kanban/federation/signal/2026-08-07-tui-first-dj-workstation-field.md`

## Evidence

- X: TUI-as-product, CLI essence, agent non-blocking status lines, termixer adjacent
- Live: pure snapshot TUI, capabilities manifest, heatmap/Deck transition already landed
- Anti-patterns: Automix, glass faders in curses, AppKit multitouch in TTY

## Requested Action

1. When free of current dirty KEYMAP/tui wave: ship **P0** footer status line +
   non-blocking `?` help overlay (from brief §3).
2. **P1** composer accepting real command IDs; stage-before-apply for Prep bulk.
3. Do **not** implement AppKit gestures in curses; see trackpad task for native host.
4. Keep every new action on the command spine (ADR-008).

## Blockers

None. Leave Grok off `tools/migx-cli/**` while you own the TUI dirt.
