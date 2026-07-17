---
id: migx-playbook-patterns-breakage-navigation
type: playbook
title: "Patterns, Breakage, and Navigation"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/patterns/
  - AGENTS.md
  - kanban/AGENTS.md
---

# Patterns, Breakage, and Navigation

> Migx playbook chapter. Defers to `kanban/patterns/` (pattern SSoT), repo-root `AGENTS.md` (house physics), and `kanban/AGENTS.md` (MG-1..MG-6). Cites by anchor ID; does not restate.

## 1. Pattern doctrine

The pattern catalogue at `kanban/patterns/` is Migx's **compounding memory**. A design decision that recurs across two dossiers or PRs becomes a `P-NN`; a mistake made twice (or once, expensively) becomes an `AP-NN`. Write it once, cite it forever — the second time you'd re-explain a rule in a PR thread is the moment it should have been a numbered card instead. The catalogue is how the codebase gets *smarter per week* rather than merely larger: every sealed dossier that surfaces a `P-NEW:` candidate feeds the same corpus the next dossier reads before it starts.

**Anchor, not name.** `P-02`, `AP-01` are *immutable anchor IDs* (MG-3). Cite them in code comments, commit messages, dossier decisions, and PS `resolves:`/`risks:`/`acceptance:` edges — never by prose ("the audio-thread thing"). Prose names can't be lint-checked and drift silently; a grep for `P-02` returns a queryable ledger, a grep for "real-time safety" returns noise. Numbers are never reused; a superseded pattern is marked `status: superseded`, not deleted and not renumbered.

**Skills cite, they don't restate (`P-05`).** A `.claude/skills/pat-NN-*` skill is only the *auto-load trigger* — the thing that fires on the relevant code context and says "this surfaces `P-NN`, read the card." Its body is 2–4 lines with `metadata.cites_patterns` and a `defers_to:` link. The card in `kanban/patterns/` is the single source of *what*; the skill is the single source of *when-to-surface-it*. Two copies of a rule is two truths that drift (MG-3), so the lint `verify-skill-defers-not-restates.py` fails any `pat-*` skill whose body duplicates card prose.

**Where citations live.** Patterns are cited at two altitudes. *In code:* an annotation at the exact line where the invariant bites — e.g. a `NOTE(P-02)` on an engine `process()` fast path that must stay allocation-free — so the rule survives PR churn and the next agent reads it in place. *In dossiers:* the PS `acceptance:` block names the benchmark and threshold a `P-03` contract demands; the `91-LOOP-CLOSURE` retro cites the `P-NN`/`AP-NN` the bet exercised or the breakage it hit. A perf PR that cites no pattern has not consulted the catalogue — that absence is itself a review signal.

**The Migx pattern themes.** Rather than a service/edge cluster taxonomy, the catalogue organizes around five load-bearing surfaces of *this* codebase:

- **Real-time safety** — the RT audio callback allocates nothing, locks nothing, blocks nothing (`P-02`, MG-6). This is house physics; the repo-root `AGENTS.md` is its substance SSoT.
- **Benchmark contracts** — a performance claim ships with a repeatable benchmark, a pinned baseline, and a numeric threshold measured as a *delta on the same machine* (`P-03`). The north-star (Apple Silicon speed) is entirely perf work, so this is the most-exercised theme.
- **Closed loops** — every load-bearing change names its four beats (Trigger · Capture · Intelligence · Adjustment) and the automatic re-check (`P-01`, MG-1). If you can't name what re-closes the loop, the work is a wish.
- **Qt ownership** — `parented_ptr`/`make_parented` object-tree lifetime, ControlObject/ControlProxy `[Group], key` for inter-component talk. Ownership bugs are ordinary C++/Qt hazards raised to house-physics severity because they surface as crashes under load.
- **GPU/CPU boundary** — Metal offload and unified-memory data paths must respect the RT deadline; the audio thread never waits on the GPU (see `AP-02`).

These themes are the *map*. The cards are the territory: consult `kanban/patterns/` for the specific entry, and when a structural decision has no governing pattern, surface a `P-NEW:` candidate at loop-closure rather than inventing a number (that's an MG-3 violation).

## 2. Breakage catalogue

The named ways teams break the harness. Each entry: what it looks like, what catches it, how to recover. Every one has a Migx shape.

**Rehearsing on an unstable base.** *Looks like:* benchmarking an optimization against a moving `main` that shifted under you — other commits landed between baseline and measurement, so the delta is noise attributed to your change. *Catches it:* `P-03` rule 4 — always measure the delta against a *pinned commit* on the same M4 config, never against a churning branch. *Recovery:* re-pin the baseline commit, re-run both arms on the same machine, discard the contaminated `EVD-*` record.

**Open loop.** *Looks like:* a change produces output nobody re-checks — a "smoother now" waveform rewrite with no benchmark, a script whose result no sensor validates. It looks done; it silently rots (MG-1, MG-2). *Catches it:* the `P-01` review question — "what re-closes this loop?" No answer ⇒ open loop ⇒ not done. *Recovery:* attach the missing beat (a benchmark run, a capture at a stable path, a declared threshold) before the seal; do not seal around the gap.

**Ledger creep.** *Looks like:* annotation tags and rules accumulate from single prompts and never get removed — bodyless `TODO`s, "for now" notes in `AGENTS.md`, a stale `NOTE(invariant)` whose context merged months ago. The harness reads every line as authoritative, including the dead ones. *Catches it:* `verify-before-trusting-any-rule` — grep the codebase to confirm the rule is still obeyed; the size cap forces the file to stay readable. *Recovery:* verify the rule is live (if unobeyed, delete without ceremony); trace its origin in `git log`; promote a still-load-bearing rule to a numbered pattern, delete the rest.

**Dead-dossier routing.** *Looks like:* a plan or PR cites a *sealed* dossier as if it were current truth. A sealed dossier is a dated snapshot of THEN (MG-5) — current truth lives in the code, the `architecture/` map, and the pattern catalogue. Routing a fix off a stale snapshot redoes shipped work or chases a decision that's been superseded. *Catches it:* the pre-work check — before acting on a dossier claim, confirm it against live code with file:line evidence, distinguishing "not implemented" from "implemented but not wired." *Recovery:* re-derive the current state from source, re-route the work to the pattern/ADR that now owns the decision.

**Green-over-red seal (`AP-01`).** *Looks like:* `sealed: true` with a "met" verdict while acceptance is actually unmet, unmeasured, or the retro is boilerplate. This poisons the closure corpus that `mine-dossier-retrospectives` learns from — future dossiers inherit a false lesson and the open work silently disappears. *Catches it:* `91-LOOP-CLOSURE` honest-gate checklist; a "met" criterion with no cited benchmark; lint `verify-sealed-dossier-has-closure.py`. *Recovery:* if the bet didn't land, **halt honestly** — `sealed: true` with a `halted` verdict, a named successor dossier, an owner, and the re-fire condition. An honest halt is a respectable closure; a false green is not.

**Audio-thread regression disguised as a speedup (`AP-02`).** *Looks like:* an optimization improves an average or throughput number but slips a heap allocation or lock onto the RT callback, a data race onto a `ControlObject`, or shares a GPU buffer with the audio path without respecting the boundary. Average is 5% better; worst case now drops out. DJ software is judged on **worst-case glitch-free playback**, so this is a correctness bug, not a perf win. *Catches it:* the `P-03` contract must assert the invariant — zero RT-thread allocations, **p99 not mean** frame/buffer time, no new locks on the callback; review flags any `new`/`std::vector`/`QMutex` in a `process*()`; Phase-3 tooling adds an allocation-counting allocator and thread-sanitizer on the engine tests. *Recovery:* move state and scratch setup to construction (once), keep the fast path lock-free, re-measure the tail; if the tail regressed, the optimization is reverted regardless of the mean.

**Metal/GPU offload that stalls the audio deadline.** *Looks like:* waveform or DSP work is pushed to Metal for throughput, but the audio thread ends up waiting on GPU completion — a `waitUntilCompleted`, a synchronous readback, or a shared unified-memory buffer the RT path reads while the GPU writes. On the M4 SoC the shared address space makes this *tempting and invisible*: no copy, so it looks free, until GPU latency gates a buffer period and you underrun. *Catches it:* `P-02` + `AP-02` — the audio thread never blocks on another engine; the benchmark asserts the RT deadline holds under GPU load, not just at idle. *Recovery:* decouple with a lock-free handoff (GPU produces into a triple-buffered slot; the RT thread reads the last-completed slot, never waits); never let the GPU sit on the critical path of the callback.

## 3. Codebase navigation for a large C++/Qt project

Migx is ~335k LOC of C++/Qt6. At that scale, name collision is real and full-file reads are wasteful. The discipline is **symbol, not string**.

**Symbol-not-string with clangd.** Names repeat across `src/engine/`, `src/effects/`, `src/library/`, and the test tree — `EngineBuffer` helpers, `process()` overrides, or a `WaveformRenderer` variant appear in a dozen places. Pattern-matching by string lands you on the wrong copy. Use clangd's semantic operations instead: **go-to-definition** to disambiguate which `process()` you're editing, **find-references** (not `grep -r 'functionName'`) to enumerate every caller before a refactor, **hover** for a type, **rename-symbol** for an atomic cross-workspace rename. Reserve full-file `Read` for the file you're actually changing; navigate the other 334k lines by definition/references and read only the relevant span.

**compile_commands.json is the prerequisite.** clangd needs the compilation database to resolve includes and templates. Migx builds with CMake, so generate it by configuring with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` and point clangd at the resulting `build/compile_commands.json` from the repo root. Without it, clangd falls back to guessed flags and silently mis-resolves half the tree — the navigation is only as good as the database. A `.clangd` file at the root pins any per-target flag overrides.

**Qt MOC.** Qt's `AUTOMOC` is on for the Migx targets, so `Q_OBJECT` classes generate `moc_*.cpp` at build time. clangd indexes those generated files once the build has run — which is why signals/slots, `Q_PROPERTY` accessors, and QML-exposed types resolve correctly only *after* a configure+build has populated the database. If find-references on a slot comes back empty, the moc output isn't indexed yet: build, then re-index.

**ControlObject lookups are the one place string search wins.** ControlObject/ControlProxy wiring is addressed by *runtime* keys — `[Group], key_name` string literals, not C++ symbols. clangd can't follow `[Channel1],play` from producer to consumer because the link is a string, not a call. So for "who reads/writes this control?", `grep` the `[Group]`/`key` literal across `src/` and `res/` (skins, QML, and controller JS/XML all reference controls by the same string keys). This is the deliberate exception to symbol-first: control topics are a string-keyed bus, and the string *is* the identifier.

**How subagents should explore.** For "where does X live / how is Y wired," dispatch the **Explore** agent with an explicit breadth ("medium" vs "very thorough, multiple naming conventions") — it reads excerpts and returns the conclusion (file:line), not a file dump, so the primary context stays clean. Explore locates code; it does not audit it. Grep for *symbols* (class/function names) when clangd isn't available in the subagent, and grep for *control keys* when tracing the ControlObject bus. clangd/LSP is a developer-and-agent productivity layer, not a runtime dependency and not a substitute for the lint suite (pre-commit stays the fast quality gate). Migx's scale is squarely in LSP+grep territory — no vector search.
