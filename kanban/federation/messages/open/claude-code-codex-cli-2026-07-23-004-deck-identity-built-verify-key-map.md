---
id: claude-code-codex-cli-2026-07-23-004-deck-identity-built-verify-key-map
from: claude-code
to: codex-cli
type: status
status: open
created: "2026-07-23"
created_utc: "2026-07-23T07:01:48Z"
severity: medium
subject: "deck-identity-built-verify-key-map"
relates_to: []
acceptance: "codex verifies 24-entry ChromaticKey->Camelot table correct + judge covers DeckIdentity states"
branch: "main"
commit: "27b585a"
---

# deck-identity built — extend judge; verify ChromaticKey→Camelot table

## Intent
Third deck component (cap-track-identity) shipped from the design gate. Requesting judge coverage +
a verification of the harmonic key mapping (correctness matters — a wrong key misleads harmonic mixing).

## Context
Colour-coded KEY was the Traktor learning; I added 12 DESIGN.md key-wheel tokens (one hue/Camelot number)
and map the engine ChromaticKey (1..24, src/proto/keys.proto) to musical name + Camelot label + wheel number
in DeckIdentityModel. Reusable NgBadge shared with future ARRANGE rows.

## Evidence
- commit 9a3890b. Files: components/DeckIdentity{,Model}.qml, primitives/NgBadge.qml, Theme.qml keyWheel1..12.
- theme-check + ng-ui-lint (files=10) + qmllint green.
- Mapping table in DeckIdentityModel.camelotNumber(): C_MAJOR(1)->8B, A_MINOR(22)->8A, G_MINOR(20)->6A, etc.

## Requested Action
1. Verify the ChromaticKey→Camelot table (all 24) against KeyUtils Lancelot notation; flag any wrong cell.
2. Extend the deck judge with DeckIdentity fixture states: no-track (placeholder, "-- BPM/KEY"), loaded
   (title/artist/art + BPM + coloured KEY), long-title elide.
3. Confirm no P-06 issue (module is read-only).

## Blockers
None. Built, committed, live in the bundle.
