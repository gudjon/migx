---
id: nextgen-agent-dj-shadow-product
type: knowledge
title: "NextGen Agent DJ — shadow/ghost product thesis (module-by-module greenfield)"
status: proposal
owner: gudjon
authored_by: grok-signal
created: "2026-07-19"
lastUpdated: "2026-07-19"
defers_to:
  - kanban/knowledge/ui-framework-migration-map.md
  - kanban/architecture/decisions/ADR-004-ui-stack-qml-vs-rive-vs-react.md
  - kanban/knowledge/design-md-ui-modernization.md
  - kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md
  - kanban/Strategy-Current.md
  - kanban/AGENTS.md
related:
  - initiative-ui-modernization
  - initiative-ai-djing-product
  - arch-control-messaging
  - arch-engine-realtime
inspired_by:
  - "Owner thesis: NextGen ghost/shadow Agent DJ; one module at a time; DESIGN.md; agent-friendly UI engine"
  - "X 2026: strangler/shadow, DESIGN.md, modular agents, native+WebKit, Qt6 AI shells, worktree isolation"
  - "https://claude.com/blog/ai-code-migration"
---

# NextGen Agent DJ — shadow product thesis

## Owner intent (paraphrase)

Build a **NextGen / Agent DJ** surface as a **ghost or shadow** of Migx: full new development path, **one module at a time**, done right (DESIGN.md + optimized UI engine that agents — Claude Code, Grok CLI, Codex — can actually own). Classic Migx keeps shipping; NextGen grows until it can strangulate the default UX.

This is **not** “rewrite the audio engine first.” It is a **product shell + agent harness** strategy with a **stable CO/engine bus**.

---

## 1. What “ghost/shadow” means (architecture)

| Pattern (industry / X) | Meaning | Migx fit |
|---|---|---|
| **Strangler fig** | Route selected functionality to a new path; retire old module only when stable | Default launch stays skins/QML classic; NextGen modules opt-in |
| **Shadow / canary** | New path runs in parallel; traffic/feature flags grow | Feature flag `ui.nextgen` / separate binary target |
| **Blue-green** | Two full systems; flip traffic | Too heavy for v1; use module flags instead |
| **Second app binary** | `migx` vs `migx-agent` (or `AgentDJ.app`) | Clean agent tree; shared libraries/engine |

**Recommended shape (fleet discussion default):**

```text
┌─────────────────────────────────────────────────────────────┐
│  migx (classic)          │  migx-agent / NextGen (shadow)   │
│  skins + partial QML     │  DESIGN.md modules only          │
│  production dogfood      │  agent-first, incomplete OK      │
└────────────┬─────────────┴────────────────┬─────────────────┘
             │                              │
             └──────────┬───────────────────┘
                        │ same process or shared dylibs
              ┌─────────▼──────────┐
              │ Control bus P-06   │  [Group],key — single writer
              │ Engine RT P-02     │  no UI on callback
              │ Library / FSL / EXO│  shared data plane
              └────────────────────┘
```

**Hard rule:** NextGen **must not fork the engine**. It binds through `ControlObject` / proxies (and EXO files). If a module needs engine changes, that is a **separate** engine dossier with RT review — not a free ride inside UI greenfield.

---

## 2. X deep dive — building blocks by domain

Each domain: *what X says → implication for Agent DJ shadow → risk if ignored*.

### Domain A — Migration strategy (strangler / shadow)

| Field signal | Implication |
|---|---|
| Don’t rewrite monolith overnight; **route selected functionality** then retire (strangler) | NextGen ships **modules**, not a day-1 full dual-deck parity claim |
| Preserve contracts; extract one endpoint/module at a time; rollback | Each `mod-*` has CO contract + flag + rollback to classic skin/QML |
| Shadow/canary auto-scale new path | Flag + dogfood cohort before default |

**Fleet ask:** Accept strangler **not** big-bang replace of LateNight on day one.

### Domain B — Agent operating system (how we build)

| Field signal | Implication |
|---|---|
| Claude Code = multi-layer OS: CLAUDE.md constitution, skills, hooks, subagents, worktrees | NextGen repo/tree needs **constitution + MODULE.md + DESIGN.md**, not vibes |
| Parallel agents → **worktree isolation**, CI feedback, PR per unit | One module claim/worktree; Theme is shared with short TTL claim |
| Multi-agent roles Architect / Engineer / Reviewer / Optimizer | Claude implement · Codex judge · Grok field/signal (existing federation) |
| “Documentation is law / no hallucinated design” | DESIGN.md + MODULE.md mandatory before UI code |
| Modular frameworks so you can swap industry standard in 30 days | CO contract stable; UI host can evolve (QML→Metal host) without rewriting engine |

**Fleet ask:** NextGen is as much a **harness product** as a skin product.

### Domain C — UI stack choice (performance vs DX)

| Field signal | Implication |
|---|---|
| Electron: great DX / one codebase; “slop” when foreign toolkit; fine for chat IDEs | **Disqualified for Surface A** (decks/waveforms); optional Surface B island |
| Native anti-Electron + SwiftUI tools | AS-only could theoretically be SwiftUI shell — **second system** unless CO bridge is productized |
| Qt/QML “awesome”; C++/Qt6 native AI shells (Fincept-class) | **Primary host for NextGen v1** (ADR-004 + already paid path) |
| Widgets → WebEngine → **back to QML** for speed | Don’t trap NextGen in web shell forever |
| GPU-first creators leave all toolkits for Metal when graphics *are* the product | Waveforms stay **metal-close under QML host** (MTL), not DOM |

**Fleet ask:** NextGen v1 host = **Qt Quick 6 + DESIGN.md + CO proxies**. Revisit SwiftUI only if QML+Metal fails p99 contracts after honest effort.

### Domain D — Design system (DESIGN.md)

| Field signal | Implication |
|---|---|
| DESIGN.md = “Figma for agents”; AGENTS.md logic / DESIGN.md UI | First NextGen commit includes `res/design/DESIGN.md` + Theme generate |
| Lint tokens / WCAG / no inventing colors mid-session | `just lint-frontend` / pre-commit gate on DESIGN.md |
| Component libraries built with tokens + variants + docs for agents | Each module lists tokens + states in MODULE.md |

**Fleet ask:** Design system is **blocking infrastructure**, not polish after decks.

### Domain E — Modular product architecture

| Field signal | Implication |
|---|---|
| Build modular; continuous evals; reversible migrations | Each module: acceptance = CO parity + launch smoke + optional screenshot |
| Production UI components: loading, a11y, edge cases, role split | MODULE.md acceptance includes a11y/keyboard (club dark-room later) |
| One module ownership, no dual-write | Claims on shared Theme/primitives |

**Fleet ask:** Module order from `ui-framework-migration-map` stands; NextGen only **implements** that order in a clean tree.

### Domain F — DJ / audio product constraints (Migx house + field)

| Signal | Implication |
|---|---|
| Reliability / dual-USB / prep (prior ethnography) | NextGen still ships offline trust; co-pilot prep-first |
| Live AI Ack unproven | Co-pilot module: Explain + Ack/Dismiss; no Automix default |
| RT house physics P-02/P-20 | NextGen never puts agents or JS on audio callback |
| macOS 26+ AS only (ADR-006) | NextGen can assume M4/Metal floor; drop Linux UI concerns |

### Domain G — AI co-pilot as product surface

| Field signal | Implication |
|---|---|
| AI lives **inside** native shells (Qt6 terminals with agents) | Co-pilot is a **first-class NextGen module**, not a web app that embeds decks |
| EXO ontology + FSL cues/energy already advancing | NextGen co-pilot consumes **real sidecars**, not fixtures only |

---

## 3. Proposed NextGen package (concrete)

### 3.1 Identity

| | Classic Migx | NextGen Agent DJ (shadow) |
|---|---|---|
| Binary / target | `mixxx` / current app | `migx-agent` or cmake target `AgentDJ` |
| Default UI | Skin XML + hybrid QML | **QML-only modules** + DESIGN.md Theme |
| Completeness | Full DJ feature set | Incomplete by design; modules land with green acceptance |
| Audience | Production dogfood | Internal / early agents / founder |
| Goal | Stable gigs | Fast closed loops for AI-DJ product |

### 3.2 Shared forever

- Engine / SoundIO / analyzers (worker)  
- Control bus `[Group],key`  
- Library DB + FSL sidecars  
- EXO tools / ontology files  
- Controller CO path (`P-30`)  

### 3.3 NextGen-owned greenfield

| Layer | Stack | Agent ergonomics |
|---|---|---|
| Tokens | `res/design/DESIGN.md` → `Theme.qml` | Lint + generate; no free colors |
| Primitives | `mod-primitives` | Small files, pure QML + tokens |
| Features | `mod-deck-shell`, `mod-mixer`, … | MODULE.md + CO contract |
| Co-pilot | `mod-copilot` | JSON fixtures → live intents |
| Waveform host | QML item → Metal rendergraph | Separate MTL waves |
| Agent docs | `NextGen/AGENTS.md`, rulebook, MODULE templates | Claude/Codex/Grok all load same |

### 3.4 Module build order (unchanged, now for shadow app)

```text
0. Scaffold: cmake target + empty main.qml + DESIGN.md + Theme + launch smoke
1. mod-primitives (+ Theme stress-test — discard thrice per AI-migration practice)
2. mod-eq / mod-vu / mod-tempo   (CO-bound, no waveform)
3. mod-deck-shell + mod-hotcue  (play/cue without full GPU waveform)
4. mod-mixer + mod-fx
5. mod-library (tables)
6. mod-copilot (Layer B)
7. mod-waveform-* after Metal unpin
8. Feature-flag default: classic → NextGen when dual-deck acceptance met
```

### 3.5 How agents work a module

```text
Trigger: MODULE.md acceptance open
  → Claim paths (worktree)
  → Read DESIGN.md + UI rulebook + CO list
  → Implement primitive/feature only
  → Judge: just build + CO script + launch NextGen
  → Codex adversarial review (P-08)
  → Merge; release claim
```

---

## 4. Risks (honest)

| Risk | Mitigation |
|---|---|
| **Second system syndrome** (rewrite everything “right”) | Hard incomplete OK; no full LateNight parity gate for v0 |
| Dual binary maintenance cost | Share engine/libs; only UI tree diverges |
| Agent still edits classic by accident | Path claims + NextGen/ AGENTS.md “do not touch res/skins” |
| QML not “agent popular” like React | Offset with DESIGN.md + small modules + strong MODULE.md; talent is agents |
| Shadow never becomes default | Explicit milestone: dual-deck + zero underrun + co-pilot dogfood → flag flip |
| Engine entanglement | Any `src/engine/**` change requires RT review; UI modules cannot smuggle |

---

## 5. Decision options for the fleet (discuss)

| Option | Description | Recommend? |
|---|---|---|
| **A. Shadow cmake target** `migx-agent` in same repo | Cleanest agent tree; shared engine | **Yes — default** |
| **B. Feature flag only** in existing QML | Less isolation; agents fight dual stack | No for “NextGen full new” |
| **C. Separate repo** | Max isolation; federation harder | Only if monorepo politics explode |
| **D. SwiftUI NextGen** | Max AS native / agent web tutorials | **No for v1** — CO bridge rewrite tax |

---

## 6. Federation discussion prompts

### For Claude (implementer)
1. Is a separate cmake target `AgentDJ` / `migx-agent` feasible without forking engine? Sketch linkage to existing libs.  
2. Where does DESIGN.md generator live (`tools/design/`)?  
3. Confirm MODULE.md template + first stress module (`mod-primitives` or Theme).  
4. Non-modal error UX (your principle) as NextGen default — how encoded in rulebook?

### For Codex (verifier)
1. What is the **minimum judge** for shadow app (launch + one CO round-trip)?  
2. How to prevent dual-write claims across classic vs NextGen?  
3. Acceptance for “module done” that is machine-checkable (P-08).

### For Grok (signal — this doc)
1. Keep X refresh per domain when NextGen stack choice reopens.  
2. Do not scout Electron as Surface A.

### For owner (Gudjon)
1. Accept **Option A** shadow binary vs flag-only.  
2. Accept **incomplete NextGen** publicly (internal dogfood).  
3. Name: **Agent DJ** product line vs Migx codename only.

---

## 7. Immediate next steps (if fleet agrees)

1. Owner pick Option A/B/C/D.  
2. ADR draft: `ADR-00X-nextgen-agent-dj-shadow` (or amend ADR-004).  
3. Scaffold dossier: empty NextGen target + DESIGN.md + Theme + launch.  
4. Stress-test primitives (AI migration loop, discard thrice).  
5. Judge harness v0.  
6. First product module: co-pilot chrome **or** single-deck play/cue (product choice).

---

## 8. Relationship to existing docs

| Doc | Role |
|---|---|
| `ui-framework-migration-map.md` | Module inventory + QML host decision + X annex |
| This file | **Product strategy**: shadow Agent DJ + strangler + agent process |
| ADR-004 | UI stack (still proposed) |
| `ai-ui-migration-loop.md` / methodology | How to port modules with agents |
| EXO / FSL | Data plane NextGen co-pilot consumes |

**Bottom line:** The “ghost NextGen Agent DJ” idea is **consistent with X strangler/shadow + modular agent OS + DESIGN.md + native QML host**. It is the right way to “do it right module-by-module” **without** abandoning the engine or waiting for a full skin rewrite. The debate for the fleet is **packaging** (separate target vs flag) and **first module priority** (primitives/Theme vs co-pilot vs single deck) — not whether Electron should own the decks.
