---
id: upstream-mixxx-watch-skill
type: task
title: "Agent skill: periodic upstream mixxxdj/mixxx watch (cherry-pick candidates, no ancestry)"
status: open
owner: gudjon
priority: low
initiative: initiative-apple-silicon
parent_dossier: ""
depends_on: []
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon 2026-07-17 — after fresh-git re-init (no fork ancestry), watch upstream for new dev via a skill instead of git remote tracking."
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A `.claude/skills/` skill (e.g. `mixxx-upstream-watch`) that, on demand or on a cadence:
  - queries mixxxdj/mixxx for merged PRs / releases / notable issues since a stored last-checked marker
    (via `gh` against the public repo — Migx has NO git remote link to it anymore),
  - summarizes bug fixes / features / perf changes relevant to Migx's subsystems (engine, waveform,
    controllers, library), flagging Apple-Silicon-relevant ones,
  - proposes cherry-pick/port candidates as tasks or a small dossier — port by re-implementation, never
    by adding an upstream git remote (fresh history is intentional; ADR-002 hard-fork stance),
  - records the last-checked marker so runs are incremental.
  Ships with a cadence hook (or documented `/loop` usage). Complements [[triage-upstream-easy-issues]].
---

# Upstream mixxx watch skill

After the fresh-git re-init, Migx no longer shares git ancestry with mixxxdj/mixxx (intentional — clean
history, own destiny). We still want to *learn from* upstream development without re-coupling. Build a
skill that periodically diffs upstream activity and surfaces port candidates as Migx tasks/dossiers —
re-implemented into Migx, not merged. This is the sanctioned channel for upstream signal, replacing any
git remote tracking. Related research lens: [[triage-upstream-easy-issues]], [[mine-upstream-issues-m4-features]].
