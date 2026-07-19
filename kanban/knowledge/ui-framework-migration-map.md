---
id: ui-framework-migration-map
type: knowledge
title: "UI framework migration map — what to migrate to, modular components, AI-migration process"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-07-19"
lastUpdated: "2026-07-19"
defers_to:
  - kanban/architecture/decisions/ADR-004-ui-stack-qml-vs-rive-vs-react.md
  - kanban/knowledge/design-md-ui-modernization.md
  - kanban/architecture/ddd/bounded-contexts/arch-qml-ui.md
  - kanban/architecture/ddd/bounded-contexts/arch-skin-widgets.md
  - kanban/Strategy-Current.md
inspired_by:
  - "https://claude.com/blog/ai-code-migration (2026-07-16 Anthropic — fix the process/loop, not only the code)"
  - "https://github.com/anthropics/code-migration-kit-with-claude-code"
---

# UI framework migration map (first step: **what** + **modular units**)

**Ask:** Migrate Migx UI into a “new and better” framework, modular and manageable — informed by AI code-migration practice and trends.  
**First step (this doc):** decide **target stack**, inventory **components as migration units**, define **module seams**. Not a full port plan yet.

**Core insight (Anthropic migration guide):** *Don’t fix only the code — fix the **process (loop)** that will produce the new UI.* Rulebook → dependency map → gap inventory → stress-test → translate in batches → mechanical judge (tests / visual contracts / CO parity).

---

## 1. What we have today (dual stack)

| Layer | Bounded context | Truth paths | Maturity |
|---|---|---|---|
| **Legacy performance shell** | `arch-skin-widgets` | `src/skin/`, `src/widget/`, `res/skins/*` (XML + QSS + WWidget) | Hardened, upstream-shaped |
| **New Qt Quick shell** | `arch-qml-ui` | `src/qml/`, `res/qml/` (~116 `.qml` files) | Developing, `fork_delta: migx-new` |
| **Control bus (stable)** | `arch-control-messaging` | `[Group],key` via `ControlProxy` / `QmlControlProxy` | Load-bearing — **not migrated away** |
| **Waveform / GPU** | `arch-waveform-render` + `arch-rendergraph` | C++ render path; QML hosts items | Separate program (MTL); UI only *hosts* |

**Today’s product reality:** most gigs still run **QWidget skins** (LateNight, Tango, …). QML is the **destination shell** (ADR-004) but not yet sole primary. Co-Pilot chrome already lives in QML (`res/qml/Settings/CoPilot.qml`).

```text
                    ┌─────────────────────────────────────┐
  GUI thread only   │  Surface A: Performance shell       │
  (P-20)            │  decks · waveforms · mixer · FX     │
                    │  ── today: skin XML OR QML ──       │
                    └──────────────┬──────────────────────┘
                                   │ QmlControlProxy /
                                   │ ControlWidgetConnection
                    ┌──────────────▼──────────────────────┐
                    │  Control bus  [Group],key  (P-06)   │  ← keep forever
                    └──────────────┬──────────────────────┘
                                   │ lock-free / CO
                    ┌──────────────▼──────────────────────┐
  RT thread         │  Engine (never hosts UI)            │
                    └─────────────────────────────────────┘

  Surface B (latency-tolerant): Library tables · Settings · Co-pilot · onboarding
  ── today: hybrid skin widgets + QML Settings/Library ──
```

---

## 2. Framework decision (recommendation)

### 2.1 Candidate “new UI frameworks”

| Candidate | Fit Surface A (decks/waveforms) | Fit Surface B (library/AI) | Agent/DX | Verdict for Migx |
|---|---|---|---|---|
| **Qt Quick / QML 6** (already in tree) | Strong if Metal unpinned | Strong | Good; DESIGN.md → Theme bridge | **Primary destination** (ADR-004) |
| **Legacy QWidget skins** | Proven | Clunky for AI chrome | Weak for agents | **Retirement source**, not target |
| **SwiftUI + AppKit** (AS-only) | Possible with Metal views; **rewrites** all CO bridges | Excellent for settings | High agent hype | **Not first migration** — second-system risk; keep as long-range option if QML+Metal fails |
| **Electron / React full shell** | **Disqualified** (ADR-004, RT + fps) | Good for chat panels | Best AI codegen | **Arm’s-length only** (AI panel in WebView) |
| **Flutter / RN** | Weak for sample-synced waveforms | Mediocre desktop | Mixed | **No** |
| **Rive** | Motion components only | N/A | Designer-owned | **Optional polish inside QML**, not the framework |
| **Slint / iced / pure Metal UI** | Speculative | Weak ecosystem | Thin | Research only |

### 2.2 Recommended target architecture

| Surface | Framework | Module packaging |
|---|---|---|
| **A — Performance shell** | **Qt Quick 6 (QML)** + C++ proxies + Metal rendergraph | Feature modules under `res/qml/<Feature>/` + `src/qml/` proxies |
| **B — Management / AI** | **QML first**; optional **WebView/React island** for pure chat/docs | `Settings/`, `Library/`, `CoPilot/` modules |
| **Design system** | **DESIGN.md** tokens → generated `Theme.qml` (+ later QSS vars) | `res/design/DESIGN.md` SSoT |
| **Motion candy** | Optional **Rive** embeds | Isolated components, not layout host |

**What we are *not* migrating:** engine, ControlObject bus, analyzer, library DB — only the **GUI presentation** layer that binds to them.

**What “better” means here (measurable):**
1. One primary shell (QML), skins retired or viewer-only.  
2. Every screen is a **module** with clear inputs (controls/models) and no RT touch.  
3. Tokens/theme agent-editable (DESIGN.md).  
4. Metal path for waveforms (unpin OpenGL RHI).  
5. Co-pilot is first-class chrome, not a bolted dialog.

ADR-004 stays **proposed** until owner accept; this map assumes accept-with-modular-discipline.

---

## 3. Modular component inventory (migration units)

Each unit is a **batch for AI migration**: one rulebook entry, one dependency edge set, one visual/CO acceptance check. Prefer **feature slices**, not “port all QML files.”

### 3.1 Surface A — performance shell modules

| Module ID | QML / host today | CO / proxy seam | Legacy skin counterpart | Migrate as… |
|---|---|---|---|---|
| `mod-deck-shell` | `Deck.qml` + `Deck/*` | `QmlPlayerProxy`, play/cue/hotcue/sync COs | Deck XML blocks | Atomic vertical slice |
| `mod-waveform-scroll` | `WaveformDisplay.qml`, `Mixxx/Controls/WaveformDisplay.qml` | `QmlWaveformDisplay` | `WWaveformViewer` | **Depends on MTL** (Metal unpin) |
| `mod-waveform-overview` | `WaveformOverview.qml`, markers | overview COs + hotcue markers | `WOverview` | After scroll path stable |
| `mod-mixer` | `Mixer.qml`, `MixerColumn.qml`, `CrossfaderRow.qml` | channel faders, XF, PFL | Mixer skin | Parallel to decks |
| `mod-eq` | `EqColumn.qml`, `EqKnob.qml` | EQ kill/gain COs | EQ widgets | Small, good stress-test |
| `mod-fx` | `EffectUnit.qml`, `EffectSlot.qml`, `EffectRow.qml` | `QmlEffectsManagerProxy` | FX skin | Medium |
| `mod-hotcue` | `Hotcue*.qml`, `Deck/HotcueAndStem.qml` | hotcue COs | Hotcue buttons | Ties to FSL cues export |
| `mod-tempo` | `Deck/TempoColumn.qml`, sync/bpm widgets | rate/sync COs | Tempo widgets | Small |
| `mod-spinny` | `Deck/Spinny.qml`, `Mixxx/Controls/Spinny.qml` | vinyl/spinny COs | `WSpinny` | Optional / polish |
| `mod-sampler` | `Sampler.qml`, `SamplerRow.qml` | sampler group COs | Sampler skins | After dual-deck |
| `mod-vu` | `VuMeter.qml` | peak/vu COs | VU widgets | Small |
| `mod-mic-aux` | `Microphone*.qml`, `AuxiliaryUnit.qml` | mic/aux COs | Mic section | Later |

### 3.2 Surface B — management / AI modules

| Module ID | Paths | Seam | Notes |
|---|---|---|---|
| `mod-library` | `Library.qml`, `Library/*` | `QmlLibraryProxy` | Dense tables — keep QML; not Electron |
| `mod-settings` | `Settings.qml`, `Settings/*` | prefs COs / dialogs | Already modular categories |
| `mod-copilot` | `Settings/CoPilot.qml`, `CoPilot/*` | EXO JSON / intents (Layer B) | **Product differentiator** — grow here |
| `mod-controller-prefs` | `Settings/Controller*.qml` | controller manager | Maps stay JS/XML (`P-30`) |
| `mod-sound-hardware` | `Settings/SoundHardware.qml`, AudioRouter | sound device config | First-run pain surface |
| `mod-theme` | `Theme/Theme.qml` | DESIGN.md generator output | **Design system root** |
| `mod-primitives` | `Button.qml`, `Knob.qml`, `Fader.qml`, `Mixxx/Controls/*` | pure UI + optional CO | **Shared kit** — migrate/stabilize first |

### 3.3 C++ proxy / host modules (not optional)

| Module ID | Path | Role |
|---|---|---|
| `mod-qml-app` | `src/qml/qmlapplication.*` | Engine bootstrap, type registration |
| `mod-qml-control-proxy` | `src/qml/qmlcontrolproxy.*` | Generic `[Group],key` |
| `mod-qml-player-proxy` | `src/qml/qmlplayerproxy.*` | Deck state |
| `mod-qml-library-proxy` | `src/qml/qmllibraryproxy.*` | Track lists |
| `mod-qml-waveform` | `src/qml/qmlwaveformdisplay.*` | Waveform item host |
| `mod-qml-effects-proxy` | `src/qml/qmleffectsmanagerproxy.*` | FX model |

**Invariant for every module:** GUI thread only; engine only via CO; no second writers (`P-06`/`P-20`).

### 3.4 Dependency sketch (order of work)

```text
mod-theme + mod-primitives          ← stress-test batch (DESIGN.md loop)
        │
        ▼
mod-eq, mod-vu, mod-tempo           ← small CO-bound widgets
        │
        ▼
mod-deck-shell + mod-hotcue         ← vertical deck without full waveform GPU
        │
        ▼
mod-mixer + mod-fx
        │
        ▼
mod-waveform-*   (after MTL Metal unpin)
        │
        ▼
mod-library + mod-settings (parity with skin prefs)
        │
        ▼
mod-copilot (Layer B product)
        │
        ▼
Retire arch-skin-widgets default path  (viewer/export only if needed)
```

---

## 4. How we work with each component (modular rules)

### 4.1 Module contract (every `mod-*`)

```yaml
# res/qml/_modules/<id>/MODULE.md  (proposed layout — future)
id: mod-eq
surface: A
qml_root: EqColumn.qml
proxies: [QmlControlProxy]
controls_read: ["[ChannelN],filterLow", ...]
controls_write: []   # or single-writer CO keys if any
theme_tokens: [color.control.fill, space.sm]
rt_safety: none
acceptance:
  - visual: screenshot vs golden (optional)
  - behavior: CO values match when UI actuated (gtest or scripted)
  - no_src_engine_edit: true
```

### 4.2 Binding pattern (canonical)

| UI action | Allowed path | Forbidden |
|---|---|---|
| Show value | `QmlControlProxy` / typed proxy read | Polling engine from QML timer on RT data |
| User moves fader | Single CO writer path as today | Direct `EngineBuffer` calls from QML |
| Waveform paint | Scene graph / rendergraph item | Sync wait on audio callback |
| Co-pilot propose | Files / intent inbox → QML model | Automix without Ack |

### 4.3 Folder target (manageable tree)

```text
res/qml/
  Theme/                 # generated + hand tokens
  primitives/            # Button, Knob, Fader (rename from root clutter over time)
  modules/
    deck/
    mixer/
    library/
    settings/
    copilot/
  main.qml
src/qml/
  proxies/               # optional reorg; keep ABI-ish registration stable
```

Migrate **in place first** (rulebook + MODULE.md), physical reorg second (avoids big-bang path thrash).

---

## 5. AI migration process (adapted from Anthropic guide)

| Step | Migx UI meaning | Artifacts |
|---|---|---|
| **0. Judge** | CO parity scripts + optional screenshot contracts + “app launches” | `tools/ui/` or gtest; dogfood checklist |
| **1. Rulebook** | QML style, CO binding, theme tokens, no-RT rules | `kanban/architecture/ui-migration-RULEBOOK.md` |
| **1. Map** | Module deps (above) | this file §3 |
| **1. Gaps** | Skin-only widgets with no QML twin; OpenGL pin; accessibility | `ui-migration-GAPS.md` |
| **2. Stress-test** | Port **one** small module three ways; refine rules; **discard** code | e.g. `mod-eq` or Theme spike (DUI) |
| **3. Translate batches** | Parallel agents per module; `// TODO(ui-port):` for unknowns | worktrees per module |
| **4–6. Compile / run / match** | `just build`; launch dogfood; CO + visual parity | build daemon pattern if multi-agent |

**Human hours front-loaded** on rulebook + stress-test. After that: queues burn down.

**Do not** start a SwiftUI rewrite as the stress-test — that is a second product. Stress-test is **QML module quality + DESIGN.md**, unless an owner decision reopens ADR-004.

---

## 6. Gap inventory (high-level)

| Gap | Why it blocks “better UI” | Owner program |
|---|---|---|
| QWidget skins still default for many users | Dual stack cost | Skin → QML module batches |
| QML RHI pinned OpenGL on macOS | Blocks Metal north-star | MTL / ADR path |
| No DESIGN.md → Theme pipeline yet | Agents restyle inconsistently | `design-md-ui-modernization` / DUI |
| Waveform host dual paths | Two physics stories | Host only QML item after MTL |
| Co-pilot offline vs live | Product seam incomplete | EXO Layer B after green app |
| Keyboard/locale path bugs | Dogfood polish | Small fix (already signaled) |
| No portable UI judge | Migration without referee fails | Build CO/visual harness first |

---

## 7. What “new framework” is **not**

- Not Electron for decks.  
- Not “rewrite engine in Rust/Swift” as a prerequisite for UI.  
- Not DESIGN.md alone (tokens without modules).  
- Not Rive as the app shell.  
- Not waiting for perfect SwiftUI DAW ecosystem.

---

## 8. Immediate next steps (ordered)

1. **Owner accept/amend ADR-004** (QML-primary modular shell).  
2. **Register initiative** `initiative-ui-qml-shell` (or fold under design-md) + prefix for dossiers.  
3. **Write RULEBOOK** (one page: bindings, theme, file layout, RT bans).  
4. **Mechanical inventory script**: list every `.qml` + every skin widget type → CSV module tags.  
5. **Stress-test dossier**: DESIGN.md → Theme + one primitive row + one CO-bound control (eq or knob).  
6. **Judge spike**: scripted CO toggle + launch with `--resource-path` stays up.  
7. Only then: batch-migrate `mod-deck-shell` without full waveform Metal dependency.

---

## 9. Success metrics (migration loop)

| Metric | Gate |
|---|---|
| Default shell is QML | New installs / dogfood flag |
| Skin engine not required for dual-deck | Feature flag off |
| Theme from DESIGN.md | Lint + generate in CI |
| Waveform p99 vs MTL contract | Unchanged or better on Metal |
| Co-pilot module shippable without skin | QML Settings category |
| Agent can add a control without touching engine | Proxy + MODULE.md only |

---

## 10. References

- ADR-004 (stack decision)  
- `design-md-ui-modernization.md` (token SSoT)  
- Anthropic: [How Anthropic runs large-scale code migrations with Claude Code](https://claude.com/blog/ai-code-migration) — process, not language port  
- [code-migration-kit](https://github.com/anthropics/code-migration-kit-with-claude-code) — rulebook/map templates  
- `arch-qml-ui` / `arch-skin-widgets` — ownership  
- Strategy priority **4**: QML-primary shell + DESIGN.md
