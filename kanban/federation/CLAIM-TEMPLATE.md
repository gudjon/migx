---
id: codex-cli-2026-07-17-001-example-claim
owner: codex-cli
status: active
created: "2026-07-17"
created_utc: "2026-07-17T12:00:00Z"
expires_utc: "2026-07-18T00:00:00Z"
subject: "example-claim"
paths: "kanban/scripts/migx-fed, kanban/federation"
branch: ""
commit: ""
---

# <Short lane title>

## Intent
One short sentence explaining why this side owns the lane for now.

## Scope
- `path/or/dossier`
- `another/path`

## Release
Run:

```bash
./kanban/scripts/migx-fed release --id <id> --by <side> --resolution "done / superseded / stale"
```

If this claim overlaps another live claim, `migx-fed claim` will fail unless the sender passes
`--force`. Forced overlaps must be intentional and visible in `migx-fed sync`.
