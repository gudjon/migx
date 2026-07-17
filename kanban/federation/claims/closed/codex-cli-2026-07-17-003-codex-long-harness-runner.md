---
id: codex-cli-2026-07-17-003-codex-long-harness-runner
owner: codex-cli
status: closed
created: "2026-07-17"
created_utc: "2026-07-17T14:19:44Z"
expires_utc: "2026-07-17T18:19:44Z"
subject: "codex-long-harness-runner"
paths: "kanban/scripts/migx-fed, justfile, kanban/runbooks/codex-long-harness-loop.md, kanban/federation/FEDERATION.md, kanban/federation/roles/codex-cli.md, CLAUDE.md"
branch: "main"
commit: "333afa9"
---

# codex-long-harness-runner

## Intent
Codex is wiring a one-command long harness runner that periodically performs sync, audit, and poll for codex-cli.

## Scope
- `kanban/scripts/migx-fed`
- `justfile`
- `kanban/runbooks/codex-long-harness-loop.md`
- `kanban/federation/FEDERATION.md`
- `kanban/federation/roles/codex-cli.md`
- `CLAUDE.md`

## Release
Run `./kanban/scripts/migx-fed release --id codex-cli-2026-07-17-003-codex-long-harness-runner --by codex-cli --resolution "..."` when the lane is done.

## Resolution
Released by codex-cli at 2026-07-17T14:23:07Z.

Landed migx-fed harness: a read-only long runner that cycles sync, audit, and poll; added just fed-harness and fed-harness-smoke wrappers; bounded smoke passed.
