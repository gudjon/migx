---
id: prune-outdated-legacy-code
type: task
title: "Identify outdated/legacy code to prune for a clean Migx structure (fork-aware, owner-gated)"
status: open
owner: gudjon
priority: medium
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon request 2026-07-17 — remove outdated parts / outdated codebase; clean structure of everything"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A pruning proposal (kanban/knowledge/prune-candidates.md) that:
  - inventories outdated/legacy/removable parts of the Migx codebase, bucketed:
    (A) deprecated code paths (e.g. src/waveform/renderers/deprecated/, Qt5 fallback if Migx goes
        Qt6-only, old GL paths), (B) legacy UI (QWidget skins vs the QML/AI-DJing direction — big call),
    (C) genuinely dead/unused files, (D) features off the AI-DJing thesis worth dropping,
  - RATES each candidate: size, build risk (LOW/MED/HIGH — HIGH = likely to break the build/tests),
    and reversibility. (No upstream-merge risk — Migx is a true hard fork, ADR-002.)
  - RECOMMENDS: safe-to-remove-now (dead files, stray artifacts, our own redundant scaffolding) vs
    owner-decision (larger legacy subsystems / value calls about what Migx keeps) vs keep (still needed),
  - the value judgment (what Migx keeps) is Gudjon's; nothing is blocked by merge concerns.
  Then approved cuts are executed in a follow-on dossier, each behind a build+test verifiability gate.
---

# Prune outdated/legacy code (true hard fork)

Goal: a clean Migx structure. **Migx is a true hard fork (ADR-002)** — no upstream-merge constraint, so
pruning/restructuring is fully on the table. The only gates are **build+test** and **deliberate change
management** (not merge-risk). The value call — *what Migx keeps* — is Gudjon's; nothing is blocked by
merge concerns anymore.

**Do (analysis):** inventory + risk-rate removal candidates (deprecated renderers e.g.
`src/waveform/renderers/deprecated/`, Qt5 fallback paths → Qt6-only, legacy QWidget skins vs QML-first,
dead files, off-thesis features) by **build risk + reversibility + value-to-Migx**. **Execute** approved
cuts in a follow-on dossier, each behind a build+test verifiability gate so nothing silently breaks
(`P-03`/house physics). Safe immediate cleanup (dead files, stray artifacts) can proceed now. Ties to
the AI-DJing thesis (README) and the QML-first direction ([[design-md-ui-modernization]]).

## 2026-07-17 hold

Do **not** wholesale-delete `src/waveform/renderers/deprecated/` or `widgets/deprecated/` yet. Claude
found active allshader / GL waveform includes still depend on deprecated headers; deletion must become
a render-owner untangling dossier with a build+test gate, sequenced after the DUI token spike.
