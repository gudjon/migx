---
id: MTL-baseline-loop-closure
type: loop-closure
dossier: 2026-07-17-gudjon-MTL--waveform-render-baseline
prefix: MTL
sealed: true
sealed_date: "2026-07-17"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# 91 — Loop Closure

The dossier's expression of MG-1: a bet (the problem is real · the approach works · the gates catch
failure). `90-EXECUTION/` placed it; this scores it. **This is Migx's first sealed dossier** — the full
build→bench→baseline loop, demonstrated end-to-end.

## Verdict (one glance)

| | |
|---|---|
| **Definition-of-Done met?** | ☑ yes (partial on the load-clean tail number) |
| **Criteria green** | 3 of 3 completion-criteria met (`PS-MTL-01`): pinned baseline `EVD-0001` ✓ · data-path documented (backend + `COPY-MAP.md`) ✓ · p99/max + dropped frames captured ✓ (with honest tail caveat) |
| **Headline number** | RGB per-frame CPU vertex rebuild **≈34–39µs floor / ~38–45µs p50** on M4 (RelWithDebInfo, arm64); Filtered ~1.3×; 0/4000 dropped. **Independently reproduced** (P-08). |
| **One next action** | Open the zero-copy VBO optimization dossier (`2026-07-17-gudjon-MTL--waveform-zero-copy-vbo`, already scaffolding) — beat this number. |
| **Do NOT trust** | p99/max tail (82–417µs) — load-sensitive, measured under load avg ~20; needs a quiescent-host re-run for a clean tail. The floor is trustworthy. |

## Retrospective — five passes
1. **Premise vs. actual (root).** Premise: "we can measure a *trustworthy* M4 waveform baseline." Held.
   Root insight: the dominant per-frame cost is a **CPU-side full vertex rebuild** feeding a **no-VBO
   CPU→GPU copy every draw** (`basegeometrynode.cpp:89`) — a real `AP-12`/`P-22` violation in *this*
   codebase, not a guess.
2. **Process.** The **tractable-first** strategy was the win: measuring the CPU rebuild (no GL context
   needed) yielded a real, pinned, verified number without burning the wave on offscreen-GL plumbing.
   Deferring Phase B (GPU frame-time) per the ≥0.4 confidence fork rule was correct.
3. **Coordination.** First real **multi-agent** run (Claude subagents + a parallel user/Grok/Codex
   session). A federation-build collision was detected and resolved correctly (align, don't fork —
   AP-07/MG-3). Ownership by DDD context kept src/test (bench) and kanban/federation (docs) non-colliding.
4. **Ruled-out durable facts.** Phase-B GPU harness is NOT needed to establish a baseline. Per the
   arcflow research, io_uring (Linux) and NUMA pinning (multi-socket) are non-investments for the M4.
   Debug-build perf numbers are meaningless (RelWithDebInfo is the measurement build).
5. **Action.** Opened the optimization dossier (VBOs); filed follow-ons: a quiescent-host tail re-run
   and Phase-B GPU frame-time.

## Forecast vs. actual (the bet)
| Forecast | Actual | Delta / lesson |
|---|---|---|
| A repeatable bench reproduces within ±5% | Floor (min) reproduces within **1–2%**; p50 ~6%; **p99/max NOT** within tolerance | Under host load, only the floor is a trustworthy pinned number — report the floor + flag the tail (P-01/P-03) |
| The waveform bench is buildable headless | Yes — `src/test/waveformrenderbenchmark.cpp` runs offscreen, no GL context (CPU rebuild only) | Phase B (GPU) does need a GL context — deferred |

## System understanding AT CLOSE
Default QWidget-skin path renders via `rendergraph_gl` (custom QOpenGL). Every vsync, per deck:
`allshader::WaveformRenderer{RGB,Filtered}::preprocess()` rebuilds the entire vertex buffer (scalar
per-pixel), then `basegeometrynode.cpp:89-102` binds **client memory** → `glDrawArrays` copies the whole
buffer CPU→GPU (no VBOs). The SceneGraph backend already uses GPU buffers. Graphics API is **forced to
OpenGL** (`coreservices.cpp:826`) *because offscreen rendering must work* — so a Metal switch is gated on
solving offscreen-render-on-Metal. (This snapshot is THEN's truth; current truth lives in the code +
`kanban/architecture/`.)

## Wiring ledger (no anonymous open ends)
| Produced | Consumer | Wired? |
|---|---|---|
| `results/EVD-0001.md` (baseline) | the VBO optimization dossier (delta target) | ☑ WIRED |
| `src/test/waveformrenderbenchmark.cpp` | reusable for all render-perf dossiers | ☑ WIRED |
| `results/COPY-MAP.md` | the VBO/Metal optimization dossier (the target sites) | ☑ WIRED |

## What feeds back (landed this loop)
| Learning | Rooted at | Landed? |
|---|---|---|
| `P-22`/`AP-12` is real here (no-VBO per-frame copy) | the copy-map + the new optimization dossier | ☑ |
| Forced-OpenGL exists for offscreen-render → Metal-switch prerequisite | `EVD-0001` + `arch-rendergraph` card context | ☑ |
| A reusable offscreen render benchmark pattern | `src/test/waveformrenderbenchmark.cpp` | ☑ |

## Honest gate
- [x] No green-over-red — the baseline is real, cited, and independently reproduced.
- [x] No house-physics regression — the bench is off the RT audio path (`P-02`); no engine change.
- [x] Every produced surface is WIRED (table above).
- [x] The retrospective is authored, not boilerplate.

## Next bet + follow-on tasks
- **Next dossier:** `2026-07-17-gudjon-MTL--waveform-zero-copy-vbo` (persistent VBO, dirty-range upload) —
  beat `EVD-0001` (in flight).
- **Follow-on tasks** (spun out, owned): a **quiescent-host tail re-run** for a clean p99/max; **Phase B**
  offscreen GPU frame-time; both under `initiative-apple-silicon`.

## Closure metrics
Waves: 4/4. Days-open: <1. Files produced: bench + EVD-0001 + COPY-MAP. Commits: 1546d31 (Wave 2/3),
79a5c67 (Wave 4). Derived-from-git; not hand-tracked.
