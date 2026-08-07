---
id: portfolio-index
type: portfolio
title: "00-PORTFOLIO — what to build, how agents pick work"
status: active
owner: gudjon
created: "2026-08-07"
lastUpdated: "2026-08-07"
defers_to:
  - kanban/Strategy-Current.md
  - kanban/AGENTS.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
  - kanban/planning/00-PORTFOLIO/capability-gap-matrix.md
---

# Portfolio — agent entry for product buildout

**Start here** when an agent is about to open work, run an overnight loop, or
answer “what should we build next for the full DJ product?”

This folder is the **portfolio spine**. It does not replace dossiers (execution)
or the capability catalogue (product domain cards). It **queues** verifiable gaps.

## Read in this order (product build session)

| # | Doc | Why |
| --- | --- | --- |
| 1 | [`capability-gap-matrix.md`](capability-gap-matrix.md) | **Living queue** — commands, TUI gaps, caps, ArcFlow, top-10 |
| 2 | [`kanban/Strategy-Current.md`](../../Strategy-Current.md) | Why we build what we build |
| 3 | ADR-008 + [`tui-first-agentic-dj-workstation.md`](../../knowledge/tui-first-agentic-dj-workstation.md) | Command spine + TUI-first human product |
| 4 | [`arcflow-tui-agentic-dj-integration.md`](../../knowledge/arcflow-tui-agentic-dj-integration.md) | World model off RT |
| 5 | [`capability-catalogue.md`](../../architecture/ddd/capability-catalogue.md) | Product `cap-*` cards (SSoT for names) |
| 6 | Closed-loop doctrine signal | [`signal/2026-08-07-full-dj-closed-loop-agentic-buildout.md`](../../federation/signal/2026-08-07-full-dj-closed-loop-agentic-buildout.md) |

Then: **compound-before-create** → scaffold dossier from `_template/` **or** fold into an open dossier.

## Files in this folder

| File | Role |
| --- | --- |
| `capability-gap-matrix.md` | Operational status + ranked queue (§C) for automatic agentic buildout |
| `prefix-registry.yaml` | 3-letter dossier prefixes (register before use) |
| `migx-harness-roadmap.md` | How the *harness itself* was stood up (historical + residual) |

## Automatic agent procedure (short)

```text
fed-sync + poll
→ read capability-gap-matrix.md §C (top unblocked gaps)
→ ≤2 active implementer dossiers; claim paths; prefer worktree
→ PS with EARS + acceptance: check command / ctest / judge
→ waves → pre-commit → targeted tests
→ Codex P-08 seal (generator ≠ evaluator)
→ 91-LOOP-CLOSURE harvest → update matrix status
→ leave Dream / night harness running
```

**Peers:** Claude implements · Codex verifies · Grok signal/research only.  
**House physics** always bind (repo-root `AGENTS.md`).

## Related

- Playbook (how we work): `kanban/playbook/`
- HARNESS-BIBLE origin (external doctrine reference, not in-repo SSoT):
  oz-platform `kanban/HARNESS-BIBLE/` — Migx distillation is the playbook
- Federation: `kanban/federation/FEDERATION.md`
- Onboarding: `kanban/AGENT-ONBOARDING.md`
