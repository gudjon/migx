---
id: governance-review-2026-07-17
type: knowledge
title: "Governance review — reconciling the harness with the hard-fork / AI-DJing / licensing decisions"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md
  - kanban/architecture/decisions/ADR-003-licensing-and-openness.md
---

# Governance review — 2026-07-17

Pass to bring the whole governance layer into line with the strategic decisions Gudjon set today.

## The decisions governance must reflect
1. **AI-DJing thesis** — Migx is an AI-DJing platform; an agent (e.g. Claude Code) reads and *affects*
   a live session (cue points, song order, the experience ontology). (`README`, world-model task.)
2. **True hard fork** (`ADR-002`) — free to restructure, prune, reshape; no upstream tracking; the
   Cursor→VS-Code model, for AI-DJing. Withdrew ADR-001's no-restructure non-goals.
3. **Licensing** (`ADR-003`) — Mixxx is GPLv2 (copyleft), unlike VS Code's MIT. Closed *development* is
   fine (keep repo private); closed *distribution* of the DAW is not GPL-compatible; put proprietary
   value in an arm's-length AI service. Needs legal advice — status `proposed`.
4. **Attribution** — all fork additions credited to Gudjon; no AI co-author (`kanban/AUTHORS.md`).

## Surfaces reviewed & reconciled
| Surface | Status |
|---|---|
| `ADR-001` (task orchestrator) | Amended by ADR-002: `justfile`/recipes stand; no-restructure non-goals **withdrawn**. ✓ |
| `ADR-002`, `ADR-003` | Authored today (hard fork; licensing). ✓ |
| `README.md` | Fixed — removed "tracks upstream / improvements flow both ways"; now states true hard fork + GPL. ✓ |
| `kanban/tasks/prune-outdated-legacy-code.md` | Reframed — merge-risk gate dropped; build+test + value-to-Migx only. ✓ |
| `P-33` | Fixed line that assumed upstream-tracking; rewrite allowed behind a build+test gate. ✓ |
| Memory `migx-cursor-model` | Corrected to the final hard-fork position. ✓ |
| DDD cards `fork_delta` | Redefined by ADR-002 as **heritage-only** (inherited / divergent / migx-new), not mergeability. Card usage compatible — no edits needed. ✓ |
| `kanban/AGENTS.md`, `kanban/playbook/` | MG-1..6 + closed-loop doctrine are fork-agnostic — unchanged. A `fork_delta` mention in playbook ch.02 (MTL research context) is softened by ADR-002; acceptable. ✓ |

## Still open / owner actions
- **Licensing (ADR-003):** decide openness posture with legal counsel before any distribution; keep repo
  private meanwhile.
- **GitHub:** detach the fork relationship on `github.com/gudjon/migx` (GitHub-side action).
- **Pruning:** the prune-outdated task can now proceed to an execution dossier (build+test-gated).
- A delegated sweep confirms no remaining "upstream-tracking as a constraint" language contradicts
  ADR-002 across `kanban/` + `.claude/`.

The governance layer is now consistent with the hard-fork / AI-DJing / licensing frame. Doctrine
(MG-1..6, closed loops, everything-is-code) is unchanged — those are strategy-agnostic.
