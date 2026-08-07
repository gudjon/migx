---
id: grok-signal-claude-code-2026-08-07-002-macbook-trackpad-mode-language-v1-keymap-landed
from: grok-signal
to: claude-code
type: signal-handoff
status: open
created: "2026-08-07"
created_utc: "2026-08-07T22:53:33Z"
severity: medium
subject: "macbook-trackpad-mode-language-v1-keymap-landed"
relates_to: []
acceptance: "Claude acks and either (a) schedules AppKit v1 three-gesture bridge behind KEYMAP twins, or (b) defers with named successor wave; does not re-enable QTouchEvent on macOS."
branch: "feat/migx-cli-spotify-mirror"
commit: "02db5ac"
---

## Intent

Hand Claude the MacBook trackpad mode language + KEYMAP Trackpad column so NextGen
modes get AppKit-native accelerators without re-enabling broken Qt touch, without
trackpad-as-glass-mixer, and without implementer collision on open engine waves.

## Context

ADR-006 = Apple Silicon / MacBook-first. NextGen PERFORM / ARRANGE / LIBRARY needs
one-gesture mode switch and spatial browse under cognitive load. Mixxx/Migx still
disables `WA_AcceptTouchEvents` on macOS (`wwidget.cpp` / QTBUG-103935).

Scout delivered:
- Full brief: `kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md`
- KEYMAP SSoT already has Trackpad column + rules: `res/design/KEYMAP.md`
- X field: trackpad loved for spatial UX; booth still controller-first; niche open

v1 ship set only (three behaviors):
1. Pinch-over-waveform → zoom (PERFORM)
2. 2-finger momentum scroll (ARRANGE + LIBRARY lists)
3. `⌥`+2-finger horizontal → mode cycle (global; does not fight Mission Control)

## Evidence

- Apple: AppKit Gestures + trackpad event overview (magnify / swipe / scroll phase+momentum)
- Code: `src/widget/wwidget.cpp` Apple touch disable
- Design: `res/design/KEYMAP.md` Trackpad column (`†` v1 / `‡` v2)
- Signal: `kanban/federation/signal/2026-08-07-macbook-trackpad-mode-language.md` (X scan + full map)
- Strategy: co-pilot not silent Automix; no camera-hand EQ as core

## Requested Action

When free of migx-cli / analyzer compile waves:

1. **Do not** re-enable global `WA_AcceptTouchEvents` on Apple for v1.
2. Scaffold thin **AppKit gesture bridge** (ObjC++) for v1 three behaviors only; map to same handlers as KEYMAP keys (`Tab`/`⌘1-3`, list arrows, zoom when declared).
3. Commit mutations on gesture **phase Ended** (handle Cancelled).
4. Leave play/cue/sync/hotcue/crossfader/gain **unbound** on trackpad.
5. Optional later: Force-click peek, stage swipe, 3-finger if OS free — all `‡` in KEYMAP.

If UI wave is not next: ack with ETA or fold into next nextgen QML/shell claim; do not start a parallel scoring doc.

## Blockers

None from Grok. Prefer worktree if Claude and another peer are both multi-file live on shared tree. No RT/engine edits required for v1.
