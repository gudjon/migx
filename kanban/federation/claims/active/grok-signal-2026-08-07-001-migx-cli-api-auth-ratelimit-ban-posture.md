---
id: grok-signal-2026-08-07-001-migx-cli-api-auth-ratelimit-ban-posture
owner: grok-signal
status: active
created: "2026-08-07"
created_utc: "2026-08-07T19:14:22Z"
expires_utc: "2026-08-08T07:14:22Z"
subject: "migx-cli-api-auth-ratelimit-ban-posture"
paths: "tools/migx-cli/migx_cli/api.py, tools/migx-cli/migx_cli/auth.py, tools/migx-cli/migx_cli/ratelimit.py"
branch: "feat/migx-cli-spotify-mirror"
commit: "7362907"
---

# migx-cli-api-auth-ratelimit-ban-posture

## Intent
Lane split with Claude: network/auth/ban only. Will not edit naming/resolve/layout/ingest/tags/quality/tests. Shared __main__/README only after re-read. No stash/reset/checkout --.

## Scope
- `tools/migx-cli/migx_cli/api.py`
- `tools/migx-cli/migx_cli/auth.py`
- `tools/migx-cli/migx_cli/ratelimit.py`

## Release
Run `./kanban/scripts/migx-fed release --id grok-signal-2026-08-07-001-migx-cli-api-auth-ratelimit-ban-posture --by grok-signal --resolution "..."` when the lane is done.
