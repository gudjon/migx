---
id: migx-pattern-catalogue-plan
type: plan
title: "Pattern & antipattern catalogue — buildout plan"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/patterns/AGENTS.md
  - kanban/patterns/P-05-pat-skill-cites-not-restates.md
---

# Pattern & Antipattern Catalogue — Buildout Plan

Distilled from the reference catalogue (~340 cards): keep the **engineering-discipline core**
re-expressed in Migx's vocabulary (ControlObject, parented_ptr, RT callback, rendergraph/Metal, DAO,
controller JS, ctest/benchmark); drop everything robotics-domain. Existing seeds: P-01, P-02, P-03,
P-05, AP-01, AP-02 (P-04 reserved/unused). New patterns extend from **P-06**, antipatterns from **AP-03**.

Card format = the tight Migx seed shape (`kanban/patterns/AGENTS.md`), NOT the reference's heavier
provenance machinery.

## Patterns P-06..P-32

| ID | Title | Statement (1-line) | Domain |
|---|---|---|---|
| P-06 | controlobject-single-writer | Each `[Group],key` has exactly one writer; others read via ControlProxy. | ssot/engine |
| P-07 | single-authority-per-concept | One canonical home per concept; other views derived, never restated. | ssot |
| P-08 | generator-is-not-evaluator | The author of a change doesn't grade it; an independent evaluator runs the P-09 contract. | harness |
| P-09 | evaluation-contract | Acceptance criteria measurable · runnable · bounded, frozen at creation. | harness/testing |
| P-10 | twin-shadow-live-promotion | Audio-behaviour change: offline-bench → shadow (not driving audio) → live. | harness/engine |
| P-11 | refactor-over-layer | Change in place or migrate-all-callers+delete; never a `_v2` beside. Every add deletes. | harness |
| P-12 | freeze-retired-before-delete | Commit a frozen golden (measured fidelity) before deleting code a differential proves against. | testing |
| P-13 | verify-before-trusting-a-rule | Every current-state doc claim carries an inline verify command; confirm before acting. | harness |
| P-14 | proof-before-fix-bench | Before an RT/DSP fix, an offline bench on real signal proves the candidate beats the current path. | engine/harness |
| P-15 | trace-before-refactor | Trace affected call paths file:line before touching an engine subsystem. | harness |
| P-16 | lock-free-rt-handoff | GUI↔engine data crosses via SPSC ring / atomic double-buffer / ControlObject (`util/fifo.h`), never a mutex. | engine |
| P-17 | object-lifetime-off-the-rt-thread | Create/destroy engine objects on GUI/worker; hand to RT via lock-free swap — never new/delete on the callback. | qt-ownership/engine |
| P-18 | p99-not-mean-for-perf | Perf gates assert tail latency (p99/max) + zero underruns, not mean throughput. | engine/testing |
| P-19 | parent-before-parented_ptr | A make_parented/QObject acquires a valid parent before its parented_ptr destructs. | qt-ownership |
| P-20 | qobject-thread-affinity | A QObject lives on its creating thread; cross-thread via queued signals; RT never mutates/receives-sync a QObject. | qt-ownership/engine |
| P-21 | metal-offload-must-not-gate-audio | GPU/waveform work off the audio thread; GPU latency never blocks the callback deadline. | gpu/metal |
| P-22 | zero-copy-gpu-waveform | Waveform data stays in GPU-accessible buffers across frames; no per-frame CPU round-trip. | gpu/metal |
| P-23 | render-on-display-clock-not-audio-clock | Visual redraw driven by display refresh/guitick/VisualPlayPosition, decoupled from the buffer period. | gpu/metal |
| P-24 | arm64-native-build-flags | Build native arm64 (Accelerate/vDSP available, `-mcpu` tuned); never x86_64/Rosetta for perf. | build |
| P-25 | pin-the-benchmark-baseline | Pin baseline to commit + recorded HW; measure deltas against it, never a moving main. | build/harness |
| P-26 | compile-commands-for-clangd | Emit compile_commands.json (`CMAKE_EXPORT_COMPILE_COMMANDS=ON`) for clangd + agents. (missing today) | build |
| P-27 | versioned-db-schema-migration | SQLite schema changes go through forward-only versioned steps (schema.xml), not ad-hoc ALTER. | library/db |
| P-28 | dao-is-the-db-boundary | All library DB access via the `dao/` typed layer; no raw SQL scattered across callers. | library/db |
| P-29 | controller-mapping-is-data | MIDI/HID mappings live in declarative XML/JS, not hardcoded C++. | controllers |
| P-30 | controller-script-talks-via-controlobject | Controller JS on its own thread reaches the engine only via ControlObject; never blocks RT. | controllers/engine |
| P-31 | given-when-then-tests | GoogleTest cases structured GIVEN/WHEN/THEN, one behaviour each. | testing |
| P-32 | rt-safety-assertions-in-tests | Engine tests assert house physics: allocation-counting allocator (zero RT allocs) + TSan. | testing/engine |

## Antipatterns AP-03..AP-16

| ID | Title | Statement (1-line) | Domain |
|---|---|---|---|
| AP-03 | second-writer-on-a-controlobject | Two components write the same key → fighting values / races. | ssot/engine |
| AP-04 | doc-restates-data | A doc/skill/AGENTS.md copies a value with a canonical home → silent drift. | ssot |
| AP-05 | author-grades-own-change | The session that wrote a change declares it passing, no independent evaluator. | harness |
| AP-06 | open-loop-promotion | "Sounds smoother, ship it" — promoted with no baseline/re-check/named loop. | harness |
| AP-07 | layering-over-refactor | A `_v2`/parallel path added beside the canonical one "to clean up later." | harness |
| AP-08 | stale-binary-after-source-edit | Benchmarking without rebuilding → measuring the old binary. | build |
| AP-09 | benchmark-on-moving-main | Measuring a perf delta against a churning main instead of a pinned baseline. | build/harness |
| AP-10 | tautological-green | A test rewritten to assert new code against itself → green forever, tests nothing. | testing |
| AP-11 | mean-hides-the-underrun | A mean/throughput number as the perf gate, hiding the glitch-producing tail. | engine/testing |
| AP-12 | gpu-cpu-copy-in-the-render-hot-path | Copying waveform/texture GPU→CPU→GPU every frame. | gpu/metal |
| AP-13 | qobject-without-parent | A QObject/parented_ptr that never gets a valid parent → leak/double-free. | qt-ownership |
| AP-14 | rt-thread-touches-gui-or-blocks | The audio callback mutates a GUI object, receives a signal sync, or blocks cross-thread. | engine/qt-ownership |
| AP-15 | hardcoded-tuning-or-mapping-value | A mapping/DSP constant hardcoded in C++ instead of its config SSoT. | controllers/build |
| AP-16 | silent-audio-error-swallow | Catch-and-continue on an audio error without recording it → invisible degradation. | engine |

## The `pat-*` skills (~10 — thin, cite-not-restate per P-05)

Each: `metadata.cites_patterns`, `defers_to:` the card, `description:` = auto-trigger on the code context.

| Skill | Cites | Fires when editing… |
|---|---|---|
| pat-02-rt-no-alloc *(seed)* | P-02, AP-02 | a `process*()`/callback under src/engine/ |
| pat-03-benchmark-as-contract *(seed)* | P-03, P-25 | a benchmark or perf hot path |
| pat-06-controlobject-single-writer | P-06, AP-03 | a ControlObject writer in src/control|engine/ |
| pat-16-lock-free-rt-handoff | P-16, P-17, AP-14 | cross-thread engine channels (util/fifo.h, engineworker*) |
| pat-19-parent-before-parented_ptr | P-19, AP-13 | make_parented/parented_ptr/new QObject in src/ |
| pat-21-metal-offload-deadline | P-21, P-22, AP-12 | src/rendergraph/, src/shaders/, waveform renderers |
| pat-08-generator-not-evaluator | P-08, P-09 | review/promotion of an engine/perf change |
| pat-11-refactor-over-layer | P-11, AP-07 | an edit that would add a `_v2`/parallel path |
| pat-27-db-schema-migration | P-27, P-28 | src/library/ schema/DAO files |
| pat-30-controller-via-controlobject | P-30, AP-15 | src/controllers/ (esp. scripting/) |

Doctrine-only patterns (P-07/10/12/13/14/15/18/20/23/24/26/31/32) get **no** skill — they're
design/review-time disciplines surfaced in the card + AGENTS.md, not auto-loaded per file open (P-05
keep-it-cheap rationale).

## Authoring order
1. **House-physics spine:** P-06,16,17,19,20,18 · AP-03,13,14,11 + skills pat-02,06,16,19.
2. **North-star perf loop:** P-14,25,21,22,23,24,26 · AP-12,09,08 + skills pat-03,21.
3. **Harness/SSoT discipline:** P-07,08,09,10,11,13,15 · AP-04,05,06,07,10,16 + skills pat-08,11.
4. **Subsystem breadth (lazy):** P-12,27,28,29,30,31,32 · AP-15 + skills pat-27,30.

Keep `kanban/patterns/AGENTS.md` index updated as cards land (or generate it in Phase 3).
