---
id: FSL-loop-closure
type: loop-closure
dossier: 2026-07-17-antigravity-cli-FSL--filesystem-sidecar-spike
prefix: FSL
sealed: true
sealed_date: "2026-07-18"
created: "2026-07-17"
lastUpdated: "2026-07-18"
---

# 91 — Loop Closure

This is the dossier's expression of MG-1: a dossier is a *bet* (the problem is real · the approach
works · the gates catch failure); `90-EXECUTION/` placed it, this file **scores** it. It is a Sprint
Review + Retrospective in artifact form — retrospective only (git holds chronology; do not build a
ledger here).

**Seal gate.** You may set `sealed: true` only when the Definition-of-Done is verified (met or
explicitly partial), OR the bet is honestly **halted** with a named successor + owner + re-fire
condition. Never green-over-red (AP: honest-gate). An empty/boilerplate retro must NOT be sealed —
it starves the cross-dossier learning loop.

---

## Verdict (one glance)

| | |
|---|---|
| **Definition-of-Done met?** | met for the additive sidecar bet |
| **Criteria green** | `TrackDAO::saveTrack()` writes additive `track.json`, skips unchanged content, logs failures, writes atomically, and exports optional cues + waveform energy when present |
| **Headline number** | `TrackDAOTest.*` 3/3 passed; EXO tool tests and sidecar smoke passed |
| **One next action** | EXO/analyzer successor: production sections/structure, richer energy, graph derivation, and backfill policy |
| **Do NOT trust** | This is not a full DB->sidecar authority flip and not analyzer-derived song structure |

## Retrospective — five passes

1. **Premise vs. actual.** The premise was right: agents need a greppable per-track home before EXO can
   reason over a real library. The first slice was thinner than the product need because bpm/key alone left
   cue prep and set energy flat. The root cause was a source-to-decision mismatch: the code solved storage
   plumbing first, while customer/discovery evidence made cues the urgent product field.
2. **Process.** The federation worked once the lane was claimed. Claude kept the build lane clear, Grok
   supplied the external cue/energy priority signal, and Codex took the code/test/docs closure. The durable
   improvement is explicit path claims before touching `trackdao`.
3. **Coordination.** Antigravity's paused work was recoverable because the dossier had enough context and
   messages named the missing acceptance. The owner label was stale; the closure now records current reality
   without rewriting authorship history.
4. **Ruled-out durable facts.** FSL should not own full EXO ontology interpretation, analyzer structure,
   or live ControlObject writes. `track.json` should carry raw Track facts; EXO can derive prep/session
   meaning from those facts.
5. **Action.** Seal FSL as the additive raw sidecar layer. Keep analyzer/structure/graph work in a successor
   loop and keep cue/energy bridge tests as the contract between FSL and EXO.

## Forecast vs. actual (score the bet)

| We forecast | Actual | Delta / why |
|---|---|---|
| A save hook can write an additive, greppable per-track sidecar without removing SQLite | Met: `exportToSidecar()` writes `<track-location>.migx/track.json` from `saveTrack()` | The DB can remain the current runtime index while agents get a file surface |
| Wave 1 would only carry bpm/key/replaygain/peak | Exceeded: sidecar now also carries optional `cues[]` and coarse waveform `energy_curve` | Cue prep was the field-validated P0, so the raw Track sidecar needed to move before smarter planner work |
| File I/O hardening must be verified before seal | Met: unchanged content skip, `QSaveFile`, warning paths, focused C++ tests | The sidecar path is safe enough for the next EXO/analyzer loop |
| EXO ontology can be a later interpretation layer | Met: `ontology_from_sidecar.py` maps raw energy/cues through without inventing absent data | FSL owns raw Track facts; EXO owns product interpretation |

## System understanding AT CLOSE

`TrackDAO::saveTrack()` updates the DB, then calls `exportToSidecar()` off the real-time path. The sidecar
directory is `<track-location>.migx/`; `track.json` is serialized first, compared against existing content,
and written with `QSaveFile` only when bytes changed. The sidecar currently records:

- always: bpm, key, replaygain ratio, replaygain peak
- when cues exist: cue type, hotcue index, label, color, frame/ms positions, and beat positions when a
  beatgrid supports conversion
- when waveform data exists: a 32-sample track-fraction energy curve plus all/low/mid/high band arrays

No RT thread parses JSON. No ControlObject path writes this file. No SQLite authority was removed.

## Wiring ledger (no anonymous open ends)

Every surface this dossier produced must name a consumer. A produced-but-unconsumed surface is an
open loop.

| Produced | Consumer | Wired? |
|---|---|---|
| `<track>.migx/track.json` bpm/key/gain/peak | EXO `ontology_from_sidecar.py`; filesystem-driven architecture plan | ☑ WIRED |
| Sidecar `cues[]` | EXO session-local `prep.cue_points` | ☑ WIRED |
| Sidecar `energy_curve` | EXO song ontology energy and co-pilot energy scoring | ☑ WIRED |
| Analyzer-derived sections/phrases/graph | EXO/analyzer successor work | ☑ NAMED SUCCESSOR |

## What feeds back (must LAND this loop, not "queued")

Each durable learning re-homes into the living layer *now*:

| Learning | Rooted at (stable path) | Landed? |
|---|---|---|
| Raw sidecar facts and EXO interpretation are separate bounded contexts | `src/library/dao/trackdao.cpp`; `tools/exo/ontology_from_sidecar.py`; FSL/EXO journals | ☑ |
| Cue prep is a stronger immediate product signal than smarter ordering without cue data | `kanban/federation/signal/2026-07-18-x-thin-data-energy-cues-planner-live.md`; C++ sidecar regression | ☑ |
| Coarse waveform energy is useful planner evidence but not a replacement for analyzer-derived structure | FSL journal; `kanban/tasks/research-analyzer-structure-energy-mlx.md` | ☑ |

## Honest gate

- [x] No green-over-red: every "met" criterion has a passing benchmark/test cited above.
- [x] No house-physics regression (MG-6): no new RT-thread allocation/lock; Qt ownership sound.
- [x] Every produced surface is WIRED or has a follow-on task.
- [x] The retro above is authored, not boilerplate.

## Next bet + follow-on tasks

- `kanban/tasks/research-analyzer-structure-energy-mlx.md` — production structure/energy research and successor decision.
- EXO follow-on: derive richer ontology/session graph from sidecar facts without moving raw Track ownership out of FSL.

## Closure metrics (auto-derived where possible)

<Commits, files touched, benchmark deltas, days-open — derived from git by
`kanban/scripts/derive-closure-metrics.py` (Phase 3), not hand-typed.>
