---
id: federation-agents
type: doctrine
title: "kanban/federation/ — agent routing for Migx peer federation"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/federation/FEDERATION.md
  - kanban/AGENTS.md
---

# federation/ — what lives here

Cross-agent coordination between **Grok**, **Claude Code**, and **Codex CLI** on this box.
**Antigravity (`agy` / `antigravity-cli`) is paused** (no tokens, 2026-07-17) — do not address new
open mail there. Protocol SSoT: [`FEDERATION.md`](FEDERATION.md). Do not invent a parallel chat log.

## Read order (session start)

1. This file + `FEDERATION.md` (skim if you already know the protocol).
2. Your role charter under `roles/` (`grok-signal`, `claude-code`, `codex-cli`).
3. `./kanban/scripts/migx-fed sync`, then `poll --to <your-side>` — act on open mail and active claims.

## Layout

| Path | What |
|---|---|
| `FEDERATION.md` | Protocol (SSoT) |
| `peers.yaml` | Side ids + tools + worktrees |
| `channels.yaml` | Surfaces and writers |
| `roles/` | Per-side mandate (what you do / don't do) |
| `signal/` | Grok field intel briefs (not work orders) |
| `messages/open\|ack\|closed/` | Handoffs; **state = folder** |
| `claims/active\|closed/` | Temporary edit-lane claims; visible collision warnings |
| `MSG-TEMPLATE.md` | Required body sections |
| `CLAIM-TEMPLATE.md` | Claim frontmatter/body shape |
| `scratchpad/` | Local only — **gitignored**; never commit |

## Rules of engagement

- **Coordination is a commit.** If it isn't in `kanban/federation/` (or a task/dossier it cites), it
  didn't happen for the other peer.
- **Pull delivery.** Sender commits; receiver polls. No expectation of instant chat.
- **One owner per unit of work (MG-4).** A handoff does not steal an open dossier — it proposes; the
  implementer folds into an existing open dossier or scaffolds a new one.
- **Claim before mutating shared lanes.** `migx-fed claim` blocks overlapping live claims unless the
  peer explicitly uses `--force`; forced overlaps must be intentional and visible in `migx-fed sync`.
- **House physics bind every implementer.** Grok may propose ideas that allocate on the RT thread;
  Claude rejects or redesigns (`P-02`). Signal is not authority.
- **Worktrees for file mutation.** Federation messages may be written from either worktree; avoid
  dual uncommitted edits to the *same* message file.

## CLI

```bash
./kanban/scripts/migx-fed doctor
./kanban/scripts/migx-fed sync
./kanban/scripts/migx-fed claims
./kanban/scripts/migx-fed claim --by "$MIGX_FED_SIDE" --subject short-lane --paths path
./kanban/scripts/migx-fed poll --to "$MIGX_FED_SIDE"
./kanban/scripts/migx-fed list --status open
```
