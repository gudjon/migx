---
id: signal-2026-07-18-x-thin-data-energy-cues-planner-live
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [exo, copilot, energy, cues, set-planner, layer-b, discovery]
mapped_to:
  - research-analyzer-structure-energy-mlx
  - fsl-sidecar-export-hardening
  - discovery-continuous-customer-evidence-loop
  - 2026-07-18-ontology-bpm-cues-energy-for-copilot
  - EXO set-level planner (534d9a9)
method: "X field discourse vs three stated product gaps (energy/cues, greedy planner, offline→live)"
confidence: medium
---

# X on the thin data under a solid reasoning layer

**Frame (from fleet):** tempo/key path advanced (`db4cfa7` FSL→ontology; set planner `534d9a9`); energy still flat ~0.50; cues missing; planner greedy; still offline.  
**Question:** Does public X discourse validate those gaps as *customer/market* pain, or only *our* engineering debt?

---

## Gap 1 — Energy & cue points (highest value)

### What X actually says (past_behavior / craft)

| Evidence | Class | Read |
|---|---|---|
| @djSlickStuart (2026-07): “Mark your **hot cues**, check **transitions**, soundcheck early → no panic” | past_behavior / advice-from-experience | Cues are **prep ritual**, not optional metadata. Flat energy *and* empty cues make “transition check” impossible for a co-pilot. |
| JP working DJs (2026-07): Memory Cue vs Hot Cue craft; CALL-to-set-cue; grid on PC then cue on hardware; Denon export drops one cue type | past_behavior | Cue **types and export fidelity** are active pain. FSL without cues = Lexicon-class failure mode. |
| @GetOraDJ / Ora DJ (2026-06): product pitch = prep app with **auto hot cues**, Track Prep tabs, set canvas — “basics: beatgrid + cue points” | commitment (competitor) | Market validates **cue-first prep** as a product surface. |
| Setlist Planer tools advertising BPM + **energy levels** for transitions | commitment (vendor) | Energy is the advertised differentiator once BPM exists — matches our “flat 0.50 arc is useless” diagnosis. |
| Loudness/energy macro (Youlean etc.) | adjacent (mix eng) | Macro dynamics narrative exists; DJs rarely name “energy curve file format” — they name **cues + transitions**. |

### Verdict (field)
- **Cues >> numeric energy** in first-person DJ talk. Energy appears in **tool marketing** and set-planning ads more than in “I lost a gig because energy was wrong.”  
- Empty FSL cues is the **customer-shaped** hole; flat energy is the **planner-shaped** hole. Both matter; coordinate export of **existing** Cue objects first, then AnalyzerEnergy.

### Coordinate, don’t collide
- C++ cue/energy in **Codex FSL lane** → Grok/Claude: **signal + schema/fixtures only**, no `src/analyzer/**` or FSL C++ while claim active.  
- EXO tools can consume cues as soon as sidecar has them (Python planner) — parallel, not fork.

---

## Gap 2 — Greedy / myopic set planner

### What X says

| Evidence | Class | Read |
|---|---|---|
| @cryptokwueene: Spotify sort by BPM → **Claude rearrange by taste** for event | past_behavior (event/org, not club CDJ) | Offline **LLM reordering** is already a real prep workflow. V1 greedy planner is *behind* what power users do with chat. |
| @lilyraynyc: Claude + Spotify analyze playlist → curate new list (“DJ brain”) | past_behavior / delight | Demand for **set-level reorder assist** is real — still **prep**, not mid-deck. |
| Setlist Planer (BPM + energy transitions) | vendor | Market sells **global** arc (duration, energy, BPM path), not only nearest-neighbor. |
| @saluteAUT AI setlist-from-prompt ad reject (~1.2k likes) | preference | Full **automix/set authorship** still cultural landmine; **assist + human taste** OK. |

### Verdict (field)
- Smarter optimizer is **validated as prep UX**, not as “AI owns the set.”  
- DC-PDCL-5.3 V1 greedy is fine if explainable; upgrade path people already invent: **BPM sort + human/LLM global pass**.  
- Long-set quality = energy arc + phrase boundaries — **blocked by Gap 1 data**, not by algorithm cleverness alone. Don’t burn cycles on TSP solvers until energy/cues exist.

---

## Gap 3 — Offline only; live session mirror ↔ intent-inbox

### What X says

| Evidence | Class | Read |
|---|---|---|
| AI setlist ads / “AI DJ Agency” / BeatGrid AI auto-playlist | hype / vendor | Live **replacement** narrative is marketing, not DJ past_behavior. |
| Magenta RealTime / Co-Driver (Ableton co-pilot live) | research / product | Live AI is **hot in production/jamming**, not CDJ club dual-deck. |
| Still **no** “I Ack’d next-track on CDJs mid-gig” first-person | negative evidence | Live Layer B remains **assumption**. |
| Prep assist (Claude+Spotify, cues early, dual-USB) | past_behavior | Offline co-pilot matches how people already use AI. |

### Verdict (field)
- **“Claude affecting my live session”** is founder thesis, not X ethnography.  
- Field rewards: **prep** (cues, transitions, set order, export integrity).  
- Live bridge = high technical ambition, **low customer past_behavior** right now. Ship session-mirror when dogfood demands it; don’t let it block energy/cues.

---

## Priority stack (X-aligned + fleet-safe)

| Priority | Work | Owner lane | Why (X) |
|---|---|---|---|
| **P0** | FSL/sidecar **cues** (+ bpm/key already flowing) | **Codex FSL** (coordinate) | Prep ritual #1 on X |
| **P0** | EXO planner consumes real energy when present; mark stub | Claude tools | Avoid silent flat 0.50 |
| **P1** | Worker **energy curve** (DSP) → sidecar | Analyzer task / Codex after cues | Unblocks arc; vendor set planners sell this |
| **P2** | Better-than-greedy set optimizer (global energy + BPM) | Claude EXO | Only after non-flat energy |
| **P3** | Session-mirror ↔ intent-inbox (live Layer B) | Engine/CO careful | Thesis; weak X past_behavior |

---

## What not to claim

- DJs are asking for a live AI co-pilot on X (they aren’t, in first person).  
- Energy ratings alone fix set quality (cues/transitions dominate craft talk).  
- Smarter TSP without energy/cues data will impress (it won’t — data is the bottleneck).

---

## Handoffs

None auto-sent (signal only). Suggested next if Claude wants fleet mail:  
`coord` to **codex-cli** — “cues in FSL sidecar is P0 for planner; energy after; EXO will not edit analyzer C++.”

---

## Bottom line

Your diagnosis matches the field: **reasoning ahead of data**. X puts **cue prep** first, **energy for set shape** second (tools market it), **global reorder assist** as optional prep luxury, and **live session AI** as unproven. Coordinate FSL cues with Codex; keep greedy V1; leave live bridge as deliberate later bet.
