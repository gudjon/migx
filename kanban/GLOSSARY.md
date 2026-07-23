---
id: migx-glossary
type: doctrine
title: "Migx Glossary — the typed-ID system"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/AGENTS.md
  - kanban/planning/00-PORTFOLIO/prefix-registry.yaml
---

# Migx Glossary — Typed IDs

Load-bearing things carry a **typed ID** so they can be cited by `grep`, cross-linked, and
lint-checked. This file states the *rules* for IDs; the live catalogue of *which* IDs exist is the
files themselves (derive, don't restate — MG-3). Registered prefixes are immutable and live in
`kanban/planning/00-PORTFOLIO/prefix-registry.yaml`.

## Prefix families

| Prefix | Meaning | Home | Example |
|---|---|---|---|
| `P-NN` | **Pattern** — a validated, recommended approach. Immutable anchor ID. | `kanban/patterns/` | `P-03` |
| `AP-NN` | **Antipattern** — a named failure mode / "don't do this". | `kanban/patterns/` | `AP-02` |
| `ADR-NNN` | **Architecture Decision Record** — a decided, path-pinning choice (stronger than a pattern). | `kanban/architecture/decisions/` | `ADR-001` |
| `PS-{PFX}-NN` | **Problem Statement** — one machine-parseable spec unit inside a dossier. `{PFX}` = the dossier's registered prefix. | `<dossier>/00-FOUNDATION/` | `PS-ASI-01` |
| `EVD-NNNN` | **Evidence** — a benchmark/measurement record backing a claim. | dossier `results/` | `EVD-0001` |
| `initiative-{slug}` | **Initiative** — a thin *lateral* wrapper (hypothesis + one metric + one guardrail) pointing at the dossiers that execute it. NOT a unit of work — dossiers are (MG-5). No typed anchor; the filename slug is the id. | `kanban/initiatives/` | `initiative-apple-silicon` |
| `<pfx>` (3-letter) | **Dossier** key — the unit of work. Registered before first use. | `kanban/planning/` | `ASI`, `MTL` |
| `task-{slug}` | **Task** — a flat backlog item not owned by a live dossier. Filename is the ID. | `kanban/tasks/` | `task-audit-rt-allocs` |
| `TR-{slug}` | **Trigger** — a cadence/event firing row. | `kanban/triggers/registry.yaml` | `TR-nightly-dream` |
| `BRND-*` | **Branding** — pillars, DIY steps, mistakes (process anchors). Not a dossier prefix. | `kanban/playbook/branding/` | `BRND-P1`, `BRND-DIY-1` |
| `DC-PDCL-*` | **Product discovery / customer leadership** concepts (when cited). | `kanban/knowledge/product-discovery-customer-leadership-migx.md` | (see that file) |

## Rules

1. **Anchor vs. semantic ID.** `P-NN`/`AP-NN` are *immutable anchors* — use them in code comments,
   commits, and cross-references. A human-readable name (e.g. "single-writer") is a display alias
   only; never invent your own anchor number, and never cite by name in code (that recreates a dual
   source of truth).
2. **Register before use.** A new dossier/initiative prefix goes into `prefix-registry.yaml` before
   any file uses it. Lint enforces coherence.
3. **No prose references.** Cite `P-07`, not "the closed-loop pattern". Prose references are banned
   because they can't be lint-checked and drift silently (MG-3).
4. **Cross-reference by edge fields.** Patterns/PSes/tasks link via frontmatter edges
   (`resolves:`, `risks:`, `related:`, `depends_on:`), not prose. Edges are bidirectional-lint-checked.
5. **Numbers never reused.** A retired `P-NN` stays retired (status `superseded`), its number burned.
   History lives in git; the ID stays stable so old commits keep resolving.

## EARS (for Problem Statements)

Every `PS-*` body opens with one **EARS** sentence, classed in frontmatter (`ears_class`):
`ubiquitous` (always) · `state-driven` (While <state>) · `event-driven` (When <trigger>) ·
`optional` (Where <feature>) · `unwanted` (If <condition>, then) · `complex` (combination).
The `acceptance:` block is the machine-consumable evaluation contract — a numeric threshold plus the
benchmark/test/query that checks it. That contract is what closes the loop (MG-1).
