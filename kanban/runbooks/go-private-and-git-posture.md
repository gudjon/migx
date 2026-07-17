---
id: runbook-go-private-and-git-posture
type: runbook
title: "Git posture — public early, agora transfer later, optional private for Intelligence"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md
  - kanban/architecture/decisions/ADR-003-licensing-and-openness.md
  - kanban/Strategy-Current.md
---

# Git posture (public early → agora org)

Hard-fork product development without thrashing visibility mid-scaffold.

## Owner decision (2026-07-17)

| Phase | Posture |
|---|---|
| **Early (now)** | Keep **`github.com/gudjon/migx` public**. Fine while harness, strategy, and instrument work land. |
| **Later** | Move the product under **[`github.com/orgs/agora`](https://github.com/orgs/agora)** (transfer or new repo + push). |
| **Layer C / secrets** | Prefer **private** repos under agora when Intelligence / keys / billing exist — not required for early Layer A+B. |

**Do not** treat “go private now” as a P0 gate. Product progress (MTL, EXO, QML) outranks a visibility flip.

> Agents: **do not** force-push, delete remotes, transfer orgs, or rewrite history unless Gudjon
> explicitly orders it.

---

## Current state

- Remote: `https://github.com/gudjon/migx.git` (personal account)  
- Visibility: **public** (intentional for early phases)  
- Hard fork: ADR-002 (no obligation to track `mixxxdj/mixxx`)  
- Product license model: MIT-equivalent / Cursor path (ADR-003) — proprietary ship allowed  

---

## Goals by phase

### Now
1. Ship strategy + instrument + harness in public.  
2. Never commit **secrets** (API keys, customer data, private model weights). Proprietary *code* may
   live in-tree under the MIT operating model; go private or split repos before sensitive ship.  
3. Optionally detach GitHub *fork network* badge when convenient (ADR-002) — independent of public/private.

### Later (agora)
1. Canonical home under **agora** org (team, permissions, brand).  
2. Decide visibility per repo: DAW may stay public (open-core) or go private; **Intelligence private**.  
3. Update remotes, CI, agent `MIGX_REPO_ROOT` clones, federation peers if paths change.

---

## Decision tree

| Option | What | When | Risk |
|---|---|---|---|
| **0. Stay public on gudjon/migx** | Status quo | **Early phases (default now)** | Low — don't commit secrets |
| **1. Transfer to agora** | GitHub “Transfer ownership” → `agora/<name>` | Product past pure scaffolding | Medium — update remotes/clones |
| **2. New agora repo + push history** | `gh repo create agora/…` + push all branches/tags | Prefer clean name / no transfer friction | Medium |
| **3. Make private (any host)** | Visibility flip | Secrets risk, or closed dev preference | Low if already under agora |
| **4. Orphan history rewrite** | Drop history | Only catastrophic secret leak | **High** — avoid |

**Default path:** Option 0 now → Option 1 or 2 later → Option 3 only for Layer C or if product policy requires.

---

## Later — transfer under agora (owner checklist)

### T1. Preconditions
- [ ] Agora org exists and you have owner rights: https://github.com/orgs/agora  
- [ ] Local work committed / multi-agent worktrees clean  
- [ ] Choose name: e.g. `agora/migx` (confirm final slug)

### T2. Transfer (GitHub UI)
Repo **Settings** → **Danger Zone** → **Transfer ownership** → `agora`  
Or create empty `agora/migx` and:

```bash
git remote rename origin personal
git remote add origin https://github.com/agora/migx.git   # final slug
git push -u origin --all
git push origin --tags
```

### T3. After move
```bash
git remote -v
gh repo view --json nameWithOwner,isPrivate,url
# update CI, docs that hardcode gudjon/migx, agent clones, worktrees
```

### T4. Strategy log
Append decision date to `kanban/Strategy-Current.md` §10.

---

## Optional — private visibility (not early default)

```bash
gh repo edit <owner>/<repo> --visibility private
```

Use when:
- Layer C service repo  
- Accidental secret (also rotate the secret)  
- Explicit product policy for closed DAW *development* (still GPL on distribute)

---

## Optional — detach Mixxx fork network

Independent of public/private. If GitHub still shows a fork parent of `mixxxdj/mixxx`, detach via
Support or by Option 2 (new non-fork repo + push). Aligns with ADR-002.

```bash
gh repo view --json isFork,parent
# git remote remove upstream   # if present and unused
```

---

## Secrets hygiene (always — especially while public)

- No API keys, `.env`, or proprietary model weights in this repo  
- Layer C credentials only in private Intelligence repo / secret store  
- If a secret lands in history: rotate first; rewrite only if required  

---

## Multi-agent note

Visibility changes do not change federation protocol (`migx-fed`). After agora transfer, each
worktree updates `origin` and re-auths `gh`/SSH for the org.

---

## Acceptance — early phase (now)

- [x] Public on `gudjon/migx` is **allowed and preferred** for early work  
- [x] Strategy records agora as **later** home  
- [ ] No secrets in tree  
- [ ] ADR-002 hard fork still holds (no upstream-merge obligation)  

## Acceptance — agora phase (later)

- [ ] Canonical remote under `agora/…`  
- [ ] Clones / CI / docs updated  
- [ ] Layer C plan (private) if monetizing  
- [ ] Strategy decision log updated  

---

## Related

- Strategy: `kanban/Strategy-Current.md`  
- ADR-002 hard fork · ADR-003 licensing · ADR-005 open-core + Intelligence  
- Task: `kanban/tasks/transfer-migx-to-agora-org.md` (later; not P0)
