---
id: performance-capability-uplifts-x-field-map
type: knowledge
title: "Performance & capability uplifts — X field map → Migx (macOS 26+ Apple Silicon)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md
  - kanban/knowledge/architecture-apple-silicon-macos26-refactor-map.md
  - kanban/knowledge/apple-audio-frameworks-os26-wwdc25.md
  - kanban/knowledge/arcflow-m4-perf-techniques.md
  - kanban/Strategy-Current.md
related:
  - kanban/initiatives/initiative-apple-silicon.md
  - kanban/initiatives/initiative-experience-ontology.md
  - kanban/initiatives/initiative-ai-djing-product.md
  - kanban/federation/signal/2026-07-17-deep-x-community-alignment.md
  - kanban/tasks/tahoe-m4-soundio-soak-rebaseline.md
sources:
  - "https://x.com/VipulDivyanshu/status/2029070807914193379"
  - "https://x.com/ulmentflam/status/2077118506009579659"
  - "https://x.com/antirez/status/2058163603119763510"
  - "https://x.com/eugenebokhan/status/2035121338432565520"
  - "https://x.com/mike64_t/status/1932742185276903629"
  - "https://x.com/Raullen/status/2073434533891043460"
  - "https://x.com/bstnxbt/status/2043696397388554447"
  - "https://x.com/0xClandestine/status/2044381562926457335"
  - "https://x.com/sanchitmonga22/status/2030190754367426841"
  - "https://x.com/bassmicrobe/status/2049869426158432259"
  - "https://x.com/rebutter_/status/2069634857823781140"
  - "https://x.com/amot_amot_amot/status/2031715079889309956"
  - "https://x.com/somi_ai/status/2061250227831820761"
  - "https://x.com/mauricekleine/status/2075612977659617305"
  - "https://x.com/aakashgupta/status/2008323156780736669"
note: >
  X-grounded ranking of where Migx should invest for perf + capability on the
  only supported platform. Complements the architecture refactor map (how);
  this note is what + why (field signal).
---

# Performance & capability uplifts — X field → Migx

Deep scan of **X (mid‑2025 → mid‑2026)** around Apple Silicon compute, Metal, MLX, Core Audio /
pro-audio latency culture, local audio AI, and DJ-relevant tooling — then mapped onto Migx’s
**macOS 26+ · arm64-only** floor ([ADR-006](../architecture/decisions/ADR-006-platform-scope-apple-silicon.md))
and the feature-preserving refactor program
([architecture-apple-silicon-macos26-refactor-map](architecture-apple-silicon-macos26-refactor-map.md)).

**Thesis from the field:** the community optimizes **three different games**. Migx must win **game A**
and selectively borrow from **B/C** without polluting the RT path.

| Game | What X optimizes | Migx stance |
|---|---|---|
| **A. Real-time audio trust** | Core Audio simplicity, low latency, no glitches | **Primary product trust** |
| **B. On-device AI throughput** | MLX / Metal / ANE tok/s, speculative decode | **Worker / co-pilot only** |
| **C. Spatial / capture cool** | FOA, Audio Mix, AirPods HQ | **Sidecar features**, not decks |

---

## 1. Executive ranked opportunity board

Priority = **(field heat × Migx fit × feature preservation)** under house physics (`P-02`).

| Rank | Opportunity | Class | X heat | Migx domain | Wave |
|---|---|---|---|---|---|
| **1** | **Underrun-proof Core Audio path** (exclusive, buffer, device flake soak on 26) | Perf + stability | High (pro culture) | `arch-audio-io` | W1 |
| **2** | **Metal-native waveform / rendergraph** (UMA, zero-copy, persistent buffers) | Perf + stability | High (UMA discourse) | waveform / rendergraph | W3 |
| **3** | **Accelerate/vDSP on engine hotspots** (EQ, scale, filters, analysis prep) | Perf | Med-High (implied via “use Apple libs”) | engine / effects | W4 |
| **4** | **CoreAudio-first decode** (ALAC/AAC/CAF) on workers | Perf + capability | Med | sources | W4 |
| **5** | **Worker-side on-device AI** (MLX stems/structure/embeddings for EXO) | Capability | **Very high** | analyzer / EXO | W7 / research |
| **6** | **Heterogeneous offload policy** (CPU vs Metal vs ANE for non-RT) | Perf architecture | High | analyzer, co-pilot | W4–W7 |
| **7** | **Co-pilot latency as product** (local ranker first; LLM off hot path) | Capability | High (harness + local LLM) | Layer B/C | W6 |
| **8** | **Native Core Audio SoundDevice** (if PA is ceiling) | Perf | Med | soundio | W5 optional |
| **9** | **OS 26 FOA / AUAudioMix / rec** | Capability | Med | rec sidecar | W7 flags |
| **10** | **Mac clustering / multi-machine AI** | Capability (fringe) | Med | out of scope | Park |

**Anti-opportunities (X noise — do not chase as RT wins):**

| Noise | Why skip for Migx RT |
|---|---|
| Peak LLM tok/s races (M4 Max vs M3 Ultra drama) | Not the audio deadline |
| Speculative decoding / DFlash | Co-pilot worker only |
| Metal4 neural accelerator brag posts | Great for MLX; forbidden on `process*()` |
| Windows ASIO envy | We already chose Mac (field: DJs cite Core Audio as reason to use Mac) |
| Cloud stem SaaS | Local-first is the X prestige path for tools |

---

## 2. Field themes (what X is actually saying)

### 2.1 Core Audio is why DJs/producers stay on Mac

**Signal:** Japanese/English pro and DJ posts treat **Core Audio** as the reliability differentiator vs
Windows ASIO/MME complexity; multi-channel DVS into DAW “Mac Core Audio is competent” moments.

**Examples:** [@bassmicrobe](https://x.com/bassmicrobe/status/2049869426158432259) (DJ + Mac Core
Audio vs Windows audio hell); [@rebutter_](https://x.com/rebutter_/status/2069634857823781140)
(studio Pro Tools + kernel-level Core Audio trust).

**Counter-signal:** Tahoe-era caution — some DAWs slow to green-light OS 26; Core Audio “still has
issues” chatter ([@amot_amot_amot](https://x.com/amot_amot_amot/status/2031715079889309956)).

**Migx uplift:**

| Opportunity | Action | Metric |
|---|---|---|
| Prove 26.x stability | `tahoe-m4-soundio-soak-rebaseline` | xruns = 0; device-change survival |
| Prefer CA semantics in prefs UX | Exclusive, buffer, aggregate clarity | User can hit &lt;5–10 ms class paths when HW allows |
| Don’t fight the OS | Validate PA→CA; rewrite only if EVD proves ceiling | p99 buffer time |

**Capability without feature loss:** every existing routing/vinyl/clock-ref feature stays; we improve
**trust** and **latency headroom**.

---

### 2.2 Unified memory + Metal: stop paying PC GPU taxes

**Signal:** Engineers emphasize Apple Silicon **coherent CPU–GPU memory** — traditional discrete-GPU
copy habits are the wrong mental model ([@mike64_t](https://x.com/mike64_t/status/1932742185276903629)
on UMA / bandwidth). Metal Performance Primitives / cooperative tensor / M5 memory layout posts show
Apple is still investing in **GPU math primitives**
([@eugenebokhan](https://x.com/eugenebokhan/status/2035121338432565520)). Hand-tuned Metal can beat
naïve MPS; **MLX still often leads** for ML
([@ulmentflam](https://x.com/ulmentflam/status/2077118506009579659)). Neural Accelerator via Metal
APIs shows up in “now fast on M5 Max” shipping software
([@antirez](https://x.com/antirez/status/2058163603119763510)).

**Migx uplift:**

| Opportunity | Domain | Guardrail |
|---|---|---|
| Zero-copy / persistent waveform VBOs | `arch-waveform-render` | `P-21` GPU never gates audio |
| Metal-preferred RHI path only | rendergraph / allshader | Feature parity before delete GL |
| No per-frame CPU→GPU waveform reupload | `P-22` / `AP-12` | EVD frame time p99 |

**Capability without feature loss:** same cues/RGB/overview/stems marks — faster, smoother UI under
load (dual waveform + library + co-pilot chrome).

---

### 2.3 MLX / on-device AI is the loudest “capability” market

**Signal:** Explosive energy on **lossless speedups**, speculative/MTP decode, fused Metal quant
kernels, ANE+GPU hybrid inference
([@Raullen](https://x.com/Raullen/status/2073434533891043460),
[@bstnxbt](https://x.com/bstnxbt/status/2043696397388554447),
[@0xClandestine](https://x.com/0xClandestine/status/2044381562926457335)).
ANE efficiency bragging (TFLOPS/W)
([@VipulDivyansju](https://x.com/VipulDivyanshu/status/2029070807914193379)).
Local TTS/RTF on Metal
([@sanchitmonga22](https://x.com/sanchitmonga22/status/2030190754367426841)).

**What this means for Migx (carefully):**

| Use MLX / Metal ML for | Never use for |
|---|---|
| Stem separation **offline / worker** | Anything on `process*()` |
| Structure / energy / embedding for EXO | Synchronous deck load |
| Optional local co-pilot LLM | Audio callback, CO spam |
| Analyzer batch jobs | Blocking GUI thread |

**Capability uplift (features *gained*, RT unchanged):**

1. **Local stems** competitive with StemDeck/Ableton narrative (X: local &gt; cloud SaaS prestige)  
2. **Track embeddings** for “what’s next” beyond Camelot (field: MuQ-class hobby tools)  
3. **On-device privacy co-pilot** (aligns Strategy freemium + privacy mode)

**Perf metric for this lane:** wall-clock analyze time / track on M4; **not** audio buffer p99.

---

### 2.4 Heterogeneous acceleration is the architecture story

**Signal:** “ANE + GPU in parallel — M-series was designed for this”
([@0xClandestine](https://x.com/0xClandestine/status/2044381562926457335)).
Arcflow-style **route then kernel** (already in `arcflow-m4-perf-techniques.md`) matches X’s
heterogeneous narrative.

**Migx uplift:** explicit **policy layer**:

```text
Work item
  → classify: RT | worker-CPU | worker-Metal | worker-ANE | GPU-display
  → never promote worker→RT
  → measure each lane with the right metric
```

This is the structural way to “double down on M-series” **without** feature loss or RT regressions.

---

### 2.5 Pro latency culture: exclusive + small buffers + full-chain profile

**Signal:** Cross-platform live audio advice still: exclusive drivers, small buffers, profile the
whole chain (GPU dispatches can add delay)
([@grok reply culture](https://x.com/grok/status/2076787698904240578) summarizing sub-20 ms targets).
Mac users report Scarlett-class interfaces under ~5 ms with Core Audio shared/exclusive setups.

**Migx uplift:**

| Capability | Product surface |
|---|---|
| Safe low-latency presets | “Gig mode” buffer recipes for M4 + common interfaces |
| Full-chain budget | Audio p99 + UI frame p99 + co-pilot worker SLO separately |
| Device change resilience | Soak tests (W1) — community still hits Tahoe/device flakes |

---

### 2.6 Local audio AI & DJ tooling (capability, not RT)

**Signal:** Local Demucs/StemDeck “fast on Apple Silicon”; embedding+BPM/key matchers for set building;
Ableton GPU stems as producer table-stakes (prior scouts).

**Migx uplift:**

| Capability | How without losing features |
|---|---|
| Stem prep | Worker job → stem files / EXO tags; decks play results |
| Smart next-track | Offline ranker now; embeddings later on worker |
| Library intelligence | EXO + FSL; never blocks load |

---

### 2.7 Harness / co-pilot performance (meta)

**Signal:** “Agent harnesses are the new agents” — long-running reliability over model peak
([@aakashgupta](https://x.com/aakashgupta/status/2008323156780736669)). Local LLM desks for private
agent work (M4 Max “fast enough that workflow stops feeling rented”).

**Migx uplift:**

| Opportunity | Why it matters |
|---|---|
| Deterministic EXO ranker on hot path | Instant “why next” (already dogfood) |
| LLM only for slow reasoning | Protects RT + battery |
| Session artifacts on disk | Survives context window death (harness lesson) |

---

## 3. Opportunity deep-dives (actionable)

### P1 — Audio deadline supremacy (stability + perf)

**X says:** Core Audio is the Mac moat; OS 26 still needs proof.  
**Architecture:** Wave 1 of refactor map; `arch-audio-io`.  
**Work:**

1. Soak EVD (built-in / USB / BT; exclusive/shared)  
2. Publish “Gig mode” defaults for M4  
3. Only then consider native CA `SoundDevice`  

**Uplift:** lower achievable buffer sizes, fewer xruns under dual-deck + waveform + library.  
**Features kept:** 100% routing/vinyl/controller.

---

### P2 — Display path Metal / UMA (stability + perceived perf)

**X says:** UMA makes zero-copy the default mindset; Metal primitives still evolving (MPP, Metal4).  
**Architecture:** Wave 3; MTL dossiers.  
**Work:**

1. allshader feature parity matrix  
2. Persistent VBO / zero-copy (EVD)  
3. Retire deprecated GL  

**Uplift:** smoother dual waveforms under load; less CPU steal from audio cores.  
**Features kept:** all waveform/cue visuals after parity gate.

---

### P3 — Accelerate on DSP hotspots (perf)

**X says:** “Use Apple’s stack” (MLX/Metal/ANE); for DSP the analogue is **Accelerate**, not hand NEON
first ([arcflow note](arcflow-m4-perf-techniques.md)).  
**Architecture:** Wave 4.  
**Work:**

1. Profile `process*` top consumers  
2. vDSP swaps with golden tests (epsilon policy)  
3. Analyzer FFT/filterbank via Accelerate  

**Uplift:** headroom for more effects/decks/keylock at same buffer.  
**Features kept:** same DSP feature set; sound within documented epsilon.

---

### P4 — Decode path CA-first (perf + battery)

**X says:** less direct; follows “native frameworks win.”  
**Work:** provider ranking so ALAC/AAC prefer CoreAudio; FFmpeg long tail.  
**Uplift:** faster load/analyze, less energy on library ops.  
**Features kept:** all formats still open via FFmpeg fallback.

---

### P5 — On-device music AI capability suite (workers)

**X says:** loudest capability market of 2026 on Mac.  
**Work packages (feature *adds*):**

| Package | X analogue | Migx delivery |
|---|---|---|
| Local stems | StemDeck / Ableton | Worker → library stems |
| Embeddings | MuQ hobby matchers | EXO edges / ranker features |
| Structure/energy | Analyzer research task | EXO sections (replace hand stubs) |
| Local co-pilot LLM | MLX desk culture | Layer C optional; never RT |

**Uplift:** co-pilot quality and privacy without touching RT deadline.  
**Features kept:** classic decks always work offline-of-AI.

---

### P6 — Full-chain SLOs (product trust)

**X says:** profile the whole chain; GPU can add latency.  
**Define three SLOs:**

| Lane | Metric | Gate |
|---|---|---|
| RT audio | p99 buffer time, xruns | zero underruns |
| UI/Metal | p99 frame time | no audio correlation |
| Co-pilot worker | p95 intent proposal time | &lt;100 ms deterministic; LLM async |

This matches X’s separation of “local AI desk speed” vs “live audio feel.”

---

## 4. Capability uplift map (product features *gained*)

| Capability | Field demand | Depends on | Blocks nothing if delayed |
|---|---|---|---|
| Gig-mode low-latency profile | High | W1 soak | — |
| Butter-smooth dual waveforms on M4 | High | W3 Metal | — |
| Local stem prep | High | W7 MLX/Demucs worker | Decks still full mix |
| Embedding “crate intelligence” | Med-High | EXO + analyzer | Camelot ranker works today |
| Privacy-local co-pilot LLM | Med | Layer C | Deterministic why-next works |
| Spatial rec / Audio Mix tools | Med | OS26 APIs | Optional |
| MusicKit prep crate | Med | Rights | Spotify-style prep path |

---

## 5. Explicit non-investments (X can wait)

| Topic | Field heat | Migx decision |
|---|---|---|
| Win the LLM tok/s leaderboard | Extreme | No — not product |
| Multi-Mac MLX clustering | Rising | Park (single-machine DJ) |
| Cloud stem APIs | High marketing | Prefer local |
| ASIO-on-Windows port | Eternal | Out of platform scope |
| RT neural nets on callback | Recurring fantasy | Forbidden (`P-02`) |

---

## 6. Alignment to refactor waves

| Wave | Perf / capability from this note |
|---|---|
| **W1** SoundIO soak | P1 stability proof |
| **W2** Platform prune | Free CI/CPU from foreign OS; focus engineering |
| **W3** Metal waveforms | P2 UMA/zero-copy |
| **W4** Accelerate + CA decode | P3/P4 |
| **W5** Native CA device | P1/P8 if needed |
| **W6** QML + CO co-pilot | P6/P7 product latency |
| **W7** MLX/stems/OS26 | P5 capability suite |

---

## 7. Suggested OKRs (north-star compatible)

| Objective | Key results (examples) |
|---|---|
| **O1 Underrun-free on 26+M4** | Dual-deck soak EVD: 0 xruns @ documented buffer; survives device switch |
| **O2 UI never steals the gig** | Waveform p99 frame under load; no correlation with audio xruns |
| **O3 DSP headroom** | ≥N% reduction p99 process time on top 3 hotspots via Accelerate (EVD) |
| **O4 Capability without cloud** | Local stem job + EXO energy/structure from analyzer on M4 within T seconds/track |
| **O5 Co-pilot snappy** | Deterministic why-next &lt;100 ms; LLM suggestions async |

---

## 8. Claims table (confidence)

| Claim | Conf. | Evidence class |
|---|---|---|
| DJs/producers treat Core Audio as Mac’s reliability moat | **high** | JP/EN pro + DJ posts |
| Tahoe/26 still needs validation, not assumption | **med-high** | DAW green-light lag, flake talk |
| UMA makes zero-copy GPU buffers the correct default | **high** | Eng discussion + Migx P-21/22 |
| On-device ML (MLX/Metal/ANE) is the loudest Mac capability race | **high** | Sustained high-engagement posts |
| That race must stay off the audio callback | **high** | House physics + live-audio latency culture |
| Local stems/embeddings are the DJ-adjacent capability uplifts | **high** | StemDeck + set-matcher field |
| Speculative decoding is irrelevant to RT mix quality | **high** | Domain separation |
| Multi-Mac clustering is not a DJ product need | **med** | AI-supercomputer narrative |

---

## 9. Immediate actions (ordered)

1. **Run W1** — `tahoe-m4-soundio-soak-rebaseline` (field: prove Core Audio trust on 26).  
2. **Keep W3 path clear** — allshader parity before GL delete (field: UMA/Metal is the render bet).  
3. **Open DSP inventory** — top `process*` consumers → Accelerate candidates (field: use Apple math).  
4. **Park MLX stems behind worker design** — feature add, not RT rewrite (field: local AI prestige).  
5. **Publish three SLOs** in ASI initiative (audio / UI / co-pilot).  

---

## 10. One-line field alignment

**X is screaming about local AI tok/s and Metal ML — Migx should harvest that on workers for stems,
embeddings, and private co-pilot, while the product’s real moat remains what pro Mac users already
believe: Core Audio that never glitches, plus Metal UI that never steals the audio cores.**
