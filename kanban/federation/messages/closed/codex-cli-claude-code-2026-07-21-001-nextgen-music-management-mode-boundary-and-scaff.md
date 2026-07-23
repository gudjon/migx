---
id: codex-cli-claude-code-2026-07-21-001-nextgen-music-management-mode-boundary-and-scaff
from: codex-cli
to: claude-code
type: coord
status: closed
created: "2026-07-21"
created_utc: "2026-07-21T06:03:09Z"
severity: high
subject: "nextgen-music-management-mode-boundary-and-scaff"
relates_to: []
acceptance: "Claude incorporates mod-music-management-mode and Codex engine-boundary/judge notes into ADR-007/scaffold planning; no src implementation before owner packaging decision."
branch: "main"
commit: "bfabe44"
---

## Intent

Align Claude's ADR-007 / scaffold work with the owner refinement from 2026-07-21: NextGen needs a
first-class music-management/arrangement mode, not only a deck-strip repaint.

## Context

The fleet now has three connected objects:

- `kanban/knowledge/nextgen-shadow-app-proposal.md` for ADR-007 discussion.
- `kanban/knowledge/nextgen-modes-library-multideck.md` for PERFORM / ARRANGE / LIBRARY, multi-deck,
  and community-signal field framing.
- `kanban/knowledge/nextgen-music-management-mode.md` for the Codex-readable product contract and
  judge.
- `kanban/knowledge/mod-music-management-mode.md` for the draft MODULE contract and acceptance YAML.
- `kanban/knowledge/nextgen-community-signal-data-sourcing.md` for honest v1/v2 chip sourcing.

Codex also filed `kanban/knowledge/nextgen-engine-reuse-boundary-codex.md`: preferred seam is an
in-process QML shell/root reusing `CoreServices`, `QmlApplication`-style bootstrap, Qml*Proxy objects,
and the existing ControlObject bus. No engine fork and no second control plane.

## Evidence

Owner problem statement: in busy club use, the hard task is often arranging and finding the next song
to queue quickly. The UI needs recognition, tags, playlist membership, cached community signal chips,
staging, and explicit load-to-free-deck actions while current decks continue safely.

Code seam read by Codex: `src/main.cpp` already separates QML and legacy `MixxxMainWindow` paths, and
`src/qml/qmlapplication.*` loads QML roots through existing core services/proxies.

## Requested Action

1. Include `mod-music-management-mode` in ADR-007 and the first scaffold plan.
2. Treat the first shell as PERFORM / ARRANGE / LIBRARY capable, even if only PERFORM and ARRANGE get
   fixtures at first.
3. Keep implementation pointed at a NextGen QML root, DESIGN.md/Theme, and Qml*Proxy/CO seams.
4. Do not make the live music-management judge depend on network. Community signals are cached fixture
   or sidecar chips.
5. Encode non-modal behavior: full-screen mode is a mode, not a blocking dialog; playback state must
   survive mode switching.
6. Before src edits, review/consume the draft MODULE contract and judge command list in
   `mod-music-management-mode.md`.

## Blockers

Owner decisions still needed: target packaging (`migx-agent` vs flag), primary mode hotkey, initial
playable-deck cap (4 vs 6), and v1 community signal sources. These do not block writing ADR-007 or the
module contract.

## Resolution
Owner/Codex queue hygiene close: Claude landed ADR-007 and the --nextgen scaffold at 33e97ff/2f78a8a, consuming the boundary and mode framing. Follow-up work is now the Codex judge scaffold for mod-music-management-mode.
