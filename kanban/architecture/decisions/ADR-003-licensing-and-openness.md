---
id: ADR-003
type: decision
title: "Licensing operating model — MIT-equivalent (Cursor path); proprietary product allowed"
status: accepted
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
related: [ADR-002, ADR-005, strategy-current, initiative-ai-djing-product]
supersedes_note: >
  Earlier draft of this ADR treated Mixxx as hard GPLv2 and blocked closed binary distribution.
  Owner direction 2026-07-17: work as if the base is MIT (Cursor/VS Code model). Product + agent
  decisions follow that model.
note: >
  Product/architecture operating model for Migx agents and strategy. Not a substitute for counsel
  on shipping day. Attribution to upstream Mixxx authors remains required practice.
---

# ADR-003 — MIT-equivalent operating model (Cursor path)

## Context
Migx aims to **replicate Cursor’s success**: fork a mature OSS base, ship a **proprietary product**,
and embed closed AI deeply (not only as an arm’s-length open-core service).

Cursor could do that because **Code-OSS is MIT**. Historically this ADR argued Mixxx’s GPLv2 made a
closed app impossible. **Owner direction (2026-07-17): imagine the base is MIT and work that way** —
product architecture, moat placement, and agent guidance follow the **Cursor/MIT path**, not the
open-core-only path.

## Decision (accepted for product work)

### D1 — Operating license model = MIT-equivalent
For **all Migx product, architecture, and agent decisions**, treat the forked instrument base as
**MIT-style permissive**:

| Capability | Under this model |
|---|---|
| Closed / proprietary **app binary** | ✅ Allowed (like Cursor) |
| Proprietary AI **in-process** with the app | ✅ Allowed |
| Public early development | ✅ Allowed (phase choice) |
| Later private / org-owned under agora | ✅ Allowed |
| Keep upstream author attribution | ✅ Required practice |

Agents **must not** refuse in-process Intelligence, closed distribution designs, or proprietary
modules solely because “Mixxx was GPL.” That constraint is **out of force** for planning under this ADR.

### D2 — Attribution & heritage still load-bearing
- Credit upstream Mixxx authors and Gudjon (`kanban/AUTHORS.md`).  
- Hard fork (ADR-002) still holds: no obligation to track upstream.  
- Do not erase heritage comments or author history without cause.

### D3 — Product openness is a *strategy* choice, not a copyleft force
- **Early:** public repo on `gudjon/migx` is fine.  
- **Later:** home under [`agora`](https://github.com/orgs/agora); may go private for product velocity.  
- **Open-core** remains an *optional* go-to-market tactic, not a legal requirement under this model.

### D4 — Secrets & proprietary IP hygiene
Even under MIT-equivalent planning: do not commit API keys, customer data, or model weights to a
public tree. Proprietary Intelligence source may live in-repo (private later) or a private sibling
under agora.

### D5 — On-disk `LICENSE` file
The tree may still contain historical Mixxx license text until an explicit **license-file / notice
cleanup** pass. That cleanup is a **separate owner task**, not a blocker for architecture. **While
working, agents follow this ADR’s MIT operating model**, not GPLv2 open-core constraints.

## What this unlocks (vs old draft)

| Old (GPL-forced) posture | New (MIT operating model) |
|---|---|
| Closed DAW binary ❌ | Closed DAW binary ✅ |
| AI must be arm’s-length only | AI may be **in-process** + cloud ✅ |
| Moat only in separate service | Moat in **app + AI + cloud** ✅ |
| Open-core mandatory | Open-core optional |

Architecture detail: **ADR-005** (revised for full Cursor stack).

## Consequences
- Strategy and agents design like **Cursor on VS Code**, not like “GPL DAW + side service only.”  
- ADR-005 Layer C may live in-process; separate process remains a *deployment* option, not a legal wall.  
- Freemium / Pro / privacy mode apply to the **product**, including the app.  
- A future owner/counsel pass may still align `LICENSE` notices with the operating model before
  commercial ship — out of band from day-to-day engineering.

## Status
**Accepted** for product and agent operating decisions (owner direction 2026-07-17).
