---
id: ADR-004
type: decision
title: "UI stack — QML-primary for the performance shell; Rive optional polish; React only arm's-length"
status: proposed
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
supersedes: []
amends: []
related:
  - ADR-002
  - ADR-003
  - design-md-ui-modernization
  - world-model-experience-ontology
  - initiative-apple-silicon
  - arch-qml-ui
  - arch-skin-widgets
  - arch-rendergraph
  - arch-waveform-render
note: >
  Revised 2026-07-17 after tree scan + industry/X discourse review. Status stays `proposed`
  until Gudjon accepts. Framing is QML-primary (not purity "QML-only").
---

# ADR-004 — UI stack: QML-primary shell (not Rive-as-framework, not React-for-all)

## 1. Context

### 1.1 The question
Is **QML-only** better for Migx's UI than the **Rive** engine or **React** (typically Electron /
webview) for *all* UI?

### 1.2 Why this is load-bearing
Migx is a hard fork (ADR-002) of a C++/Qt DJ app, aimed at **AI-DJing** with deep native engine access
and a north-star of **blazingly fast on Apple Silicon (Metal)**. The UI stack choice determines:

- whether sample-synced waveforms and sub-frame control stay on a viable path;
- whether the #1 legacy retirement (`arch-skin-widgets` QWidget skins) is the same work as product UI;
- whether proprietary AI value can sit arm's-length (ADR-003) without Chromium owning the deck surface;
- whether MTL/render benchmarks measure a path we will keep.

A wrong "one framework for everything" choice is expensive to reverse after skins, designers, and
agents have invested in it.

### 1.3 What already exists in the tree (not a greenfield pick)
| Asset | Location / fact | Implication |
|---|---|---|
| Qt Quick UI (developing) | `src/qml/` (~74 files), `res/qml/` (`Deck.qml`, `Mixer.qml`, …) | In-process path already paid for |
| Control binding | `QmlControlProxy` → `[Group],key` | Matches house bus (`P-06`); no web bridge required |
| Waveform items | `QmlWaveformDisplay` / overview | Hosted on scene graph / `arch-rendergraph` |
| Legacy skin engine | `src/skin/legacy/` + `src/widget/` (`arch-skin-widgets`) | Retirement target; dual-stack today |
| Forced OpenGL RHI pin | `src/coreservices.cpp:826` — `QQuickWindow::setGraphicsApi(OpenGL)` | Blocks native Metal for QML until MTL un-pins |
| Design-token plan | `kanban/knowledge/design-md-ui-modernization.md` | DESIGN.md → `Theme.qml` first; Tailwind for web only |
| Experience ontology | `kanban/knowledge/world-model-experience-ontology.md` (EXO) | Co-pilot v1 is **files + CO**, not a web shell |
| MTL readiness | native arm64 `mixxx` / `mixxx-test`; bench harness live | Perf contracts will run on the Qt render path |

### 1.4 Industry / X discourse (2025–2026) — what to take and what to ignore

X (and adjacent eng discourse) is **not** a vote; it is a map of incentives. Patterns relevant to Migx:

**A. Electron/React wins DX; users pay the tax.**  
Common framing: ship 500 MB+ Electron so devs avoid Qt; web teams and AI codegen favor React. Counter:
Qt/QML praised when people want *non*-"Electron slop," lower footprint, and real desktop performance.
A recurring split: *devs prefer Electron; power users and systems people prefer Qt/native.* For a gigging
DJ app on M4 under load, **user/thermal constraints dominate developer convenience.**

**B. "Electron is fine now" is about chat/IDEs/docs — not continuous GPU + audio.**  
Claims that a well-written Electron app is "not that much heavier" than modern Qt may hold for
document UIs. They do not transfer to **sample-synced dual-deck waveforms at 60–144 fps** next to a
real-time audio callback. Media/tooling discourse still treats scrubbing / continuous render as a reason
to stay native (or abandon web shells mid-project).

**C. Hybrid "native host + web panel" is the grown-up pattern when web is needed.**  
Discourse increasingly favors native shells (SwiftUI/Qt/C++) with optional WebKit/webview for
browser-shaped features — not Chromium for the whole product. That pattern maps cleanly to Migx:
**QML shell + optional arm's-length React surface for AI/chat.**

**D. Rive is winning as a motion/runtime, not as an app framework.**  
Rive's public story: state machines, designer-owned interactive graphics, C++ runtime, strong GPU path
(Rive Renderer demos vs Skia/Impeller), dramatic size/CPU wins vs Lottie for *animations*. Integrations
are host-embedded (Flutter, Unity, web, iOS/Android). Gaps called out even by fans: host resize/sync
friction, production reliability of editor/runtime, and the fact that a `.riv` file is a **component
mini-app**, not a library table / settings tree / accessibility stack. **No credible line of discourse
positions Rive as a full DAW/DJ shell.**

**E. High-perf visual tools still go metal-close.**  
Builders who care about frame time abandon layered abstractions (SwiftUI / Tauri / Electron / RN /
Flutter) for **direct Metal/DX** or native GUI + GPU APIs when continuous interactive graphics are the
product. Waveform viewers that matter are LOD/GPU-native, not DOM-native.

**Takeaway for this ADR:** X rewards React/Electron for *shipping speed on generic apps* and Rive for
*premium motion*. Migx's product is the opposite constraint set: **native RT coupling + Metal + low
thermal headroom**. Discourse that optimizes for SaaS desktop DX is out of scope.

---

## 2. Decisive constraint — two surfaces, opposite physics

A DJ product is **not one UI**. Collapsing both surfaces into one framework is the root mistake.

### Surface A — Performance shell (must stay native)
Decks, scrolling **waveforms**, mixer, jog/scratch, FX, meters under load.

| Requirement | Why |
|---|---|
| Sample-synced visual position | Playhead must track audio; lock-free visual taps (`VisualPlayPosition` / CO), not IPC polls |
| 60–144 fps under multi-deck load | Frame budget is a **contract** (`P-03`, `P-18`) — p99/max, not mean |
| Metal on Apple Silicon | OpenGL-on-macOS is deprecated/compat; north-star is M4/M5 + Metal (`initiative-apple-silicon`) |
| In-process C++ binding | Deep native access thesis (ADR-002 Cursor analogy) |
| Off the audio deadline | GUI may never gate or block the RT callback (`P-02`, `P-20`, `P-21`) |
| Sub-frame input path | Scratch/jog latency is product quality |

**Disqualifiers for Surface A:** Chromium/Electron whole-app, GC-heavy render loops as the waveform
host, any design that makes the audio path wait on UI IPC.

### Surface B — Management / AI surface (latency-tolerant)
Library browser, crates, preferences, onboarding, **AI co-pilot** (chat, suggestions, session coach).

| Requirement | Why |
|---|---|
| Dense data UI | Tables, filters, multi-pane library |
| Fast iteration + agent tooling | DESIGN.md / Tailwind / web AI stack thrive here |
| May be process- or network-separated | ADR-003 arm's-length proprietary service |
| Must not own decks/waveforms | Boundary integrity |

EXO/world-model v1 further weakens "need React for AI": the co-pilot's first closed loop is
**sidecar files + ControlObject** (`ontology.json`, session mirror), not a browser shell. React is an
*optional presentation* for Surface B, not a prerequisite for intelligence.

---

## 3. Options considered

### 3.1 QML (Qt Quick) — primary shell

**What it is:** Declarative UI + JS on Qt's scene graph; C++ types/proxies registered into the QML
engine; on modern Qt, SceneGraph → **QRhi** → Metal/Vulkan/D3D/OpenGL.

**Fit to Migx:**
- Already integrated (`arch-qml-ui`): `QmlControlProxy`, `QmlWaveformDisplay`, player/library/effects
  proxies; GUI-thread only, engine only via CO (`src/qml/AGENTS.md`).
- Same process as the engine — no JS↔C++ desktop bridge for every fader tick.
- Waveform path can share `arch-rendergraph` / scenegraph work with MTL (once OpenGL pin is removed).
- Retiring `arch-skin-widgets` **is** the QML migration — product UI and legacy prune are one program
  under ADR-002 freedom.

**Honest cons:**
- Smaller talent pool than React; designer motion tooling weaker than Rive.
- QML is not automatically fast: binding thrash, JS on the hot path, or naive models can miss frame
  budgets. **Discipline + benchmarks required** (`P-03`).
- Mixxx QML is still dual-stack and incomplete vs legacy skins; "primary" is multi-dossier, not a flag.
- Forced OpenGL at `coreservices.cpp:826` is a known blocker for Metal QML — owned by MTL / render work.

**Verdict:** **Only viable primary for Surface A.** Also the default host for most of Surface B
(library, prefs) until a *decoupled* web surface is deliberately introduced.

### 3.2 Rive — complement, not framework

**What it is:** Designer tool + stateful `.riv` format + lightweight multi-platform **runtime** (C++
core; optional Rive Renderer with strong GPU demos). Embeds into hosts; not a layout/OS UI toolkit.

**Fit to Migx:**
- Excellent for **branded motion**: knobs, deck transitions, AI "presence" chrome, onboarding moments.
- Native-ish embedding possible (C++ runtime, Metal-capable renderer) — **no Chromium required**.
- Aligns with premium product feel without rewriting the shell.

**Hard limits:**
- No full app shell: complex layout, text input, virtualized library lists, a11y tree, prefs, menus.
- Does **not** replace `QmlWaveformDisplay` / sample-synced waveform pipelines.
- Extra composite layer if embedded poorly → risk of fighting scenegraph or display budget (`P-21`).
- Production/editor reliability is a known industry caveat; treat as **optional dependency**, not
  critical path.

**Verdict:** **Optional complement inside the QML host**, after Metal/QML baselines exist. **Never**
"all UI." **Not** on the critical path for MTL or EXO spikes.

### 3.3 React — arm's-length only (never the performance shell)

**What it is:** Web UI library. On desktop, almost always **Electron (Chromium)** or a **webview**
(Qt WebEngine / WKWebView) or a separate browser/companion app.

**Where it shines (and discourse agrees):**
- Talent density, component ecosystem, AI/agent codegen, DESIGN.md → Tailwind for free.
- Chat UIs, dashboards, account/billing for a **proprietary AI service** (ADR-003).
- Companion web/mobile clients that do not drive waveforms.

**Where it fails Surface A (fatal):**
- Chromium memory/CPU/thermal cost fights Apple Silicon north-star under multi-deck + waveform load.
- Waveform-as-canvas/WebGL is a second engine, not the Mixxx visual pipeline; sample sync across IPC is
  latency and complexity debt.
- Deep engine access becomes bridge protocol design instead of `QmlControlProxy` — opposite of ADR-002's
  "Cursor-depth" thesis.
- Whole-app Electron makes the GPL DAW binary drag a browser; still doesn't make closed distribution
  legal (ADR-003) — you pay the cost without solving licensing.

**Variants explicitly rejected for Surface A:**
| Variant | Why rejected for decks/waveforms |
|---|---|
| Electron whole app | Chromium tax; wrong render model; process boundary everywhere |
| Qt WebEngine as main UI | Still Chromium-class weight; waveforms don't belong there |
| Tauri + React shell | Thinner than Electron but still webview UI; bridge to Mixxx engine remains wrong for Surface A |
| React Native Desktop | Better for some apps; not wired to Mixxx CO/scenegraph; not Metal waveform path |

**Verdict:** **Allowed only for Surface B as a decoupled surface** (separate app, optional panel, or
service front-end). **Forbidden** as host for decks, mixer, or waveforms. Prefer proving co-pilot value
via EXO files + QML chrome **before** introducing React.

### 3.4 Other options (briefly rejected)
| Option | Why not |
|---|---|
| Stay on legacy QWidget skins forever | Largest legacy surface; blocks modern theming/agent UI; dual-maint forever |
| SwiftUI-only (macOS) | Abandons cross-platform Qt base and existing QML investment; rewrite tax |
| Dear ImGui / custom immediate GUI | Fast prototypes; poor for library/a11y/product skinning; not Mixxx's trajectory |
| Flutter as full shell | Second runtime; no existing investment; still not the CO/waveform stack |
| Hand-rolled Metal UI framework | Heroic; abandons Qt ecosystem; multi-year distraction from AI-DJing thesis |

---

## 4. Decision

**Pending owner acceptance** (`status: proposed`). The recommended decision:

1. **QML-primary for the product shell.**  
   Surface A (performance) is **QML + C++ proxies + scenegraph/RHI only**. Surface B defaults to QML
   (library, prefs, primary AI chrome). Framing is **QML-primary**, not purity "QML-only" — complements
   may exist at clear boundaries.

2. **Rive is optional polish, not a framework.**  
   Embed only as QML/scenegraph-hosted components for motion/brand. **Deferred** until:
   - OpenGL pin removed / Metal path baselined (MTL), and
   - Primary deck/library flows work in QML.  
   No Rive dependency on the critical path.

3. **React only arm's-length, non-real-time.**  
   Allowed for: proprietary AI service UI, companion web/mobile, optional co-pilot panel that never owns
   decks/waveforms/mixer. **Forbidden:** Electron (or equivalent) as the main app host; web-rendered
   primary waveforms; React as the ControlObject authority path.

4. **Design tokens are framework-agnostic.**  
   DESIGN.md remains SSoT (`design-md-ui-modernization`): generate `res/qml/Theme.qml` for the shell;
   stock Tailwind/DTCG export for any web surface. Look-and-feel consistency does **not** require one
   runtime.

5. **Legacy retirement is the same program as QML-primary.**  
   Under ADR-002, Migx may retire `arch-skin-widgets` behind build+test gates. Do not maintain a third
   parallel UI stack (QWidget + QML + React-core).

6. **House physics apply to every UI path.**  
   - GUI-thread only for UI objects (`P-20`, `AP-14`).  
   - One writer per ControlObject (`P-06`, `AP-03`).  
   - Waveform/GPU work never gates the audio deadline (`P-21`, `P-23`).  
   - Perf claims need p99/max + zero underruns vs pinned baseline (`P-03`, `P-18`) — not "feels smooth."

---

## 5. Architecture sketch (target)

```text
┌──────────────────────────────────────────────────────────────────────┐
│  Migx process (GPLv2-derived DAW)                                    │
│                                                                      │
│  [ Engine RT C++ ] ── CO / lock-free visual taps ──► [ QML shell ]   │
│       P-02                                              Surface A+B  │
│                                                         SceneGraph   │
│                                                         → RHI →Metal │
│                                                              │       │
│                                              optional ┌──────┴─────┐ │
│                                                       │ Rive items │ │
│                                                       │ (polish)   │ │
│                                                       └────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                    │ files / IPC / network (arm's-length)
                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Optional proprietary AI surface (ADR-003)                           │
│  React/web or other — chat, account, cloud intelligence              │
│  NEVER owns decks / waveforms / mixer authority                      │
└──────────────────────────────────────────────────────────────────────┘
```

EXO/session ontology lives in **sidecars + engine state**; UI (QML or web) is a reader/proposer, not a
second predictor of engine phase (world-model T8).

---

## 6. Consequences

### 6.1 Positive
- Aligns UI with MTL: benchmarks improve the path we ship.
- Legacy skin retirement has a destination (`arch-qml-ui`), not a vacuum.
- Preserves deep native access and Apple Silicon thesis.
- Leaves room for premium motion (Rive) and proprietary AI UX (React) without contaminating Surface A.
- DESIGN.md works for both shell and web without forcing one framework.

### 6.2 Costs / risks
- Must invest in QML skill, component library, and agent skills (DESIGN.md / `pat-*`) to offset React DX.
- Dual-stack period (legacy skin + QML) until retirement gates pass — plan dossiers, don't indefinite-fork.
- Bad QML can still jank; require render/input benchmarks as acceptance, not aesthetics alone.
- Optional Rive adds dependency and compositing complexity if adopted early — hence **deferred**.

### 6.3 Non-goals (explicit)
- Electron (or full-app Chromium) as the Migx host.
- Rive as layout system, library browser, or waveform engine.
- React as writer of deck/mixer ControlObjects or host of primary waveforms.
- Rewriting the engine UI layer in Flutter / SwiftUI / custom immediate-mode as the default path.
- Blocking MTL or EXO file spikes on Rive/React decisions.

---

## 7. Success metrics & falsification

### 7.1 Accept this ADR's direction when
| Metric | Gate |
|---|---|
| Waveform/render | p99 frame time under multi-deck scenario ≤ budget vs pinned MTL baseline; **zero audio underruns** |
| Input | Jog/scratch path latency competitive with pre-change native path (measured) |
| Coupling | Surface A reaches engine only via CO/proxies; no new RT alloc/lock from UI (`P-02`) |
| Stack count | At most one primary shell (QML); legacy skins shrinking behind gates; no third full stack |
| Thermals/memory | Multi-deck + waveforms sustainable on target M-series without Chromium-class baseline RAM |

### 7.2 Falsify / revisit if
- QML+scenegraph+Metal cannot meet p99/underrun contracts after good-faith MTL work **and** a web or
  alternate path demonstrably can (measured, same scenarios).
- Product strategy abandons desktop native DJ performance for a pure companion/cloud UX (different app).
- A future host runtime appears that is in-process, Metal-native, CO-bindable, and cheaper than QML
  *with* a migration path from `src/qml` (unlikely near-term).

Until falsified, **do not** re-open "React for all UI" or "Rive for all UI" as default strategy.

---

## 8. Sequencing (execution order)

```text
Now     MTL baseline (EVD) on current render path; un-pin OpenGL → Metal when ready
        Accept/reject this ADR (strategy freeze)
        DESIGN.md → Theme.qml spike (DUI) when ready — does not block MTL

Next    QML feature parity for primary deck + library flows
        Retire legacy skin paths behind build+test gates (ADR-002 prune)

Later   Optional Rive embed for branded motion (post-baseline)
        Optional React co-pilot / companion (post EXO file loop; ADR-003 boundary)
```

**Dependencies:**
- MTL does **not** wait on Rive/React.
- EXO v1 does **not** wait on React (files + CO first; `FSL` sidecar first).
- UI modernization initiative (if stood up) owns QML-primary + skin retirement; cites this ADR.

---

## 9. Alternatives summary (decision table)

| Concern | QML-primary | Rive-all | React/Electron-all |
|---|---|---|---|
| Sample-synced waveforms | ✅ path exists | ❌ not a waveform pipeline | ❌ wrong model / bridge |
| Metal / Apple Silicon | ✅ RHI path (after pin) | ⚠️ possible embed only | ❌ thermal/RAM fight |
| In-process CO binding | ✅ `QmlControlProxy` | ❌ no app data model | ❌ IPC-centric |
| Library / a11y / prefs | ✅ Qt models | ❌ missing shell | ✅ strong |
| Motion design tooling | ⚠️ moderate | ✅ best | ✅ web-strong |
| Talent / AI codegen | ⚠️ smaller | ⚠️ niche | ✅ largest |
| ADR-003 AI service UI | optional QML chrome | n/a | ✅ arm's-length web |
| Legacy prune alignment | ✅ same effort | ❌ new stack | ❌ abandons investment |
| **Role in Migx** | **Primary shell** | **Optional polish** | **Optional Surface B only** |

---

## 10. Status & follow-ups

**Status:** `proposed` — recommendation for Gudjon. On accept:
- Flip `status: accepted` and record date.
- Seed / align UI-modernization + legacy-retirement initiative with this ADR as SSoT.
- Cite from `arch-qml-ui`, `arch-skin-widgets`, DESIGN.md knowledge note, and EXO initiative (when registered).
- Keep Rive/React as **explicit non-blocking** options in planning; do not gate MTL.

**If rejected:** document the chosen alternative with the same Surface A metrics table — do not silently
drift into Electron-for-convenience.

---

## Appendix A — Key code anchors
| Anchor | Path |
|---|---|
| OpenGL RHI force-pin | `src/coreservices.cpp:823–826` |
| QML app + proxies | `src/qml/qmlapplication.cpp`, `qmlcontrolproxy.*`, `qmlwaveformdisplay.*` |
| QML assets | `res/qml/` |
| Legacy skins | `src/skin/legacy/`, `src/widget/` |
| Rendergraph / scenegraph | `src/rendergraph/` |
| Domain charters | `src/qml/AGENTS.md`, `kanban/architecture/ddd/bounded-contexts/arch-qml-ui.md` |

## Appendix B — Discourse notes (non-normative)
Industry/X themes that informed §1.4 (illustrative, not citations of truth):
- Qt/QML defended as non-Electron "real desktop"; Electron defended for DX and complex-app velocity.
- Native + optional webview hybrid preferred over full Chromium for system apps.
- Rive positioned as cross-platform interactive **animation** with strong GPU runtime demos; host
  integration quality varies; not marketed as a full application framework.
- Continuous interactive graphics / waveform tooling still gravitates to GPU-native pipelines.

Agents must not treat social consensus as acceptance criteria; §7 metrics do.
