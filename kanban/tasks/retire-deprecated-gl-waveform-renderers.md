---
id: retire-deprecated-gl-waveform-renderers
type: task
title: "Retire the deprecated GL/Qt waveform renderers + widgets (untangle live base classes first)"
status: blocked
owner: gudjon
priority: medium
initiative: initiative-ui-modernization
parent_dossier: "kanban/planning/2026-07-17-gudjon-PLT--macos26-platform-alignment"
depends_on: ["waveform-parity-visual-dogfood"]
authored_by: claude-code
authored_kind: agent
triggered_by: "merge-all-branches 2026-07-17 — agy commit a6d109141b tried a bulk delete of src/waveform/**/deprecated/ but it breaks the build; captured here instead of landed."
created: "2026-07-17"
lastUpdated: "2026-07-17"
blocked_reason: "PLT Wave 3 parity matrix written; HOLD until live base-class rewire + visual dogfood. See results/WAVEFORM-PARITY-MATRIX.md — do not bulk-delete."
acceptance: |
  A dossier (prefix UIX) that retires the deprecated waveform renderers/widgets AND still builds arm64
  + passes waveform tests. It MUST first untangle the live dependencies that a naive delete misses:
  - `src/waveform/renderers/glwaveformrenderbackground.h:5` and
    `src/waveform/widgets/glwaveformwidgetabstract.h:3` `#include`
    `waveform/renderers/deprecated/glwaveformrenderer.h` — an ACTIVE base class, not dead code.
  - `src/waveform/renderers/glvsynctestrenderer.h:3` `#include`
    `waveform/renderers/deprecated/glwaveformrenderersignal.h`, and `GLVSyncTestWidget` is still
    registered in `waveformwidgetfactory.cpp` (lines ~36/1052/1186) — a LIVE widget.
  Approach: promote the still-needed base headers (`glwaveformrenderer.h`,
  `glwaveformrenderersignal.h`) out of `deprecated/` into the active tree (or rewire the 3 includers),
  update CMakeLists + the factory, THEN delete the genuinely-dead widgets. Gate: `cmake --build` green +
  `ctest -R Waveform` green. Never green-over-red (`AP-01`).
---

# Retire deprecated GL/Qt waveform renderers

The agy branch (`a6d109141b`, "retire deprecated UI code") attempted `git rm -r`-style deletion of
`src/waveform/renderers/deprecated/` + `src/waveform/widgets/deprecated/` (~27 files). Verified on
2026-07-17: **it does not build** — the "deprecated" folder still holds base classes that the *active*
GL waveform path inherits from, and the commit patched none of the includers, the CMake lists, or the
widget factory. It was NOT landed; the intent is captured here.

This is a real refactor (untangle → promote base headers → rewire → delete → verify), not a bulk
delete. Open it as a `UIX` dossier when the UI-modernization thrust resumes. Complements the
`initiative-ui-modernization` DESIGN.md→Theme.qml (DUI) work. Related: the deprecated GL path is the
same legacy surface the MTL render optimizations target.
