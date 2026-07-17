---
id: signal-2026-07-17-antigravity-cli-strengths-federation
type: signal-brief
author: grok-signal
created: "2026-07-17"
topics: [antigravity-cli, federation, multi-agent, harness]
sources:
  - "X @shengzheyao Antigravity CLI 1.1.0 modes (2026-07-08)"
  - "X Agent Teams /teamwork / subagents (2026-07)"
  - "X @antigravity / @Google: parallel agents, terminal harness (IO 2026)"
  - "X practitioners: specs+skills+agy CxB; Claude+Antigravity combo"
relevance: actionable
promoted_to: null
---

# Signal — What Antigravity CLI is good at (for Migx federation)

## Summary
X discourse (mid-2026) converges: **agy is a multi-agent execution harness**, not a chat CLI.
Strengths are **parallel specialized subagents**, **async background work**, **mode control**
(plan / review / accept-edits), **terminal log–driven self-correction**, and **good cost/speed** on
Gemini Flash for mechanical waves. Weaknesses relative to Claude Code: deep single-thread reasoning
and “frontier coding excellence” are often still attributed to Claude — so **pair them**, don’t
replace Claude on RT-critical Migx work.

## What X says is “good”

| Strength | Signal | Federation use |
|---|---|---|
| **Agent Teams / subagents** | `/teamwork` (preview), lead agent spawns specialized workers; async, separate context; Flash for cheap workers | Fan-out: plan / implement / test **inside one agy goal**, then **one** `migx-fed` close with artifacts |
| **Mechanical subagents** | Master offloads “mechanical” tasks to subagents | Bulk renames, file scaffolding, test boilerplate, doc generation |
| **Parallel tracks** | Official demos: backend + frontend agents at once | e.g. Theme.qml + one QML screen in parallel — **not** parallel with Claude on same files |
| **Modes (1.1.0+)** | Shift+Tab: **default review-first**, **accept-edits**, **plan** (no writes) | **plan** for federation design; **review-first** on shared trees; **accept-edits** only on `agy/*` worktree |
| **Realtime terminal feedback** | Parses console/tool output and unblocks CLI tools (Flutter/Vite-class loops) | `pre-commit`, `ctest -R`, cmake config loops — self-correct green gates |
| **Autonomy balance** | “Exploratory + self-correct”; control how much it does alone | Own **bounded goals** with acceptance lines in mail, not unbounded “fix the app” |
| **Specs + skills + agents** | Practitioners: architecture specs + HUs + stack skills → strong CxB | Feed AGENTS.md / dossiers / DESIGN.md; install skills for QML/Qt |
| **Claude + Antigravity combo** | Repeated “combine Claude Code + Antigravity” playbooks | Claude = RT/engine precision; agy = swarm product/UI execution |
| **Go harness, async** | Google: snappy CLI, background multi-agent, same harness as desktop | Long product waves while Claude runs MTL |

## What X says to avoid overclaiming

- Raw coding / long-horizon single-agent reliability still often **Claude- or Codex-preferred**
- Rate limits / tier quotas on Google consumer plans still bite (your banner: Starter Quota)
- Multi-agent noise: hard to know which agent beeped — use worktrees + named federation sides

## Map onto Migx federation peers

```text
                    Grok (X freshness)
                         │ research-request / signal-handoff
                         ▼
  Claude ◄── coord / RT asks ──► Antigravity (agy)
  RT/MTL                         teams: UI · ontology · tests · docs
  precision                      modes: plan → review → accept on worktree
                         │
                         ▼
                    Codex (verify / EVD / cartography)
```

| Give **agy** | Keep **away** from agy (default) |
|---|---|
| ADR-004 QML screens + Theme.qml generator | `src/engine/**` process* / RT alloc paths |
| EXO `ontology.json` schemas + 3-track hand-author | Sealing MTL perf claims without EVD |
| Layer B session-mirror / intent-inbox **file** shapes | Competing edits on Claude’s open wave files |
| Parallel: docs + tests + UI for one feature | Being the only X scout |
| `/plan` then implement with review-first | Force-push / history rewrite |

## Recommended prompt pattern (agy session)

1. `migx-fed poll --to antigravity-cli`  
2. Mode **plan** → write contract (paths owned, acceptance, out of scope RT)  
3. Worktree `agy/*` only  
4. Mode **review-first** or **accept-edits** on that worktree  
5. Optional internal Agent Teams for plan/code/test split  
6. `pre-commit` / targeted tests  
7. `migx-fed close` with paths + commands  

## Suggested next step
- [x] Land this brief  
- [ ] Optionally promote: coord to `antigravity-cli` listing first 2 goals (Theme.qml spike + EXO schema file)  
- [ ] Keep Claude on open MTL mail  

## Non-goals
Using agy as Gemini CLI chat replacement or as sole implementer of the RT engine.
