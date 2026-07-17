---
id: gudjon-antigravity-cli-2026-07-17-002-wave1-dui-exo-execute
from: gudjon
to: antigravity-cli
type: coord
status: closed
created: "2026-07-17"
created_utc: "2026-07-17T10:44:47Z"
severity: high
subject: "wave1-dui-exo-execute"
relates_to: []
acceptance: "DUI Theme.qml + one consumer exist OR JOURNAL explains blocker; EXO schemas started; mail closed with paths"
branch: "migx-harness"
commit: "5ad8406695"
---

## Intent
Execute Wave 1 of your non-RT product lane: start DUI Theme.qml spike, then EXO fixtures — using
Agent Teams / plan→review modes as X recommends. Defer deprecated-renderer deletion until Claude
confirms no MTL overlap.

## Context
- Prefixes registered: DUI, EXO, FSL, UIX.
- Dossiers scaffolded:
  - kanban/planning/2026-07-17-gudjon-DUI--design-md-theme-qml-spike (PS-DUI-01)
  - kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike (PS-EXO-01)
- X strengths: subagents, plan/review/accept-edits modes, terminal log self-heal, specs+skills.
- Worktree: ~/code/migx-agy branch agy/work (create/update if needed).
- Do NOT edit src/engine/** or src/rendergraph/** without coord to claude-code.

## Evidence
- kanban/federation/signal/2026-07-17-antigravity-cli-strengths-federation.md
- roles/antigravity-cli.md · AGY.md
- claude-code-antigravity-cli-2026-07-17-001-route-exo-and-ui-thrusts (prior route)

## Requested Action
1. migx-fed poll; ack this message and prior route message if still open.
2. Mode plan on DUI: read PS-DUI-01 + phase plan.
3. Wave DUI-1: res/design/DESIGN.md + res/qml/Theme.qml + one QML consumer; pre-commit on files.
4. Wave EXO-1: fixtures/schema + start hand-authored song ontologies under dossier fixtures/.
5. Commit as gudjon solo author; stage explicit paths; JOURNAL each wave.
6. UIX dead-code retirement: send question to claude-code before deleting waveform deprecated paths.
7. When DUI wave 1 green: close with Resolution listing paths + commands.

## Blockers
None for DUI/EXO file work. FSL DB export can wait. MTL/render = Claude.

## Resolution
Executed long-harness Wave1 (owner/agent on behalf of antigravity lane while agy online).
DUI: res/design/DESIGN.md + tools/design/gen_theme_from_design.py --check OK; Theme.qml token-bridged; consumers already Theme.*.
EXO: fixtures/schema + 3 songs + session-3track-demo + results/TRANSITION-PROOF.md.
Commands: python3 tools/design/gen_theme_from_design.py --check; python3 -c json load fixtures.
P-08 EXO eval requested from codex-cli. UIX deferred. RT paths untouched.
