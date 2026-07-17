---
id: craft-principles-pattern-audit
type: task
title: "Audit Migx codebase + pattern catalogue against oz-platform engineering-craft principles"
status: done
owner: gudjon
priority: medium
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon request 2026-07-17 — systematic check vs oz-platform kanban/references/knowledge-base/14-engineering-craft-principles.md; update kanban/patterns accordingly"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A findings note (kanban/knowledge/craft-principles-audit.md) that:
  - distills the transferable engineering-craft principles from
    /Users/gudjon/code/oz-platform/kanban/references/knowledge-base/14-engineering-craft-principles.md,
  - cross-checks each against our existing 47-card catalogue (kanban/patterns/) — which principles are
    already covered (by P-NN/AP-NN), which are gaps,
  - proposes concrete additions/refinements: new P-NN/AP-NN candidates (with id, title, statement,
    domain) OR edits to existing cards, distilled to Migx's C++/Qt/RT context (not OZ domain),
  - flags any craft principle our CODEBASE visibly violates (spot-check, file:line) worth a pattern,
  - keeps the recommendation lean (distill-don't-clone) — only genuinely additive principles.
---

# Craft-principles pattern audit

Check Migx against oz-platform's engineering-craft principles and refine `kanban/patterns/` where it
compounds. Distill-don't-clone; only add what our 47-card catalogue genuinely lacks and that fits a
C++/Qt real-time audio app. Produces a proposal; the actual card authoring follows on approval.
