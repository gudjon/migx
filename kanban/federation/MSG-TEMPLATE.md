---
id: REPLACE-from-to-YYYY-MM-DD-NNN-slug
from: grok-signal          # or claude-code | codex-cli | gudjon (antigravity-cli is paused)
to: claude-code
type: signal-handoff       # signal-handoff | research-request | status | blocker | question | coord
status: open
created: "YYYY-MM-DD"
created_utc: "YYYY-MM-DDTHH:MM:SSZ"
severity: medium           # low | medium | high | blocker
subject: "short-slug"
relates_to: []
acceptance: "One line — verifiable done condition"
branch: ""
commit: ""
---

# <Action-oriented title>

## Intent
What you want the receiver to do or decide. One short paragraph.

## Context
Why now. Migx thesis link (Apple Silicon / AI-DJing / EXO / UI / engine). Prior msgs or ADRs.

## Evidence
Links, X post ids/URLs, file:line, paper titles, measured claims. Prefer primary sources.

## Requested Action
Concrete checklist the receiver can execute:
1. …
2. …

## Blockers
What you already know is stuck / missing. Empty if none.

<!-- On close, receiver appends:

## Resolution
- landed: paths / SHAs / task ids
- deferred: where it went (or "none")
-->
