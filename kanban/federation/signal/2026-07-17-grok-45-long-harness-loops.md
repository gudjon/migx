---
id: signal-2026-07-17-grok-45-long-harness-loops
type: signal-brief
author: grok-signal
created: "2026-07-17"
topics: [harness, loops, grok-4.5, multi-agent, claude-code]
sources:
  - "X: harness>model / Claude Code architecture threads (2026)"
  - "X: loop engineering + Karpathy LOOPS.md summaries"
  - "X: Grok Build / Grok 4.5 agentic ecosystem"
  - "kanban/knowledge/grok-long-harness-and-loops.md"
relevance: actionable
promoted_to: null
---

# Signal — Grok 4.5 long harness ≈ Claude Code loops (via disk + federation)

## Summary
Trending X discourse agrees: **long agent work is harness + loop design**, not a bigger chat.
Claude Code’s power is the outer system (streaming loop, compaction, permissions, subagents, hooks,
verify). Grok 4.5 is strong at agentic reasoning/coding and uniquely strong at **live X signal**.
For Migx, Grok gets Claude-like long runs by **disk contracts + wave loops + migx-fed**, while Claude
keeps native `/loop` for engine/MTL. Dual peer is the product tandem.

## Relevance to Migx
- AI-DJing product velocity (MIT model, Strategy) — multi-agent fleet  
- Federation already built — pull mail is the multi-vendor mailbox  
- Scout mode is Grok’s unfair advantage (X tools)  
- Loop engineering matches playbook ch.04 / MG-1  

## Claims (tagged)

| Claim | Confidence | Evidence |
|---|---|---|
| Harness matters more than model for multi-hour runs | high | widespread X teardown consensus |
| State must live on disk for restart | high | LOOPS.md / loop-engineering discourse |
| Generator ≠ evaluator | high | already `P-08` in Migx |
| Grok Build aims at agent runtime + self-correction | medium | Grok/product posts 2026-07 |
| Dual Claude+Grok worker pattern is in production use | medium | multi-CLI / worktree posts |

## Suggested next step
- [x] Land knowledge + runbook (done this session)  
- [ ] Operator: first Mode A multi-wave run with scratchpad contract  
- [ ] Optional later: wire `TR-grok-signal-scout` to cron/tmux  
- [ ] Promote handoff only if Claude needs a research burst mid-MTL  

## Non-goals
- Waiting for Grok to clone Claude Code’s `/loop` binary feature-for-feature  
- Letting Grok self-seal RT/perf dossiers  
