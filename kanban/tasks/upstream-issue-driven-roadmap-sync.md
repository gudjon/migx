---
id: upstream-issue-driven-roadmap-sync
type: task
title: "Build an upstream-issue-driven roadmap + a sync mechanism with mixxxdj/mixxx issues"
status: open
owner: gudjon
priority: medium
initiative: initiative-apple-silicon
parent_dossier: ""
depends_on: [mine-upstream-issues-m4-features]
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon request 2026-07-17 — build a kanban roadmap from highly relevant mixxxdj/mixxx issues, with a sync"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A kanban roadmap surface (e.g. kanban/planning/00-PORTFOLIO/upstream-roadmap.md) that curates the
  highly-relevant upstream issues into Migx roadmap items mapped to dossiers/initiatives, PLUS a
  repeatable SYNC mechanism:
  - a script kanban/scripts/sync-upstream-issues.py that pulls filtered mixxxdj/mixxx issues (via gh)
    into a structured, git-tracked snapshot (delta-only vs a watermark, like the Dream), and
  - a trigger row (extend TR-nightly-dream's upstream tier, or a new TR-upstream-issue-sync) in
    kanban/triggers/registry.yaml so it runs on cadence and surfaces new relevant issues as roadmap
    candidates / tasks — never silently, always with provenance (authored_by: agent, issue #).
  - the roadmap distinguishes: adopt-now, track, and won't-do (with reason).
---

# Upstream-issue-driven roadmap + sync

**Do AFTER `mine-upstream-issues-m4-features`** (that produces the first curated list;
`kanban/knowledge/upstream-issues-m4-features.md`). This task turns that one-shot survey into a
**living, synced roadmap**.

Design notes:
- The sync is a closed loop (MG-1): trigger = cadence/gh query; capture = a git-tracked issue snapshot
  (delta vs a watermark); intelligence = relevance-filter + subsystem mapping; adjustment = new roadmap
  items / `tasks/` cards with the issue # as provenance.
- Reuse the Dream shape (playbook ch.04): the `upstream-mixxx-changelog-delta` tier already exists —
  extend it or add a sibling `TR-upstream-issue-sync` rather than building a parallel system (P-11).
- Keep the roadmap derive-friendly: the synced list is generated; human curation (adopt/track/won't-do)
  is the value-authorship layer that stays manual.
- Respect the fork model: adopting an upstream feature is `fork_delta` tracking; a Migx-only capability
  is `migx-new`. Record which.
