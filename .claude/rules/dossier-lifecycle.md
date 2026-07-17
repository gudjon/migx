---
description: "A dossier is a single-use sprint backlog: write → execute → seal → read-only history"
---

# Rule — dossier lifecycle

A dossier is a **single-use sprint**: `scaffold → foundation → research → architecture → execution →
seal (91-LOOP-CLOSURE) → read-only history`. Once sealed it is a dated snapshot of THEN.

## Harvest at closure (before `sealed: true`)
Durable facts must **re-home into the living layer** first — a `P-NN` card, an `ADR`, an in-code
annotation, a `src/**/AGENTS.md`, or the `architecture/` map. If a learning only lives in the dossier,
it dies with the seal. The `91-LOOP-CLOSURE` "What feeds back" table must show each learning landed
*this loop*, not "queued."

## Living docs never depend on a dossier
Code, patterns, ADRs, and `architecture/` cards may mention a `kanban/planning/**` path only as prose
provenance — never as a `defers_to` dependency. Current truth lives in the living layer; the dossier is
history.

## Never route new work into an old dossier
Open-but-dormant counts as dead. New work has three valid homes: an **active** dossier that owns the
scope, a **new** dossier, or the system of record (a pattern/ADR/task). Routing a fix off a sealed
snapshot is the "dead-dossier routing" breakage (playbook ch.02).

## After sealing
The only allowed edit is an append-only dated `enriched:` note. Do not reopen a sealed dossier to add
work — open a successor and link it.
