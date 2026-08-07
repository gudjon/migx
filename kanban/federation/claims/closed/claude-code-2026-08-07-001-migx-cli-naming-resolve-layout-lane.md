---
id: claude-code-2026-08-07-001-migx-cli-naming-resolve-layout-lane
owner: claude-code
status: closed
created: "2026-08-07"
created_utc: "2026-08-07T19:08:05Z"
expires_utc: "2026-08-08T07:08:05Z"
subject: "migx-cli-naming-resolve-layout-lane"
paths: "tools/migx-cli/migx_cli/naming.py, tools/migx-cli/migx_cli/resolve.py, tools/migx-cli/migx_cli/layout.py, tools/migx-cli/migx_cli/ingest.py, tools/migx-cli/migx_cli/tags.py, tools/migx-cli/migx_cli/quality.py, tools/migx-cli/test_migx_cli.py"
branch: "feat/migx-cli-spotify-mirror"
commit: "9512fa7"
---

# migx-cli naming+resolve+layout lane

## Intent
Shared checkout with Grok CLI. Grok owns api.py/auth.py/ratelimit.py (network+ban posture); Claude owns matching/naming/layout/ingest. __main__.py and README.md are SHARED — re-read immediately before editing, commit right after.

## Scope
- `tools/migx-cli/migx_cli/naming.py`
- `tools/migx-cli/migx_cli/resolve.py`
- `tools/migx-cli/migx_cli/layout.py`
- `tools/migx-cli/migx_cli/ingest.py`
- `tools/migx-cli/migx_cli/tags.py`
- `tools/migx-cli/migx_cli/quality.py`
- `tools/migx-cli/test_migx_cli.py`

## Release
Run `./kanban/scripts/migx-fed release --id claude-code-2026-08-07-001-migx-cli-naming-resolve-layout-lane --by claude-code --resolution "..."` when the lane is done.

## Resolution
Released by claude-code at 2026-08-07T19:22:38Z.

Lane work landed: scored resolver, duration extraction, smart_split, playlist-order tokens, resolver registry, config, Collection/Crates, ingest. Merged to main. Releasing so Grok is unblocked across the whole tools/migx-cli tree.
