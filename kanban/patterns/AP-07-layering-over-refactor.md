---
id: AP-07
type: antipattern
title: "Layering over refactor"
status: active
severity: MUST-NOT
domain: harness
related: [P-11, P-15, P-12]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-07 — Layering over refactor

## What it looks like
A `_v2` / `New*` / parallel implementation is added *beside* the canonical one "to clean up later,"
leaving two live paths for one behavior. Some callers use the old one, some the new; nobody deletes
the old.

## Why it's harmful
Two implementations of one behavior are two sources of truth (MG-3): two sets of bugs, and every
call site is a coin flip about which is authoritative. "Later" rarely comes, so the layer calcifies and
the next agent can't tell which path is live. In the engine a stale second path can still be reachable
from `process()` and silently regress house physics. The codebase accretes instead of evolving.

## What to do instead
- Change in place, or add-migrate-all-callers-and-delete in the *same* change (`P-11`) — every add
  deletes.
- Trace the callers first (`P-15`) so you know the full migration scope.
- If full migration genuinely must wait, freeze the old path as a golden (`P-12`) and scope the
  remaining migration explicitly — don't leave two unlabeled live paths.

## Detection
Review: a new `*_v2`/`*New`/parallel symbol added without deleting its predecessor. Grep the old
symbol after the change — nonzero remaining callers with a new path present is the smell.

## Cross-references
Violates `P-11`; skips the caller trace `P-15`; the disciplined deferral is `P-12`.
