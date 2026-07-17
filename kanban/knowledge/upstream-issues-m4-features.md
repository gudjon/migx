---
id: upstream-issues-m4-features
type: knowledge
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: >
  gh CLI against mixxxdj/mixxx (public). Queries (all --state open):
  gh issue list --search "<term>" for terms: macOS, "Apple Silicon", Metal,
  performance, latency, CoreAudio, waveform, OpenGL, RHI, "CPU usage", GPU,
  scenegraph, M1, SIMD, dropout, keylock. Detail via `gh issue view <n>`.
  Cross-referenced with kanban/architecture/README.md (DDD roster) and
  kanban/initiatives/initiative-apple-silicon.md. Confirmed in-tree lead at
  src/coreservices.cpp:826.
---

# Upstream issues → Migx Apple-Silicon (M4) findings

Distilled from the upstream `mixxxdj/mixxx` open-issue tracker, filtered for what moves the
**macOS / Apple-Silicon (M4)** initiative (`initiative-apple-silicon`): Metal render offload (`MTL`),
M4 DSP via NEON/Accelerate (`DSP`), and arm64 build + SoC tuning (`ASI`). Each item names the Migx
bounded context it touches (DDD roster in `kanban/architecture/README.md`) and a recommended home.

## The load-bearing fact (north-star lead, confirmed in-tree)

`src/coreservices.cpp:826` unconditionally forces the Qt Quick RHI backend to OpenGL:

```cpp
// Currently, it is required to enforce QQuickWindow RHI backend to use
// OpenGL on all platforms to allow offscreen rendering to function as expected
QQuickWindow::setGraphicsApi(QSGRendererInterface::OpenGL);
```

So Migx never lets Qt select **Metal** on macOS — every QML/scenegraph waveform runs the deprecated
OpenGL path. The comment pins *why*: offscreen rendering (controller preview screens) currently
depends on it. Upstream is independently migrating renderers off OpenGL onto the RHI/SceneGraph
backend (see B/D below), which is the same door the `MTL` dossier walks through. **This one line is
the primary `MTL` target.** Touches: `arch-rendergraph`, `arch-waveform-render`, `arch-qml-ui`.

---

## (A) macOS / Apple-Silicon BUGS

| # | title | context | notes / home |
|---|---|---|---|
| **#13871** | ThreadSanitizer data race in `AudioIOProc` vs `Pa_StopStream` (arm64/CoreAudio) | `arch-audio-io` (src/soundio) | RT-safety, arm64-specific. Close/stop races the CoreAudio callback. → `ASI`/backlog bug, RT (P-02/AP-02). |
| **#16067** | macOS 12 AudioUnit crash on startup (effects) | `arch-effects-chain` | AudioUnit enumeration crash on Monterey; persists in `--safeMode`. → backlog bug. |
| **#14069** | Remove AVX requirement on the macOS build (illegal instruction) | `ASI` build | x86-only symptom, but it is a build-flags/arch-gating bug — data point for the `ASI` arm64-native/flags audit. → `ASI`. |
| **#13871+ suite** | TSan data races: `#13895` ControlValueAtomic, `#13894` Waveform ptr swap, `#13893` engineworkerscheduler, `#13863/#13870` PortAudio ring buffer, `#13861` BrowseThread | `arch-control-messaging`, `arch-audio-io`, `arch-waveform-render` | Cross-thread hand-off races (pat-16). Several reproduce on arm64. → TRACK + selectively fix under RT audit. |
| **#12970** | Qt bug: high CPU when scrolling library on macOS | `arch-library-db`/`arch-qml-ui` | Upstream Qt; watch for Qt version fix. → TRACK. |
| **#13101** | CPU overload peak triggering hotcues at 5.33 ms (macOS) | `arch-engine-realtime` | Xrun on hotcue at low buffer. Related to #8688. → `DSP`. |
| **#15522** | m4a low `audioVisualRatio` → overview OOM + crash | `arch-analyzer`/`arch-waveform-render` | Runaway allocation building overview. → backlog bug. |
| **#14561** | crash in `WaveformRenderMark::updatePlayPosMarkTexture` (OpenGL) | `arch-rendergraph` | OpenGL texture path crash; disappears in safe mode. Extra reason to move off forced-GL. → feeds `MTL`. |
| **#16370 / #10591** | startup crash on macOS / `std::bad_alloc` crash on macOS | (varies) | Low-detail; triage. → backlog. |
| **#14322 / #8614** | very long tracks truncated / end of some MP3s cut, macOS | `arch-sources-decode` | macOS decoder edge cases. → backlog. |
| **#13643 / #16270** | settings menu unreadable on macOS auto dark-mode / wrong system language | `arch-skin-widgets` | Cosmetic macOS-platform bugs. → low-priority backlog. |

## (B) Performance / GPU / DSP UPLIFTS

| # | title | context | maps-to |
|---|---|---|---|
| **#11761** | OpenGL deprecated since macOS 10.14 (`glTexSubImage2D`, `glDrawArrays` …) | `arch-rendergraph`/`arch-waveform-render` | The upstream motivation to leave OpenGL. Direct **`MTL`** driver alongside coreservices lead. |
| **#14990** | Add `WaveformRendererTextured` support in the **SceneGraph** backend | `arch-rendergraph` | Detailed/textured waveforms only exist on the OpenGL path; porting them to SceneGraph is what lets the Metal RHI backend render them. Core enabler for **`MTL`**. |
| **#13385** | Textured waveforms on OpenGL **ES** (ES-compatible rewrite of `WaveformRendererTextured`) | `arch-rendergraph` | Same rewrite unblocks RHI/Metal + iOS. → **`MTL`**. |
| **#14407** | SceneGraph rendergraph silently drops geometry past a vertex cap (stem waveforms render partially) | `arch-rendergraph` | Must be solved for stems on the SceneGraph/Metal path. → **`MTL`**. |
| **#11838** | Retire Simple GL and GLSL waveforms | `arch-waveform-render` | Renderer-surface reduction; fewer paths to port to Metal. → **`MTL`** (scope-shaping). |
| **#7084** | Waveforms need optimization/caching (high idle CPU even paused) | `arch-waveform-render` | Long-standing CPU cost; zero-copy GPU buffers + caching is exactly the `MTL` thesis (pat-21). → **`MTL`**. |
| **#7934 / #12953** | waveforms hitch when clicking new tracks / cover-art low-fps + waveform dropped frames | `arch-waveform-render` | Frame-time spikes on load; p99 frame-time metric target. → **`MTL`**. |
| **#8719** | Audit syscalls made from the PortAudio callback (dtrace) | `arch-audio-io`/`arch-engine-realtime` | Canonical RT-cleanliness task; NEON/Accelerate work must not reintroduce syscalls (P-02). → **`DSP`** (RT hygiene baseline). |
| **#8688** | Priority inversion: first track load spikes CPU → xrun | `arch-engine-realtime` | Warm-up/initialization moved off first-load. → **`DSP`**. |
| **#16120** | STEM loading CPU spike + dropout | `arch-engine-realtime` (stems) | Decode/allocation spike on load crossing RT deadline. → **`DSP`**. |
| **#15192** | Soundtouch keylock consumes all CPU (Rubberband fine) | `arch-engine-realtime`/`arch-effects-chain` | Time-stretch hot loop — prime NEON/vDSP candidate. → **`DSP`**. |
| **#13973 / #13986** | Rubberband v4 `RubberBandLiveShifter` / `OptionWindowShort` for `PitchShiftEffect` latency | `arch-effects-chain` | Lower-latency stretch path; measure on M4. → **`DSP`**. |
| **#6063 / #16077** | small PortAudio user-buffer regardless of host latency / support lower-latency interfaces | `arch-audio-io` | CoreAudio low-latency tuning; feeds the "feels like vinyl" latency goal. → **`ASI`**/`DSP`. |
| **#8687** | Thread priorities not set (Linux-reported; same RT-thread-priority concern applies to macOS P/E-core scheduling) | `arch-engine-realtime` | Relevant to `ASI` P/E-core awareness. → **`ASI`** (track + verify on macOS). |
| **#15242 / #13780** | Remove `-fno-lto` everywhere / `-ffast-math` + `infinity()` UB | `ASI` build | Build-flag correctness that any arm64/DSP fast-math tuning must respect. → **`ASI`**. |
| **#14545 / #16700 / #15376** | optimize metering / `final` QML properties (Qt 6.10) / heavy library ops off GUI thread | `arch-qml-ui`/`arch-library-db` | GUI-thread throughput; secondary to render/DSP. → backlog/track. |
| **#6383 / #6952** | sync controller polling with audio buffer | `arch-controllers-mapping` | Latency coupling; minor for M4. → track. |

## (C) FEATURES worth implementing

| # | title | context | note / home |
|---|---|---|---|
| **#15495** | Epic: HTDemucs ONNX offline stem separation | `arch-analyzer` | Strong M4 story — offload to Neural Engine / Accelerate / CoreML. High user value, self-contained worker (rt_safety none). → **NEW dossier** candidate (analyzer, aligns with `DSP`/ASI hardware). |
| **#7624** | Spectrogram waveform display | `arch-waveform-render` | New renderer; naturally lands on the tuned Metal path once `MTL` exists. → track for `MTL` follow-on. |
| **#13265 / #13499 / #6682 / #9224** | stacked overview / slip-mode animation / extended zoom / waveform gestures | `arch-waveform-render` | Waveform UX backlog; ride on `MTL` render work. → backlog. |
| **#16467 / #16521 / #16297** | stem waveform display/volume/sync features | `arch-waveform-render` (stems) | Couples to #14407 vertex-cap fix. → track with `MTL`. |

## (D) Upstream work to TRACK (fork_delta)

- **RHI/SceneGraph migration arc** — `#14990`, `#13385`, `#14407`, `#11838`, `#14377` ("accelerated GL ES
  waveforms broken on iOS", regression), `#13385`. Upstream is moving renderers off OpenGL onto the
  RHI/SceneGraph backend; this is the same substrate Migx needs for Metal. **Track closely and pull the
  SceneGraph renderer ports** rather than re-implementing — then delete the forced-OpenGL line
  (`coreservices.cpp:826`) once offscreen/controller-preview works under RHI. `arch-rendergraph`.
- **`#15537` Meta: Waveform things** — upstream's own waveform meta-tracker; watch for consolidation.
- **TSan race suite** (`#13871`, `#13895`, `#13894`, `#13893`, `#13863`, `#13870`, `#13861`) — cross-thread
  hand-off correctness (pat-16); several arm64. Track upstream fixes; fix locally only where they block
  RT guardrails.
- **`#12970`** macOS library-scroll CPU is an upstream Qt issue — track Qt version bumps.
- **`#16728` Android / `#14377` iOS** — upstream cross-platform RHI pressure keeps the Metal-capable
  backend healthy; free tailwind for `MTL`.

---

## Top ~10 (ranked by M4-relevance × user-value × tractability)

| # | issue | why it ranks | recommended home |
|---|---|---|---|
| 1 | **coreservices.cpp:826 + #11761 / #14990** | The single line forcing OpenGL is the north-star `MTL` blocker; #11761/#14990 are the upstream levers to remove it. Highest M4 relevance. | **`MTL` dossier** (baseline + Metal-enable) |
| 2 | **#8719** audit PortAudio-callback syscalls | Establishes the RT-clean baseline every `DSP` change is judged against (P-02); high tractability. | **`DSP` dossier** (RT hygiene wave) |
| 3 | **#15192** Soundtouch keylock all-CPU | Concrete DSP hot loop; textbook NEON/vDSP win, measurable. | **`DSP` dossier** |
| 4 | **#8688** priority inversion → first-load xrun | Real audible glitch on M4 sets; fixable via warm-up init. | **`DSP` dossier** (or task) |
| 5 | **#7084** waveform caching / idle CPU | Directly tests the zero-copy-GPU thesis (pat-21); user-visible CPU/battery. | **`MTL` dossier** |
| 6 | **#13871** arm64 CoreAudio close/stop race | arm64-specific RT correctness bug; guardrail-relevant. | **`ASI`/backlog bug**, RT-reviewed |
| 7 | **#14407** SceneGraph vertex cap (stems) | Must be solved for stems on the Metal/SceneGraph path; blocks stem waveforms. | **`MTL` dossier** |
| 8 | **#15495** HTDemucs ONNX stem separation | Flagship M4 feature (Neural Engine/CoreML); high user value, isolated worker. | **NEW analyzer dossier** |
| 9 | **#16120** STEM load CPU spike + dropout | Audible dropout crossing RT deadline; sharpens `DSP` load-path work. | **`DSP` dossier** |
| 10 | **#6063 / #16077** low-latency CoreAudio buffer | Advances the "feels like vinyl" latency goal on Apple audio HW. | **`ASI`/`DSP`** |

## How this was gathered (reproducible)

```
# public repo, gh 2.87.3, authenticated
for T in macOS "Apple Silicon" Metal performance latency CoreAudio waveform \
         OpenGL RHI "CPU usage" GPU scenegraph M1 SIMD dropout keylock; do
  gh issue list --repo mixxxdj/mixxx --state open --limit 30 --search "$T"
done
# detail:
gh issue view <n> --repo mixxxdj/mixxx --json number,title,labels,body
# in-tree confirmation of the Metal blocker:
grep -n setGraphicsApi src/coreservices.cpp   # -> line 826
```
Notes: `RHI` returned no title/body hits (Mixxx issues say "SceneGraph"/"RHI backend" in prose, not
titles); the RHI arc surfaced via the OpenGL/scenegraph queries instead. Counts are open issues as of
2026-07-17.
