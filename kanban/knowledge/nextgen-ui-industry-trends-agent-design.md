---
id: nextgen-ui-industry-trends-agent-design
type: knowledge
title: "Industry UI trends for agent-built apps — DESIGN.md, shadcn, Claude Design, native hosts"
status: active
owner: gudjon
authored_by: grok-signal
created: "2026-07-19"
lastUpdated: "2026-07-19"
defers_to:
  - kanban/knowledge/design-md-ui-modernization.md
  - kanban/knowledge/nextgen-ui-engine-scout.md
  - kanban/federation/signal/2026-07-19-nextgen-ui-engine-scout.md
  - kanban/knowledge/nextgen-agent-dj-shadow-product.md
  - kanban/knowledge/ui-framework-migration-map.md
related:
  - ADR-004
  - ADR-007
sources:
  - "Anthropic Claude Design (Labs, Apr 2026+) — design system from codebase, Code handoff"
  - "Anthropic frontend-design skill — anti-slop aesthetic direction before code"
  - "Google Stitch DESIGN.md / awesome-design-md field"
  - "shadcn/ui + Tailwind agent component culture 2025–26"
  - "Prior Migx engine scorecard (QML 17 / Slint 15 / web 14 / SwiftUI 12–13)"
---

# Industry UI trends that fit NextGen (and what does not)

## 1. The real industry split (2026)

There are **two different conversations** people collapse into one:

| Conversation | What the market optimizes for | Typical stack |
|---|---|---|
| **A. Agent-native product UI** | Agents edit, lint, and ship UI fast; design system is code | DESIGN.md + React/Vue + Tailwind + **shadcn** + Claude Design / v0 / Stitch |
| **B. Real-time native performance UI** | 60–120fps custom GPU surfaces, C++ engines, controllers | Qt/QML, native Metal/SwiftUI, custom RHI, occasional Slint |

**Migx is both.** Dual-deck waveforms + RT engine = conversation **B**. Co-pilot chrome, library tables, settings, marketing, docs = conversation **A**.

**Cursor-path lesson:** Cursor did not rebuild VS Code’s text buffer in React to get Agent UI — they put a **new product surface** on a **working native base**. Same here: do not pick the web stack for Surface A just because agents are best at it.

---

## 2. Trend: DESIGN.md + component libraries (shadcn-class)

### What the field is doing

| Pattern | Why agents love it | Caveat for Migx |
|---|---|---|
| **DESIGN.md / token markdown as law** | AGENTS.md controls logic; DESIGN.md controls UI; lintable, greppable | **Adopt fully** as SSoT (`design-md-ui-modernization.md`) |
| **shadcn/ui + Tailwind** | Copy-paste components into *your* repo; agents know the API cold; no heavy runtime DS | Targets **React/web**. Not QML. |
| **awesome-design-md packs** | Drop Stripe/Linear/Vercel-like systems into agent context | Great for **aesthetic reference** + Surface B |
| **Anti-slop skills** (Anthropic `frontend-design`) | Force aesthetic direction *before* code; ban Inter + purple gradient | Port the *discipline* to QML MODULE rules |
| **Atomic design system first** | Claude Design power users: define tokens/components, then micro-edit — not one giant page prompt | Matches our module cadence |

### Preference ranking *in the agent industry* (not Migx physics)

1. **Web: DESIGN.md + shadcn/Tailwind** — default for almost every agent-built SaaS/UI
2. **SwiftUI + Apple agent skills** — rising hard on Apple platforms (Xcode exportable skills)
3. **Slint** — niche, agent-readable DSL, MCP-in-toolkit interest; not mainstream agent training data
4. **QML** — industrial/pro-audio quiet strength; **weaker public agent lore**, strong *our* codebase lore

So: **industry preference ≠ Migx Surface A preference.** Industry prefers web; we prefer **QML host + industry agent *process***.

---

## 3. Claude Design — what it is and how it helps us

**Claude Design** (Anthropic Labs, 2026): conversational visual tool that:

1. **Reads a codebase / design files / brand** and extracts a **design system**
2. Generates **live HTML prototypes** (not just static images)
3. Stays on-brand on subsequent work
4. **Hands off to Claude Code** for implementation
5. June 2026+: import design systems from repos, WYSIWYG canvas, better token use

**Companion:** official **frontend-design** skill for Claude Code — pick aesthetic direction first, then build (kills purple-slop).

### How Claude Design fits the Migx Cursor path

```text
┌─────────────────────────────────────────────────────────────┐
│  Claude Design (prototype + design system discovery)        │
│  - dual-deck layout studies                                 │
│  - co-pilot panel aesthetics                                │
│  - token/palette exploration                                │
│  - export DESIGN.md-shaped rules + HTML reference           │
└───────────────────────────┬─────────────────────────────────┘
                            │ handoff
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  DESIGN.md (repo SSoT)  →  Theme.qml generator              │
│  + MODULE.md acceptance                                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          ▼                                   ▼
┌──────────────────────┐            ┌──────────────────────┐
│ Surface A — QML      │            │ Surface B — optional │
│ decks / waveforms    │            │ WebView island       │
│ Claude Code + Theme  │            │ shadcn / React ok    │
│ Metal-close render   │            │ library / co-pilot   │
└──────────────────────┘            └──────────────────────┘
```

| Claude Design strength | Use for Migx | Do **not** use for |
|---|---|---|
| Visual layout exploration | Dual-deck IA, library density, co-pilot chrome | Deciding RT waveform host |
| Design system extraction | Bootstrap `res/design/DESIGN.md` from moodboards / mock HTML | Replacing CO contracts |
| Handoff to Claude Code | Generate MODULE.md + first QML from agreed tokens | “Ship HTML as the DJ app” |
| On-brand consistency | Keep Agent DJ aesthetic across modules | Mid-set modal patterns |
| Micro-edits on a system | Token tweaks after system exists | Open-ended “make it pretty” loops |

**Practical workflow (recommended):**

1. **Claude Design:** “DJ performance UI, dual deck, dark booth, Serato-clean, no purple AI slop; explore 2 layouts.”
2. Lock **tokens + component inventory** into `DESIGN.md`.
3. Generator → `Theme.qml`.
4. **Claude Code** implements `mod-*` in QML only (Surface A).
5. Optional: same DESIGN.md → Tailwind export for Surface B shadcn co-pilot later.
6. Judge: launch + CO + DESIGN lint (no free `#hex`).

---

## 4. Host engines revisited under the agent-design trend

| Host | Industry agent momentum 2026 | Fit for **Surface A** (decks) | Fit for **Surface B** (library/AI) | Verdict for us |
|---|---|---|---|---|
| **QML design system** | Medium (less Twitter; strong in-repo) | **Best** (bind + Metal/RHI) | Good | **Default** |
| **DESIGN.md + shadcn (web)** | **Highest** | Poor (120fps waveform) | **Best** | Island only |
| **Slint** | Low–med (clean DSL, MCP) | Challenger bake-off | Possible | Optional evidence |
| **SwiftUI** | High on Apple (skills) | Weak (C++ bridge tax) | OK pure-Apple apps | No for shell |
| **Qt Widgets / skins** | Low for agents | Legacy keep-alive | No | Classic only |
| **ImGui / immediate** | Tooling agents only | Prototype tools | No product DS | Reject product UI |

**Preference that fits us:**

1. **Process:** industry-best → DESIGN.md + Claude Design + anti-slop skill + module judges
2. **Surface A host:** QML design system (not shadcn)
3. **Surface B host (optional later):** shadcn/React WebView **consuming the same DESIGN.md tokens**
4. **Challenger:** Slint only if bake-off budgeted
5. **Not default:** SwiftUI shell, full Electron/Tauri dual-deck

This is the only way to get **both** agent industry leverage **and** DJ RT physics.

---

## 5. “shadcn strategy” without becoming a web app

Steal the **method**, reimplement the **catalog** in QML:

| shadcn idea | QML equivalent |
|---|---|
| Copy component into repo (you own source) | `mod-primitives/` Button, Slider, Knob, Meter — owned QML |
| Variants via class/props | `variant:` enums + Theme tokens |
| Compose, don’t fork framework | No second control plane; compose on CO |
| CLI add component | Scaffold script / MODULE template |
| Tokens in CSS vars | DESIGN.md → Theme.qml |
| Storybook / visual check | Screenshot judge + dogfood binary |

Name it mentally **“shadcn for QML”** = small owned primitive set + DESIGN.md, not “install shadcn in Migx.”

---

## 6. Decision table (owner-facing)

| Question | Industry default | Migx NextGen answer |
|---|---|---|
| Where do agents design best? | Web + DESIGN.md + Claude Design | Same tools for **design**; different host for **decks** |
| Should we pick shadcn for the whole app? | Often yes for SaaS | **No** for dual-deck; **maybe** for co-pilot island |
| QML vs Slint vs SwiftUI? | Mixed / niche | **QML** default; Slint optional; SwiftUI no |
| How does Claude Design help? | Prototype + DS + Code handoff | Bootstrap aesthetic + DESIGN.md; never replace engine |
| First concrete step? | Install frontend-design skill | DESIGN.md + Theme + Claude Design dual-deck study → `mod-shell` |

---

## 7. Immediate recipe (fits Cursor path + DJ needs map)

1. Run **Claude Design** on dual-deck + library IA (Serato-clean, dark booth).
2. Freeze tokens → `res/design/DESIGN.md`.
3. Generate `Theme.qml`; lint no free colors.
4. Claude Code: `mod-shell` + `mod-library` + `mod-deck-a` in QML.
5. Keep classic Migx dogfoodable.
6. Defer shadcn WebView until co-pilot needs rich agent chat UI — still same tokens.

**Bottom line:** Industry is winning with **DESIGN.md + shadcn + Claude Design** for agent UX velocity. We adopt that **operating system** fully, but host **performance decks in QML**. That is preference *for us*: not “pick web because agents like it,” but “use agent design tools to drive a native design-system shell the way Cursor layered Agent UI on a working editor.”
