---
id: migx-harness-roadmap
type: roadmap
title: "Migx Agent Harness — buildout roadmap"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# Migx Agent Harness — Buildout Roadmap

Standing up a Claude Code agent harness in Migx, adapted from the mature harness in
`/Users/gudjon/code/oz-platform`. **Migx** is Gudjon's DJ-software brand — a fork of Mixxx
(the Cursor-from-VS-Code model). We inherit the *practice* doctrine (which is deliberately
company-agnostic) and leave the OZ *domain* behind (venues, detectors, federation, robotics).

## The two ground rules we keep (everything below is a corollary)

1. **Everything is a closed loop** — Trigger → Capture → Intelligence → Adjustment. If work ships
   without a closed loop attached, it isn't done.
2. **Everything is code** — load-bearing decisions live at stable, grep-able paths. Not in chat,
   not in a PR thread. If it isn't at a stable path, it's scratch.

Human-side companion: *you can outsource thinking, not understanding.*

## What we adapt vs. what we drop

**Adapt (the transplant kit):** kanban markdown-SSoT · typed-ID system · patterns/antipatterns
catalogue · dossier = sprint + 91-loop-closure · trigger registry + Dream cadence (lightweight) ·
schema/edge/derive lint scripts · `.claude/` skills/agents/workflows/rules/hooks · the thin-CLAUDE.md
/ portable-AGENTS.md split.

**Drop (OZ-domain):** federation/, venues, cameras/detectors, NATS, `data/context/` runtime mirror,
sales/people/patents, the multi-repo tier model, cloud-routine complexity.

**Fit to Migx reality:** C++/Qt6/CMake, ~335k LOC, GoogleTest/CTest, **pre-commit is the fast
quality gate** (full builds are heavy). Existing top-level `AGENTS.md` house rules (RT engine
no-alloc/no-lock, ControlObject/ControlProxy, parented_ptr Qt ownership) are honored and EXTENDED,
never duplicated.

## The north-stars the harness serves

The harness is not built for its own sake — it exists to drive two product bets (SSoT:
`kanban/Strategy-Current.md`):

1. **AI-DJing product (Cursor for music)** — hard fork of Mixxx under **MIT operating model**
   (proprietary app + in-process Intelligence allowed); public early then under agora org.
   Initiative: `initiative-ai-djing-product` · ADR-003 · ADR-005.
2. **Blazingly fast on Apple Silicon (M4/M5 SoC)** — Metal GPU offload, NEON/Accelerate DSP, arm64
   tuning. Initiative: `initiative-apple-silicon`.

Missing capabilities become **development dossiers**, each a closed loop. Performance dossiers score
benchmarks; product dossiers score co-pilot/ontology acceptance.

## Phases (executed under the fast `/loop`)

- **Phase 0 — Doctrine spine.** `kanban/AGENTS.md` (MG-1..MG-6 operating doctrine + closed-loop
  test + work model + routing), `kanban/GLOSSARY.md` (typed-ID rules), `prefix-registry.yaml`,
  `kanban/HARNESS.md` (condensed bible), `kanban/AGENT-ONBOARDING.md` (tiered reading list).
- **Phase 1 — Templates + catalogue.** `_template/` dossier skeleton (incl. 91-LOOP-CLOSURE + PS
  template with EARS/acceptance), `patterns/` catalogue format + seed Migx patterns, `tasks/` format.
- **Phase 2 — `.claude/` harness.** thin `CLAUDE.md`, `rules/` (SSoT, dossier-lifecycle,
  planning-harness, worktree-hygiene, agentic-decision-authority + Migx-specific rt-audio-safety &
  build-test), `settings.json` (cmake/ctest/pre-commit perms + warn-only hooks), `hooks/`,
  `skills/` (add-task, add-pattern, dossier-build, build-migx, run-tests, pattern-check, pat-* ...),
  `agents/` (codebase-researcher, validator, dossier-decomposer, adr-reviewer),
  `workflows/` (dossier-pass-fanout, code-review-fanout, nightly-dream).
- **Phase 3 — Lints + triggers + CI.** `scripts/` (lint-dossier-frontmatter, lint-naming,
  verify-prefix-registry, verify-ps-citations, verify-sealed-dossier-has-closure, derive-dossier-state),
  `architecture/lint/verify-skill-grounding.py`, `triggers/registry.yaml` + `heartbeats.yaml`,
  `.github/workflows/kanban-discipline.yml`.
- **Phase 4 — Dogfood + wire-up.** Re-express this buildout as the first real dossier and seal it at
  91-LOOP-CLOSURE. Point top-level `AGENTS.md` + new `CLAUDE.md` at the harness.

## Status — harness core COMPLETE (2026-07-17)

All five phases are built and the enforcement layer is green:

- **Phase 0 — doctrine:** `kanban/AGENTS.md` (MG-1..6), GLOSSARY, prefix-registry, AGENT-ONBOARDING. ✅
- **Playbook:** `kanban/playbook/` (00-README + 4 chapters) — the deep bible distillation. `HARNESS.md`
  is now a pointer to it (MG-3, refactor-over-layer). ✅
- **Phase 1 — templates + catalogue:** dossier `_template/`; **47 pattern cards** (P-01..32, AP-01..16);
  task + initiative formats. ✅
- **Phase 2 — `.claude/`:** CLAUDE.md, 7 rules, settings.json, 2 tested warn-only hooks, 3 subagents,
  2 workflows (dossier-pass-fanout + nightly-dream), 10 `pat-*` skills. ✅
- **Phase 3 — enforcement:** 10 discipline lints **ALL GREEN** + gen-pattern-index + ddd/gen-index
  (marker-based, `--check`) + triggers/registry + heartbeats + dream-watermark + CI workflow
  `kanban-discipline.yml`. Shared lint helper is PyYAML-backed. ✅
- **Phase 4 — dogfood:** root `AGENTS.md` wired to the harness; **DDD map COMPLETE** — all 16
  bounded-context cards + 16 per-domain `src/*/AGENTS.md` charters + seams (10/10 lints green); **first
  real dossier execution-ready** — `2026-07-17-gudjon-MTL--waveform-render-baseline` (baseline the M4
  waveform render path; key lead: `coreservices.cpp:826` forces OpenGL, so the modern path isn't on
  Metal). ✅

## Harness build-out COMPLETE. Now: preparation round + backlog (2026-07-17)

The harness is fully built (47 patterns, 16 DDD contexts, playbook, `.claude/`, green enforcement). Work
now shifts to *using* it. A **preparation round** is underway before executing dossiers:
- **Build readiness:** `kanban/runbooks/build-setup-macos-m4.md` — this M4 is NOT yet buildable (Qt6 +
  ninja/clang-format/pre-commit missing; run `tools/macos_buildenv.sh setup`). **Blocker for execution.**
- **Execution-surface map** (render/DSP/benchmark code) — in flight (codebase-researcher).
- **Repo-structure + Turborepo-inspired orchestration** proposal — in flight (respecting the upstream-fork constraint).
- **Backlog tasks queued:** `mine-upstream-issues-m4-features`, `triage-upstream-easy-issues`,
  `upstream-issue-driven-roadmap-sync`, `learn-arcflow-m4-perf` (kanban/tasks/).

**Then:** execute the MTL baseline dossier (first real C++ work). Optional git commit (uncommitted on
`main` — ask first).

**Expanded knowledge-layer streams (design plans persisted; authoring pending):**
- **Playbook** — `kanban/playbook/` (00-README + 01 frame-cadence-compounding · 02 patterns-breakage-navigation · 03 harness-engineering-outer-ring · 04 daily-loop-and-the-dream). **COMPLETE.**
- **Pattern catalogue** — plan at `kanban/patterns/PATTERN-CATALOGUE-PLAN.md` (P-06..P-32, AP-03..AP-16, ~10 `pat-*` skills, 4-phase order). Authoring pending.
- **Architecture / DDD** — plan at `kanban/architecture/DDD-BUILDOUT-PLAN.md` (16 bounded-context cards keyed on the RT-thread axis, per-domain `src/**/AGENTS.md`, generated index, 3 lint scripts). Authoring pending. Tool-agnostic (Claude Code / Codex / Grok).
- **Claude Code capabilities** — `kanban/knowledge/claude-code-capabilities.md` to write (current CC feature surface the harness leverages).

**Small cleanup pending:** finish the initiative refactor (rename to `initiative-apple-silicon`,
OZ-aligned `pm_overlay`, add `_template.md`, delete old `INIT-apple-silicon.md`, fix refs); update
`AGENT-ONBOARDING.md` HARNESS.md→playbook refs.

Progress is tracked live in the `/loop`; this file is the durable record.
