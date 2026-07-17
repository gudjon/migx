---
id: apple-audio-frameworks-os26-wwdc25
type: knowledge
title: "Apple audio frameworks — WWDC25 / OS 26 (macOS · iPadOS · iOS) → Migx map"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
sources:
  - "https://developer.apple.com/videos/play/wwdc2025/251/"
  - "https://developer.apple.com/documentation/AVFoundation/capturing-spatial-audio-in-your-ios-app"
  - "https://developer.apple.com/documentation/Cinematic/editing-spatial-audio-with-an-audio-mix"
  - "https://developer.apple.com/videos/play/wwdc2025/403/"
  - "https://developer.apple.com/videos/play/wwdc2025/297/"
  - "https://developer.apple.com/videos/play/wwdc2026/254/"
  - "https://developer.apple.com/documentation/audiotoolbox/"
  - "https://developer.apple.com/audio/"
  - "https://developer.apple.com/musickit/"
  - "https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes"
defers_to:
  - kanban/Strategy-Current.md
  - kanban/initiatives/initiative-apple-silicon.md
  - kanban/initiatives/initiative-ai-djing-product.md
  - kanban/initiatives/initiative-experience-ontology.md
  - kanban/architecture/ddd/bounded-contexts/arch-audio-io.md
  - kanban/architecture/ddd/bounded-contexts/arch-engine-realtime.md
related:
  - kanban/knowledge/spotify-dj-integration-landscape-2026.md
  - kanban/knowledge/spotify-octave-style-doable-steps.md
  - kanban/knowledge/arcflow-m4-perf-techniques.md
  - kanban/knowledge/oz-audio-engine-learnings.md
  - kanban/federation/signal/2026-07-17-deep-x-community-alignment.md
note: >
  Distillation of Apple platform audio for Migx product/engine thinking.
  Not an implementation plan. House physics (P-02) still bind any RT path.
---

# Apple audio frameworks — OS 26 / WWDC25 → Migx

Detailed field note: what is new and “cool” in Apple’s audio stack as of **WWDC 2025** and the
**version-26 OS line** (iOS 26 · iPadOS 26 · **macOS Tahoe 26** · visionOS 26), how the three
consumer platforms **share** vs **diverge**, and where each item maps onto Migx initiatives.

**Primary session:** [WWDC25-251 — Enhance your app’s audio recording capabilities](https://developer.apple.com/videos/play/wwdc2025/251/).

---

## 1. Executive snapshot

Apple’s latest cool audio work is **not** a greenfield Core Audio replacement for pro DJ engines.
It is a **converging spatial + capture product surface**:

1. **Record** the sound field as **First Order Ambisonics (FOA)** and deliver via **APAC**  
2. **Split** dialog vs ambience with **Audio Mix / AUAudioMix** (system stem-ish API)  
3. **Select** inputs (and AirPods as HQ lavs) **inside the app**  
4. **Ship immersive** production formats (**ASAF**) especially for visionOS  
5. Keep **MusicKit** as the Apple Music catalog/play surface (AutoMix stays first-party Music app)

**Migx default posture:**

| Layer | Use Apple stack? |
|---|---|
| **A — RT engine / decks** | Stay on **existing SoundIO + engine** (Core Audio HAL under the hood on Mac). Do **not** move the callback to AVAudioEngine. |
| **B — agent seams / EXO** | Optional: MusicUnderstanding / analysis on **local PCM** only; never RT. |
| **C — Intelligence** | MusicKit-class catalog access is a **partner-style** product path (like Spotify DJ integration), not dual-deck free PCM. |
| **Sidecar / rec / mobile** | FOA capture, AirPods HQ, Audio Mix, input picker are **high interest**. |

---

## 2. Framework stack (shared mental model)

```text
┌──────────────────────────────────────────────────────────────┐
│  MusicKit · Apple Music API     catalog, library, licensed play │
├──────────────────────────────────────────────────────────────┤
│  AVFoundation · AVFAudio · AVKit   sessions, files, players, UI │
│  Cinematic                         spatial Audio Mix edit (26)  │
├──────────────────────────────────────────────────────────────┤
│  AudioToolbox                      convert, parse, Audio Units  │
│  AUAudioMix (new)                  FOA → dialog + ambience      │
├──────────────────────────────────────────────────────────────┤
│  Core Audio                        HAL, devices, low-level RT   │
└──────────────────────────────────────────────────────────────┘
```

| Framework | Role | Typical Migx touch |
|---|---|---|
| **Core Audio** | Device I/O, low-level timing | `src/soundio` (Mac path) |
| **AudioToolbox** | Units, format convert, FOA helpers | Effects / offline tools; not RT graph ownership |
| **AVFAudio / AVFoundation** | Sessions, file I/O, high-level play/record | Sidecar, rec, analysis workers |
| **Cinematic** | Spatial mix styles for FOA assets | Optional edit/rec product features |
| **MusicKit** | Apple Music catalog + user library play | Product Layer C / streaming partner analog |
| **RealityKit audio / ASAF** | Spatial computing / immersive | Out of near-term Migx desktop deck scope |

---

## 3. What’s new and cool (WWDC25 / OS 26)

### 3.1 Spatial Audio capture — FOA + dual-track assets

**What it is**

- Mic array captures a 3D scene → transformed to **Ambisonics**  
- Stored as **First Order Ambisonics (FOA)**: 4 channels  
  - W — omni  
  - X / Y / Z — perpendicular dipoles (front-back, left-right, up-down)  
- Benefits: Spatial playback, **AirPods head tracking**, mix metadata  

**iOS 26 advances** (session 251)

| Capability | Detail |
|---|---|
| **AVAssetWriter** FOA path | Custom pipelines beyond `AVCaptureMovieFileOutput` |
| **Two AudioDataOutputs** | One FOA (4ch) + one Stereo (2ch) when `multichannelAudioMode = .firstOrderAmbisonics` |
| **`spatialAudioChannelLayoutTag`** | Stereo **or** HOA-ACN-SN3D (FOA layout) |
| **Metadata sample** | `AVCaptureSpatialAudioMetadataSampleGenerator` — timed sample enabling Audio Mix at stop |
| **`.qta` (QuickTime audio)** | Audio-only container with alternate track groups (for apps like Voice Memos class) |
| **Simultaneous MovieFileOutput + AudioDataOutput** | Record to file **and** live buffers for meters / waveforms / FX |

**Proper Spatial Audio asset shape**

```text
Track A: Stereo (AAC or PCM)     — compatibility
Track B: FOA / APAC (or PCM)     — spatial
Track C+: Metadata               — Audio Mix enable + tuning params
```

During ProRes-class capture, audio tracks may be **PCM**; delivery often uses **APAC**.

**Cross-platform**

| | iOS | iPadOS | macOS |
|---|---|---|---|
| FOA capture APIs | Yes (best HW on recent iPhone) | Same API family | AVCapture / writer available |
| Best built-in mic array | iPhone | iPad (device-dependent) | Continuity / external |
| APAC via AVAssetWriter | Yes | Yes | Yes (+ visionOS) |

**Migx map**

| Initiative | Fit |
|---|---|
| `initiative-ai-djing-product` | Optional **rec / broadcast sidecar** (not deck engine) |
| `initiative-apple-silicon` | Live AudioDataOutput while recording = visualization off RT audio thread |
| EXO | Spatial metadata is **not** the same as song ontology; keep separate |

**House physics:** FOA processing and file write belong on **worker threads**, never in Mixxx `process*()`.

---

### 3.2 Audio Mix / AUAudioMix — dialog vs ambience (system “stems”)

**What it is**

New in **iOS 26 and macOS 26** (Cinematic + AudioToolbox unit):

- Control balance of **foreground** (speech/dialog) vs **background ambient FOA**  
- Same family as Photos spatial video edit  
- Modes include **Cinematic, Studio, In-Frame** plus additional app modes  
- Can extract:
  - **Dialog-only** (mono foreground stem)  
  - **Ambience-only** (FOA background)  
  - Full spatialized layouts when spatialization enabled (e.g. 5.1, 7.1.4)

**Two integration levels**

| Path | Use when |
|---|---|
| **AVPlayer + `CNAssetSpatialAudioInfo` → `AVAudioMix`** | Media player UIs, simple intensity/style sliders |
| **`AUAudioMix` Audio Unit** | Custom graphs (not AVPlayer); FOA in → separation → optional AUSpatialMixer |

**AUAudioMix internals (conceptual)**

```text
FOA in (4 ch)
    → speech/ambience separation
    → [optional] AUSpatialMixer (headphones / built-in / external)
    → out: 5-ch (FOA ambience + mono dialog) if spatialization off
           or common multichannel layouts if on
```

Also requires **SpatialAudioMixMetadata** (CFData) from the asset — auto-generated at capture for EQ/gain tuning.

**Sample:** Apple’s SpatialAudioCLI (preview / bake / process modes) linked from session 251.

**Migx map**

| Initiative | Fit |
|---|---|
| AI-DJing / analyzer research | **Offline** “foreground vs bed” for spoken intros or rec; **not** kick/snare/vocal DJ stems |
| Apple Silicon | On-device separation — compare later to HTDemucs/local Demucs task |
| Engine RT | **Do not** put AUAudioMix on the audio callback |

**Honest limit:** This is **speech/ambience** separation for spatial captures, not Serato/Neural Mix multi-stem for dance tracks.

---

### 3.3 In-app input route picker (iOS / iPadOS 26)

**API:** `AVInputPickerInteraction` (AVKit)

- System sheet of inputs with **live level metering**  
- Mic **mode** list per device  
- Stack **remembers** last selection per app  
- No trip to Settings  

**Setup sketch (from session):** configure `AVAudioSession` → create picker → `addInteraction` on a control → `present()`.

**Cross-platform:** First-class **iPhone/iPad** creator UX. Mac still uses system/Core Audio device model for pro interfaces; conceptual “choose input without leaving app” is the shared product idea.

**Migx map:** Mobile/sidecar capture UX if/when iOS/iPad companion exists; desktop Sound Hardware prefs stay authoritative for pro I/O.

---

### 3.4 AirPods high-quality recording

**Opt-in**

| API surface | Flag |
|---|---|
| `AVAudioSession` | Category option `bluetoothHighQualityRecording` |
| `AVCaptureSession` | `configuresApplicationAudioSessionForBluetoothHighQualityRecording = true` |

- Media tuning (lav-like voice + room)  
- More reliable BT link for this mode  
- Falls back to classic HFP Bluetooth if unsupported  
- Stem press start/stop via capture-controls (related WWDC25 session)

**Cross-platform:** Same story on **iOS/iPadOS**; Mac can use AirPods as input but pro decks still prefer wired interfaces.

**Migx map:** Low priority for core instrument; high for **voice memo / rec / co-pilot voice note** experiments.

---

### 3.5 Apple Positional Audio Codec (APAC) & higher-order ambisonics

- **APAC** — delivery codec for spatial / ambisonic content  
- AVAssetWriter encoder on **iOS, macOS, visionOS** supports **1st / 2nd / 3rd order** ambisonics (immersive media sessions)  
- Recommended bitrates called out in Projected Media Profile sessions (e.g. FOA-class starting ~384 kbps band — verify current docs)

**Migx map:** Long-horizon export/immersive; not deck playback core.

---

### 3.6 Apple Spatial Audio Format (ASAF) — immersive production

From [WWDC25-403 Immersive Video](https://developer.apple.com/videos/play/wwdc2025/403/):

| Piece | Role |
|---|---|
| **ASAF** | Production format: linear PCM + spatial metadata + system spatial renderer |
| Adaptive render | Object + **listener** pose (not pre-baked binaural) |
| Point sources + HOA scenes | High-resolution spatial beds |
| Carriage | Broadcast Wave–class files with PCM + metadata |
| Delivery | Often paired with **APAC** encode |

**Center of gravity:** visionOS immersive media. Cross-Apple playback story expands over time.

**Migx map:** Out of near-term dual-deck thesis; watch if “DJ in spatial venue” ever becomes a product bet.

---

### 3.7 MusicKit / Apple Music (catalog layer)

- [MusicKit](https://developer.apple.com/musickit/) — Swift APIs for catalog, library, play on Apple platforms  
- [WWDC26-254 Integrate MusicKit](https://developer.apple.com/videos/play/wwdc2026/254/) — concurrency/SwiftUI-oriented integration  
- **AutoMix** in the **Music app** (iOS 26+) is a **consumer product** feature  

**Critical developer reality (forums / community):**

- No documented **public MusicKit Automix API** for third parties (devs still requesting)  
- **MusicUnderstanding**-class APIs (emerging docs / WWDC Q&A): interesting for analysis; **not** a license to read Apple Music stream PCM for arbitrary DSP (typically need readable buffers / non-MusicKit sources)  
- djay-class apps with deep Apple Music behavior are often **partner / special** arrangements — same class of barrier as Spotify DJ integration  

**Migx map**

| Strategy | Implication |
|---|---|
| Spotify Octave path | Mirror: **metadata + prep + sequence**; dual-deck needs partner path |
| EXO | Apple Music IDs can be ontology `external_ids` without decode rights |
| Anti-identity | Do not market “we have Apple AutoMix” |

See also: `spotify-dj-integration-landscape-2026.md`, `spotify-octave-style-doable-steps.md`.

---

### 3.8 Core Audio / pro Mac (Tahoe 26 field notes)

Not a single flashy WWDC “new engine” talk, but **operationally critical** for Migx:

| Observation | Implication |
|---|---|
| Reports of **coreaudiod** flakiness / “no devices” on 26.x | Soak-test SoundIO on Tahoe + M4 |
| Occasional **NSSound / caulk allocator SIGILL** reports | Prefer proven audio paths; stress exclusive mode |
| Pro community notes on **safety offset / latency** tweaks | Re-measure buffer/underrun baselines (P-03 / P-18) after OS jumps |
| Tahoe as last Intel macOS (Rosetta narrative) | Double-down **native arm64** builds (`P-24`) |

**Migx map:** `initiative-apple-silicon` + `arch-audio-io` — **validate, don’t rewrite**.

Companion compute notes: `arcflow-m4-perf-techniques.md` (vDSP/Metal/QoS) — orthogonal to spatial capture APIs.

---

## 4. Shared vs divergent: macOS · iPadOS · iOS

| Domain | Shared across three | Diverges |
|---|---|---|
| AVFoundation play/record concepts | High | Device matrix & session policies |
| AudioToolbox / AU processing | High | Mac hosts pro AU ecosystems |
| FOA / APAC / Audio Mix story | Growing everywhere | Best capture = phone arrays |
| AVAudioSession | iOS ≈ iPadOS | Mac route model different |
| In-app input picker | iOS/iPadOS 26 | Mac uses system/Core Audio UX |
| Core Audio HAL multi-client I/O | Conceptual | **Mac = pro workstation** |
| MusicKit catalog | Yes | Automix = first-party app |
| ASAF / RealityKit spatial | visionOS center | Partial elsewhere |

**One sentence:** Apple is **unifying spatial capture/mix/delivery** while **keeping Core Audio as the Mac pro spine**.

---

## 5. Migx initiative mapping (actionable matrix)

| Apple capability | Coolness | Migx home | Priority | Notes |
|---|---|---|---|---|
| Core Audio HAL (existing) | — | `arch-audio-io`, engine | **P0 keep** | RT path unchanged |
| Tahoe Core Audio soak tests | Survival | `initiative-apple-silicon` | **P0** | p99/underrun re-baseline |
| FOA + live AudioDataOutput | High | Product rec/sidecar | **P3 later** | Worker thread only |
| AUAudioMix speech/ambience | High | Analyzer research | **P3 later** | Not dance stems |
| AVInputPicker + AirPods HQ | High (mobile) | iOS/iPad companion | **P4 if mobile** | Not desktop deck core |
| APAC / ASAF | High (immersive) | Watch only | **Park** | visionOS-first |
| MusicKit catalog | Medium | Layer C / streaming prep | **P2 research** | Like Spotify: rights-bound |
| Music AutoMix API | Hype | — | **None** | Not public |
| MusicUnderstanding (local PCM) | Medium-High | EXO / analyzer | **Watch + spike** | Local files only |
| vDSP / Accelerate / Metal | High | ASI + MTL dossiers | **P1 ongoing** | Already north-star |

---

## 6. Patterns / house physics (do not violate)

| Pattern | Apple API risk |
|---|---|
| **P-02** RT no alloc/lock | Never run FOA encode, AUAudioMix, MusicKit, or JSON on `process*()` |
| **P-16** lock-free handoff | Capture/analysis → ring buffer → engine params only via CO |
| **P-03 / P-18** bench contracts | Re-pin after OS 26 upgrades |
| **P-06** single CO writer | MusicKit/session state ≠ second writer on deck load |
| **P-21** GPU off audio deadline | Spatial viz on GPU must not gate audio callback |

---

## 7. What Apple is *not* giving third parties

| Expectation | Reality |
|---|---|
| Multi-deck **Apple Music PCM** like Serato partner streams | Not a public free-for-all; partner-class only |
| **AutoMix** in MusicKit | First-party Music app; no documented third-party API |
| Drop-in replacement for Mixxx RT engine via AVAudioEngine | Wrong latency/underrun product for pro DJ |
| Full multi-stem (kick/hat/vocal) via AUAudioMix | Dialog/ambience spatial split only |

---

## 8. Suggested research / task seeds (not scheduled)

Use only if an owner opens work; do not invent dossiers without compound check.

| Seed | Type | Depends on |
|---|---|---|
| Tahoe + M4 SoundIO soak (underrun/device flake matrix) | task under ASI | build machine on 26.x |
| Spike: offline AUAudioMix on a FOA test file (non-RT) | research note | macOS 26 SDK |
| MusicUnderstanding on **local** library file → EXO fields | EXO research | API availability + PCM access |
| MusicKit metadata-only crate (parity with Spotify paste-import) | product research | MusicKit terms |
| iPadOS input picker + AirPods HQ demo app (sidecar) | optional mobile | product priority |

Existing related tasks: `research-analyzer-structure-energy-mlx.md` (stems/MLX — compare philosophy to AUAudioMix).

---

## 9. Primary references (prefer these)

| Resource | Why |
|---|---|
| [WWDC25-251 Recording](https://developer.apple.com/videos/play/wwdc2025/251/) | Input picker, AirPods HQ, FOA writer, Audio Mix |
| [Capturing Spatial Audio (docs)](https://developer.apple.com/documentation/AVFoundation/capturing-spatial-audio-in-your-ios-app) | Implementation |
| [Editing Spatial Audio mix (docs)](https://developer.apple.com/documentation/Cinematic/editing-spatial-audio-with-an-audio-mix) | Cinematic / mix |
| [WWDC25-403 Immersive](https://developer.apple.com/videos/play/wwdc2025/403/) | ASAF |
| [WWDC25-297 Projected Media](https://developer.apple.com/videos/play/wwdc2025/297/) | APAC ambisonics encode |
| [WWDC26-254 MusicKit](https://developer.apple.com/videos/play/wwdc2026/254/) | Catalog integration |
| [AudioToolbox](https://developer.apple.com/documentation/audiotoolbox/) | Units / toolbox |
| [developer.apple.com/audio](https://developer.apple.com/audio/) | Hub |
| [macOS 26 release notes](https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes) | Platform bugs/fixes |

---

## 10. One-line alignment for Migx

**Apple’s new cool is spatial capture and intelligent mix of *recorded scenes*; Migx’s cool is real-time multi-deck *performance* with an agent that understands a set.**  
Borrow FOA/Audio Mix/MusicUnderstanding on **workers and product sidecars**; keep the **RT instrument** on proven Core Audio + house physics; treat MusicKit like Spotify — **identity and prep first, dual-stream only with rights**.
