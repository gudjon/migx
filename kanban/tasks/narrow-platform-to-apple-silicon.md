---
id: narrow-platform-to-apple-silicon
type: task
title: "Prune non-macOS packaging/CI — macOS 26+ Apple Silicon only (ADR-006 Wave 2)"
status: done
owner: gudjon
priority: high
initiative: initiative-apple-silicon
parent_dossier: "kanban/planning/2026-07-17-gudjon-PLT--macos26-platform-alignment"
depends_on: []
authored_by: claude-code
authored_kind: agent
triggered_by: "ADR-006 sole product = macOS 26+ arm64; architecture-apple-silicon-macos26-refactor-map Wave 2"
created: "2026-07-17"
lastUpdated: "2026-07-17"
completed: "2026-07-17"
evidence: "PLT Wave 2: .github/workflows/build.yml macOS arm64 only; packaging DORMANT; release flatpak if:false"
acceptance: |
  Executes ADR-006 Wave 2 (architecture-apple-silicon-macos26-refactor-map.md). Wave by wave with
  build+test gates on macOS arm64 26+ (deployment target already 26.0 — do not re-do that):
  - Removes Linux DESKTOP packaging + CI: packaging/debian/, packaging/flatpak/, CPackDebInstall.cmake,
    CPackDebUploadPPA.cmake, .github/workflows/flatpak.yml, Linux legs of build.yml/checks.yml.
  - Windows packaging/wix/ + CI → DORMANT (no Win design work).
  - iOS/android not shipping — leave dormant; no investment.
  - Collapse foreign-OS #ifdefs only when a file is already touched (P-11); no mega-delete.
  - Result: macOS-arm64-only CI green; mixxx-lib + mixxx-test arm64; ctest green; no Mac DJ feature loss.
  Gate every wave on cmake --build + ctest; never green-over-red (AP-01).
---

# Narrow platform (ADR-006 Wave 2)

[ADR-006](../architecture/decisions/ADR-006-platform-scope-apple-silicon.md): **macOS 26.\*+ · Apple
Silicon only**. Full program:
[`architecture-apple-silicon-macos26-refactor-map.md`](../knowledge/architecture-apple-silicon-macos26-refactor-map.md).

**Wave 2 only** — packaging/CI prune. Does **not** rewrite Core Audio or delete GL (Waves 1/3).
Feature-preserving for Mac DJs.

Complements [[retire-deprecated-gl-waveform-renderers]] and [[tahoe-m4-soundio-soak-rebaseline]].
