---
id: nextgen-agent-dj-shadow-product
type: knowledge
title: "NextGen Agent DJ — shadow/ghost product thesis (module-by-module greenfield)"
status: proposal
owner: gudjon
authored_by: grok-signal
created: "2026-07-19"
lastUpdated: "2026-07-19"
enriched: "2026-07-19 — §Methods from X; Cursor-path owner framing (VS Code fork → Agent UI)"
defers_to:
  - kanban/knowledge/ui-framework-migration-map.md
  - kanban/knowledge/nextgen-dj-needs-and-leader-ui-map.md
  - kanban/knowledge/nextgen-music-management-mode.md
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
  - nextgen-dj-needs-and-leader-ui-map
  - nextgen-music-management-mode
inspired_by:
  - "Owner thesis: NextGen ghost/shadow Agent DJ; one module at a time; DESIGN.md; agent-friendly UI engine"
  - "Owner analogy: Cursor path — VS Code fork first, then promote Cursor Agent UI; Migx classic stays base, all new UI work is NextGen until full migration"
  - "X 2026: strangler/shadow, DESIGN.md, modular agents, native+WebKit, Qt6 AI shells, worktree isolation"
  - "X methods annex: shadow deployment, read-then-write strangler, deploy≠release flags, worktree isolation bottleneck, micro-agent→verifier, expand-contract"
  - "https://claude.com/blog/ai-code-migration"
---

# NextGen Agent DJ — shadow product thesis

## Owner intent (paraphrase)

Build a **NextGen / Agent DJ** surface as a **ghost or shadow** of Migx: full new development path, **one module at a time**, done right (DESIGN.md + optimized UI engine that agents — Claude Code, Grok CLI, Codex — can actually own). Classic Migx keeps shipping; NextGen grows until it can strangulate the default UX.

This is **not** “rewrite the audio engine first.” It is a **product shell + agent harness** strategy with a **stable CO/engine bus**.

### The Cursor path (owner framing — locked)

Same track Cursor took: **start from a working fork** (VS Code → Cursor; Mixxx/classic Migx → us), keep that base reliable, and **put the real product work into a new UI** that eventually becomes what you promote (Cursor Agent UI ↔ NextGen Agent DJ).

| Cursor | Migx |
|---|---|
| VS Code fork as the working IDE | Classic Migx (skins + partial QML) as the working DJ app |
| New Agent UI grows beside it | NextGen shell grows beside classic |
| New features / agent UX land in the new UI | **All new UI work lands only in NextGen** |
| Old surface kept until new is default | Classic kept until dual-deck + dogfood acceptance |
| Promote Agent UI as the product | Promote Agent DJ / NextGen as the product |

**Operating rule for the fleet:**

1. **Do not invest feature work in classic UI** beyond keep-alive (build, crash, RT, launch). No new product chrome on LateNight/legacy skins.
2. **All forward UI work is NextGen** — one module at a time, DESIGN.md, agent-owned modules, judge-gated.
3. **Migrate by strangulation**, not dual forever: each module moves capability old → new; when classic is unused, freeze/delete the twin.
4. **End state is one product** on the new UI framework — not a permanent two-app company. Classic is the VS Code-era base we graduated from, not a second roadmap.

```text
Phase 0  classic works (fork dogfood)          ← we are here / just past
Phase 1  NextGen shell + primitives + Theme    ← first agent work
Phase 2  modules strangulate feature-by-feature
Phase 3  NextGen is default launch / marketed surface
Phase 4  classic UI path frozen or removed
```

### Music management is a first-class mode

Owner refinement, 2026-07-21: Agent DJ must solve the arrangement/next-queue problem, not only repaint
the decks. The DJ needs a fast full-screen music-management mode for recognition, tags, playlist
membership, cached community signal, staging, and explicit load-to-free-deck actions while the current
set keeps playing. That mode is specified in `nextgen-music-management-mode.md` and should be included
in ADR-007 and the first module-order debate.

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

## 7. Methods — how to best do this (X + field practice)

Methods below are **how**, not **what**. They refine Option A (shadow binary) + module strangler.
Field refresh (2026-07-19 X): strangler/facade, **shadow traffic**, deploy≠release flags, expand-contract, **worktree isolation as the bottleneck**, micro-agent→verifier, orchestrator non-overlapping lanes.

### 7.1 Migration topology methods

| Method | What X/practitioners say | Apply to Agent DJ |
|---|---|---|
| **Strangler fig** | Build alongside legacy; route one function at a time; retire old only when stable; users shouldn’t feel a flip | Each `mod-*` has a route (flag or binary menu); classic remains default until dual-deck acceptance |
| **Facade first (Stage 0)** | Intercept layer *before* migration; clients keep same interface while backend swaps | **CO bus is already the facade** — NextGen and classic both talk `[Group],key`; never invent a second control plane |
| **Read path first, then writes** | Proxy reads to new service while writes stay on monolith; move writes only after reads are trusted | For shared library/FSL: NextGen **reads** first; any dual-write expands sidecar fields (expand-contract), never hot-cut writers |
| **Shadow / mirror traffic** | Parallel env gets duplicated requests; prod still answers; compare outputs; activate only when compare is green | Optional later: shadow CO observers / offline judges replaying classic sessions against NextGen UI contracts — not day-1 |
| **Decouple deploy from release** | Merge code when ready; flip flag when the feature is | Merge NextGen modules to main anytime; **release** via flag/`migx-agent` dogfood only |
| **Feature flags from day one** | Retrofitting flags later is painful; agent changes (prompts/tools/UI modules) need gradual rollout + kill-switch | `ui.nextgen.*` flags + fallback = classic skin/QML path; agents may stage flags, **humans approve enable** |
| **Rollback without redeploy** | Flip flag back; no new build required for safety | Prefer flag kill-switch over “git revert the monorepo” |
| **Expand-and-contract** | Add-only → dual-write → backfill → drop old later; blue-green **lies** if schema diverges (flip-back 500s) | Shared FSL/library: expand sidecar first; NextGen reads new fields; classic keeps working; drop never blocks classic |
| **Preserve contracts** | Gateway/BFF routes old vs new; one endpoint/module at a time | Contract = `[Group],key` + MODULE.md acceptance — UI can change, CO cannot drift |

**Anti-method:** Big-bang rewrite of LateNight; “shadow” that shares no contracts; flipping default before judge is green; dual-write without expand-contract.

### 7.2 Agent execution methods (how the team builds modules)

| Method | What X says | Apply |
|---|---|---|
| **Plan → structure → build → isolate → guardrail → evaluate** | Don’t open Claude and ask it to “build the app” | BMAD/PRD/MODULE.md first; then code |
| **Bounded coding loop inside a DAG** | Single loop OK for small tasks; full product needs parallel implement → independent review → integration gate → checkpoint → next layer | Wave per module; federation mail = gate |
| **Micro-agent loop** | Fast context fetch → **single-task** LLM → verifier checker → ship behind flag | One claim = one module task; judge is the verifier; flag is release |
| **Brainstorm → Plan → Work → Review → Compound** | Parallel agents; **compound** learnings into repo knowledge after each fix | Update rulebook/LESSONS after each module |
| **Worktree isolation = the bottleneck** | Models already write code; clobbering one cwd kills the speed gain; isolation is infrastructure not ceremony | One worktree (or `isolation: worktree`) per `mod-*` claim; never two agents on main checkout |
| **Orchestrator enforces non-overlapping lanes** | Orchestrator skill: non-overlap, status updates, then **independent** fleet review | Grok/Claude orchestrate claims; Codex review after completion — not same agent |
| **Human becomes picker of best output** | Senior role shifts to “orchestrate N agents, review branches, pick winner” | Owner + Codex pick; Claude does not self-merge |
| **Never grade own work** | Second agent assumes first is broken; agentic review + flag + test before release | Codex verify; P-08; no Claude self-seal |
| **Persist to disk not chat** | Results land on disk; context window is not memory | MODULE.md status, EVD, federation close notes |
| **Schedule / loop** | 24/7 autonomous only with discover→handoff→verify→persist | Grok Mode A for signal; implement loops for modules |
| **PRD then tasks then implement groups** | Speak/spec PRD → generate tasks → implement batch → build+test → commit → next batch | MODULE.md = PRD; tasks in dossier waves |
| **Structured I/O** | Free-form agent output is fragile | MODULE acceptance YAML machine-checkable |
| **Hooks for safety** | Pre/post tool lint, block dangerous ops | pre-commit + RT path bans in CLAUDE.md |
| **Shadow/mirror mode for agent changes** | Field joke with teeth: agent code starts behind flags / mirror, multi-week rollout not “YOLO main” | NextGen modules ship dark; dogfood cohort; then widen |

### 7.3 Concrete operating cadence (recommended)

```text
For each module M:
  1. SPEC     — MODULE.md + CO list + DESIGN tokens (human + Grok field if UX)
  2. CLAIM    — worktree + claim paths (Claude); orchestrator checks non-overlap
  3. BUILD    — implement only M (Claude); no adjacent "cleanup"
  4. JUDGE    — launch NextGen + CO script + DESIGN lint (mechanical)
  5. REVIEW   — Codex assumes broken; P1/P2/P3 (independent)
  6. COMPOUND — rulebook/LESSONS update if pattern found (any peer)
  7. FLAG     — enable M behind flag / ship in migx-agent only (deploy ≠ release)
  8. STRANGLE — when classic path unused, delete or freeze classic twin
```

**Integration gate between layers:** no `mod-deck-shell` until primitives+Theme judge green; no default flip until dual-deck + underrun contract.

**Strangler order inside a module (X read-then-write):**
1. Facade already exists (CO).
2. NextGen **renders** from CO (read).
3. NextGen **writes** CO only when single-writer rule still holds (P-06).
4. Classic twin retired only after dogfood + judge green.

### 7.4 What “done” means for a shadow module (method acceptance)

| Check | Owner |
|---|---|
| MODULE.md acceptance block green | Mechanical judge |
| DESIGN tokens only (no free `#hex`) | lint / Theme |
| No `src/engine/**` unless separate RT claim | Claims + pre-commit |
| Classic still builds and launches | CI / smoke |
| Independent review not self-review | Codex / P-08 |
| Flag documented fallback | MODULE.md |
| Deploy path ≠ release path documented | MODULE.md / flag table |

### 7.5 Methods explicitly rejected by field practice

| Reject | Why |
|---|---|
| Big-bang UI rewrite | Strangler discourse: business still needs classic |
| Self-grading agents | “Agent never grades own work” is widespread production rule |
| One mega-agent for whole product | Bounded roles; DAG; hallucination rises when one agent does everything |
| Two agents, one working directory | Worktree isolation is the bottleneck; race conditions eat the speedup |
| Ship without evals | “No looks good — pass/fail” |
| Deploy = release | Flags separate merge from user exposure |
| Dual-write schema without expand-contract | Rollback becomes a lie |
| Flip blue-green after destructive schema drop | Expand-contract first or rollback is fake |
| Agent self-enable production flags | Stage yes; enable needs approval + audit trail |

### 7.6 X sources (methods annex — durable themes, not every URL)

| Theme | Representative field signal |
|---|---|
| Strangler + facade | Route selected functionality; Stage 0 facade; low-risk gradual replace |
| Shadow deployment | Parallel env, duplicate traffic, compare, then activate (migration case study pattern) |
| Read then write | Reads via proxy first; writes later; always-on rollback to monolith |
| Expand-contract | Dual write + backfill + late drop; honest rollback vs blue-green schema lies |
| Deploy ≠ release / flags | Flags for agent logic; kill-switch; % rollout; agents stage, humans enable |
| Worktree multi-agent | Isolation is the moat; fleet/parallel agents; non-overlapping lanes + independent review |
| P-08 culture | Generator ≠ evaluator; micro-agent + verifier; flag before release |

---

## 8. Immediate next steps (if fleet agrees)

1. Owner pick Option A/B/C/D.  
2. ADR draft: `ADR-00X-nextgen-agent-dj-shadow` (or amend ADR-004).  
3. Scaffold dossier: empty NextGen target + DESIGN.md + Theme + launch.  
4. Stress-test primitives (AI migration loop, discard thrice).  
5. Judge harness v0 (method §7.4).
6. First product module: co-pilot chrome **or** single-deck play/cue (product choice).
7. Adopt cadence §7.3 as initiative operating rule.

---

## 9. Relationship to existing docs

| Doc | Role |
|---|---|
| `ui-framework-migration-map.md` | Module inventory + QML host decision + X annex |
| This file | **Product strategy**: shadow Agent DJ + strangler + agent process |
| ADR-004 | UI stack (still proposed) |
| `ai-ui-migration-loop.md` / methodology | How to port modules with agents |
| EXO / FSL | Data plane NextGen co-pilot consumes |

**Bottom line:** The “ghost NextGen Agent DJ” idea is **consistent with X strangler/shadow + modular agent OS + DESIGN.md + native QML host**. It is the right way to “do it right module-by-module” **without** abandoning the engine or waiting for a full skin rewrite. The debate for the fleet is **packaging** (separate target vs flag) and **first module priority** (primitives/Theme vs co-pilot vs single deck) — not whether Electron should own the decks.
