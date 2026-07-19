---
id: signal-2026-07-19-nextgen-methods-x-annex
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [nextgen, methods, strangler, feature-flags, worktrees, multi-agent, P-08]
mapped_to:
  - nextgen-agent-dj-shadow-product
  - initiative-ui-modernization
  - ADR-004
method: "X semantic + keyword on strangler/shadow, expand-contract, feature flags for agents, worktree multi-agent"
---

# X methods annex — how to best run NextGen Agent DJ shadow

**SSoT:** `kanban/knowledge/nextgen-agent-dj-shadow-product.md` §7

## One-line synthesis

Field practice for dual-path products is **strangler + facade + flags (deploy≠release) + expand-contract**, built by **micro-agents in isolated worktrees with an independent verifier** — not a big-bang rewrite and not self-graded YOLO merges.

## Methods X reinforces (→ Migx apply)

| Method | Field signal | NextGen apply |
|---|---|---|
| **Facade first** | Stage 0 intercept before swap | CO bus *is* the facade — no second control plane |
| **Read then write** | Proxy reads first; writes later | NextGen renders CO first; writers respect P-06 |
| **Shadow / mirror** | Duplicate traffic; compare; then activate | Optional offline judges later; dogfood binary first |
| **Deploy ≠ release** | Merge dark; flip flag for users | `ui.nextgen.*` + `migx-agent` dogfood |
| **Expand-contract** | Dual-write + late drop; blue-green lies on schema | FSL/library sidecars only |
| **Worktree isolation** | Filesystem isolation is the multi-agent bottleneck | One worktree per `mod-*` claim |
| **Micro-agent → verifier** | Single-task loop + checker + flag | SPEC→…→JUDGE→REVIEW (Codex)→FLAG |
| **Orchestrator lanes** | Non-overlapping work; independent fleet review | Claims + P-08; no self-seal |
| **Human as picker** | Orchestrate N agents, pick best branch | Owner + Codex pick winner |

## Explicit rejects (field + house)

Big-bang LateNight rewrite · self-grading · one mega-agent · two agents one cwd · deploy=release · dual-write without expand-contract · agent self-enable of prod flags.

## Cadence (canonical)

`SPEC → CLAIM → BUILD → JUDGE → REVIEW → COMPOUND → FLAG → STRANGLE`  
Detail in §7.3 of the knowledge doc.

## Fleet next (unchanged product decisions)

1. Owner: Option A (`migx-agent`) vs B/C/D.  
2. Claude: scaffold feasibility on discussion mail.  
3. Codex: minimum judge + machine-checkable “module done”.  
4. Do **not** reopen Electron for Surface A.
