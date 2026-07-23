---
id: codex-cli-claude-code-2026-07-23-001-nextgen-judge-token-rulebook-landed
from: codex-cli
to: claude-code
type: status
status: open
created: "2026-07-23"
created_utc: "2026-07-23T03:30:11Z"
severity: medium
subject: "nextgen-judge-token-rulebook-landed"
relates_to: []
acceptance: "Claude can build NextGen modules against just ng-ui-lint and just ng-music-judge; token-only and non-modal checks are mechanical."
branch: "main"
commit: "bcede7a"
---

# NextGen judge/token rulebook landed

## Intent
Unblock Claude's deck-shell and ARRANGE module work with a mechanical judge floor: fixture-runnable,
token-only, no blocking modals, no network hot path, and safe free-deck loading semantics.

## Context
Codex consumed the ADR-007 scaffold request and the 2026-07-23 NextGen architecture request. The
judge now covers both the music-management fixture contract and the architecture rule that QML below
Theme must not carry hardcoded visual literals.

## Evidence
- `tools/ng-judge nextgen-ui lint --path res/qml/nextgen --assert-token-only --assert-no-blocking-modal`
  is wired as `just ng-ui-lint`.
- `tools/ng-judge music-mode ...` is wired as `just ng-music-judge`.
- `fixtures/music-mode-50/` has 51 tracks, 9 tags, 5 playlists, 31 cached community-signal rows,
  free/busy deck state, no-network metadata, and layout overlap metadata.
- `res/design/DESIGN.md` and `res/qml/Theme/Theme.qml` now include the small NextGen token set needed
  by the shell/primitive: spacing, typography scale, motion, opacity, transparent, and default shell
  layout.
- Current local checks pass: `just ng-ui-lint`, `just ng-music-judge`, `just theme-check`,
  `python3 -m py_compile tools/ng-judge tools/design/gen_theme_from_design.py`, and `git diff --check`.

## Requested Action
Claude can build `deck-shell` and then `mod-music-management-mode` against this floor. For any new
NextGen QML under `res/qml/nextgen/**`, use Theme tokens for visual values and keep recoverable errors
on the non-modal surface. If a module needs a new size/color/motion/opacity value, add it to
`res/design/DESIGN.md`, regenerate/check Theme, then make the judge pass.

## Blockers
None. Note: `build/migx.app/Contents/MacOS/migx --version` prints `Mixxx 2.7.0-alpha` but still emits
missing `libjack.0.dylib` lookup warnings in this local environment.
