---
id: research-onbeat-play-phase-snap
type: knowledge
title: "Research — on-beat play / instant phase snap (always-on-beat PLAY)"
status: research
owner: gudjon
authored_by: grok-signal
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/knowledge/nextgen-cognitive-load-perform-arrange-library.md
  - kanban/knowledge/nextgen-modes-library-multideck.md
  - res/design/KEYMAP.md
related:
  - kanban/knowledge/arrange-nexttrack-copilot-scoring.md
  - kanban/knowledge/copilot-transition-intelligence.md
  - kanban/knowledge/migx-brand-positioning-experience-designer.md
  - kanban/knowledge/oz-audio-engine-learnings.md
  - initiative-ai-djing-product
  - initiative-ui-modernization
sources:
  # Competitive / product
  - "Serato DJ — Sync, Smart Sync, Quantize (help.serato.com): tempo+phase; quantize on hot cues/loops/roll; play not fully launch-quantized like Ableton"
  - "Native Instruments Traktor — Beat Sync / Phase Sync / Tempo Sync; Snap/Quantize for cues/loops; master deck timebase"
  - "Pioneer DJ rekordbox / CDJ — Beat Sync, Quantize, Beat Jump; club literacy for on-grid actions"
  - "Ableton Live — Launch Quantization (none / 1/16 … 1 bar … 8 bars): wait-for-boundary paradigm (Mode B)"
  - "VirtualDJ / Engine DJ / djay — auto BPM + sync variants; consumer ‘press play and it works’ expectation"
  # MIR / DSP
  - "Davies, Degara, Plumbley — Evaluation methods for musical audio beat tracking (C4DM tech report / ISMIR lineage)"
  - "Böck et al. — multi-model beat tracking; madmom; F-measure + CMLt/AMLt continuity metrics"
  - "Ellis — beat tracking by dynamic programming (classic MIR baseline)"
  - "McFee & Ellis — robust onset aggregation for beat tracking"
  - "Meier & Müller (TISMIR 2024) — real-time PLP beat tracking, zero-latency / lookahead for interactive software"
  - "MIREX Audio Beat Tracking — annual bake-off; F-measure, continuity, metrical-level confusion"
  - "Goto / PLP (predominant local pulse) lineage — tempo-periodicity for online pulse"
  # Perception / HCI
  - "London — Hearing in Time (meter, entrainment)"
  - "Large & Palmer — phase correction in sensorimotor sync (humans tolerate / correct small phase error)"
  - "Sweller CLT; Endsley SA — cited via nextgen-cognitive-load-perform-arrange-library"
  # Code (Migx / Mixxx)
  - "src/engine/sync/synccontrol.cpp — beatsync, beatsync_phase, beatsync_tempo, sync_enabled"
  - "src/engine/controls/bpmcontrol.cpp — getBeatDistance, getPhaseOffset, calcSyncAdjustment, findClosestBeat path"
  - "src/engine/controls/quantizecontrol.cpp — [Group],quantize"
  - "src/engine/enginebuffer.cpp — requestSyncPhase; quantize on play/repeat paths"
  - "src/track/beats.h — findNextBeat, findPrevBeat, findClosestBeat, iteratorFrom"
---

# Research — on-beat play / instant phase snap

**Owner idea (2026-07-23):** As a *simplicity* feature — when the DJ presses **PLAY** on a deck while another track is already playing, the new deck should **immediately** start **on-beat** relative to what is already sounding: no manual nudge, no “wait for the next bar” silence if we can avoid it. Default **ON**. Mixing becomes “stupid simple”: the system is always configured for on-beat start; the reward is **instant auditory confirmation**.

**One-line verdict:** **Feasible now** by composing Mixxx/Migx beatgrids + existing sync/phase/quantize COs into a **default-on PLAY policy** (instant phase jump). Deep MIR/DNN improves grid *quality* and phrase awareness; it is **not** required for a v1 “always on-beat play” product if grids are good. The hard problems are **defaults, failure honesty, and latency of reward** — not inventing beat math.

**Not Automix.** This is **assistive transport**, not track selection. Selection stays human or ARRANGE co-pilot; PLAY only fixes *when* the sample starts relative to the master pulse. Aligns with Ritual brand / anti-Automix posture.

**Execution home (later):** Open a short dossier when implementing (prefix TBD in `prefix-registry.yaml`). This file is the **research SSoT** until then — not a sealed sprint.

---

## 1. Problem definition

### 1.1 Job to be done

| | |
|---|---|
| **When** | PERFORM: at least one playable deck is already running; DJ loads/cues another and hits PLAY |
| **I want** | The new deck to enter the mix already phase-aligned (and usually tempo-aligned) |
| **So that** | I get immediate musical reward, zero “is it on?” dual-task load, and mixing feels default-safe |

### 1.2 What “on-beat” means (precision)

Let deck **A** be the **timebase** (sync leader / NOW / main-playing).  
Let deck **B** be the deck receiving PLAY.

Define fractional **beat phase** φ ∈ [0, 1) from the beatgrid:

```text
φ(deck, t) = distance_from_previous_beat(t) / beat_period(t)   // or Beats iterator equivalent
```

**On-beat start** means at the first audible sample after PLAY:

```text
φ(B, t_start) ≡ φ(A, t_start)   (mod 1 beat)
```

Optional stronger forms:

| Level | Constraint | Musical effect |
|---|---|---|
| **Beat** | φ mod 1 | Kick-aligned; may start mid-bar of B |
| **Bar** | φ mod 4 (4/4) | Phrase-safer; larger seek jumps |
| **Phrase** | φ mod 16/32 + structure tags | Club-DJ ideal; needs phrase markers |

v1 recommendation: **beat** default; **bar** as preference; phrase later via intro/outro/EXO.

### 1.3 Two UX paradigms (must not confuse)

| | **Mode A — Instant phase jump** (owner ask) | **Mode B — Wait for boundary** (Ableton launch quantize) |
|---|---|---|
| **Behavior** | Seek B so its playhead is already at matching φ, then open audio **now** | Arm PLAY; hold silent or muted until next beat/bar of A |
| **Latency** | ~0 extra (one seek + same/next buffer) | Up to 1 beat or 1 bar of *waiting* |
| **Reward** | Immediate sound | Delayed sound; cleaner “drop on 1” |
| **Risk** | Starts mid-phrase of B content | Feels laggy; violates “instant reward” |
| **Industry** | DJ sync phase-lock + play | Ableton Live clip launch quantize |

**Owner language maps to Mode A.** Mode B remains a power option (“start on next 1”).

### 1.4 Non-goals (research scope)

- Choosing *which* track to play (ARRANGE / co-pilot / transition intelligence)
- Full Automix / hands-off set generation
- Replacing beatgrids with live MIR on the RT callback
- Vinyl absolute-position magic without timecode analysis

---

## 2. Competitive & prior art

| Product | What exists | Gap vs owner ask |
|---|---|---|
| **Serato** | Sync (tempo+phase), Smart Sync (key-aware rate), **Quantize** for hot cues / loops / roll / slip reverse | Quantize is not primarily “PLAY always phase-jumps”; skill still expected for transport |
| **Traktor** | Tempo Sync / Phase Sync / full Beat Sync; Snap + Quantize for cue/loop; master deck | Power-user surface; defaults not “stupid simple” |
| **rekordbox / CDJ** | Beat Sync, Quantize, Beat Jump; club-standard literacy | Hardware culture: quantize on *actions*, not always invisible PLAY |
| **Ableton Live** | Launch Quantization (Mode B) | Opposite latency tradeoff; DAW not booth-first |
| **VirtualDJ / Engine / djay** | Auto BPM, sync, consumer “it just works” | Quality of grids + phase honesty varies; still multi-step in pro modes |
| **Mixxx / Migx (today)** | `quantize`, `beatsync`, `beatsync_phase`, `beatsync_tempo`, `sync_enabled`, `requestSyncPhase()`, `Beats::findClosestBeat` | **Composition + default policy missing**: PLAY does not equal “instant on-beat vs master” as a product default |

**Insight:** The industry ships **tools** (sync, quantize). The owner asks for a **policy**: PLAY *is* on-beat, default ON, zero thought. That is a **product differentiator** on top of commodity engine features — not a paper algorithm.

---

## 3. Technology stack (layers)

```text
┌─────────────────────────────────────────────────────────────┐
│  L4  Musical intelligence (optional)                         │
│      phrase / intro-outro / EXO structure / transition prior │
├─────────────────────────────────────────────────────────────┤
│  L3  Tempo lock                                              │
│      one-shot or continuous BPM×rate match to timebase       │
├─────────────────────────────────────────────────────────────┤
│  L2  Phase snap (core of this research)                      │
│      seek so φ(B)=φ(A); Mode A instant vs Mode B arm-wait    │
├─────────────────────────────────────────────────────────────┤
│  L1  Beatgrid / meter (offline)                              │
│      beat positions, BPM path, bar phase, confidence         │
└─────────────────────────────────────────────────────────────┘
         ▲
         │ analysis worker (never RT callback)
```

### 3.1 L1 — Beatgrid & meter (offline)

**Classical pipeline**

1. Onset strength envelope (spectral flux, complex domain, multi-band)
2. Tempo / period estimation (autocorrelation, tempogram, PLP)
3. Beat tracking (DP, HMM/DBN, multi-model)
4. Optional downbeat / bar tracking
5. User edit (Serato/rekordbox-style grid editor) → ground truth for that library

**DNN / modern MIR**

- madmom / Böck-class RNN+DBN beat & downbeat
- TCN sequence labeling beat trackers
- Joint tempo–beat–downbeat models (ISMIR 2014–2020 lineage)
- Real-time PLP (Meier & Müller 2024) for *live* pulse — useful for re-grid or input, **not** required if PLAY only reads a stored grid

**Evaluation (what “good grid” means)**

| Metric | Meaning for on-beat play |
|---|---|
| **F-measure** (±70 ms typical window) | Local hit rate of beat times |
| **CMLt / AMLt** | Continuity at correct / allowed metrical level |
| **Phase error** (mean absolute φ error) | **Directly** predicts snap quality |
| **Metrical octave errors** (½× / 2× BPM) | Catastrophic for phase + tempo lock |

**Product rule:** store `grid_confidence` (or reuse analyzer quality). Below threshold → **do not claim** on-beat; degrade honestly.

### 3.2 L2 — Phase snap (core algorithm)

**Inputs**

- Timebase deck A: `frame_A`, `Beats_A`, rate/BPM effective
- Incoming deck B: intended start `frame_B0` (cue / current pause pos / intro), `Beats_B`
- Snap unit: beat | bar
- Mode: A (instant) | B (wait)

**Mode A — Instant phase jump (recommended default)**

```text
φ_A = beat_phase(A, frame_A)                    # ∈ [0,1) or bar-normalized
candidates = beats near frame_B0 on B           # prev/closest/next family
frame_B* = argmin_f | beat_phase(B, f) − φ_A |  # same phase class
           preferring minimal |f − frame_B0|    # stay near DJ’s intent
seek(B, frame_B*)
play(B)                                         # same control edge if possible
```

Mixxx already exposes the pieces:

| Need | Code / CO |
|---|---|
| Fractional beat distance | `BpmControl::getBeatDistance(FramePos)` |
| Phase offset to align | `BpmControl::getPhaseOffset` + sync path |
| Request alignment | `EngineBuffer::requestSyncPhase()` |
| Closest beat | `Beats::findClosestBeat` / next / prev |
| Quantize flag | `[ChannelN],quantize` (`QuantizeControl`) |
| One-shot phase sync | `[ChannelN],beatsync_phase` |
| Tempo sync | `[ChannelN],beatsync_tempo` / `beatsync` / `sync_enabled` |

**v1 implementation shape (policy, not new DSP):**

```text
on Play(B):
  if onbeat_play_enabled AND exists_playing_timebase(A) AND grids_ok(A,B):
    if tempo_lock_enabled: one_shot_or_enable tempo match B→A
    phase_snap_seek(B, φ(A))   # Mode A
    start_playback(B)
  else:
    legacy_play(B)
```

Optional: bind as explicit CO `play_onbeat` / preference `OnBeatPlay` default true in PERFORM.

**Mode B — Wait for boundary**

```text
on Play(B):
  arm B; compute t_boundary = next beat/bar of A
  at t_boundary: seek B to matching downbeat class; start
```

Feels like Ableton; use for “drop on 1” power users — **not** the default if the goal is instant reward.

### 3.3 L3 — Tempo lock

| Strategy | Behavior | Use |
|---|---|---|
| **One-shot** | Match BPM×rate at PLAY; free after | Feels natural; DJ can nudge |
| **Soft lock** | Continuous phase adjust (`calcSyncAdjustment`) while both play | Classic sync; can feel “rubber” |
| **Lock then free** | Soft lock for N bars then release | Hybrid |
| **Safe window only** | Tempo match only if \|BPM_A − BPM_B\| / BPM_A < ε (e.g. 6–8%) | Avoid chipmunk / extreme stretch |

Half/double detection: Mixxx already reasons about `kBpmHalve` / `kBpmDouble` in `SyncControl` — on-beat play must inherit that or DJs get “on phase” at wrong meter.

### 3.4 L4 — Musical intelligence (optional polish)

Not required for “on phase,” but upgrades “on the right *part* of the track”:

| Signal | Role |
|---|---|
| Intro/outro cues | Prefer mix-in point as `frame_B0` before phase snap |
| Phrase / structure (EXO) | Snap unit = phrase; cold-start structure tags |
| Transition priors (`transitions.json`) | ARRANGE chooses *what*; on-beat play still owns *when* |
| Energy / vocal activity | Avoid starting B on a vocal pile-up (advanced) |

**Separation of concerns (product architecture):**

```text
ARRANGE / co-pilot  →  which track, which region (cue/intro)
On-beat play        →  phase/tempo so start is musical vs NOW
PERFORM             →  faders, EQ, FX, crowd — spare capacity
```

---

## 4. Perceptual science (why small phase error matters)

- Humans **entrain** to a pulse (London; Large & Palmer). Phase errors of a few percent of beat period are audible as “dragging” or “rushing,” especially on kick-heavy material.
- At 128 BPM, beat period ≈ 469 ms. **±10 ms** phase error ≈ 2% of a beat — often acceptable; **±40–70 ms** is the classic MIR annotation window but can feel sloppy on four-on-the-floor.
- **Product acceptance** should use **phase error in ms and in % of beat**, not only MIR F-measure of the grid analyzer.

**Immediate reward loop (cognitive load):**

```text
PRESS PLAY → sound within ~1 buffer → brain confirms “I started the mix”
```

vs

```text
PRESS PLAY → silence until next bar → dual-task anxiety (“did it arm?”)
```

Ties to `nextgen-cognitive-load-perform-arrange-library.md`: reduce dual-task load on transport so attention stays on crowd and blend.

---

## 5. Failure modes & honest degradation

| Failure | Symptom | Mitigation |
|---|---|---|
| Bad / missing grid | “On-beat” but wrong | Confidence gate; raw play; UI “no grid” |
| Half/double BPM | Phase “ok” but bar wrong | Meter detect; prefer bar snap when uncertain |
| Swing / shuffle / live band | Grid assumes straight 4/4 | Genre/crate policy; allow raw play |
| Two decks playing, no clear leader | Snap to wrong timebase | Explicit NOW / sync leader / main-out rule |
| Extreme BPM delta | Stretch artifacts | Safe window; phase-only without tempo |
| Intentional off-beat art | Feature fights DJ | Modifier: **raw play** (hold Shift / preference off) |
| Seek discontinuity | Click / drop | Equal-power short cross or zero-crossing; existing engine seek path |
| Mode B wait | Feels broken if user expected Mode A | Don’t default Mode B for PERFORM simplicity |

**Trust rule:** One bad automatic snap costs more trust than ten manual nudges. Prefer **skip assist** over **wrong assist**.

---

## 6. House physics & RT safety

| Rule | Implication |
|---|---|
| **P-02** no alloc/lock on RT | Grid already in memory; phase math uses existing `Beats` iterators; no MIR on callback |
| **P-06** one writer per CO | Define single writer for any new `play_onbeat` / preference COs |
| **P-16** lock-free handoff | Analysis results published like today’s track beats — not mutex on play |
| **P-03 / P-18** | If claiming “immediate,” measure **p99 time-to-audible** and **phase error**, not mean “feels fine” |

Seek + play must use existing engine paths (`EngineBuffer` seek/play). New code is **policy at the play edge**, preferably GUI/controller thread setting COs, not novel RT DSP.

---

## 7. Product design (Migx / Ritual)

### 7.1 Naming (pick in branding pass)

| Candidate | Notes |
|---|---|
| **On-beat play** | Clear, technical |
| **Phase snap** | Accurate for Mode A |
| **Instant lock** | Consumer-friendly |
| **Swing-in** | Owner metaphor; may confuse with musical swing |
| **Always on-beat** | Feature family name |

Avoid: AutoDJ, Automix, Smart Mix (brand clash).

### 7.2 Defaults

| Context | Default |
|---|---|
| PERFORM | **ON**, Mode A, snap = **1 beat**, tempo one-shot within safe window |
| ARRANGE preview | ON (same) so prep matches booth |
| LIBRARY audition | OFF or headphones-only no snap (browse ≠ mix) |
| Power user | Preference: snap unit beat/bar; Mode A/B; raw-play modifier |

### 7.3 KEYMAP / controls

- PLAY remains PLAY (no new primary key).
- Document **raw play** modifier (e.g. Shift+PLAY) in `res/design/KEYMAP.md` if shipped.
- Controller: map optional “on-beat play toggle” only if needed; default should not require a button.

### 7.4 Visual / haptic feedback

- Waveform / beat markers of B **click** into alignment with A at the moment of play.
- Optional controller LED blink on successful snap; different pattern on degrade-to-raw.

---

## 8. Acceptance contract (research → future PS)

Machine-consumable targets for a later problem statement:

```yaml
# draft — not a sealed PS yet
id: PS-OBP-01  # prefix register before dossier
acceptance:
  - metric: phase_error_ms
    threshold: "p95 < 15ms vs timebase at first audible buffer after PLAY"
    setup: "two decks, known synthetic grids, A playing steady"
  - metric: time_to_audible_ms
    threshold: "p95 < 1.5 × audio_buffer_ms (Mode A); no intentional bar wait"
  - metric: underruns
    threshold: 0 during 100 play presses
  - metric: degrade_honesty
    threshold: "missing grid → no false snap; UI/log reason"
  - judge: "tools/ng-judge or engine test fixture (offline grids)"
```

Fixture idea: extend music-mode / deck fixtures with two grids at known phase offset; simulate PLAY; assert seek target.

---

## 9. Implementation ladder (when execution starts)

| Wave | Deliverable | Verify |
|---|---|---|
| **0 Research** | This document | Peer read; owner Mode A/B confirm |
| **1 Policy compose** | PLAY path: if other playing → tempo (safe) + `requestSyncPhase` / equivalent seek + play | Manual dogfood; unit test phase error |
| **2 Preference + KEYMAP** | Default ON PERFORM; raw-play escape; KEYMAP row | pre-commit; KEYMAP lint culture |
| **3 Confidence gate** | Skip assist if no/poor grid | Fixture missing-beats case |
| **4 Snap unit** | Beat vs bar preference | Bar-phase tests |
| **5 Mode B optional** | “Start on next 1” | Explicit UX, not default |
| **6 Phrase / intro** | L4 region choice before snap | EXO / cue integration |
| **7 Analyzer uplift** | Only if dogfood shows grid errors dominate | MIR metrics + library re-analysis |

**Do not** start at wave 7. Commodity grids + policy unlock most of the owner feeling.

---

## 10. Open research questions

1. **Timebase selection:** sync leader vs NOW deck vs highest channel gain vs master out — which matches DJ mental model on multi-deck PERFORM?
2. **Paused vs stopped:** if B is paused mid-track, is intended start = pause position or cue?
3. **Headphones cueing:** should cue-channel PFL play also snap, or only main PLAY?
4. **Three+ decks:** snap to leader only, or to “dominant” playing deck?
5. **Genre packs:** default bar snap for techno, beat snap for breaks?
6. **Telemetry (later):** accept/override of automatic snap as closed-loop product evidence (DC-PDCL) — not for v1 privacy surface without design.
7. **Licensing/brand:** feature name under Ritual.

---

## 11. Relationship to other Migx research

| Doc | Relationship |
|---|---|
| `nextgen-cognitive-load-perform-arrange-library` | **Why** instant transport reward frees booth attention |
| `arrange-nexttrack-copilot-scoring` | **What** to load; this doc is **when** it starts |
| `copilot-transition-intelligence` | Corpus says good *successors*; on-beat play does not pick tracks |
| `mod-music-management-mode` / modes docs | PERFORM default surface for the policy |
| `oz-audio-engine-learnings` | RT discipline when touching play/seek edges |

---

## 12. Bibliography (short)

**Product / manuals**

- Serato DJ — Sync, Smart Sync, Quantize help topics  
- NI Traktor — Beat Sync / Phase / Tempo; Snap & Quantize  
- Pioneer — rekordbox / CDJ Beat Sync & Quantize  
- Ableton — Launch Quantization  

**MIR**

- Davies, Degara, Plumbley — *Evaluation methods for musical audio beat tracking algorithms*  
- Böck et al. — multi-model beat tracking; madmom ecosystem  
- Ellis — beat tracking by dynamic programming  
- McFee & Ellis — robust onset aggregation  
- Meier & Müller — real-time PLP beat tracking (TISMIR 2024)  
- MIREX Audio Beat Tracking results & metrics (F-measure, continuity)  

**Perception / HCI**

- London — *Hearing in Time*  
- Large & Palmer — phase correction / sensorimotor synchronization  
- Sweller; Endsley — via Migx cognitive-load brief  

**Code**

- `src/engine/sync/synccontrol.cpp`  
- `src/engine/controls/bpmcontrol.cpp` / `.h`  
- `src/engine/controls/quantizecontrol.cpp`  
- `src/engine/enginebuffer.cpp` (`requestSyncPhase`)  
- `src/track/beats.h` / `beats.cpp`  

---

## 13. Recommendation (locked for product discussion)

| Decision | Recommendation | Confidence |
|---|---|---|
| Ship feature family? | **Yes** — high leverage simplicity | high |
| Default mode | **Mode A instant phase jump** | high (matches owner) |
| Default snap unit | **1 beat**; bar optional | medium-high |
| Tempo | One-shot within safe %; soft lock optional | medium |
| v1 tech | **Compose existing COs + seek policy** | high |
| v1 MIR | **No new live tracker** | high |
| Brand language | Assistive transport, not Automix | high |
| Next artifact | Owner confirm Mode A + timebase rule → then dossier / PS | — |

---

## 14. Changelog

| Date | Note |
|---|---|
| 2026-07-23 | Initial deep research brief (grok-signal); grounded in Mixxx sync/beats code + MIR/competitive survey |
