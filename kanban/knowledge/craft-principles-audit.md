---
id: craft-principles-audit
type: knowledge
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: /Users/gudjon/code/oz-platform/kanban/references/knowledge-base/14-engineering-craft-principles.md
---

# Engineering-Craft Principles — audit against the Migx pattern catalogue

Distills the transferable craft principles from reference doc 14 (the "legendary-dev" method:
Torvalds/Carmack/Ritchie/Dean/Hejlsberg), maps them against our 47-card catalogue (`P-01..P-32`,
`AP-01..AP-16`), and proposes a lean set of additive refinements. The reference is OZ-grounded
(Python/TS services); everything below is re-expressed for a C++/Qt6 real-time audio app. **Robotics/CV/
web-domain framings are dropped, not translated.**

Principle: *distill, don't clone.* Only gaps the 47 cards genuinely lack **and** that fit a real-time
audio engine are proposed. Most of doc 14 is already covered — the catalogue was built on the same
lineage.

## 1. Distilled craft principles (from doc 14)

Grouped by what they govern. `DC-CRAFT-0` is the founding gate; `1..7` are the per-change checklist.

**Measurement / honesty**
- **DC-CRAFT-0 — Honest measurement, never overclaim.** Measure before you claim; an honest scope-
  complete RED beats a fabricated green. Gates all seven — a principle "applied" but unmeasured is not
  applied.

**Complexity control**
- **DC-CRAFT-1 — Simplicity first.** Prefer the boring, obvious mechanism; delete the abstraction that
  earns less than its weight. Could a junior read it cold?
- **DC-CRAFT-2 — Eliminate special cases (Linus "good taste").** Restructure so the `if`/edge-case
  *disappears* into the normal path, rather than adding a per-case branch cluster.
- **DC-CRAFT-3 — Reduce cognitive load.** Flat over nested; explicit over magic; bounded function/file
  size; a reader holds < 5 things in their head.

**Structure**
- **DC-CRAFT-4 — Modularity with clean interfaces.** One module owns one concern behind a documented
  seam; testable/replaceable without touching neighbors.

**Robustness**
- **DC-CRAFT-5 — Reliability by design — assume failure.** Bad input / dead peer / race fails with a
  *classified* error, never a silent fallback; timeouts on external calls; asserts on invariants.

**Performance**
- **DC-CRAFT-6 — Pragmatic performance — profile first.** Optimize the proven hotspot only; don't let
  an abstraction hide a real cost.

**Longevity**
- **DC-CRAFT-7 — Long-term maintainability + reviewability.** Reads cleanly in a year; the PR is small,
  focused, self-describing — the diff tells its own story.

## 2. Coverage table

| Craft principle | Covered by | Verdict |
|---|---|---|
| DC-CRAFT-0 Honest measurement | P-01, P-03, P-08, P-09, P-18, AP-01, AP-11 | **Covered** (this is the catalogue's spine) |
| DC-CRAFT-1 Simplicity first | P-11 (refactor over layer); playbook "deletion test" | **Partial** — no card names "prefer the boring mechanism / delete the sub-weight abstraction" |
| DC-CRAFT-2 Eliminate special cases | — | **GAP** — nothing encodes "good taste": designing the edge into the normal path |
| DC-CRAFT-3 Reduce cognitive load | AP-15 (no magic tuning value → "explicit over magic") | **Partial** — function/file size + nesting depth uncovered (lint-shaped) |
| DC-CRAFT-4 Modularity / clean interfaces | P-06, P-07, P-16, P-28 (seams: single writer, single authority, lock-free handoff, DAO boundary) | **Covered** by domain-specific seam cards |
| DC-CRAFT-5 Reliability / classified error / no silent fallback | AP-16 (silent audio-error swallow — *audio path only*) | **Partial → GAP** — no general "fail classified, never silently fall back" for library/controller/soundio paths |
| DC-CRAFT-6 Profile first | P-03, P-14, P-18, P-25 | **Covered** |
| DC-CRAFT-7 Maintainability / reviewable PR | P-11, P-15 (trace before refactor) | **Partial** — "small, focused, self-describing PR" is process, not a code pattern |

## 3. Proposed additions (the high-value few)

### P-33 — `eliminate-the-special-case` (NEW — author now)
- **Statement:** When a change adds an `if`/branch for an edge case, first try to restructure the data
  or the normal path so the edge is handled *without* a branch; add the special case only when the
  restructure is genuinely more complex than the branch.
- **Domain:** `engine` (applies broadly, but the RT/DSP path is where it bites).
- **Encodes:** DC-CRAFT-2 (Linus "good taste"). Partially DC-CRAFT-1/3.
- **Why it fits Migx:** DSP/RT code is branch-sensitive — a per-buffer `if (isFirstFrame)` or
  `if (rate == 0)` cluster in `process()` costs cognitive load *and* pipeline predictability. The
  house-physics tell: absorb "zero rate", "no track loaded", "buffer boundary" into the normal read
  path (e.g. read from a silent/neutral buffer) instead of branching per callback. Real signal today:
  `src/engine/controls/cuecontrol.cpp` (2930 lines, 21 `else if`) and `loopingcontrol.cpp` (2176) are
  inherited upstream branch clusters — the card gives review a name for "was this edge designable-out?"
- **Related:** P-11, P-02. Pairs with (deferred) cognitive-load card.

### P-34 — `fail-classified-never-silent-fallback` (NEW — author now)
- **Statement:** Off the RT path, an operation that cannot meet its contract (bad input, missing
  device, failed migration, DB error) shall fail with a *classified, logged* error and propagate it —
  never substitute a silent default and continue as if it succeeded.
- **Domain:** `library` (also soundio/controllers; the non-RT reliability seam).
- **Encodes:** DC-CRAFT-5 (reliability by design, "no fallbacks").
- **Why it fits Migx:** `AP-16` already forbids *silently swallowing an audio error on the RT path*;
  it says nothing about the much larger non-RT surface — schema migrations (`src/database/`, `P-27`),
  DAO operations (`P-28`), soundio device open, controller mapping load. A migration that returns a
  silent default, or a DAO that eats a SQL error and returns an empty result, corrupts library state
  invisibly. This is the positive pattern for which `AP-16` is one RT-specific instance. Note: on the
  RT path itself, "classified error" means degrade-gracefully-and-signal (P-16), *not* throw/log —
  the card must scope itself to the non-RT boundary to avoid contradicting P-02.
- **Related:** AP-16 (its audio-path instance), P-27, P-28. Would warrant a paired `AP-17
  silent-fallback-masks-failure`, but hold that until the positive card exists (lean-catalogue rule).

### Refinement (no new card): broaden AP-16's framing
- `AP-16 silent-audio-error-swallow` currently reads as RT-only. Add a one-line cross-reference to the
  new `P-34` so review sees the general principle behind the audio-specific instance. **Do not** widen
  AP-16 itself — its RT scope is correct; P-34 carries the general case.

## 4. Codebase spot-check — visible craft signals

Grep/read pass under `src/`. The codebase is **generally disciplined**; findings are signals, not
crises:

- **Reliability is mostly honored.** 208 `DEBUG_ASSERT`/`VERIFY_OR_DEBUG_ASSERT` invariants in
  `src/engine/**` (DC-CRAFT-5 asserts-on-invariants is a lived habit). No empty or comment-only
  `catch{}` swallow found in `src/`. Audio-device error logging present (`src/soundio/`,
  `src/engine/`). → confirms P-34 is a *guard*, not a fix for existing rot.
- **Cognitive load / special cases (DC-CRAFT-2/3) — the one real signal.** Inherited upstream control
  files are large branch clusters: `src/engine/controls/cuecontrol.cpp:1` (2930 lines, 21 `else if`),
  `src/engine/controls/loopingcontrol.cpp:1` (2176), `src/engine/enginebuffer.cpp:1` (1679),
  `bpmcontrol.cpp:1` (1360). These predate Migx and aren't worth a rewrite dossier, but they are
  exactly what proposed **P-33** gives review a name to resist *when touched*. Worth a pattern: yes —
  as a forward guard on new edits, not a retro-cleanup mandate.
- **Nesting depth is fine.** Zero lines at ≥5 tab indents in `enginebuffer.cpp` — flat-over-nested
  (DC-CRAFT-3) is broadly respected in the hot path.
- **TODO/FIXME/HACK:** 80 in `src/engine/**/*.cpp` — typical for a mature fork; not a craft violation,
  no pattern warranted.

No principle is *visibly violated* badly enough to demand a corrective pattern beyond the two proposed;
the large-file signal is captured forward-looking by P-33.

## 5. Recommendation — author now vs defer

**Author now (2 cards + 1 refinement):**
- **P-33 eliminate-the-special-case** — genuine gap (DC-CRAFT-2 wholly uncovered), deep C++/DSP fit,
  gives review live vocabulary for the biggest existing signal (large control files). Highest ROI.
- **P-34 fail-classified-never-silent-fallback** — genuine gap (DC-CRAFT-5 covered only for the RT
  audio path); generalizes AP-16 to the library/DB/soundio surface where silent fallbacks corrupt
  state invisibly. Scope carefully to the *non-RT* boundary so it never contradicts P-02/P-16.
- **AP-16 cross-ref refinement** — one line pointing to P-34; do when P-34 lands.

**Defer (real but lower ROI / lint- or process-shaped):**
- **DC-CRAFT-1 simplicity / "delete the sub-weight abstraction"** — largely covered by P-11 + the
  playbook deletion test; a standalone card risks being generic/preachy. Revisit only if a real
  "speculative abstraction" regression recurs (the ≥2-occurrence bar).
- **DC-CRAFT-3 function/file-size + nesting bound** — mechanizable as a clang-tidy/review lint, not a
  judgment pattern. Better as a Phase-3 detector than a card. Defer to tooling.
- **DC-CRAFT-7 small-focused-PR** — process discipline (already in the playbook checklist), not a code
  pattern. No card.
- **AP-17 silent-fallback-masks-failure** — hold until P-34 exists, then add as its paired antipattern.

**Count of proposed additions: 2 new pattern cards (P-33, P-34) + 1 refinement (AP-16 cross-ref).**
Deferred/declined gaps: 4 (DC-CRAFT-1 card, DC-CRAFT-3 lint, DC-CRAFT-7, AP-17-for-now).
