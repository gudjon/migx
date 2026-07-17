---
id: migx-patterns-catalogue
type: doctrine
title: "Pattern & antipattern catalogue — format and conventions"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/GLOSSARY.md
  - kanban/AGENTS.md
---

# Pattern & Antipattern Catalogue

The compounding memory of *how we build Migx*. A **pattern** (`P-NN`) is a validated, recommended
approach; an **antipattern** (`AP-NN`) is a named failure mode. Cite them by **anchor ID** in code
comments, commit messages, dossier decisions, and PS `resolves:`/`risks:` edges — never by prose
name (MG-3). The `pat-NN-*` skills in `.claude/skills/` are the auto-load triggers that *point* to a
pattern; they never restate it (P-05).

## When to add one

- A design decision recurs across ≥2 dossiers/PRs → it's a pattern. Write it once, cite it forever.
- A mistake gets made ≥2 times (or once, expensively) → it's an antipattern. Name it so review can
  catch it by ID.
- A one-off, path-pinning decision that forecloses alternatives → that's an **ADR**
  (`kanban/architecture/decisions/`), not a pattern. A pattern *recommends*; an ADR *decides*.

## File format

One file per pattern: `P-NN-<kebab-slug>.md` / `AP-NN-<kebab-slug>.md`. Numbers are immutable and
never reused (GLOSSARY). Frontmatter + body:

```yaml
---
id: P-NN
type: pattern            # pattern | antipattern
title: "<imperative one-liner>"
status: active           # active | superseded
severity: SHOULD         # MUST | SHOULD | MAY   (antipattern: MUST-NOT)
domain: <engine|waveform|gpu|build|harness|library|...>
related: []              # [P-NN, AP-NN] cousins
created: "YYYY-MM-DD"
lastUpdated: "YYYY-MM-DD"
---
```

Body sections: **Statement** (EARS-shaped where it fits) · **Why** · **How to apply** ·
**Example — wrong** / **Example — right** · **Detection** (how a lint/review/benchmark catches a
violation) · **Cross-references** (by ID).

## Index

<!-- pattern-index:start -->
| ID | Title | Domain |
|---|---|---|
| P-01 | Name the closed loop before you ship | harness |
| P-02 | Never allocate or lock on the real-time audio thread | engine |
| P-03 | A performance claim needs a benchmark contract | harness |
| P-05 | A pattern skill cites its pattern, never restates it | harness |
| P-06 | Each ControlObject has a single writer | ssot |
| P-07 | One canonical home per concept; every other view is derived | ssot |
| P-08 | The author of a change does not grade it | harness |
| P-09 | Acceptance criteria are measurable, runnable, and frozen at creation | harness |
| P-10 | Promote an audio-behaviour change offline → shadow → live | engine |
| P-11 | Change in place or migrate-all-callers-and-delete; never add a _v2 beside | harness |
| P-12 | Freeze a golden of retired code before deleting it | testing |
| P-13 | Every current-state claim carries an inline verify command | harness |
| P-14 | Prove the candidate beats the current path before you fix | engine |
| P-15 | Trace the affected call paths file:line before touching a subsystem | harness |
| P-16 | GUI↔engine data crosses via a lock-free handoff | engine |
| P-17 | Object lifetime happens off the real-time thread | engine |
| P-18 | Performance gates assert the tail, not the mean | engine |
| P-19 | A QObject gets a parent before its parented_ptr destructs | qt-ownership |
| P-20 | Respect QObject thread affinity; the RT thread never touches a QObject | qt-ownership |
| P-21 | GPU/waveform work never gates the audio callback deadline | gpu |
| P-22 | Waveform data stays in GPU buffers across frames | gpu |
| P-23 | Redraw on the display clock, never the audio buffer period | gpu |
| P-24 | Build native arm64 with tuned flags for perf work | build |
| P-25 | Pin the benchmark baseline to a commit and recorded hardware | build |
| P-26 | Emit compile_commands.json for clangd and agents | build |
| P-27 | SQLite schema changes go through forward-only versioned migrations | library |
| P-28 | All library DB access goes through the typed DAO layer | library |
| P-29 | MIDI/HID mappings live in declarative data, not C++ | controllers |
| P-30 | Controller scripts reach the engine only via ControlObject | controllers |
| P-31 | GoogleTest cases are structured GIVEN / WHEN / THEN | testing |
| P-32 | Engine tests assert house physics: zero RT allocations and TSan-clean | testing |
| P-33 | Eliminate the special case, don't just handle it | engine |
| P-34 | Fail classified — never a silent fallback (off the RT path) | library |
| AP-01 | Green-over-red closure | harness |
| AP-02 | Speedup that regresses house physics | engine |
| AP-03 | Second writer on a ControlObject | ssot |
| AP-04 | A doc restates a value that has a canonical home | ssot |
| AP-05 | The author grades their own change | harness |
| AP-06 | Open-loop promotion | harness |
| AP-07 | Layering over refactor | harness |
| AP-08 | Stale binary after a source edit | build |
| AP-09 | Benchmark on a moving main | build |
| AP-10 | Tautological green | testing |
| AP-11 | Mean hides the underrun | engine |
| AP-12 | GPU↔CPU copy in the render hot path | gpu |
| AP-13 | QObject without a parent | qt-ownership |
| AP-14 | RT thread touches GUI or blocks | engine |
| AP-15 | Hardcoded tuning or mapping value | controllers |
| AP-16 | Silent audio-error swallow | engine |
<!-- pattern-index:end -->

*Full planned catalogue (P-06..P-32, AP-03..AP-16 + `pat-*` skills): `PATTERN-CATALOGUE-PLAN.md`.
Keep this index in sync when adding files — or derive it with `kanban/scripts/gen-pattern-index.py`
in Phase 3.*
