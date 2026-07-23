---
id: nextgen-cognitive-load-perform-arrange-library
type: knowledge
title: "NextGen — cognitive load research: PERFORM rides on ARRANGE + LIBRARY"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/knowledge/nextgen-modes-library-multideck.md
  - kanban/knowledge/nextgen-music-management-mode.md
  - kanban/knowledge/mod-music-management-mode.md
  - kanban/knowledge/nextgen-community-signal-data-sourcing.md
  - kanban/knowledge/nextgen-dj-ux-modes-and-signal.md
  - kanban/knowledge/product-discovery-customer-leadership-migx.md
related:
  - initiative-ai-djing-product
  - initiative-ui-modernization
  - nextgen-music-management-mode
  - nextgen-bakeoff-deck-strip-copilot
sources:
  - "Sweller CLT — intrinsic / extraneous / germane load; split-attention; expertise reversal"
  - "Endsley (1995) Situation Awareness — perception / comprehension / projection in dynamic systems"
  - "Wickens dual-task / multiple resource models — continuous control vs discrete decision"
  - "Clifford (& Willox) line — DJ cognitive load; digital library UX as load source (RCA/NIME ecosystem)"
  - "NIME HCI — Battle of the DJs / virtual vs hybrid setups (natural mapping vs deck mimicry)"
  - "CHI/arXiv AI-DJ cluster — selection cost, trust, no silent automation, prep vs live"
  - "X 2025–2026 field: Serato crate search as workflow win; function crates; curation vs AI setlist; Rekordbox escape tools"
  - "Owner-DJ evidence 2026-07-21 — next-track under booth load is the hard job (DC-PDCL)"
---

# Cognitive load research — why PERFORM needs ARRANGE + LIBRARY

**Thesis (research-backed product claim):** A busy-club DJ can only **PERFORM** (ride the mix with spare capacity for crowd read) when **LIBRARY** has already built external schemas offline and **ARRANGE** has already handled **projection** (what loads next). Stacking library search on the dual-deck surface is an **extraneous-load** design error.

This note is the SSoT for **cognitive science + HCI evidence** behind the modes architecture. Product surfaces live in:

| Surface | SSoT |
|---|---|
| Modes / multi-deck / chips UX | `nextgen-modes-library-multideck.md` |
| Music-management product contract | `nextgen-music-management-mode.md` |
| MODULE + judge acceptance | `mod-music-management-mode.md` |
| Community signal feasibility | `nextgen-community-signal-data-sourcing.md` |
| Owner first-hand evidence | `nextgen-dj-ux-modes-and-signal.md` |

---

## 1. Causal model (closed loop)

```text
┌──────────────── LIBRARY (prep / rescue) ────────────────┐
│ External memory: crates, tags, roles, analysis, cache   │
│ Builds long-term schemas (germane load offline)         │
└───────────────────────────┬─────────────────────────────┘
                            │ schemas available at gig
┌──────────────── ARRANGE (set brain) ────────────────────┐
│ Level-3 SA: stage 1–5, free-deck target, candidate why  │
│ Discrete decisions between phrases (scheduled dual-task)│
└───────────────────────────┬─────────────────────────────┘
                            │ next track already decided
┌──────────────── PERFORM (mix literacy) ─────────────────┐
│ Intrinsic load only: phrase, EQ, XF, crowd              │
│ Thin now/next ribbon — no dense search                  │
└─────────────────────────────────────────────────────────┘
```

**Closed-loop claim (P-01 style):**  
Trigger = booth dual-task stress → Capture = time-to-stage / NASA-TLX / mix continuity → Intelligence = mode design reduces extraneous load → Adjustment = MODULE acceptance + dogfood.

---

## 2. Foundational frameworks (transferable science)

### 2.1 Cognitive Load Theory (Sweller)

| Load | Definition | Booth mapping | Design move |
|---|---|---|---|
| **Intrinsic** | Inherent task complexity | Mixing timing, energy arc, harmonic match | Accept; train skill; don’t fake-simplify the music |
| **Extraneous** | Load from poor design | Dense tables, wrong remix ambiguity, live network, modals over waveforms, split attention | **Kill** — primary job of LIBRARY/ARRANGE UX |
| **Germane** | Load that builds schemas | Tagging, function crates, reviewing set history | Push to **LIBRARY/PREP**, not PERFORM |

**Effects that bite in DJ UIs:**

| Effect | Meaning | NextGen rule |
|---|---|---|
| **Split-attention** | Integrating two visual sources costs WM | Full-screen modes; don’t overlay library on zoom waveform |
| **Expertise reversal** | Novice scaffolds hurt experts mid-set | No wizards on PERFORM; recognition for pros |
| **Element interactivity** | Many simultaneous elements explode load | Cap candidates 3–5; stage queue short; one primary task per mode |

### 2.2 Situation Awareness (Endsley 1995)

| SA level | Operator question | Mode owner |
|---|---|---|
| **L1 Perception** | What’s on A/B? Bars left? Free deck? BPM/key? | PERFORM + **always-on ribbon** in other modes |
| **L2 Comprehension** | Energy rising? Crowd holding? Mix safe? | PERFORM (expert automaticity) |
| **L3 Projection** | What loads in 16–32 bars? | **ARRANGE** (and pre-stage in PREP) |

**Implication:** Burying L3 inside L1 chrome (skinny playlist under decks) forces projection under the same attention budget as motor control → errors, panic digs, energy drops.

**SA design principles applied:**

1. Goal-directed information (role filters: peak / closer / reset).  
2. Mental models in the tool (crates/tags = stored comprehension).  
3. Stress degrades WM → huge type, high contrast, few items.  
4. Automation must not **hide** state (silent load kills SA and trust).

### 2.3 Dual-task / multiple resources (Wickens)

Live DJing is dual-task by nature:

| Stream | Character | Competes for |
|---|---|---|
| Continuous control | EQ, XF, cue, loop | Visual+motor; audio monitoring |
| Discrete decision | Find/stage/load next | Visual search; working memory |

**Methods that preserve PERFORM:**

| Method | Application |
|---|---|
| **Task shedding** | Mid-set: no bulk organize, no prefs, no enrich network |
| **Task scheduling** | Decide next track *between* phrases in ARRANGE hop |
| **Automaticity** | Mix skills free WM only if UI doesn’t reintroduce clutter |
| **Resource separation** | Search full-screen (visual), not competing with playhead watch |

---

## 3. DJ-specific research & field evidence

### 3.1 Academic / HCI (DJ domain)

| Strand | Claim useful to Migx | Confidence |
|---|---|---|
| Clifford / Willox-style **DJ cognitive load** work | Digital library UX is a primary load source; design must externalize selection | med–high (domain-specific line; cite when PDF pinned) |
| NIME “Battle of the DJs” / virtual vs hybrid | Mimicking dual-deck chrome ≠ natural control; hybrid maps gestures better | med |
| CHI / arXiv **AI-assisted DJ** cluster | Selection is costly; silent automation rejected; prep assist > live autopilot | high (aligns with discovery + X) |
| Library organization HCI (general music + DJ tools) | Search quality and structure dominate multi-year libraries | high (industry replication) |

### 3.2 Industry / X field (2025–2026) — vernacular for modes

Nobody says “PERFORM/ARRANGE/LIBRARY.” They say:

| Vernacular | Maps to |
|---|---|
| Decks / CDJs / “don’t mess the mix” | PERFORM |
| Function crates: opener, bridge, pressure, reset, late-night weird | ARRANGE schema language |
| Crate search, organize crates, “hate Rekordbox,” Soulseek→sync escapes | LIBRARY pain / prep |
| “95% of DJing is curation” / anti–AI setlist | No silent agent DJ |
| Serato crate search = “workflow / prep speed” | Library UX = product, not polish |

**Function crates are the field invention of ARRANGE taxonomy.** Encode them as first-class chips/filters, not only genre folders.

### 3.3 Owner evidence (already load-bearing)

`nextgen-dj-ux-modes-and-signal.md`: hard job is **next-track under cognitive load**; modes are purpose-built full-screen contexts; multi-deck playable cap vs unlimited stage; community signal as EXO dimension (with honest data pipeline).

---

## 4. How each mode reduces load (design methods)

### 4.1 LIBRARY — schema factory (extraneous → germane offline)

| Method | Why (science) | UX |
|---|---|---|
| Cover art + waveform thumb | Recognition > recall under stress | Track cards, not spreadsheet-only |
| Tags + color language | Chunking / schemas | Serato-like colour; own taxonomy |
| **Function / role crates** | Goal-directed SA; field practice | opener / peak / bridge / reset / closers |
| Playlist membership chips | External memory of “where this lives” | Multi-membership visible |
| Offline analysis (BPM/key/energy) | Precompute element interactivity | Never re-analyze mid-set |
| Cached community chips | Optional L2/L3 cues; no live net | Honest kinds (see community sourcing) |
| Search quality | Cuts search cost | Crate search is table stakes |

**LIBRARY is successful when ARRANGE never needs to re-teach the DJ their own collection.**

### 4.2 ARRANGE — projection workspace (L3 SA)

| Method | Why | UX |
|---|---|---|
| Full-screen hop | Remove split-attention with PERFORM chrome | Mode bar; one key PERFORM↔ARRANGE |
| Now ribbon | Preserve L1 SA while projecting | Title, bars left, free decks |
| Stage 1–5 only | Choice overload; decision set size | Ordered stage queue |
| Filter: key-compat, energy, role, played-tonight | Goal-directed info | Chip filters |
| Co-pilot “why” + Ack | Trust; automation SA | Never silent load |
| Recognition cards | Fast identity under noise | Art + BPM/key + crates + chips |

**ARRANGE is successful when PERFORM only executes an already-chosen next load.**

### 4.3 PERFORM — residual capacity for the mix

| Method | Why | UX |
|---|---|---|
| Deck strip literacy | Industry muscle memory | Waveforms, transport, EQ, cues |
| Collapsed next-1 chip | Minimal L3 without mode switch when stable | Expand → ARRANGE |
| No dense library | Protect continuous control resources | Library is one hop away |
| Playable deck cap 4–6 | RT + cognitive span | Stage unlimited ≠ play all |
| Non-modal errors | Flow preservation | House UI rules |

**PERFORM is successful when the DJ’s working memory is about the room and the phrase, not the filesystem.**

---

## 5. Methods to *measure* the claim (research loop)

Science without a capture path is not closed-loop (P-01 / P-03 for perf; here for UX).

### 5.1 Mechanical (MODULE / judge — already sketched)

From `mod-music-management-mode.md`:

- Mode switch preserves play  
- Time budgets for search/switch (fixture)  
- Stage → load free deck + Ack only  
- No network hot path  
- Layout no-overlap screenshots  

### 5.2 Human-factors probes (dogfood / dossier wave)

| Probe | What it captures | Pass heuristic |
|---|---|---|
| **Time-to-stage** under dual-task | Extraneous search cost | p50 stage under N seconds with mix still playing |
| **NASA-TLX** (or raw TLX) after 20-min sim set | Subjective load | Lower in modes UI vs classic skinny library |
| **Freeze SA query** (SAGAT-lite) | L1/L3 awareness | Correct free deck + next energy band |
| **Error count** | Wrong remix / already-played / busy-deck load | Zero in judge; rare in dogfood |
| **Eye-track optional** | Fixations on library vs waveform | Library fixations only in ARRANGE |

### 5.3 Comparative conditions (A/B intelligence)

| Condition | Expect |
|---|---|
| A: Dual-deck + skinny list only | High TLX, slow next-track |
| B: PERFORM + full-screen ARRANGE + pre-tagged fixtures | Lower TLX, faster stage |
| C: B + co-pilot why chips | Faster when trusted; regress if silent |

---

## 6. Anti-patterns (what research + field reject)

| Antipattern | Why it fails | Cite family |
|---|---|---|
| Library always visible under decks | Split-attention; L3 under motor load | CLT split-attention |
| AI silent setlist / auto-load | Trust + SA collapse; cultural reject | CHI AI-DJ + X curation |
| Ranking only on YT views | Wrong schema (popular ≠ club tool) | Community sourcing brief |
| Live multi-API scrape mid-set | Latency + ToS + extraneous | Data sourcing + RT rules |
| Modal prefs over waveform | Flow break | Dual-task / house non-modal |
| Unlimited playable decks as default | Span + RT cost | Modes multideck + engine budget |
| Genre-only crates | Weak goal structure mid-set | Field function-crate trend |

---

## 7. Research map — what’s solid vs open

| Claim | Status | Next research step |
|---|---|---|
| Modes reduce dual-task interference | Strong theory + field analogy | Dogfood A/B + TLX |
| Function crates beat genre-only for live | Strong field; weak RCT | Fixture taxonomies in 50-track set |
| Full-screen ARRANGE > panel | Strong CLT/SA; thin DJ RCT | MODULE dogfood is the evidence |
| Community chips help mid-set | Weak / untested | Prep-only first; measure distraction |
| Crate search is load-bearing | Strong industry | Already product requirement |
| Co-pilot as L3 assist | Med; needs Ack + why | Bake-off strip+copilot |

---

## 8. Fleet wiring (how this enters the research loop)

| Agent | Consume this how |
|---|---|
| **Claude** | MODULE shell: modes, ribbon, cards; no-net hot path; function-crate filters in fixtures |
| **Codex** | Judge probes §5.1; P-08; no silent CO load; SA ribbon invariants |
| **Grok** | Refresh X/field; keep community chip honesty; signal when leaders change library UX |
| **Owner** | Value: hotkey PERFORM↔ARRANGE; playable cap; whether TLX dogfood is a dossier wave |

**Do not** open a new dossier unless dogfood measurement is scheduled — knowledge here is living SSoT; dossiers are sprints.

### Promotion path

1. Knowledge (this file) — **landed**.  
2. Signal brief → fleet awareness.  
3. MODULE acceptance already cites modes; add **cognitive-load probes** when judge exists.  
4. Optional dossier: `PS-NGM` “modes reduce TLX vs skinny library” only when owner wants formal seal.

---

## 9. One-paragraph abstract (for ADRs / PR descriptions)

Working memory is the bottleneck in live DJing. Cognitive load theory separates irreducible mix skill (intrinsic) from UI-imposed search and clutter (extraneous). Situation awareness research shows projection (“what next”) must not compete with perception of the now-playing mix. Dual-task models recommend scheduling selection between control-critical moments. Therefore NextGen uses full-screen **LIBRARY** to build schemas offline, full-screen **ARRANGE** for projection and staging, and minimal **PERFORM** for continuous control—validated by DJ HCI literature, AI-DJ trust findings, and field demand for crate search and function-based organization.

---

## 10. Related IDs (grep anchors)

- Product modes: `nextgen-modes-library-multideck`  
- MODULE: `mod-music-management-mode`  
- Community chips: `nextgen-community-signal-data-sourcing`  
- Patterns: `P-01` closed loop, `P-06` single writer, `P-08` generator≠evaluator, house RT physics when enrich jobs touch engine (they must not)
