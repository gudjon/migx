---
id: AP-15
type: antipattern
title: "Hardcoded tuning or mapping value"
status: active
severity: MUST-NOT
domain: controllers
related: [P-29, P-30, P-27, P-07]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# AP-15 — Hardcoded tuning or mapping value

## What it looks like
A value that has a config/data SSoT is baked into C++ as a literal instead: a controller's
message/note number or LED value in engine code rather than `res/controllers/`, a DSP tuning constant
inline instead of in its config, a schema column/shape written in a DAO instead of `res/schema.xml`.

## Why it's harmful
It forks the source of truth (MG-3, `P-07`): the value now lives in two worlds, or in the wrong one
entirely, so the config is no longer authoritative and users/agents can't change the behavior where
they'd expect to. A hardcoded controller value can't be overridden without a recompile (`P-29`); a
hardcoded schema shape bypasses versioned migration and risks the user's library (`P-27`); a hardcoded
tuning constant makes perf work edit C++ instead of a bounded config. Each one is a special case that
accretes.

## What to do instead
- Put the value in its data home: controller wiring/constants in `res/controllers/` (`P-29`), schema
  in `res/schema.xml` (`P-27`), tuning constants in their config SSoT (`P-07`).
- Controller scripts read those constants and reach the engine via ControlObject (`P-30`), rather than
  embedding magic numbers.
- If there's no config home yet, create one — don't inline the literal as the de-facto SSoT.

## Detection
Review: MIDI/HID status/note/LED literals or DSP tuning constants as C++ literals that duplicate or
belong in `res/controllers/`, `res/schema.xml`, or a config file; a "just this one number" inline
constant with a canonical home elsewhere.

## Cross-references
Violates `P-07`; the specific homes are `P-29` (controllers), `P-27` (schema); scripts should route via
`P-30`.
