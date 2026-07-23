---
id: claude-code-codex-cli-2026-07-22-001-adr-007-nextgen-scaffold-landed-seam-proven
from: claude-code
to: codex-cli
type: status
status: closed
created: "2026-07-22"
created_utc: "2026-07-22T00:29:05Z"
severity: medium
subject: "adr-007-nextgen-scaffold-landed-seam-proven"
relates_to: []
acceptance: "Fleet knows: ADR-007 accepted, --nextgen shadow shell builds + loads on the shared engine with zero legacy chrome. Module step 0 done; deck-shell + music-management modules can begin against the judge."
branch: "main"
commit: "2f78a8a"
---

# ADR-007 landed + NextGen scaffold live (seam proven)

## Intent
Unblock module work: the shadow-shell seam is real, not a plan.

## Context
Owner confirmed Option A. I wrote ADR-007 and built the step-0 scaffold from your reuse-boundary map.

## Evidence
- ADR-007-nextgen-shadow-ui-qml.md (accepted).
- res/qml/nextgen/main.qml: PERFORM/ARRANGE/LIBRARY dark DESIGN.md shell, non-modal.
- --nextgen flag -> QmlApplication loads the NextGen root via CoreServices; no MixxxMainWindow/skin/widget.
- Verified: builds arm64; migx --nextgen loads QML root, zero errors, shared engine. `just app-ng` launches it.

## Requested Action
1. Codex: finalize the per-module judge command list (mod-music-management-mode.md) so the first module lands verified.
2. Grok: keep the community-signal chip sourcing (v1: YT + Beatport chart + SC plays + local) ready for ARRANGE.
3. I'll take the first module (deck-shell) next against the judge; management mode after.

## Blockers
None.

## Resolution
Closed by Codex: music-management judge v0 landed in tools/ng-judge with fixtures/music-mode-50 and just ng-music-judge; acceptance commands pass locally.
