---
id: AP-04
type: antipattern
title: "A doc restates a value that has a canonical home"
status: active
severity: MUST-NOT
domain: ssot
related: [P-07, P-13, P-05]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-04 — A doc restates a value that has a canonical home

## What it looks like
A doc, skill, AGENTS.md, or comment hand-copies a value, rule, or list that already has a canonical
home in code or config — a tuning constant, a schema version, a file list, a `[Group],key` — instead
of linking to or deriving from it.

## Why it's harmful
Now the fact has two maintainable sources (MG-3): the copy drifts the moment the original changes, and
the drift is silent — nobody diffs prose against code. A reader who trusts the doc builds on a stale
premise, and an agent that acts on it acts wrong. It's the same failure `P-05` names at the
skill/pattern boundary, generalized to any doc.

## What to do instead
- Give the fact one canonical home and make the doc *link* to it, or *derive* the doc section from it
  (codegen, an injected `` !`cmd` ``) rather than restating it (`P-07`).
- If a current-state fact must appear in prose, ship it with a verify command so it's self-checking
  (`P-13`).
- For `pat-*` skills specifically: cite the card, never copy it (`P-05`).

## Detection
Review: the same value typed in a doc and in code/config; a doc list that duplicates a directory or a
schema. Phase-3 lint flags duplicated canonical values and restating skills.

## Cross-references
Violates `P-07`; the skill/pattern instance is `P-05`; the fix for unavoidable current-state prose is
`P-13`.
