---
id: architecture-apple-silicon-macos26-refactor-map
type: knowledge
title: "Architecture map — refactor to 100% macOS 26+ Apple Silicon (feature-preserving)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
enriched: "2026-07-17 PLT dossier executed Waves 1–3 (EVD-PLT-0001, CI prune, parity HOLD)"
defers_to:
  - kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md
  - kanban/architecture/README.md
  - kanban/Strategy-Current.md
  - AGENTS.md
related:
  - kanban/knowledge/apple-audio-frameworks-os26-wwdc25.md
  - kanban/knowledge/arcflow-m4-perf-techniques.md
  - kanban/knowledge/oz-audio-engine-learnings.md
  - kanban/knowledge/performance-capability-uplifts-x-field-map.md
  - kanban/initiatives/initiative-apple-silicon.md
  - kanban/tasks/narrow-platform-to-apple-silicon.md
  - kanban/tasks/tahoe-m4-soundio-soak-rebaseline.md
  - kanban/tasks/retire-deprecated-gl-waveform-renderers.md
  - kanban/tasks/prune-outdated-legacy-code.md
note: >
  Step-by-step target architecture + refactor waves. Feature-preserving: prune portability
  tax, not DJ capabilities. Every wave ends in build + ctest + (for RT) underrun EVD.
---

# Architecture map — 100% macOS 26+ · Apple Silicon

**Product floor (ADR-006):** Migx ships for **macOS 26.\*+** on **Apple Silicon (arm64) only**.  
**Goal of this map:** refactor so the codebase, runtime, and CI **double down** on that platform’s
capabilities (Core Audio, Accelerate/vDSP, Metal, unified memory, OS 26 spatial/capture APIs where
useful) **without deleting DJ features** — only the **portability tax** (Win/Linux/Intel, dead GL,
multi-backend dead weight).

**Non-goals of this map:** rewriting the RT engine from scratch; Electron; dual Spotify multi-deck
without partners; shipping iPad/Windows.

---

## 1. North-star architecture (target state)

### 1.1 One-screen picture

```text
                         ┌─────────────────────────────────────┐
                         │  QML shell + DESIGN.md Theme        │  arch-qml-ui
                         │  Co-Pilot dogfood · library · prefs │  Layer B chrome
                         └───────────────┬─────────────────────┘
                                         │ ControlObject / ControlProxy (P-06)
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
│ Controllers     │            │ Library / FSL   │            │ Analyzer        │
│ HID/MIDI/JS     │            │ crates · EXO    │            │ worker + MLX*   │
│ arch-controllers│            │ arch-library    │            │ arch-analyzer   │
└────────┬────────┘            └────────┬────────┘            └────────┬────────┘
         │                              │                              │
         │         ┌────────────────────┴────────────────────┐         │
         │         ▼                                         ▼         │
         │  ┌──────────────┐                         ┌──────────────┐  │
         │  │ Track model  │                         │ Sources      │  │
         │  │ arch-track   │                         │ CoreAudio +  │  │
         │  └──────┬───────┘                         │ FFmpeg (mac) │  │
         │         │                                 │ worker only  │  │
         │         ▼                                 └──────┬───────┘  │
         │  ┌──────────────────────────────────────────────┐ │         │
         └──►│  ENGINE (RT)  mix · scale · effects · sync   │◄┘         │
            │  arch-engine-realtime · arch-effects · mixer │◄──────────┘
            └───────────────────┬──────────────────────────┘
                                │ AudioSource::requestBuffer (pull)
                                ▼
            ┌──────────────────────────────────────────────┐
            │  SOUNDIO  Core Audio–first RT origin          │  arch-audio-io
            │  (PortAudio/CoreAudio path today → tighten)   │
            └───────────────────┬──────────────────────────┘
                                │ CSAMPLE out
                                ▼
                         Hardware / aggregate device

            ┌──────────────────────────────────────────────┐
            │  WAVEFORM / RENDERGRAPH  display clock        │  arch-waveform · arch-rendergraph
            │  allshader/RHI → Metal-preferred (P-21/P-22)  │
            └──────────────────────────────────────────────┘
```

\* MLX / on-device ML only on **workers**, never RT.

### 1.2 Platform-native capability map (what we double down on)

| Capability | Apple surface | Migx domain | Role |
|---|---|---|---|
| RT I/O | **Core Audio** (HAL) | `arch-audio-io` | Origin of deadline; exclusive mode; low buffer |
| Decode | **CoreAudio** codecs + FFmpeg where needed | `arch-sources-decode` | Worker; prefer CA for AAC/ALAC |
| DSP | **Accelerate / vDSP / vForce** (+ NEON) | engine, effects, analyzer | Batch math off hand-rolled loops |
| Render | **Metal** via Qt RHI / allshader | waveform, rendergraph | Zero-copy, no GPU on audio deadline |
| Memory | Unified memory / arm64 | all hot paths | No x86_64/Rosetta; SoA where it pays |
| OS floor | **macOS 26+** | packaging, CI, APIs | May use OS 26 APIs; soak-test first |
| Spatial/rec (optional) | FOA, AUAudioMix, APAC | sidecar / rec — **not** decks | See `apple-audio-frameworks-os26-wwdc25.md` |
| Catalog (optional) | MusicKit | Layer C prep | Metadata/play rights — not free multi-deck PCM |
| Co-pilot | EXO + intents + QML | Layer B | Offline → CO reconciler |

### 1.3 What “feature-preserving” means

| Keep (product features) | May remove / go dormant (portability tax) |
|---|---|
| Multi-deck mix, sync, keylock, effects | Linux PipeWire/ALSA-specific backends as **build defaults** |
| Controllers (MIDI/HID), vinyl/DVS | Windows WASAPI-specific packaging/CI |
| Library, crates, analysis, waveforms | Intel/x86_64 + Rosetta build matrix |
| Recording, broadcast (Icecast etc.) | debian/flatpak/PPA as **supported** products |
| QML UI, skins still needed for migration | Dead `waveform/renderers/deprecated/*` once allshader proven |
| Network sound device (if used) | Qt5-only paths if Qt6-only |
| AutoDJ, samplers, stems **if present** | “Support Windows/Linux DJs” as design constraint |

**Rule:** every cut needs a **feature map** row: *feature X still works via path Y on Mac*.

---

## 2. Current state (as-is inventory)

### 2.1 Bounded contexts (unchanged ownership)

From `kanban/architecture/README.md` — still correct. RT axis stays:

```text
sources → engine → soundio(callback) → device
              ↑ tap (lock-free)
         waveform/rendergraph (display clock)
```

**Fork delta to change:** several cards say `fork_delta: upstream-tracking` — under ADR-002/006 they
should migrate to `migx-divergent` as waves land.

### 2.2 Hot multi-platform surfaces (refactor targets)

| Surface | Today | Tax | Apple-native direction |
|---|---|---|---|
| **Audio backend** | PortAudio required; PipeWire optional; network device | PA abstracts Mac but hides CA knobs | **Core Audio–first** device path; PA only if still needed as thin shim |
| **Decode** | FFmpeg + CoreAudio option | Dual paths | Prefer **CoreAudio** for Apple codecs; FFmpeg for gap formats |
| **Waveform** | `allshader/` + `deprecated/` GL + Qt paths | Dead GL risk (allshader deps HOLD) | **allshader/RHI → Metal** only after retire gate |
| **UI** | QML + legacy skins/widgets | Dual chrome | **QML-primary** (ADR-004); skins until feature parity |
| **Packaging** | `packaging/{macos,debian,flatpak,wix,android,ios}` | CI + docs for dead platforms | **macos only** shipping |
| **CI** | Multi-OS legs (upstream-shaped) | Slow, green noise | **macOS arm64 26** only |
| **`#ifdef` matrix** | ~50+ files touch Win/Linux/Android | Mental load | Collapse as files are touched (`P-11`) |
| **CMake options** | PIPEWIRE, many platform flags | Configure complexity | Mac defaults; foreign options OFF/fatal |

### 2.3 Already decided / in motion

| Artifact | Status |
|---|---|
| ADR-006 macOS 26+ AS only | **accepted** |
| CMake floor `26.0` + arm64 | **landed** |
| MTL waveform baseline / VBO | dossiers under `initiative-apple-silicon` |
| Tahoe SoundIO soak task | open — **P0 validate** |
| Narrow platform packaging task | open — execute ADR-006 prune |
| Retire deprecated GL renderers | open — **HOLD until deps proven** |
| EXO / co-pilot Layer B | dogfood live; not RT |

---

## 3. Target domain architecture (per context)

### 3.1 `arch-audio-io` — RT origin (highest leverage + risk)

**Target:**

```text
SoundManager
  └── SoundDeviceCoreAudio (or PA→CA with explicit CA config surface)
        └── callbackProcess  →  EngineMixer::requestBuffer
```

| Phase | Work | Feature keep |
|---|---|---|
| **A0** | Soak PortAudio/CA on 26+M4 (task `tahoe-m4-soundio-soak-rebaseline`) | All routing as today |
| **A1** | Expose exclusive mode, buffer, sample-rate, aggregate devices clearly in prefs | Same features, better Mac UX |
| **A2** | Optional native `SoundDeviceCoreAudio` if PA blocks latency/stability | Bit-identical mix; lower p99 |
| **A3** | Disable PipeWire from default configure (Linux-only) | No Mac feature loss |

**Invariants:** `P-02`, `P-17`, `P-18` — never “faster on average.”

### 3.2 `arch-engine-realtime` + effects + mixer

**Target:** same graph semantics; **kernels** prefer Accelerate/vDSP where shape amortizes.

| Phase | Work | Feature keep |
|---|---|---|
| **E0** | Inventory hot `process*` paths (scale, EQ, rubberband, effects) | — |
| **E1** | Replace scalar loops with vDSP where benches win | Same sound (or documented epsilon) |
| **E2** | QoS / P-core affinity for non-RT workers only (not RT priority games without proof) | Stability |
| **E3** | No new locks; audit any OS 26 CA quirks after soak | Zero underruns |

### 3.3 `arch-sources-decode`

**Target:** CoreAudio provider first-class for ALAC/AAC/CAF; FFmpeg for the long tail.

| Phase | Work | Feature keep |
|---|---|---|
| **S0** | Matrix: format → provider on M4 | All formats still open |
| **S1** | Prefer CA where quality/latency of open wins | No “can’t play X” regressions |
| **S2** | Worker-only MLX/analysis decode reuse | Stems/structure later |

### 3.4 `arch-waveform-render` + `arch-rendergraph`

**Target:** single modern path — **allshader + Metal RHI**; zero-copy VBO (MTL dossiers).

| Phase | Work | Feature keep |
|---|---|---|
| **W0** | Prove allshader covers every skin/QML waveform feature | Visual parity checklist |
| **W1** | Retire `deprecated/` GL **only after W0** (task hold) | No blank waveforms |
| **W2** | Metal-specific residency / heap if RHI allows | Smoother UI, not RT |

### 3.5 `arch-qml-ui` + skins

**Target:** QML-primary product shell; DESIGN.md tokens; co-pilot chrome.

| Phase | Work | Feature keep |
|---|---|---|
| **U0** | Feature parity matrix: QWidget skin feature → QML | Controllers + library workflows |
| **U1** | Migrate high-traffic prefs/library to QML | Same settings |
| **U2** | Layer B co-pilot: fixture → live CO reconciler | Prep/explain; no dual-stream DRM |

### 3.6 `arch-library` / EXO / FSL

**Target:** greppable sidecars + DB; EXO session graph; hybrid Spotify **identity** (not dual stream).

Unchanged product features; Mac-only means faster local FS assumptions OK (APFS), but keep paths portable-ish inside Mac.

### 3.7 Controllers / vinyl

**Keep full HID/MIDI/DVS.** Platform prune must **not** break controller JS mappings. Test matrix: top N controllers on Mac only.

### 3.8 Packaging & CI

**Target:**

```text
.github/workflows:  macos-arm64-26 only (build + ctest + optional bench)
packaging/macos:    sole shipping artifact
packaging/{debian,flatpak,wix,android}: dormant or removed per wave
```

---

## 4. Step-by-step refactor program (waves)

Each wave: **scope → do → gate → feature checklist**. Never green-over-red (`AP-01`).

### Wave 0 — Lock the floor (done / verify)

| Item | Gate |
|---|---|
| ADR-006 + CMake `26.0` + arm64 | configure refuses Intel/iOS |
| README / AGENTS / justfile | docs match |
| Host is macOS 26+ arm64 | `sw_vers`, `uname -m` |

**Feature impact:** none.

---

### Wave 1 — **Validate SoundIO on the only OS** (P0)

**Owner task:** `tahoe-m4-soundio-soak-rebaseline`  
**Context:** `arch-audio-io`

| Step | Action |
|---|---|
| 1.1 | Dual-deck soak: built-in, USB interface, AirPods; exclusive vs shared |
| 1.2 | Sample-rate / buffer sweeps; log xruns |
| 1.3 | EVD vs MTL baseline; record OS build in baseline axis (`P-25`) |
| 1.4 | Open flake cards only if needed — **no rewrite yet** |

**Gate:** EVD with p99/max + **zero underruns** (or named residual flakes).  
**Feature impact:** none (measurement).

---

### Wave 2 — **Platform surface prune** (portability tax)

**Owner task:** `narrow-platform-to-apple-silicon` (update acceptance: **iPad not shipping**; macOS-only)

| Step | Action |
|---|---|
| 2.1 | CI: drop Linux/Windows legs; one macOS-arm64 job on 26 |
| 2.2 | packaging: stop shipping debian/flatpak/PPA; wix/android **dormant** |
| 2.3 | CMake: `PIPEWIRE` default OFF; document Mac-only options |
| 2.4 | Touch-based `#ifdef` collapse when editing files (`P-11`) — no mega-PR |

**Gate:** `cmake --build` + `ctest` green on arm64.  
**Feature impact:** none for Mac users; remove unsupported OS promises.

---

### Wave 3 — **Render path consolidation** (stability + perf)

**Owner tasks:** `retire-deprecated-gl-waveform-renderers` after parity; MTL VBO dossiers

| Step | Action |
|---|---|
| 3.1 | Feature matrix: allshader vs deprecated vs Qt legacy |
| 3.2 | Fix gaps in allshader (cues, RGB, overview, stems marks) |
| 3.3 | Delete/stop compiling `deprecated/` |
| 3.4 | Land zero-copy / persistent VBO where EVD proves win |

**Gate:** visual regression checklist + no RT regression.  
**Feature impact:** **zero visual features lost** (parity first).

---

### Wave 4 — **Decode + DSP Apple-native** (perf without feature loss)

| Step | Action |
|---|---|
| 4.1 | Format matrix + CA-first provider ranking |
| 4.2 | vDSP/Accelerate in top N engine hotspots (bench each) |
| 4.3 | Analyzer worker: Accelerate FFT/filter; optional MLX later |

**Gate:** `ctest -R Engine|SoundSource|Analyzer` + bench deltas (`P-03`).  
**Feature impact:** same formats; same musical behavior within epsilon policy.

---

### Wave 5 — **Audio backend deepen (optional rewrite)**

Only if Wave 1 shows PA is the ceiling:

| Step | Action |
|---|---|
| 5.1 | Design `SoundDeviceCoreAudio` behind same `SoundDevice` interface |
| 5.2 | Feature parity: multi-out, vinyl inputs, clock ref, aggregate |
| 5.3 | A/B underrun EVD; flip default when green |

**Gate:** full SoundManager tests + soak EVD.  
**Feature impact:** **no routing feature removed**.

---

### Wave 6 — **UI QML-primary without feature drop**

| Step | Action |
|---|---|
| 6.1 | Skin→QML feature matrix (library, effects, sampler, AutoDJ, prefs) |
| 6.2 | Port missing prefs/library flows |
| 6.3 | Co-pilot: Ack → CO reconciler (Layer B production path) |

**Gate:** manual dogfood script + controller smoke.  
**Feature impact:** parity checklist signed before skin deprecation.

---

### Wave 7 — **OS 26+ optional capabilities** (features *add*, not replace)

From `apple-audio-frameworks-os26-wwdc25.md`:

| Capability | How without losing deck features |
|---|---|
| FOA / rec sidecar | Separate from master mix path |
| AUAudioMix | Offline/worker on spatial files only |
| MusicKit prep | Identity + sequence like Spotify Octave path |
| MusicUnderstanding | Local PCM → EXO fields |

**Gate:** feature flags default off until dogfood.

---

## 5. Feature-preservation matrix (sign before big deletes)

| DJ feature | Today path | Mac-native target path | Wave |
|---|---|---|---|
| 2–4 deck mix | engine + soundio | same | — |
| Sync / keylock | engine | + Accelerate where safe | 4 |
| Effects | engine/effects | same + vDSP | 4 |
| Vinyl/DVS | vinylcontrol + inputs | same | 5 parity |
| Controllers | controllers + CO | same | 2 must not break |
| Library / crates | library DB | same + FSL | — |
| Waveforms / cues | waveform allshader | Metal allshader | 3 |
| Recording | encoder + soundio | same; optional FOA sidecar | 7 |
| Broadcast | network device | keep if Mac-used | 2 |
| Streaming prep | EXO / paste Spotify | sequence-only | — |
| Co-pilot | dogfood QML | CO reconciler | 6 |
| Stems | limited / future | worker MLX later | 7 |

---

## 6. Risk register

| Risk | Mitigation |
|---|---|
| Delete GL too early → blank waveforms | Wave 3 parity gate; HOLD until deps proven |
| Core Audio rewrite regression | Wave 1 soak first; interface-preserving adapter |
| `#ifdef` mega-delete breaks build | Touch-local only; bisectable commits |
| OS 26 coreaudiod flakes | EVD + flake cards; don’t chase rewrite for OS bugs |
| Feature “feels” gone (skin) | Explicit QML parity matrix |
| Perf win regresses RT safety | `P-02` review + underrun gate every DSP PR |

---

## 7. Suggested dossier / task ordering

```text
Wave 0  floor lock ..................... DONE (ADR-006, CMake)
Wave 1  tahoe-m4-soundio-soak .......... DONE  EVD-PLT-0001 (built-in CA solid)
Wave 2  narrow-platform packaging/CI ... DONE  PLT (GH Actions watch residual)
Wave 3  waveform parity matrix ......... DONE  HOLD delete (matrix signed)
Wave 3b retire deprecated GL ........... OPEN  UIX after visual dogfood
Wave 4  Accelerate/CA decode ........... new dossier DSP/ASI
Wave 5  native Core Audio device ....... NOT indicated by W1 (optional product only)
Wave 6  QML parity + CO co-pilot ....... after dogfood
Wave 7  OS26 spatial/MusicKit flags .... research
```

Dossier: `kanban/planning/2026-07-17-gudjon-PLT--macos26-platform-alignment/` (prefix `PLT`).

---

## 8. Success criteria (“100% aligned”)

| Criterion | Measure |
|---|---|
| Single platform story | Docs + CI + packaging match ADR-006 |
| Native arch | No Rosetta; arm64 only |
| OS floor | Deployment target ≥ 26.0; soak EVD on 26.x |
| RT trust | Dual-deck p99/max + zero underruns vs pinned baseline |
| Feature completeness | Feature matrix 100% signed for Mac |
| Render | No deprecated GL in default build |
| DSP | Documented Accelerate wins on top hotspots |
| Agent path | Layer B intents can reach engine via single CO writer |

---

## 9. What this architecture is *not*

- Not “drop PortAudio tomorrow.”  
- Not “rewrite Mixxx in Swift.”  
- Not “replace decks with AVAudioEngine.”  
- Not “iPad ships next sprint.”  
- Not feature amputation for purity.

It **is** a deliberate collapse of the portability tax so every engineering hour compounds on  
**macOS 26 + Apple Silicon performance, stability, and DJ feature depth**.

---

## 10. Cross-links

| Doc | Role |
|---|---|
| [ADR-006](../architecture/decisions/ADR-006-platform-scope-apple-silicon.md) | Platform decision |
| [architecture README](../architecture/README.md) | DDD map |
| [apple-audio-frameworks-os26](apple-audio-frameworks-os26-wwdc25.md) | OS 26 API menu |
| [arcflow-m4-perf](arcflow-m4-perf-techniques.md) | Accelerate/Metal techniques |
| [oz-audio-engine](oz-audio-engine-learnings.md) | RT handoff lessons |
| [initiative-apple-silicon](../initiatives/initiative-apple-silicon.md) | Perf umbrella |
