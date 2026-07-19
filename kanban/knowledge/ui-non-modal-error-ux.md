---
id: ui-non-modal-error-ux
type: knowledge
title: "Errors must not block the mix — non-modal error UX"
status: active
owner: gudjon
created: "2026-07-19"
lastUpdated: "2026-07-19"
related:
  - ai-code-migration-methodology
  - initiative-ui-modernization
  - P-34
  - res/design/DESIGN.md
---

# Errors must not block the mix — non-modal error UX

**The failure (observed 2026-07-19):** the legacy stack raised a **blocking modal dialog** mid-session —
*"Live Broadcasting … Can't connect to streaming server"* — repeatedly. A modal freezes the entire UI
until dismissed. **A DJ mid-set cannot stop the music to click OK.** This is a core interaction failure,
not a cosmetic one, and Migx is first and foremost about the human↔software link during performance.

## The principle
1. **Mid-session errors surface non-modally.** A recoverable/background failure (broadcast can't connect,
   analysis failed, controller disconnected, network hiccup) goes to a **persistent, dismissible status
   surface** — a status area, a toast that auto-fades, or the owning control's own indicator (e.g. a red
   broadcast icon) — **never a blocking modal**. The mix keeps playing.
2. **Non-modal ≠ silent.** The error is still classified and logged (P-34); it is just not *blocking*.
   The user can inspect it when they choose, not when the software demands.
3. **Back off, don't nag.** A retrying background connection (broadcast reconnect) surfaces its state
   **once** and backs off; it must not re-raise per attempt. (The 2026-07-19 profile shipped
   `Enabled=1 + EnableReconnect=1` with an empty host → infinite nag. Root-cause bug, tracked.)
4. **Blocking is reserved for two cases only:** (a) a genuine must-decide-now choice the user initiated,
   and (b) an unrecoverable **startup** fault that prevents launch (e.g. settings dir unwritable → exit).
   Never mid-performance.

## Binds the UI migration
Every component ported into the QML/DESIGN.md framework (see `ai-code-migration-methodology`) must route
errors through a **shared non-modal notification surface**, not `QMessageBox`. A migrated component is
not "done" if it can raise a blocking modal during a set. This is a scored acceptance criterion in the
migration judge, alongside ControlObject and pixel equivalence.

## Immediate follow-ups (bugs this surfaced)
- Default broadcast profile ships enabled with reconnect + empty host → auto-nag on every fresh install
  (`broadcastprofile.cpp`; default should be `Enabled=0`).
- Audit remaining `QMessageBox`/modal call sites reachable during a live session; reroute to the
  non-modal surface as their components migrate.
