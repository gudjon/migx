---
id: migx-knowledge-agents
type: doctrine
title: "kanban/knowledge/ — technical and product research SSoTs"
status: active
owner: gudjon
created: "2026-07-23"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/AGENTS.md
  - .claude/rules/single-source-of-truth.md
  - kanban/federation/FEDERATION.md
---

# knowledge/ — what lives here

`kanban/knowledge/` is the home for durable technical/product research and synthesis that is useful
across more than one prompt, agent, task, or dossier.

Use it for:

- research briefs that define the current model for a topic, feature, architecture option, or product
  bet before implementation starts
- product/technical SSoTs that several artifacts cite, such as NextGen mode routing, community signal
  sourcing, migration method, co-pilot scoring policy, or on-beat PLAY research
- reconciled synthesis from federation signals once the signal is worth preserving beyond a scout note

Do not use it for:

- customer evidence captures; those live in `kanban/discovery/`
- execution plans, daily logs, evidence records, or closure; those live in a dossier under
  `kanban/planning/`
- durable decisions that pin a path; those live in `kanban/architecture/decisions/` as ADRs
- recurring implementation rules or failure modes; those live in `kanban/patterns/`
- peer handoffs or field-intel breadcrumbs; those live in `kanban/federation/`

## Routing Rule

If the artifact answers "what do we currently believe or know about this topic?", it belongs here.
If it answers "what are we building in this 1-4 day loop?", open or update a planning dossier.
If it answers "what did a customer actually do?", put it in discovery.
If it answers "what has the repo decided?", write or amend an ADR.

Example: `research-onbeat-play-phase-snap.md` belongs here while it is research. A later SmartPlay /
on-beat PLAY implementation should scaffold a dossier and cite that research file instead of copying it.

## SSoT Discipline

- One topic has one primary knowledge file. A second file on the same topic must `defers_to:` the
  primary file and narrow itself to a distinct lane.
- Signal briefs may point here, but signals are not authoritative once a knowledge SSoT exists.
- A knowledge file may have `status: research`, `design`, or `active`, but that status does not mean
  implementation is underway. Implementation status lives in dossiers, tasks, code, and git.
- Keep source lists and provenance in the knowledge file when they explain evidence quality. Do not
  spread the same source list into signals, dossiers, and tasks.
- Promote work from knowledge by creating a task, ADR, dossier, or federation message with acceptance.
  Do not treat a knowledge file itself as a ticket.

## Minimum Frontmatter

```yaml
---
id: <stable-slug>
type: knowledge
title: "<reader-facing title>"
status: research | design | active
owner: gudjon
authored_by: <human-or-agent>
created: "YYYY-MM-DD"
lastUpdated: "YYYY-MM-DD"
defers_to: []
related: []
sources: []
---
```
