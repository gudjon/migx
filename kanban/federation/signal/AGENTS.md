---
id: federation-signal
type: doctrine
title: "signal/ — Grok field-intel briefs (not work orders)"
status: active
defers_to:
  - kanban/federation/FEDERATION.md
  - kanban/federation/roles/grok-signal.md
---

# signal/

Append-only **intelligence briefs** from the `grok-signal` peer. Template: [`_TEMPLATE.md`](_TEMPLATE.md).

- Writer: `grok-signal` (default)
- Consumers: Claude Code, Gudjon, later agents
- Promotion to work: only via `migx-fed send --type signal-handoff` (see FEDERATION.md)

Do not treat a brief as a ticket. Do not restate house physics here — cite `P-NN` / ADRs when assessing
relevance.
