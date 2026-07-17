---
id: DSP-loop-closure
type: loop-closure
dossier: 2026-07-17-gudjon-DSP--iir-eq-filter-simd
prefix: DSP
sealed: false             # flip to true ONLY when the Verdict below is honestly scored
sealed_date: ""
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# 91 — Loop Closure

This is the dossier's expression of MG-1: a dossier is a *bet* (the problem is real · the approach
works · the gates catch failure); `90-EXECUTION/` placed it, this file **scores** it. It is a Sprint
Review + Retrospective in artifact form — retrospective only (git holds chronology; do not build a
ledger here).

**Seal gate.** You may set `sealed: true` only when the Definition-of-Done is verified (met or
explicitly partial), OR the bet is honestly **halted** with a named successor + owner + re-fire
condition. Never green-over-red (AP: honest-gate). An empty/boilerplate retro must NOT be sealed —
it starves the cross-dossier learning loop.

---

## Verdict (one glance)

| | |
|---|---|
| **Definition-of-Done met?** | ☐ yes ☐ partial ☐ halted |
| **Criteria green** | `<X of N>` (list which acceptance criteria passed, by `PS-<PFX>-NN`) |
| **Headline number** | `<the measured result vs baseline — e.g. 1.8× waveform throughput on M4>` |
| **One next action** | `<the single most important follow-on>` |
| **Do NOT trust** | `<what in this dossier is already stale / will mislead a future reader>` |

## Retrospective — five passes

Run these as five *distinct* lenses, not one blur.

1. **Premise vs. actual (root cause).** Was the problem as framed? Where did the bet's premise
   diverge from reality, and *why* (5-whys to a durable root)?
2. **Process.** What in how-we-worked helped or hurt — the loop cadence, the tooling, the gates?
3. **Coordination.** Handoffs, blocked premises, anything that needed another owner.
4. **Ruled-out durable facts.** What did we prove is NOT true / NOT worth doing? (These prevent a
   future dossier from re-litigating.)
5. **Action.** The concrete changes this retro triggers (each must land — see "What feeds back").

## Forecast vs. actual (score the bet)

| We forecast | Actual | Delta / why |
|---|---|---|
| `<predicted number/outcome>` | `<measured>` | `<what the gap teaches>` |

## System understanding AT CLOSE

<A snapshot of how the touched subsystem actually works now — data journey, the RT/GPU boundary, any
drift from the architecture map. This is THEN's truth and will rot; current truth lives in code +
`kanban/architecture/`.>

## Wiring ledger (no anonymous open ends)

Every surface this dossier produced must name a consumer. A produced-but-unconsumed surface is an
open loop.

| Produced | Consumer | Wired? |
|---|---|---|
| `<file / pattern / benchmark / capability>` | `<who/what uses it>` | ☐ WIRED ☐ UNVERIFIED ☐ UNWIRED |

## What feeds back (must LAND this loop, not "queued")

Each durable learning re-homes into the living layer *now*:

| Learning | Rooted at (stable path) | Landed? |
|---|---|---|
| `<learning>` | `<kanban/patterns/P-NN | ADR-NNN | in-code annotation | architecture map>` | ☐ |

## Honest gate

- [ ] No green-over-red: every "met" criterion has a passing benchmark/test cited above.
- [ ] No house-physics regression (MG-6): no new RT-thread allocation/lock; Qt ownership sound.
- [ ] Every produced surface is WIRED or has a follow-on task.
- [ ] The retro above is authored, not boilerplate.

## Next bet + follow-on tasks

<The next dossier this points to, and any cross-cutting items spun out as owned
`kanban/tasks/<slug>.md` cards with `parent_dossier:` set. The closure spawns the next sprint's
backlog; it does not leak open ends.>

## Closure metrics (auto-derived where possible)

<Commits, files touched, benchmark deltas, days-open — derived from git by
`kanban/scripts/derive-closure-metrics.py` (Phase 3), not hand-typed.>
