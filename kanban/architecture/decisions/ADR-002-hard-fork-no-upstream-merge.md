---
id: ADR-002
type: decision
title: "Migx is a true hard fork — no upstream connection; free to restructure, prune, and reshape"
status: accepted
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
supersedes: []
amends: [ADR-001]
related: [ADR-003, ADR-005, strategy-current, initiative-ai-djing-product]
---

# ADR-002 — True hard fork

## Context
Migx started from Mixxx the way **Cursor started from VS Code (Code-OSS)** — copy the OSS base, then
modify the internals directly to give AI deep, native access (Cursor: cursor position / file structure /
edits woven into the editor; **Migx / AI-DJing: agent access to live session state — decks, position,
cue points, the crate, the experience ontology — woven into the core**). The goal: *replicate Cursor's
success, but for AI-DJing.*

Gudjon's decision (2026-07-17, consolidating an evolving discussion): **Migx is a *purely true hard
fork*.** The repo (`github.com/gudjon/migx`) does not need to stay fork-connected to `mixxxdj/mixxx`,
and Migx is **free to restructure, prune legacy code, and reshape around the AI-DJing thesis.**

## Decision
1. **No upstream connection, either direction.** Migx does not push to Mixxx and does not commit to
   tracking/pulling upstream. (A one-off cherry-pick of a specific upstream fix is always *possible*,
   but it is not a constraint that shapes design.) Detach the GitHub fork relationship (a GitHub-side
   action — see "Follow-ups").
2. **Free to restructure and prune.** The tree can be reorganized, the monolithic `CMakeLists.txt`
   split, deprecated code removed, Qt5 dropped for Qt6-only, and the UI moved QML-first — reshaping
   around the AI-DJing thesis. `fork_delta` in DDD cards now records *heritage only* (inherited vs
   reshaped vs Migx-new), not mergeability.
3. **Deliberate, not careless.** "Free to change" ≠ "change recklessly." Every significant restructure
   or removal lands in a dossier behind a **build + test verifiability gate** (`P-03`, house physics) so
   nothing silently breaks. `kanban/tasks/prune-outdated-legacy-code.md` drives the first pass; the
   value call (what Migx keeps) is the owner's.
4. **The differentiator is depth AND freedom.** Deep AI-first internals (the headline divergence) *plus*
   full license to modernize the base — Migx is its own product now.
5. **Licensing / openness — see `ADR-003` (MIT operating model).** Product work follows the Cursor
   path (proprietary app + AI allowed). Attribution to upstream authors remains required practice.

## Effect on ADR-001
ADR-001's `justfile` orchestrator and frontend recipes **stand**. Its structural **non-goals (no
restructure, no CMake split, no legacy pruning) are withdrawn** — those were justified by upstream-merge
risk, which no longer applies. Restructuring/pruning is now legitimate, gated on build+test.

## Follow-ups
- **GitHub (phased):** early phases may stay **public** on `gudjon/migx`; **later** transfer under
  [`agora`](https://github.com/orgs/agora) as the canonical product home. Detach Mixxx fork-network
  badge when convenient. Runbook: `kanban/runbooks/go-private-and-git-posture.md`.
- **Licensing / product model:** ADR-003 (MIT operating model, accepted) + ADR-005 (proprietary stack).
- **Strategy:** `kanban/Strategy-Current.md`.
- The AI-DJing internal-access layer (agent reads/writes live session + cue + ontology) is the headline
  divergence — seeds EXO/world-model work + Layer B agent seams under `initiative-ai-djing-product`.
