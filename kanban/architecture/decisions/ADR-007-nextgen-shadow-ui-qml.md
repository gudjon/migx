---
id: ADR-007
type: decision
title: "NextGen UI — a shadow QML shell on the shared engine, grown module-by-module (Option A)"
status: accepted
owner: gudjon
created: "2026-07-22"
lastUpdated: "2026-07-22"
supersedes: []
amends: [ADR-004]
related: [ADR-005, ADR-006, initiative-ui-modernization, ai-code-migration-methodology, ui-non-modal-error-ux, nextgen-shadow-app-proposal, nextgen-engine-reuse-boundary-codex, nextgen-dj-ux-modes-and-signal]
---

# ADR-007 — NextGen shadow UI (Option A)

## Context
The legacy Mixxx QWidget/XML-skin UI is deeply entangled and is the source of real UX failures (modal
dialogs mid-set — `ui-non-modal-error-ux`). The owner set the next undertaking (2026-07-19): build a
**NextGen "Agent DJ" version as a parallel shadow build** — the full new UI development — reusing the
proven RT engine and growing **one module at a time, done right**, DESIGN.md-driven, on the most
optimized *and* agent-friendly engine (Cursor-path: classic stays the working base until the new surface
fully strangles it). Owner **confirmed Option A** (2026-07-22). The core product job (owner-DJ evidence,
`nextgen-dj-ux-modes-and-signal`): **reduce cognitive load — find the next track fast at a busy club.**

The fleet converged independently (Grok scout + Codex boundary map + Claude implementer): a native QML
shell beats Electron/web (perf, anti-goal) and SwiftUI (Swift↔C++ RT-engine bridge tax) for v1.

## Decision
1. **NextGen is an in-process QML *shadow shell*** that reuses the existing C++ engine unchanged: it
   boots through the `mixxx::qml::QmlApplication` bootstrap + `CoreServices`, and reads/writes only via
   typed `Qml*Proxy` / `QmlControlProxy` over the **ControlObject bus** (`[Group],key`). **No engine
   fork. No second control plane.** (Per `nextgen-engine-reuse-boundary-codex`.)
2. **Launch seam:** a NextGen launch mode selects a **NextGen QML root** through the existing QML
   bootstrap (`main.cpp` already branches on `args.isQml()`), **without** `MixxxMainWindow`, legacy skin
   XML, or `src/widget` product chrome. The legacy path stays for classic.
3. **No product dependency on legacy skin/widget chrome.** The NextGen shell must not require
   `src/skin/legacy` or `src/widget`. A physical CMake split may trail the first proof but is tracked
   (coupling risks in the boundary note: `DlgPreferences`, blocking `QMessageBox`).
4. **UI = QML + DESIGN.md tokens → Theme.** Every NextGen surface is declarative, agent-legible, and
   built against `res/design/DESIGN.md` tokens (ADR-004 target, done *as a real design system*, not the
   legacy skins).
5. **Full-screen modes, not dialogs.** The shell is **PERFORM / ARRANGE (music-management) / LIBRARY**
   capable; a mode is a mode, switched instantly, and **playback state survives mode switching**.
   Recoverable errors route to a **non-modal** surface (`ui-non-modal-error-ux`); a blocking modal is
   allowed only as a pre-live-set startup gate, never mid-set.
6. **Rejected for v1:** SwiftUI (bridge tax), web/React/Tauri (perf + Electron anti-goal), flag-only in
   the legacy QML (dual-stack fights), separate repo (federation harder).

## How it is built (methodology)
Per `ai-code-migration-methodology`: **build the judge first**, keep a rulebook, **"fix the loop, not
the code,"** mechanical queue from disk, adversarial review. Module order:
`scaffold → primitives → eq/vu/tempo → deck-shell → mixer/fx → library → co-pilot → waveform (after the
forced-OpenGL/Metal unpin)`. **First product module = the deck-shell** (play/cue — also the engine
verification unit); then pivot fast to the **music-management mode** (the owner's core friction, where
co-pilot + EXO + community-signal chips converge; chips are cached fixture/sidecar, **never network in
the live judge**).

Per-module **judge**: launches the NextGen QML root, reads one deck/library state through a proxy,
matches ControlObject behaviour + rendered pixels (reuse the headless-CGL harness, `EVD-0005`), and
passes the **non-modal** check. A module is not "done" if it can raise a blocking modal during a set.

## Consequences
- A clean greenfield UI surface each agent (Claude/Codex/Grok) can work a bounded module of, verified.
- Classic Migx keeps shipping; NextGen grows until the feature-flag default flips (dual-deck acceptance).
- Amends ADR-004: QML-primary stands; ADR-007 pins the *shadow-shell strategy + engine seam + modes +
  non-modal law*. The end state is one product on the NextGen UI, not permanent dual roadmaps.
