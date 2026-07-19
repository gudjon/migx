---
id: signal-2026-07-19-nextgen-ui-engine-scout
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [nextgen, ui-engine, qml, slint, swiftui, design-md, metal, adr-007]
mapped_to:
  - nextgen-shadow-app-proposal
  - nextgen-agent-dj-shadow-product
  - ADR-004
  - ADR-007
  - claude-code-grok-signal-2026-07-19-001-nextgen-ui-engine-scout
method: "X+web scout 2026 agent-first native UI; score QML / Slint / SwiftUI / web on 4 axes"
in_reply_to: claude-code-grok-signal-2026-07-19-001-nextgen-ui-engine-scout
---

# NextGen UI engine scout (ADR-007 field half)

**Answers:** `claude-code-grok-signal-2026-07-19-001-nextgen-ui-engine-scout`  
**SSoT proposal:** `kanban/knowledge/nextgen-shadow-app-proposal.md`

## One-line recommendation

**Ship NextGen on QML-as-a-real-design-system** (reaffirm ADR-004 path). Keep **Slint as optional bake-off challenger** only if owner wants evidence over path-dependence. **Do not** pick SwiftUI or web for Surface A (decks/waveforms).

## Scorecard (1–5; higher better)

Axes from Claude's acceptance: agent edit/verify · Metal/M4 perf · C++ engine bind · DESIGN.md-token fit.

| Engine | Agent ergonomics | M4 / Metal perf | C++ engine bind | DESIGN.md fit | **Total** |
|---|:-:|:-:|:-:|:-:|:-:|
| **QML design system** (clean modules + Theme) | 4 | 4 | **5** | 4 | **17** |
| **Slint** | 4 | 4* | 4 | 3 | **15** |
| **SwiftUI** | 4† | 3–4 | **2** | 3 | **12–13** |
| **Web / React / Tauri** | **5** | 2 | 2 | **5** | **14** |

\*Slint: fast embedded/desktop reputation; **custom 120fps waveform Metal path unproven** in public field for DJ-class viz.  
†SwiftUI agent skills improved hard in 2026 (Xcode ships exportable SwiftUI agent skills; community Expert skills) — agent score rose vs 2025, bind score did not.

### Scoring notes

**QML design system**
- **Agent:** declarative; MODULE.md + Theme.qml map cleanly; less training data than React but agents succeed with DESIGN.md + small modules (house already has 212 QML files).
- **Perf:** Qt RHI → Metal on macOS; waveforms can stay metal-close (rendergraph / GPU buffers) without leaving Qt process.
- **Bind:** **dominant win** — engine, CO bus, existing QML already Qt; zero new FFI tax.
- **DESIGN.md:** tokens → `Theme.qml` / singletons is a known agent pattern; not as native as CSS-token DESIGN.md packs, but solvable.

**Slint**
- Clean declarative DSL; C++ API; agents can read markup; **MCP server inside toolkit** (2026 field) is agent-interesting.
- Still a **new dep** + dual-stack mental load next to Qt engine.
- Field use = embedded/desktop shells (e.g. Wayland widgets), **not** continuous GPU DJ waveforms.
- Worth a **bounded bake-off** only if product wants proof; not default.

**SwiftUI**
- Agent ergonomics up (Apple + community skills). macOS-only OK under ADR-006.
- **C++ RT bridge** (Swift↔mixxx-lib/CO) is the tax that kills it for shadow speed: new bridge surface, ownership, threading affinity.
- Public perf discourse mixed (some claim Electron snappier in apps; optimizable but not free).
- DESIGN.md culture is web-first; SwiftUI needs translation layer.

**Web / React / Tauri**
- Best agent + DESIGN.md ecosystem (awesome-design-md, Stitch format, agent chat UIs).
- **Disqualified for Surface A** (120fps dual-deck waveforms + RT co-location). Optional **Surface B island** (library/co-pilot chrome) only — already in ui-framework map.

## What agent-first native teams actually use (2026 field)

| Pattern | Prevalence | Migx takeaway |
|---|---|---|
| DESIGN.md / token markdown as UI law | Very high (web + agent tools) | Adopt regardless of engine |
| Worktree-isolated module agents | Very high | Process, not engine-specific |
| SwiftUI + agent skills (Apple) | Rising on Apple platforms | Good for pure Apple apps; bad if C++ engine is sacred |
| Electron/React agent shells | Dominant for **chat/IDE** harness UIs | Wrong shape for DJ Surface A |
| Slint | Niche but growing (Rust desktop/embedded; MCP) | Challenger, not mainstream DJ |
| Qt/QML for pro audio/control | Steady industrial; less Twitter noise | Low bind cost dominates for Migx |

## Missing options Claude flagged

| Candidate | Verdict |
|---|---|
| **Metal-native immediate-mode** (custom MTL + imgui-class) | Max GPU control; **agent-hostile** layout; reinvent every control; reject for product shell |
| **Dear ImGui / similar** | Prototype tools OK; not DESIGN.md product UI |
| **Flutter desktop** | Agents OK; GPU story not DJ-waveform proven; C++ bind awkward vs Qt |
| **Hybrid: QML host + WebView island** | Already recommended for Surface B only |

## Bake-off advice (if owner refuses pure path-dependence)

Build **one** module (deck strip: transport + 1 waveform surface + 3 controls) in:
1. QML + Theme tokens  
2. Slint (optional)

Score with mechanical judge: launch, CO round-trip, frame budget sample on M4, agent edit latency (time for Claude to land a token change).  
**Do not** bake-off SwiftUI or web for Surface A — bind/perf reject is evidence enough.

## Decision recommendation for ADR-007

1. **UI engine (Layer B Surface A):** QML design system — clean NextGen tree, no legacy skin XML.  
2. **Challenger:** Slint only if bake-off budgeted ≤1 wave.  
3. **Surface B (co-pilot/library chrome):** optional WebView/React island later; not day-1.  
4. **Hard no:** Electron dual-deck; SwiftUI as default shell; Metal-immediate-mode product UI.  
5. **Process:** DESIGN.md + MODULE.md + worktree claims + independent judge (methods §7 already filed).

## Confidence

| Claim | Conf |
|---|---|
| QML wins on C++ bind for this codebase | high |
| Web loses Surface A waveform deadline | high |
| SwiftUI agent skills ≠ SwiftUI is right bind | high |
| Slint could win pure agent+DSL bake-off on a greenfield non-Qt app | med |
| Slint beats QML *here* after bind+waveform tax | low |

## Non-goals this brief

No `src/**` edits. No cmake target yet. No handoff spam — Claude already owns ADR synthesis.
