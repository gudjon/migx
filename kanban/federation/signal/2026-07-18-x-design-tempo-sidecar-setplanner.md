---
id: signal-2026-07-18-x-design-tempo-sidecar-setplanner
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [exo, copilot, tempo, sidecar, set-planner, ux, discovery]
mapped_to:
  - tools/exo/copilot_why_next.py
  - EXO FSL bridge (db4cfa7)
  - EXO set-level planner (534d9a9)
method: "X discourse → design improvements for three landed co-pilot capabilities"
confidence: medium
---

# X design input — tempo scoring · sidecar bridge · set planner

Three landed differentiators, checked against **trending / recurring X talk** for validation and UX upgrades. Not a go/no-go on shipping (already tested); this is **how to present and harden** them.

---

## 1. Tempo scoring (beatmatch + half/double-time)

### Field validation
| Signal | Design implication |
|---|---|
| @RamonPang (~2.3k likes): DJing when you must know **174 ÷ 2** | Half/double-time is **lived skill**, not edge case — surfacing “124↔248 / 87↔174” style reasons is correct product language |
| Mashup community: **manually verified BPM & key** spreadsheets (high engagement) | Trust comes from **verifiable numbers**, not black-box “good mix” scores |
| @ODD_MOB: tracks forced into wrong BPM set “sound like ass” | Tempo clash is emotional + sonic; **penalize hard** and explain |
| Wrong-BPM song recommendations called out as “horrible” | Recs that ignore tempo = instant distrust — tempo score prevents that failure mode |

### Design upgrades (from X, cheap)
1. **Always show both BPMs** in reason text: `tempo: 124 → 126 (Δ+2)` and if half-time path used: `via half-time (87↔174)`.  
2. **Separate score chips**: Harmonic | Tempo | Energy — never let one hide a fail on another (key-agree tools still ship wrong mixes).  
3. **Manual override affordance** later: “treat as 140 not 139.96” — field memes about rekordbox 139.96 vs 140; confidence badge if source is analyzer vs human lock.  
4. **Genre-aware copy**: DnB users think in double-time; house users rarely need “×2” — still compute, label clearly when applied.

### What not to do
- Don’t bury tempo inside a single 0–100 “mixability” without breakdown (trust failure when key tools disagree).

---

## 2. Sidecar bridge (real library → co-pilot ontology)

### Field validation
| Signal | Design implication |
|---|---|
| **MIK vs Rekordbox vs Serato key disagreement ~39% triple-agree** (circulating 2026 posts) | Sidecar must carry **provenance**: `key_source`, confidence, optional multi-analyzer. Co-pilot should say “your library’s key” not “the truth.” |
| Lexicon RB↔Serato↔Traktor convert + USB export (strong JP engagement) | Market already wants **library data as portable layer** — FSL→ontology is the same idea inward |
| Manually verified BPM/key sheets for mashups | Power users **don’t trust** one analyzer; show editable truth path |
| Ora DJ prep app: fast import, correct grid, cues | “Real library not fixtures” is table stakes for any prep product |

### Design upgrades
1. **Source badge in UI / why-next JSON**: `bpm: 126 (fsl/analyzer)` vs `fixture`.  
2. **Disagreement mode (P1)**: if later multi-source keys exist, surface “Camelot X from Migx; MIK said Y” — don’t silently pick.  
3. **One-click “reanalyze this track”** path (product, not RT) when user disputes key/BPM.  
4. **Export story**: same sidecar that feeds co-pilot should eventually feed USB/crate pack (Lexicon analogy) — one data plane.  
5. **Camelot display**: field uses Camelot natively; always show Camelot + optional traditional key.

### What not to do
- Don’t present fixture-quality certainty on real library data (key is contested industry-wide).

---

## 3. Set planner (audit + smooth order)

### Field validation
| Signal | Design implication |
|---|---|
| Claude + Spotify: BPM-sort then **LLM reorder by taste** for events | Whole-set planning is **already a user-invented workflow** — Migx native planner is the productized form |
| DJ-by-night users: Claude analyzes playlist → curates | “Next track only” is insufficient for how people prep |
| Setlist Planer tools: duration + BPM path + **energy levels** | Audit should flag **energy cliffs** once energy exists; until then flag tempo/key clunk only (honest) |
| AI setlist-from-prompt cultural reject | Planner must **propose + explain + let human edit order**, never “here’s your set, ship it” |
| Role-based set norms (opener vs headliner energy jokes) | Optional **set role / arc template** later (warmup → peak → cool) — not required V1 |

### Design upgrades
1. **Two modes, labeled**:  
   - *Audit only* — keep my order, flag clunky adjacencies  
   - *Propose order* — suggest smooth sequence (current)  
2. **Per-edge reason list** for every reordered pair: tempo Δ, Camelot step, (later energy step). Matches mashup-sheet culture.  
3. **“Clunky mix” definition in product copy** = tempo clash and/or Camelot jump beyond N, not vibes.  
4. **Human lock pins**: “keep track 3 after intro forever” while re-optimizing the rest.  
5. **Duration budget** (optional): setlist tools sell total length — if known, show estimated set minutes.  
6. Until energy ≠ 0.50: **banner** “Energy arc unavailable — ranking on key+tempo only” (avoid false confidence).

### What not to do
- Don’t auto-commit order into library playlists without Ack (taste ownership).  
- Don’t market as “AI built your set” (see setlist-ad backlash).

---

## Cross-capability design system (recommended)

| UX pattern | Applies to |
|---|---|
| **Explain chips** (tempo / key / energy) | Why-next + set planner edges |
| **Provenance** (source + confidence) | Sidecar fields |
| **Ack / edit / dismiss** | All proposals |
| **Prep-first framing** | Marketing + Settings Co-Pilot panel copy |
| **Honest missing data** | Flat energy, missing cues |

---

## Competitor / adjacent shapes (for positioning)

| Shape | vs Migx |
|---|---|
| Claude + Spotify playlist (generic LLM) | No beatmatch physics, no dual-deck, no FSL |
| Lexicon | Library portability, not ranking |
| Ora DJ | Prep UX (cues/grid); not EXO ontology/co-pilot |
| Setlist Planer web tools | BPM/energy calculators; no real library bridge |
| Mixed In Key | Key/energy analysis product; not set graph in your app |

**Wedge sentence (field-aligned):**  
*“Runs on your analyzed library (not a toy playlist), ranks mixes that can actually beatmatch, and plans the whole set — with reasons you can reject.”*

---

## Priority design polish (cheap → valuable)

| P | Change | Capability |
|---|---|---|
| 1 | Tempo reason always shows both BPMs + half-time when used | Tempo |
| 2 | Split Harmonic / Tempo scores in why-next output | Tempo |
| 3 | Provenance badge on bpm/key from FSL | Sidecar |
| 4 | Audit vs Propose modes + per-edge reasons | Set planner |
| 5 | “Energy unavailable” honesty banner when stub | Set planner |
| 6 | Manual BPM/key lock path (later, with FSL) | Sidecar |

---

## Bottom line

X **validates all three** as real frictions (wrong-tempo recs, contested/fragile library analysis, whole-set prep with Claude/Spotify). Design leverage is less “new algorithm” and more **trust UI**: explain chips, provenance, honest missing energy/cues, human-owned order. That differentiates Migx from generic LLM playlist toys **and** from key-only tools that ignore tempo.
