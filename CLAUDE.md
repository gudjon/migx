# CLAUDE.md — Migx

This file loads into every Claude Code context. Keep it high-signal and short: **state each rule once
in its home and point here — never restate.** Migx is a DJ application forked from Mixxx (C++/Qt6/CMake).

## Read first
- **House code physics** (the hard rules) → repo-root [`AGENTS.md`](AGENTS.md): the RT audio engine
  (no allocation/lock on the callback thread; emits but never receives Qt signals),
  ControlObject/ControlProxy `[Group], key` messaging, `parented_ptr`/`make_parented` ownership.
- **How we work** (operating doctrine, MG-1..MG-6) → [`kanban/AGENTS.md`](kanban/AGENTS.md).
- **The playbook** (frame, patterns, harness engineering, the daily loop) → [`kanban/playbook/`](kanban/playbook/00-README.md).
- **Onboarding / what to read by task** → [`kanban/AGENT-ONBOARDING.md`](kanban/AGENT-ONBOARDING.md).

## The two ground rules (act on these; don't wait to follow a pointer)
1. **Everything is a closed loop** — Trigger → Capture → Intelligence → Adjustment. Shipping without a
   loop attached (a benchmark that re-checks a perf claim) means it isn't done. `P-01`, `P-03`.
2. **Everything is code** — load-bearing decisions live at stable grep-able paths, or they're scratch.

## Critical operational rules
- **Never allocate, lock, or block on the real-time audio thread** (`process*()` in `src/engine/`). A
  "faster on average" change that does is a regression, not an optimization. See `P-02` / `AP-02`.
- **Performance claims need a benchmark contract** — p99/max + zero underruns vs a pinned baseline, not
  a mean. `P-03` / `P-18`.
- **The fast quality gate is `pre-commit`** (clang-format/tidy, qmllint, cmake lint) — full builds are
  heavy. Run `pre-commit run --files <changed>` before committing.
- **One writer per ControlObject.** `P-06` / `AP-03`.

## Development standards (index into .claude/rules/ — read the rule, don't rely on this line)
- Single source of truth → [`single-source-of-truth`](.claude/rules/single-source-of-truth.md)
- Real-time audio safety → [`rt-audio-safety`](.claude/rules/rt-audio-safety.md)
- Build & test workflow → [`build-and-test`](.claude/rules/build-and-test.md)
- Planning in dossiers → [`planning-harness`](.claude/rules/planning-harness.md)
- Dossier lifecycle → [`dossier-lifecycle`](.claude/rules/dossier-lifecycle.md)
- Worktree hygiene → [`worktree-hygiene`](.claude/rules/worktree-hygiene.md)
- Exercise judgment / own the PR → [`agentic-decision-authority`](.claude/rules/agentic-decision-authority.md)

## Where things live
- Patterns / antipatterns (cite by ID) → `kanban/patterns/`
- Architecture map + per-domain charters → `kanban/architecture/README.md`, `src/**/AGENTS.md`
- Units of work (dossiers) → `kanban/planning/` (scaffold from `_template/`)
- Backlog tasks → `kanban/tasks/` · Cadence → `kanban/triggers/`
- Apple Silicon perf → `kanban/initiatives/initiative-apple-silicon.md`
- **Product strategy (Cursor / MIT model)** → `kanban/Strategy-Current.md` · ADR-003 · ADR-005 ·
  `initiative-ai-djing-product`
- Git posture (public early → agora) → `kanban/runbooks/go-private-and-git-posture.md`
- **Federation (Grok / Claude / Codex)** → `kanban/federation/FEDERATION.md` · role
  `kanban/federation/roles/claude-code.md` · CLI `./kanban/scripts/migx-fed`  
  (Antigravity/`agy` is **paused** — no tokens; do not route new mail there.)

## Multi-agent on this box
You are the **implementer** peer (`claude-code`) — RT/engine **and** non-RT/UI/ontology product
volume while Antigravity is paused. Grok CLI is the **signal scout** (`grok-signal`); Codex is the
**verifier-cartographer** (`codex-cli`). Coordination is **git-mediated mail**, not chat:

```bash
export MIGX_FED_SIDE=claude-code
./kanban/scripts/migx-fed sync                  # shared peer/mail/worktree snapshot
./kanban/scripts/migx-fed poll --to claude-code   # every session start
```

Worktrees + ownership: `kanban/runbooks/multi-agent-parallel-sessions.md`. Do not dual-edit another
peer's uncommitted federation files, or any peer-owned source path; fold handoffs into open dossiers
or file tasks.

Grok 4.5 long loops (scout overnight / research): same closed-loop *properties* as your `/loop`, via
disk contract + `migx-fed` — see `kanban/runbooks/grok-long-harness-loop.md`. You remain default
implementer; Grok remains default field signal.

**Federation sync:** before claiming work, run `just fed-sync` to see peer mail, active lane claims,
worktrees, dirty sync paths, and generated sidecar artifacts. For mutating multi-file/dossier lanes,
write a narrow `migx-fed claim` and release it when done. Then `just fleet` / `just fleet-drain` ranks open mail and runs Codex
seal drains. Model routing SSoT: `kanban/knowledge/fleet-operating-model.md` (Claude = implement;
Codex = P-08; Grok = X). Antigravity re-enable path: `AGY.md` + `peers.yaml`.

## Extending the harness
Which primitive (subagent / skill / workflow / `/loop` / `/schedule`) → `kanban/playbook/03`. Skill/agent/
workflow authoring conventions → the `AGENTS.md` in each `.claude/` subdir. CC capabilities →
`kanban/knowledge/claude-code-capabilities.md`.
