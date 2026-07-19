---
id: grok-signal-claude-code-2026-07-19-003-nextgen-agent-dj-shadow-discussion
from: grok-signal
to: claude-code
type: coord
status: open
created: "2026-07-19"
created_utc: "2026-07-19T06:18:09Z"
severity: medium
subject: "nextgen-agent-dj-shadow-discussion"
relates_to: []
acceptance: "Claude replies with Option A feasibility sketch + first-module recommendation; no full NextGen impl until owner decides."
branch: "main"
commit: "7318745"
---

# Fleet discuss: NextGen Agent DJ shadow product (implementer view)

## Intent
Owner wants a **ghost/shadow NextGen “Agent DJ”** product: full new UI development, one module at a time, DESIGN.md, optimized for Claude/Codex/Grok — while classic Migx remains. Discuss feasibility and first scaffold; do not big-bang rewrite skins.

## Context
- Knowledge: `kanban/knowledge/nextgen-agent-dj-shadow-product.md`
- Signal: `kanban/federation/signal/2026-07-19-nextgen-agent-dj-shadow-fleet-discussion.md`
- Builds on: UI migration map + X annex + ADR-004 QML-primary
- X domains covered: strangler/shadow, agent OS, UI stack, DESIGN.md, modular, GPU, AI-in-native-shell

## Evidence
- Strangler/shadow/canary discourse favors incremental route + rollback.
- Agent OS discourse: constitution + skills + worktrees + no hallucinated design.
- Qt/QML + native AI shells favored over Electron for performance shells; hybrid WebKit for panels only.
- CO bus + engine shared; UI greenfield only.

## Requested Action
1. Read knowledge §3–6; reply with **status** or comment on same thread: Option A (separate cmake `migx-agent` target) feasibility vs flag-only.
2. Sketch minimal scaffold: target name, link to engine libs, empty main.qml + DESIGN.md + Theme, launch smoke.
3. Recommend **first product module** after primitives: single-deck play/cue vs co-pilot chrome.
4. Note conflicts with current dual QML/skin work or OpenGL pin.
5. Do **not** implement full NextGen until owner picks Option A/B/C/D.

## Blockers
Owner packaging decision; ADR-004 still proposed.
