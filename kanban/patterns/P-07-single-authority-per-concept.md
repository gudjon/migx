---
id: P-07
type: pattern
title: "One canonical home per concept; every other view is derived"
status: active
severity: MUST
domain: ssot
related: [P-06, P-13, AP-04]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-07 — One canonical home per concept; every other view is derived

## Statement
Every load-bearing fact — a value, a rule, a schema, a mapping — has exactly one canonical home. Every
other place it appears is *derived* from that home (generated, linked, or read at runtime), never a
hand-maintained second copy.

## Why
This is MG-3, generalized past ControlObject (`P-06` is the same rule applied to the engine bus). Two
hand-maintained copies of a fact are two sources of truth: they drift, and the reader can't tell which
is current. The catalogue itself is built this way — the pattern *card* is the SSoT, the `pat-*` skill
only points at it (`P-05`); the glossary states ID *rules* and derives the live list from the files.
A single authority makes a fact citable, lint-checkable, and safe to change in one place.

## How to apply
- Decide the one home when the concept is introduced; make every other appearance derive from it
  (codegen, a link, a runtime read).
- Prefer generating derived views over writing them: an index generated from the files can't drift; an
  index typed by hand will.
- If a fact "needs" to live in two places, that's a smell — pick the home and derive the other, or
  introduce an explicit projection step that's re-run, not re-typed.
- A current-state claim about the fact carries a verify command so a reader can confirm it (`P-13`).

## Example — wrong
> A tuning constant lives in C++ *and* is restated in an AGENTS.md doc. The code changes; the doc now
> lies, and nobody notices (`AP-04`).

## Example — right
> The value lives once in its config/SSoT; the doc links to it (or a script derives the doc section
> from it). Changing the value updates every view.

## Detection
Review: the same fact typed in two maintainable places; a doc that *restates* rather than *links* a
value (`AP-04`). Phase-3 lint flags duplicated canonical values.

## Cross-references
The engine-bus instance is `P-06`; the skill/card instance is `P-05`. Its violation is `AP-04`;
verify-before-trust is `P-13`.
