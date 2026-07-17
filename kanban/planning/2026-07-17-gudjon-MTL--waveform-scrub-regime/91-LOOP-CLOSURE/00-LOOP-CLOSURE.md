---
id: MTL-waveform-scrub-regime-loop-closure
type: loop-closure
dossier: 2026-07-17-gudjon-MTL--waveform-scrub-regime
prefix: MTL
sealed: false             # flip to true ONLY when the Verdict below is honestly scored
sealed_date: ""
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# 91 — Loop Closure

This is the dossier's expression of MG-1: a dossier is a *bet* (the problem is real · the approach
works · the gates catch failure); `90-EXECUTION/` placed it, this file **scores** it. Not yet run —
scaffolded at `phase: foundation`. Do not seal until waves 1-3 have executed and the verdict below is
filled in from real measurement.

---

## Verdict (one glance)

| | |
|---|---|
| **Definition-of-Done met?** | ☐ yes ☐ partial ☐ halted |
| **Criteria green** | *(not yet run — 0 of 2 `PS-MTL-03` acceptance criteria attempted)* |
| **Headline number** | *(pending `EVD-0003`)* |
| **One next action** | Execute wave 1: extend `waveformrenderbenchmark.cpp` to the combined scrub regime and capture `EVD-0003`. |
| **Do NOT trust** | Everything below this line is template scaffold, not a real retro — do not seal on it. |

## Retrospective — five passes
*(fill in after execution)*

## Forecast vs. actual (score the bet)

| We forecast | Actual | Delta / why |
|---|---|---|
| A measurable combined-regime number (`EVD-0003`) exists where none did; wave 2 either improves p99/max or the dossier honestly halts with "no headroom problem found" | *(pending)* | *(pending)* |

## System understanding AT CLOSE
*(fill in after execution)*

## Wiring ledger (no anonymous open ends)

| Produced | Consumer | Wired? |
|---|---|---|
| `EVD-0003` combined-regime benchmark + baseline | Wave-2 optimization decision (`02-ARCHITECTURE` decision gate) | ☐ UNVERIFIED |
| Wave-2 optimization (if any lands) | `91-LOOP-CLOSURE` verdict + `patterns/` re-home if durable | ☐ UNVERIFIED |

## What feeds back (must LAND this loop, not "queued")

| Learning | Rooted at (stable path) | Landed? |
|---|---|---|
| *(pending — e.g. if the dirty-path lever generalizes, it re-homes into `P-22`/`AP-12` as an addendum; if the regime turns out not to be a bottleneck, that ruled-out fact re-homes here and into `01-RESEARCH` of any successor)* | | ☐ |

## Honest gate

- [ ] No green-over-red: every "met" criterion has a passing benchmark/test cited above.
- [ ] No house-physics regression (MG-6): no new RT-thread allocation/lock; Qt ownership sound.
- [ ] Every produced surface is WIRED or has a follow-on task.
- [ ] The retro above is authored, not boilerplate.

## Next bet + follow-on tasks
*(fill in after execution)*

## Closure metrics (auto-derived where possible)
*(derived by `kanban/scripts/derive-closure-metrics.py` at seal time)*
