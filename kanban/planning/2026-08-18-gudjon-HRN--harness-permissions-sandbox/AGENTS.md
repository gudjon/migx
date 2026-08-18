---
id: dossier-HRN
slug: 2026-08-18-gudjon-HRN--harness-permissions-sandbox
type: dossier
prefix: HRN
title: "The harness — permission classes, workspace boundary, transcript resume"
classification: none
phase: foundation
sealed: false
status_note: "Nothing exists yet: every command can do anything, there is no workspace boundary, and a night cannot be resumed."
completion-criteria:
  - "Every command in system.capabilities carries a permission class"
  - "A write outside the workspace is refused, not warned"
  - "deck.* cannot be auto-approved while a session is live"
  - "migx --resume reconstructs a night from _session.jsonl"
facilitator: gudjon
initiative: initiative-swift-tui-workstation
authored_by: claude-code
authored_kind: agent
triggered_by: "ADR-011 accepted; HRN is the only program piece that does not exist at all, and it needs neither the music volume nor audio"
created: "2026-08-18"
lastUpdated: "2026-08-18"
last_audited: "2026-08-18"
---

# HRN — the harness

The product is the harness, not the model. Permissions, workspace boundary, transcript, tool dispatch.

**Why first:** it is the only piece of the program that does not exist *at all*. There is no permission
class, no workspace boundary, no sandbox — `library.ingest` and a hypothetical `deck.load` are equally
unguarded. That is the gap an agent-operated product cannot ship with. It also needs neither the music
volume (currently unmounted) nor audio, so it is the one thing that can start today.

**Closed loop:** an agent or a DJ issues a tool call → the harness classifies it → policy admits,
gates, or refuses → the result and the decision both land in the transcript → `--resume` replays it.

Problem statement: `00-FOUNDATION/PS-HRN-01.md`. Waves: `90-EXECUTION/00-PHASE-PLAN.md`.
