---
id: signal-2026-07-18-dj-shared-library-capability
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [shared-library, dj-crates, capability, exo-hybrid]
mapped_to:
  - kanban/knowledge/dj-shared-library-capability.md
  - world-model-experience-ontology
  - ADR-005
---

# Signal — Shared libraries as Migx capability (no Plex dependency)

## Position
We want **DJ-to-DJ shared crates** as a first-class product capability: host → invite → known shares →
browse → EXO session union → play only when local/LAN policy allows.

**Plex is prior art only** (how “known servers + invites” feel). **No Plex account, server, or SDK
in the architecture.** Optional later: one-shot import adapter from existing media servers — not core.

## SSoT
`kanban/knowledge/dj-shared-library-capability.md`

## Next product waves (when scheduled)
W1 fixture hybrid session (2 DJs, 1 share) → W2 LAN host spike → W3 playability badges → invite/revoke → co-pilot over union.
