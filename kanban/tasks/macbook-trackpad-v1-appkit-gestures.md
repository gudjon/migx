---
id: macbook-trackpad-v1-appkit-gestures
type: task
title: "MacBook trackpad v1 — AppKit gestures behind KEYMAP twins (TUI-first safe)"
status: open
owner: gudjon
priority: medium
initiative: initiative-ui-modernization
parent_dossier: null
depends_on:
  - nextgen-music-management-mode
  - ui-migration-judge-rulebook-inventory
authored_by: grok-signal
authored_kind: agent
triggered_by: "2026-08-07 trackpad mode language signal + KEYMAP Trackpad column;
  TUI-first product routing (ADR-008 / Codex strategy handoff)"
created: "2026-08-07"
lastUpdated: "2026-08-07"
acceptance: |
  (1) KEYMAP Trackpad column remains SSoT; every non-empty Trackpad cell has a Key
  twin (lint/judge). (2) v1 implements only three accelerators via AppKit (not
  QTouchEvent): pinch waveform zoom, 2-finger momentum list scroll, ⌥+2-finger
  mode cycle. (3) Play/cue/sync/hotcue/crossfader/gain stay Trackpad-unbound.
  (4) Audio callback never sees gesture I/O. (5) Pure curses TUI does not claim
  custom multitouch — terminal inherits OS scroll; mode switch stays keys until
  a native host window exists. Verified on M4 MacBook with Mission Control
  3-finger on and off.
---

# MacBook trackpad v1 — AppKit gestures

## Why this task exists

Signal + KEYMAP design landed; implementers need a **bounded backlog item** that
does not reopen sealed dossiers and does not collide with migx-cli / analyzer waves.

**SSoT language:**  
`kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md`  
**KEYMAP:** `res/design/KEYMAP.md` (Trackpad column, `†` v1 / `‡` v2)  
**Mail:** `grok-signal-claude-code-2026-08-07-002-macbook-trackpad-mode-language-v1-keymap-landed`

## TUI-first routing (do not mis-implement)

Product spine is **CLI core + TUI-first human adapter** (`ADR-008`). Codex published
canonical routing (on `codex/sync`, sync when merged):

- `kanban/knowledge/tui-first-agentic-dj-workstation.md`
- `kanban/knowledge/arcflow-tui-agentic-dj-integration.md`

| Surface | Trackpad reality |
| --- | --- |
| **`migx-tui` (stdlib curses)** | No custom AppKit multitouch. 2-finger scroll is the **terminal emulator’s**. Mode cycle = KEYMAP keys (`⌘1–3`, `Tab`). Do not fake gestures in curses. |
| **Native graphical host** (Qt/QML shell, future adapter) | **AppKit gesture bridge** (magnify / scroll phase / optional swipe) → same command IDs as KEYMAP. |
| **Agents / CLI** | No trackpad; same commands via `migx …` / `--json`. |

v1 AppKit work attaches to a **native window host**, not to `curses` redraw loops.

## v1 scope (three behaviors only)

| # | Gesture | Action | Key twin |
| --- | --- | --- | --- |
| 1 | Pinch over waveform | Zoom | zoom keys when declared (`⌘+`/`⌘-` candidates) |
| 2 | 2-finger fling | List scroll + momentum | `↑` / `↓` |
| 3 | `⌥`+2-finger horizontal | Mode cycle PERFORM↔ARRANGE↔LIBRARY | `Tab` / `⇧Tab` / `⌘1–3` |

## Explicit non-goals

- Re-enable `WA_AcceptTouchEvents` on Apple (`wwidget.cpp` / QTBUG-103935)
- Trackpad play / cue / sync / hotcue / crossfader / gain
- Camera / hand-count Automix
- 3-finger mode cycle as sole path (OS may steal Mission Control)
- ArcFlow on RT path; gesture I/O in engine callback
- Expanding `‡` gestures before v1 is dogfooded

## Implementation notes

1. Prefer AppKit `NSResponder` magnify + scroll `phase`/`momentumPhase`; thin ObjC++ bridge into Qt host if needed.  
2. Commit mutations on gesture **phase Ended**; handle **Cancelled**.  
3. Map to **command spine** (ADR-008) — never gesture-only semantics.  
4. Manual matrix: System Settings → Trackpad → Mission Control 3-finger **on** and **off**.  
5. Codex: Trackpad↔Key twin lint (`grok-signal-codex-cli-2026-08-07-001-keymap-trackpad-column-lint-twins`).

## Owner / DRI

- **Design language:** grok-signal (signal sealed for v1 map; enrich only)  
- **Implement:** claude-code when UI host wave is free  
- **Verify:** codex-cli (KEYMAP lint + no RT path)

## Related

- `kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md`
- `res/design/KEYMAP.md`
- `kanban/tasks/nextgen-music-management-mode.md` (mode switch semantics)
- `kanban/tasks/ui-migration-judge-rulebook-inventory.md`
