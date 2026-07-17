---
id: claude-code-capabilities
type: knowledge
title: "Claude Code capability surface the Migx harness leverages"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: "https://code.claude.com/docs/en/how-claude-code-works + /changelog (fetched 2026-07-17)"
defers_to:
  - kanban/playbook/03-harness-engineering-outer-ring.md
---

# Claude Code capability surface (what the Migx harness leverages)

Reference for the *current* Claude Code feature set the outer-ring harness builds on. The playbook
(ch. 03) is the doctrine for *which primitive to reach for*; this is the *inventory*. Re-check against
`https://code.claude.com/docs` when a feature seems stale — this rots.

## The agentic loop
gather context → take action → verify results, repeating; you can interrupt (Esc) or steer mid-turn.
Claude Code is the harness around the model: tools, context management, execution env.

## Primitives (see playbook ch.03 for the keeper rule)
- **Subagents** (`Agent` tool) — fresh isolated context; **background by default** (notified on
  completion), return a summary → keep the main context lean. **Agent teams**: implicit per session,
  address a running teammate by name via `SendMessage`. **Nested up to 5 levels**. **Worktree
  isolation** (`isolation: 'worktree'`) for parallel file-mutating agents (prevents git mutations on
  the main repo). Per-agent `model`/`effort` override. Session cap ~200 spawns (auto-mode).
- **Skills** (`.claude/skills/<name>/SKILL.md`) — `description` is the auto-load trigger; body loads
  on demand (keep it short). `disable-model-invocation: true` → user-only `/name`. **Nested skills**
  (`<dir>:<name>` on collision). **Hotload** + **stack up to 5** (`/skill-a /skill-b do X`).
  `skillOverrides` in settings hides/adjusts skills you didn't write. Grounding contract:
  `defers_to`/`audit_gate`/`verifiable_output_shape`. `${CLAUDE_SKILL_DIR}`, `!`cmd``, `$ARGUMENTS`.
- **Hooks** (`.claude/hooks/`, wired in settings.json) — events: `PreToolUse`, `PostToolUse`,
  `SessionStart`, `Setup`, **`Stop` / `SubagentStop`** (may return `additionalContext` to give
  feedback and continue the turn), **post-session** (for `/schedule` snapshots/exports). Matchers are
  exact-match (hyphenated names too). Discipline: warn-only, read-stdin-JSON, `|| true`, always exit 0,
  per-hook `timeout`, `$CLAUDE_PROJECT_DIR`. `continue:false` halts.
- **`/loop`** — recurring or self-paced prompt (the overnight optimization loop; this whole buildout).
- **`/schedule`** — cloud cron **Routines** + webhooks + post-session lifecycle hooks (durable, runs
  after the session closes).
- **Workflows** (`Workflow` tool, `.claude/workflows/*.js`) — deterministic multi-agent JS
  orchestration (fan-out → verify → synthesize); **dynamic size**. Use ONLY for genuinely multi-agent
  shapes; a subagent + skill is preferred otherwise.

## Sessions, background, context
- **Background sessions** (`/fork`), **`/resume`** picker; long-running commands survive
  restart/update; MCP tool calls >2min auto-background (`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`).
- **Context**: `CLAUDE.md` loads every session (keep thin); **auto memory** `MEMORY.md` first 200
  lines / 25 KB loads at start; MCP tool defs are **deferred** (tool-search loads schemas on demand)
  — only names cost context until used. `/context` shows usage; compaction clears old tool outputs
  then summarizes (put durable rules in CLAUDE.md, not conversation).
- **Checkpoints** — every file edit is reversible (Esc Esc); separate from git.

## Permissions & sandboxing
- Permission modes: Manual / Accept-edits / Plan / Auto (Shift+Tab). Allow specific commands in
  `.claude/settings.json`.
- **`Tool(param:value)` rules** — match tool inputs, e.g. `Agent(model:opus)` to gate Opus subagents.
- **`sandbox.credentials`** — block sandboxed commands from reading secret/credential files.
- **Auto mode blocks destructive git** (`reset --hard`, `checkout -- .`, `clean -fd`, `stash drop`)
  unless explicitly requested. `additionalDirectories` widens file access.
- Managed: `enforceAvailableModels`, `requiredMinimumVersion`. `/config key=value` sets any setting.

## MCP
Servers connect external services; **tool-search** defers schemas (context-cheap); OAuth auto-retry;
`claude mcp login/logout <name>` (`--no-browser` for SSH).

## How the Migx harness uses this
- Research/verify → **background subagents** (Explore for navigation; general-purpose for synthesis).
- Pattern auto-load → **`pat-*` skills** firing on the relevant `src/` path (playbook ch.02, P-05).
- The Dream → a **workflow** + a **`/schedule` Routine** + a **post-session hook** (playbook ch.04).
- RT-safety / house-physics warnings → **PreToolUse hooks** (warn-only) on edits to `src/engine`.
- The optimization loop → **`/loop`** kicking build→bench→compare→optimize overnight.
- Multi-agent codebase legibility → **tool-agnostic AGENTS.md** per domain (Codex/Grok read the same).
- **Grok 4.5 long loops** → same closed-loop *properties* via disk contract + `migx-fed` (not Claude
  `/loop` binary): `kanban/knowledge/grok-long-harness-and-loops.md` +
  `kanban/runbooks/grok-long-harness-loop.md`.
