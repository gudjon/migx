---
id: signal-2026-08-08-agent-fs-hooks-x
type: signal-brief
author: grok-signal
created: "2026-08-08"
topics:
  - agent-harness
  - hooks
  - filesystem-agents
  - cli-spine
  - session-coaching
sources:
  - https://vercel.com/blog/how-to-build-agents-with-filesystems-and-bash
  - https://code.claude.com/docs/en/hooks
  - https://code.claude.com/docs/en/hooks-guide
  - https://vercel.com/blog/introducing-agent-plugins
  - https://vercel.com/changelog/introducing-bash-tool-for-filesystem-based-context-retrieval
  - x:post semantic cluster 2026-08 (Claude Code hooks / harness / filesystem agents)
relevance: actionable
promoted_to: null
defers_to:
  - kanban/knowledge/agent-filesystem-hooks-integration.md
---

# Signal — Agent filesystem + hooks architecture (field → Migx)

## Summary

Field consensus across Claude Code, Codex, and Vercel is that **agents integrate
via filesystem + bash/CLI**, not bespoke tool protocols. Hooks are the
**edge-triggered** half (JSON on stdin, timeouts, async); state files are the
**level-triggered** half (recoverable mid-session). Harness intelligence lives
outside the model: locks, state stores, dumb loops. MCP remains a second protocol
people are actively preferring away from when a good CLI exists.

Migx already ships the hard half (CLI spine, sidecars, session bind/log/feedback).
The build queue that matches the field is: **session lock → now.json/history →
hooks → live queue/plan** — never hooks before trustworthy state, never on RT.

## Sources (field)

- Vercel: *How to build agents with filesystems and bash* — replace custom tools
  with files + bash; agents already know that distribution.
- Vercel `bash-tool` / just-bash: dedicated FS+shell tools for agents.
- Claude Code hooks reference: lifecycle events, matcher → command, JSON stdin,
  timeout, async, settings hierarchy.
- X discourse (2026-05..08): Claude Code as harness (hooks/skills/subagents),
  “while loop + bash beats DAG frameworks”, CLI cheaper than MCP for browser
  agents, managed agents with external state store, Agent Plugins packaging
  skills (hooks still client-specific).
- Security side-channel: malicious hooks in `.claude/settings.json` / supply-chain
  — Migx hooks must be user-config, allowlisted paths, never silent.

## Relevance to Migx

| Field claim | Migx home |
| --- | --- |
| FS + bash > custom tools | ADR-008, Collection/sidecars, `migx --json` |
| Hooks = notify/guardrail | `agent-filesystem-hooks-integration.md` event set |
| State outside the model | `~/Library/Application Support/Migx/session/` |
| Per-user install | `./install.sh` (shipped) |
| Single writer / lock | session lock (gap; watch race already hit) |
| RT safety | hooks never on audio callback |
| MCP decline | matrix `wont-do` reinforced |

## Claims (tagged)

| Claim | Confidence | Evidence |
| --- | --- | --- |
| Agents prefer CLI/FS over MCP when CLI is complete | high | Vercel blog + agent-browser token comparison discourse; Migx owner already decided |
| Level-triggered state files required for mid-session agents | high | Vercel FS thesis; Claude FileChanged still secondary to files |
| Hooks need timeout + async or they poison the critical path | high | Claude Code hook timeout/async fields; RT physics |
| Stale lock detection is load-bearing | high | Migx watch race history; field “file exists ≠ running” |
| Session lock before hooks | high | dependency: hooks amplify state quality |
| Config layering is lower priority than now.json | med | useful after hooks; one config works for dogfood |

## Suggested next step

- [x] Park intel in knowledge: `agent-filesystem-hooks-integration.md`
- [ ] Implement **session lock** in state dir (smallest; known race class)
- [ ] Promote **now.json + history.jsonl** writer (CLI bind first, engine later)
- [ ] Hooks v0 only after state is honest
- [ ] No promote to implementer until owner picks #1 vs engine bridge contention

## Non-goals / discard

- MCP server for Migx
- Hooks that block load/play
- Multi-session concurrent writers without lock
- Treating rendered `set.play` mp3 as live session state
