---
id: narrow-platform-to-apple-silicon
type: task
title: "Prune Linux desktop build/packaging/CI; quiet Windows CI — Apple-Silicon-only per ADR-006"
status: open
owner: gudjon
priority: medium
initiative: initiative-apple-silicon
parent_dossier: ""
depends_on: []
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon 2026-07-17 — focus on macOS Apple Silicon (iPad next); Linux dropped, Windows later. ADR-006."
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  Executes ADR-006's simplification. A dossier (prefix PLT or fold into an initiative-apple-silicon
  dossier) that, wave by wave with build+test gates:
  - Removes Linux DESKTOP packaging + CI: packaging/debian/, packaging/flatpak/, CPackDebInstall.cmake,
    CPackDebUploadPPA.cmake, .github/workflows/flatpak.yml, and Linux legs of build.yml/checks.yml.
    (NOTE: keep any embedded/appliance door only as a doc note — no code kept for it now.)
  - Quiets Windows CI legs (packaging/wix/ goes DORMANT, not deleted — Windows is "later" per ADR-006).
  - Trims obviously-dead Linux-only source #ifdef paths ONLY where touched and safe (do not chase a
    full sweep; house physics + build-must-stay-green each wave).
  - Keeps the ios/ seam intact (iPad is the sensible next platform — ADR-006 point 2).
  - Result: macOS-arm64-only CI is green; mixxx-lib + mixxx-test still build arm64; ctest 100%.
  Gate every wave on `cmake --build` + `ctest`; never green-over-red (AP-01). This is a real restructure
  — scope it as its own loop, do not bulk-delete.
---

# Narrow platform to Apple Silicon (execute ADR-006)

[ADR-006](../architecture/decisions/ADR-006-platform-scope-apple-silicon.md) pins the platform to Apple
Silicon: **macOS now, iPad next, Windows later, Linux dropped** (embedded-appliance only, not now). This
task is the *execution* of that decision — retire the Linux desktop build/packaging/CI surface and quiet
Windows, shrinking the compatibility surface so iteration speeds up.

Surface to prune (grounded 2026-07-17): `packaging/debian/`, `packaging/flatpak/`,
`CPackDebInstall.cmake`, `CPackDebUploadPPA.cmake`, `.github/workflows/flatpak.yml`, and the Linux legs
of `build.yml` / `checks.yml`. `packaging/wix/` (Windows) → dormant, not deleted. `ios/` → keep (iPad).

Not a bulk `rm` — a wave-gated restructure where every wave keeps the arm64 build + `ctest` green.
Complements [[retire-deprecated-gl-waveform-renderers]] (both shrink surface). Opens as a `PLT` dossier
or folds into an `initiative-apple-silicon` execution dossier when picked up.
