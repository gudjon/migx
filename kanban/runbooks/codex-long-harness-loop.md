---
id: runbook-codex-long-harness-loop
type: runbook
title: "Run Codex CLI in a long verifier-cartographer harness on Migx"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - AGENTS.md
  - kanban/federation/FEDERATION.md
  - kanban/federation/roles/codex-cli.md
  - kanban/runbooks/multi-agent-parallel-sessions.md
---

# Codex long harness loop

Run **Codex CLI** for a long Migx session as the federation's verifier-cartographer: repo mapping,
claim verification, harness tooling, and ownership hygiene. Codex listens to federation mail
periodically, but it does not auto-claim work just because a message exists.

---

## Preconditions

```bash
cd ~/code/migx          # or ../migx-codex when mutating
export MIGX_FED_SIDE=codex-cli
export MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
./kanban/scripts/migx-fed doctor
./kanban/scripts/migx-fed sync
```

Prefer the dedicated worktree for any mutation:

```bash
cd ~/code/migx
git worktree add ../migx-codex -b codex/verify-steward 2>/dev/null || true
cd ../migx-codex
export MIGX_FED_SIDE=codex-cli
export MIGX_REPO_ROOT="$(git rev-parse --show-toplevel)"
```

---

## Mode A - Passive inbox listener

Use this when Codex should keep an eye on peer mail while Claude or Grok are doing
their primary loops.

```bash
./kanban/scripts/migx-fed listen --to codex-cli --interval 900
```

For a bounded smoke test:

```bash
./kanban/scripts/migx-fed listen --to codex-cli --interval 1 --cycles 1
```

`listen` is read-only. It prints open mail and exits only when `--cycles` is reached or the operator
presses Ctrl-C. It does **not** move messages to `ack`.

---

## Mode B - Active Codex wave

At the start of each wave, load only:

1. `AGENTS.md`
2. `kanban/federation/roles/codex-cli.md`
3. `kanban/federation/FEDERATION.md`
4. `./kanban/scripts/migx-fed sync` output, then `./kanban/scripts/migx-fed poll --to codex-cli` output
5. The active dossier or files named by the message

Then execute:

```text
1. Sync federation state, then poll inbox.
2. If a message is actionable for Codex, ack it.
3. Map code ownership and dirty files before editing.
4. Verify the claim with focused commands, tests, lint, or code-path tracing.
5. Patch only harness/docs/tooling unless explicitly assigned implementation ownership.
6. Close the message with exact paths, commands, and evidence.
7. If no mail is present, run one bounded verifier task from the current dossier or stop.
```

Ack means "Codex is taking this now." If the message should belong to Claude, Grok, or
Gudjon, close with a redirect reason or send a short `coord` message to the right side.

---

## Mode C - Restartable scratchpad

Use a gitignored scratchpad for local loop state:

```bash
RUN_ID="codex-verify-$(date -u +%Y%m%dT%H%M%SZ)"
DIR="$MIGX_REPO_ROOT/kanban/federation/scratchpad/$RUN_ID"
mkdir -p "$DIR"
```

Create `$DIR/contract.md`:

```markdown
# Contract - Codex verifier-cartographer
## Goal
Occasionally listen to codex-cli federation mail and run bounded verification waves.
## In scope
federation inbox, active dossiers, repo maps, harness scripts, focused checks
## Out of scope
latest X signal, full compile ownership, second-writer edits to Claude-owned files
## Done when
- open codex-cli mail is acked/closed or intentionally left open
- any verification claim has command/path evidence
- progress.md records NEXT=stop or NEXT=sleep
```

Create `$DIR/progress.md`:

```markdown
# Progress
- wave: 0
- next: poll codex-cli inbox
- blockers: none
```

On every wave, append what changed, what was verified, and the next wake condition. Scratchpad is
local only; durable findings move into messages, dossiers, tasks, ADRs, or committed harness docs.

---

## What not to do

- Do not auto-ack every open message.
- Do not become the second writer on Claude's implementation files.
- Do not scout X/trend signal; send that to `grok-signal`.
- Do not self-certify performance without pinned command output and tail evidence.
- Do not leave important handoffs only in scratchpad.

---

## Related

- Federation protocol: `kanban/federation/FEDERATION.md`
- Role charter: `kanban/federation/roles/codex-cli.md`
- Parallel-agent setup: `kanban/runbooks/multi-agent-parallel-sessions.md`
