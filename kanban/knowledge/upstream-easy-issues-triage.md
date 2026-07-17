---
id: upstream-easy-issues-triage
type: knowledge
title: "Upstream mixxxdj/mixxx label:easy — first-execution shortlist for Migx"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: "gh issue list --repo mixxxdj/mixxx --state open --label easy (2026-07-17)"
---

# Upstream `label:easy` — first-execution shortlist

The good-first-issue set, triaged as candidates to **exercise the harness on real code** (small, bounded,
run the full dossier loop) — prefer ones that also touch our north-star (perf / render / Qt ownership).
As a true hard fork (ADR-002) we fix these in Migx; we don't necessarily upstream them.

## Top candidates (mapped to Migx context)
| # | Title | Migx context | Why a good first execution |
|---|---|---|---|
| **16536** | Vinyl control scope update is wasting CPU | `arch-vinylcontrol` (RT-adjacent) | **On-thesis perf win** — a real CPU waste, small, bench-able (P-03/P-18). Claude/RT-lane candidate. |
| **16055** | Column delegates not deleted on exit | `arch-library-db` / Qt ownership | Clean **Qt-ownership** fix (`P-19`/`AP-13` — parented_ptr lifetime); small, testable. |
| **16174** | About window keeps Mixxx running/playing on exit | GUI lifecycle | Bounded lifecycle bug; good QML/UI-lane (Antigravity) warm-up. |
| **15933** | Add "Spiral" filter to FX | `arch-effects-chain` (RT DSP) | A **feature** — new builtin effect; RT DSP (P-02), exercises the effects backend. Confirmed. |
| **15869** | Configurable metadata broadcast volume threshold | `arch-broadcast-recording` | Small config feature; low blast radius. (Broadcast is a legacy-retirement candidate — check first.) |

## Recommendation
- **First real execution (Claude/RT lane):** **#16536** (vinyl scope CPU) — it's a genuine perf fix, aligns
  with `initiative-apple-silicon`, and runs the full benchmark-gated dossier loop end-to-end on real code.
- **Clean Qt-ownership warm-up:** **#16055** (delegates on exit) — a `P-19` fix with a clear test.
- **UI/non-RT lane (Antigravity):** **#16174** (about-window lifecycle) or **#15933** (Spiral FX).
- Each becomes a small dossier (register a prefix, e.g. `FIX`) or a `kanban/tasks/` card, build+test-gated.

_Sample of ~15 easy issues queried; full list via the gh command in `source`._
