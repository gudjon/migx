---
id: P-05
type: pattern
title: "A pattern skill cites its pattern, never restates it"
status: active
severity: MUST
domain: harness
related: [P-01]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-05 — A pattern skill cites its pattern, never restates it

## Statement
A `.claude/skills/pat-NN-*` skill is the operational auto-load trigger for a pattern; its body shall
**point to** the `kanban/patterns/P-NN-*.md` card (via `metadata.cites_patterns` + a link) and shall
not copy the pattern's text.

## Why
Two copies of a rule is two sources of truth (MG-3); they drift, and the reader can't tell which is
current. The pattern card is the SSoT of *what*; the skill is only the *when-to-surface-it* trigger.
Keeping the skill body thin also keeps it cheap to auto-load into context.

## How to apply
- Skill frontmatter: `metadata.cites_patterns: ["P-NN"]`, a `description:` that fires on the relevant
  code/context, and `defers_to: [kanban/patterns/P-NN-....md]`.
- Skill body: 2–4 lines — "This surfaces `P-NN`. Read the card." Nothing more.

## Detection
Phase-3 lint `verify-skill-defers-not-restates.py`: a `pat-*` skill whose body duplicates card prose,
or lacks `cites_patterns`, fails.

## Cross-references
Instance of MG-3 applied to the skill/pattern boundary.
