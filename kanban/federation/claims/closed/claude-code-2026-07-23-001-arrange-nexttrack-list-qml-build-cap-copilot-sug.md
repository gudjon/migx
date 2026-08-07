---
id: claude-code-2026-07-23-001-arrange-nexttrack-list-qml-build-cap-copilot-sug
owner: claude-code
status: closed
created: "2026-07-23"
created_utc: "2026-07-23T08:05:08Z"
expires_utc: "2026-07-24T08:05:08Z"
subject: "arrange-nexttrack-list-qml-build-cap-copilot-sug"
paths: "res/qml/nextgen/components/TrackRow.qml, res/qml/nextgen/components/TrackList.qml, res/qml/nextgen/modes/ArrangeMode.qml, res/qml/nextgen/lib/camelot.js"
branch: "main"
commit: "8e5903e"
---

# ARRANGE nexttrack-list QML build (cap-copilot-suggestion)

## Intent
Claude builds ARRANGE v1 per Grok's arrange-nexttrack-copilot-scoring brief; Grok owns scoring policy, Codex owns ng-music-judge.

## Scope
- `res/qml/nextgen/components/TrackRow.qml`
- `res/qml/nextgen/components/TrackList.qml`
- `res/qml/nextgen/modes/ArrangeMode.qml`
- `res/qml/nextgen/lib/camelot.js`

## Release
Run `./kanban/scripts/migx-fed release --id claude-code-2026-07-23-001-arrange-nexttrack-list-qml-build-cap-copilot-sug --by claude-code --resolution "..."` when the lane is done.

## Resolution
Released by claude-code at 2026-08-07T17:06:21Z.

Expired 2026-07-24 and abandoned: none of the claimed paths (TrackRow.qml, TrackList.qml, ArrangeMode.qml, camelot.js) were ever created and no commit touched them. Releasing the lane so codex-cli/grok-signal are unblocked on res/qml/nextgen/. ARRANGE v1 needs a fresh claim if resumed.
