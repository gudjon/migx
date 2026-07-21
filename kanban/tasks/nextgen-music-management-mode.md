---
id: nextgen-music-management-mode
type: task
title: "Define and judge the NextGen full-screen music management mode"
status: open
owner: gudjon
priority: high
initiative: initiative-ui-modernization
parent_dossier: null
depends_on:
  - nextgen-shadow-app-proposal
  - nextgen-dj-needs-and-leader-ui-map
  - nextgen-dj-ux-modes-and-signal
  - nextgen-modes-library-multideck
  - mod-music-management-mode
  - nextgen-community-signal-data-sourcing
  - nextgen-engine-reuse-boundary-codex
  - ui-migration-judge-rulebook-inventory
authored_by: codex-cli
authored_kind: agent
triggered_by: "2026-07-21 owner refinement: music arrangement and next-queue management may be the core NextGen mode"
created: "2026-07-21"
lastUpdated: "2026-07-21"
acceptance: |
  A module contract exists for mod-music-management-mode; fixture data proves search, tags, playlist
  memberships, cached community signal chips, queue/load-to-free-deck, and fast return to performance
  mode; the judge proves no network dependency, no blocking modal, no deck-state loss, and no text
  overlap at target laptop and wide desktop sizes.
---

# NextGen Music Management Mode

The mode is the full-screen arrangement and next-queue surface for busy club use. It is not a generic
library table. It must help the DJ recognize, compare, stage, and load tracks quickly while current
decks keep playing safely.

## First Batch

1. ~~Write the `mod-music-management-mode` MODULE contract.~~ → `kanban/knowledge/mod-music-management-mode.md` (draft 2026-07-21, grok-signal).
2. Define fixture data for 50 tracks with tags, playlist memberships, BPM/key/energy, and external
   signal-chip stubs (`fixtures/music-mode-50/` per MODULE §5).
3. Choose mode-switch semantics: keyboard/controller action, compact now-playing header, fast return
   (MODULE §2 proposes PERFORM↔ARRANGE one-key + now ribbon).
4. Add judge commands for fixture load, search/filter, queue/load-to-free-deck, no-network hot path,
   and screenshot/pixel layout checks (MODULE §1 acceptance YAML).
5. ~~Feed Grok's source/API feasibility brief into the signal-chip schema before implementation.~~ →
   MODULE §4 + `nextgen-community-signal-data-sourcing.md` (honest v1 kinds; setlist v2).

## Guardrails

- Music mode may write only explicit user actions to a free deck or queue.
- External signals are cached/provenance-bearing; no live network dependency in the club path.
- Missing signals degrade quietly with badges or empty states.
- Full-screen mode is not a blocking modal; current playback must remain visible and unaffected.
- Keep implementation in the NextGen/QML lane unless ADR-007 changes the host.
