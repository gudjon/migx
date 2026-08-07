---
id: P-34
type: pattern
title: "Fail classified — never a silent fallback (off the RT path)"
status: active
severity: MUST
domain: library
related: [AP-16, P-01, AP-06]
created: "2026-07-17"
lastUpdated: "2026-08-07"
---

# P-34 — Fail classified — never a silent fallback (off the RT path)

## Statement
Outside the real-time audio path, an error is surfaced as a **classified failure** — logged with its
cause and recorded or propagated to a place a human or an agent can see it — never silently swallowed or
papered over with a default value that pretends nothing went wrong.

## Scope (read this — it must not contradict RT safety)
This governs the **non-RT surface**: library/DB (`arch-library-db`), device/soundio *setup*
(`arch-audio-io`), track decode (`arch-sources-decode`), network, and controllers — **and the harness
itself**: lints, gates, CI and the scripts they call. The harness was originally read as out of scope
(this list named only product surfaces), and that reading is precisely how the 2026-08-07 instance below
survived: the rule was known, but nobody applied it to a linter. A tool that decides whether code is
correct is exactly where a silent fallback does the most damage, because its output is *trusted*. On the **RT audio
thread** you cannot log, allocate, or throw — there you use the RT-safe degradation of `P-02`/`P-16`, and
`AP-16` guards silent-swallow on the audio-adjacent path. This pattern extends that discipline to
everything that is *not* on the callback deadline.

## Why
A silent fallback hides degradation: a track that fails to load and returns silence, a DB error that
resets a setting to default, a decode error that yields an empty buffer — the user (a DJ mid-set) sees
weird behavior with no cause. A classified failure closes the loop (`P-01`): the error is captured, so it
can be surfaced, retried, or fixed. "Return a default on error" is the `AP-06` open-loop in disguise.

## How to apply
- `catch` → **classify** (what failed, why) → **record** (log + surface to the UI/library state / return
  a typed error) → decide (retry / skip-with-notice), not a bare `catch { /* continue */ }`.
- No default-value-on-error without recording that the error happened.
- For a DJ-facing failure (track won't load/analyze), make it *visible*, not silent.

## Example — wrong
```cpp
try { track = load(path); } catch (...) { track = Track(); }   // silent — the DJ gets an empty track
```

## Example — right
```cpp
auto r = load(path);
if (!r) { qWarning() << "load failed:" << path << r.error(); markTrackUnavailable(path, r.error()); }
```

## Instance — the harness (2026-08-07)
`_kanban_lint.parse_yaml_lite()` used PyYAML "when available" and otherwise fell back to the hand-rolled
frontmatter parser. That parser cannot read nested lists-of-mappings, so `prefix-registry.yaml` parsed to
`{}` — indistinguishable from *"no prefixes are registered."* The same commit therefore got **opposite
verdicts** depending on whether a library happened to be installed: red locally-green, and worse,
`lint-federation-messages` resolved peers the same way, so an empty parse made it pass **vacuously** —
green while checking nothing.

The tell is the shape, not the domain: a fallback that returns the same value as a legitimate empty
result cannot be distinguished from success. Fixed by requiring the parser and raising an actionable
error; a malformed document now raises too, rather than parsing as empty. **A gate that cannot fail is
not a gate** — see also `just verify`, which refuses to run when `mixxx-test` is missing rather than
skipping ctest and reporting green.

## Detection
Review: bare `catch { }` that continues; default-on-error with no logging/record. The engine spot-check
(craft audit) found the audio path clean; this pattern watches the library/DB/decode surface.
In the harness, ask of any gate: **what would make this report green while checking nothing?** If a
missing dependency, an empty parse, or an absent binary is one of the answers, it is this defect.

## Cross-references
Generalizes `AP-16` (silent-audio-error-swallow) to the non-RT surface; serves `P-01`; the failure mode
is `AP-06`. Encodes the classified-error craft principle (`kanban/knowledge/craft-principles-audit.md`).
