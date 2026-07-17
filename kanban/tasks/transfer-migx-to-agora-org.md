---
id: transfer-migx-to-agora-org
type: task
title: "Later: move Migx under github.com/orgs/agora (canonical product home)"
status: open
owner: gudjon
created: "2026-07-17"
priority: P3
defers_to:
  - kanban/runbooks/go-private-and-git-posture.md
  - kanban/Strategy-Current.md
  - kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md
---

# Transfer Migx under Agora org

## Why
Canonical product home should be **org-owned** under
[agora](https://github.com/orgs/agora) for team, brand, and future private Intelligence repos.
**Not blocking early work** — keep `gudjon/migx` **public** for now (owner decision 2026-07-17).

## When
After early scaffolding is past “harness + strategy + first product loops” — not before MTL/EXO have
real traction unless the owner prefers sooner.

## Done when
- [ ] Repo lives under `agora/<slug>` (transfer or new remote + history push)  
- [ ] Local remotes, worktrees, CI, and docs that hardcode `gudjon/migx` updated  
- [ ] `Strategy-Current.md` decision log notes the move date  
- [ ] Layer C (if any) planned as **private** under agora  
- [ ] LICENSE + AUTHORS intact  

## How
`kanban/runbooks/go-private-and-git-posture.md` § “Later — transfer under agora”.

## Explicit non-goals (now)
- Making the current public repo private as a P0  
- Orphan-resetting Mixxx history  

(ADR-003 MIT model: proprietary product binary is an allowed goal when we ship.)
