---
id: headless-sim-ground-truth-agentic-cli
type: knowledge
title: "Headless simulation ground truth + agentic CLI for Migx"
status: active
owner: gudjon
created: "2026-07-18"
lastUpdated: "2026-07-18"
task: kanban/tasks/research-headless-sim-ground-truth-agentic-cli.md
related:
  - closed-loops-and-tdd-feedback-gaps
  - output-verification-formats-naming
  - world-model-experience-ontology
  - P-01
  - P-02
  - P-03
  - P-08
  - P-09
  - ADR-005
recommendation: phased-go
---

# Headless simulation ground truth + agentic CLI

**Question:** Should we build a **Simulation / ground-truth** layer (e.g. `.wav` fixtures an agent can load, mix headless, and measure) so Migx supports **full CLI agentic mode** and stronger TDD?

**Recommendation:** **Phased go** — invest in a **headless mix scenario harness** (engine graph → measurable audio out) before a full product CLI. Do **not** put simulation on the RT callback path. Prefer reusing `mixxx-test` + golden artifacts over a second audio engine.

---

## 1. Why this exists

| Need | Without sim | With sim |
|---|---|---|
| Agent TDD (RED→GREEN) | Needs GUI dogfood or partial unit tests | One command: scenario → metrics/WAV |
| Independent eval (`P-08`) | Human listens or peer skims diff | CI re-runs same scenario |
| Co-pilot claims | EXO plans offline only | Prove engine accepted load/crossfade |
| Closed loop (`P-01`) | Missing product-level sensor | Trigger = scenario run; Capture = golden; Adjustment = fail task |

Club gigs stay Core Audio + GUI. **Sim is a development and agent sensor**, not a replacement instrument.

---

## 2. What we already have (do not rebuild)

| Asset | Role | Limit |
|---|---|---|
| `mixxx-test` + GoogleTest | Headless unit/E2E pieces | No standard multi-deck product scenario pack |
| `src/test/enginebuffertest.cpp`, scale, mixer, sync tests | Engine graph fragments | Synthetic buffers, not named DJ scenarios |
| `src/test/enginefilterbenchmark.cpp` | Pure CPU DSP EVD | No decks/crossfader story |
| `src/test/waveformrenderbenchmark.cpp` | Headless CGL display | Not mix out |
| `src/test/soundFileFormats/` + `generateFiles.sh` | Format matrix tones (440/1kHz) | Manual listen matrix, not golden mix |
| EXO fixtures + `just exo-*` | Layer B offline plan | No engine |
| `tools/soundio/coreaudio_pa_soak` | Device callback stability | Not mixer graph |
| Mocked engine backends in tests | Isolation | Not a product CLI |

**Conclusion:** pieces of a sim exist; the **missing product is a named scenario runner** with frozen inputs/outputs and output verification (see companion note).

---

## 3. Architecture options (ranked)

### Option A — **Engine buffer sim** (recommended Phase 1)

```text
scenario.json → load Track from fixture WAV → EngineMixer process N buffers
             → master bus CSAMPLE[] → write out.wav + metrics.json
```

| Pros | Cons |
|---|---|
| Stays in-process `mixxx-test`; no SoundIO | Not full app (no QML, limited CO surface) |
| Deterministic if clock is virtual | Must fix sample rates / buffer sizes |
| Matches EVD culture | Needs careful fixture paths |

**House physics:** all work on test thread; no real device; no alloc rules waived for production RT — sim code lives under `src/test/` or `tools/sim/`.

### Option B — **SoundDeviceNull / FileWriter device**

Register a non-hardware device that drains the engine callback into a file/ring.

| Pros | Cons |
|---|---|
| Exercises more of SoundManager | Closer to RT path — higher risk of pollution |
| Useful soak of full open path | Harder CI (timing, threads) |

Use only if A cannot reach the code under test. Prefer **pulling buffers in tests** over faking a device when possible.

### Option C — **Product CLI / agent RPC** (`migx --agent` / headless)

```text
CLI/JSON-RPC → ControlObject intents → engine → report state + optional capture
```

| Pros | Cons |
|---|---|
| True “agentic DJ mode” | Large product surface; prefs, library, threads |
| Depth of permission for co-pilot | Needs security (local socket only) |

**Phase 2+** after A proves value. Layer B intents (EXO inbox) should be the **same** messages CLI uses — one path.

### Option D — **Offline DSP-only goldens without engine**

Script pure C++ filter/mix util.

| Pros | Cons |
|---|---|
| Fastest CI | Diverges from production graph (`AP-02` risk) |

Reject as primary; ok for micro kernels only.

---

## 4. Ground-truth design (WAV + metrics)

### 4.1 Fixture corpus (proposed layout)

```text
res/sim/                          # or src/test/sim/fixtures/ — pick one SSoT (output-verification note)
  corpus/
    tone-440-1k-stereo-48k.wav    # L=440 R=1k (align soundFileFormats idea)
    click-120bpm-48k.wav          # known BPM for grid tests
    noise-pink-48k.wav            # energy/crossfade tests
  scenarios/
    S01-load-play-silence.json
    S02-two-deck-xfade-linear.json
    S03-tempo-match-click.json
  goldens/
    S02-master.wav                # or .wav.sha256 + short snippet
    S02-metrics.json
```

Keep goldens **short** (2–10 s) to bound CI. Prefer **hash of metrics + optional PCM fingerprint** over multi‑MB golden WAVs in git (store compressed or generate goldens in CI artifact).

### 4.2 Scenario contract (machine-readable)

```jsonc
{
  "schema": "migx.sim-scenario/1",
  "id": "S02-two-deck-xfade-linear",
  "sample_rate": 48000,
  "buffer_frames": 256,
  "duration_s": 4,
  "decks": [
    { "id": "A", "file": "corpus/tone-440-1k-stereo-48k.wav", "gain": 1.0 },
    { "id": "B", "file": "corpus/click-120bpm-48k.wav", "gain": 1.0 }
  ],
  "timeline": [
    { "t_s": 0.0, "op": "play", "deck": "A" },
    { "t_s": 1.0, "op": "play", "deck": "B" },
    { "t_s": 1.0, "op": "crossfader", "value": 0.0 },
    { "t_s": 2.0, "op": "crossfader", "value": 1.0 }
  ],
  "capture": { "bus": "master", "path": "out/S02-master.wav" },
  "assert": [
    { "metric": "underrun_count", "op": "==", "value": 0 },
    { "metric": "rms_master_db", "op": ">=", "value": -40 },
    { "metric": "pcm_sha256", "op": "==", "ref": "goldens/S02-master.sha256" }
  ]
}
```

**RED:** change engine → assert fails. **GREEN:** fix or intentional golden update with review.

### 4.3 Metrics that matter for agents

| Metric | Use |
|---|---|
| `underrun_count` / xrun proxy | RT safety in sim clock |
| `rms_*_db`, peak | Crossfade / kill switch |
| `pcm_sha256` or sample-epsilon vs golden | Bit-exact regressed mix |
| Optional: detected BPM error vs click | Analyzer path later |

Avoid “sounds good” — only runnable asserts (`P-09`).

---

## 5. Agentic CLI surface (phased)

### Phase 1 (test binary) — ship first

```bash
build/mixxx-test --gtest_filter=SimScenario.S02
# or
build/mixxx-test --sim res/sim/scenarios/S02-two-deck-xfade-linear.json
```

Agent workflow:

1. Edit production code  
2. Re-run scenario filter  
3. Commit only if GREEN + no RT path dirty without review  

### Phase 2 (product headless)

```bash
migx --headless --agent-socket /tmp/migx.sock
# or
migx agent run --scenario S02
```

JSON-RPC / line protocol (illustrative):

| Method | Maps to |
|---|---|
| `library.load` | Track load intent |
| `deck.play` / `deck.cue` | CO writers (single writer still) |
| `mixer.crossfader` | CO |
| `capture.start/stop` | File writer on worker |
| `scenario.run` | Full sim pack |

**Security:** localhost only; no network bind by default.  
**Same intents** as EXO `intent-inbox.v1.json` so Layer B stays one path.

---

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Sim drifts from production graph | Drive real `EngineMixer` / buffers, not a toy mixer |
| Flaky timing | Virtual time / fixed buffer steps; no wall-clock sleeps |
| RT pollution | Sim code only under test/tools; never link into callback |
| Huge goldens in git | Short clips + hashes; regenerate script |
| Agent “cheats” by editing golden | P-08: golden updates require human/evaluator ack |
| Over-scoping product CLI early | Phase 1 test harness only until 3 scenarios prove value |

---

## 7. Recommendation (go / phases)

| Phase | Deliverable | Effort (order-of-mag) | Gate |
|---|---|---|---|
| **W0** | This note + output-verification contracts for sim paths | done / parallel | — |
| **W1** | 2–3 corpus WAVs + `SimScenario` gtest runner + 1 golden | small–medium | `ctest -R SimScenario` |
| **W2** | Scenario pack S01–S03 + CI job on macOS arm64 | medium | PR fails on metric reg |
| **W3** | Wire EXO intent → same ops (no GUI) | medium | Intent fixture drives S02 |
| **W4** | Optional `migx --headless` socket | large | Dogfood agent session |

**Go:** W1–W2. **Defer** full product CLI until W1–W2 close TDD loops for engine changes.  
**No-go:** separate audio engine “for agents only.”

---

## 8. Ties to closed-loop / TDD gaps

From `closed-loops-and-tdd-feedback-gaps.md`:

- Supplies **product-level RED/GREEN** missing above unit benches.  
- Gives **independent eval** a command CI can run.  
- Complements EXO offline plans with **engine ground truth**.  
- Requires **output verification** (companion note) so scenarios/goldens have frozen names.

---

## 9. Bottom line

**Yes — build simulation ground truth**, starting as a **headless scenario harness inside `mixxx-test`** with short WAV corpus and metric/golden asserts. **Yes — aim for agentic CLI**, but as **Layer B intents + later product headless**, not a fork of the RT path. Measure twice (EVD-style); ship the sensor before the full CLI product.
