# EVD-DSP-01 — IIR EQ-filter steady-state baseline (complete)

Pinned baseline for PS-DSP-01. **Complete** (unlike EVD-0003): the IIR `process()` path never touches
a GL context, so it measures fully in the headless `mixxx-test` binary.

## Pin (P-25)
- **Commit:** `6f0d9b1` (bench added on top; see the DSP Wave-1 commit)
- **Machine:** Mac16,12 — Apple **M4**, 4P + 6E (10 logical), macOS **26.2 (25C56)**
- **Build:** `mixxx-test` verified **arm64-native** (`file` → arm64; P-24)
- **Scene:** one RT buffer = 1024 stereo frames @ 44.1 kHz (**23.22 ms** of audio); deterministic
  broadband input; filter `assumeSettled()` first → measures the steady-state loop
  (`enginefilteriir.h:241-244`), not the ramp. 20000 fixed iterations.

## Measured (two runs, per-buffer µs)
| Bench (filter) | run | p50 | p90 | p99 | max |
|---|---|---|---|---|---|
| `BM_EngineFilterBiquadPeaking` (SIZE=5 EQ band) | 1 | 3.125 | 3.167 | **3.917** | 15.9 |
| | 2 | 3.125 | 3.208 | **3.875** | 18.5 |
| `BM_EngineFilterButterworth8Low` (SIZE=8) | 1 | 4.625 | 4.708 | **5.792** | 31.8 |
| | 2 | 4.625 | 4.667 | **5.709** | 17.0 |

Reproducible: p50/p90/p99 stable to ~1% across runs; `max` is scheduler-jitter noise (p99 is the
robust figure, per P-18).

## Intelligence (what the baseline tells us — read before Wave 2)
A single IIR filter costs **~3–6 µs p99 per 23.22 ms buffer = ~0.017–0.025% of the buffer period.**
Per-instance, EQ filtering is **cheap** — it is *not* a dominant RT cost.

The vDSP/NEON win (Wave 2) is therefore real but sits on a **small absolute base per filter**. It only
becomes material when summed across the full chain: a 3-band EQ (low/mid/high, each a steep multi-order
IIR) × up to 4 decks, plus the biquad-full-kill EQ's high-order stages. **Implication:** DSP-SIMD is a
lower-priority bottleneck than the render path — enter Wave 2 only after confirming the *aggregate* EQ
cost (all bands × decks) is worth vectorizing, or deprioritize in favor of MTL. This is exactly the
"is the problem real?" gate (P-03/MG-1) — and the honest answer here is "real but small per-instance."

## Wave-1 gate status
- ✅ `BM_EngineFilter{BiquadPeaking,Butterworth8Low}` added, builds, arm64-native, reproducible.
- ✅ `EngineFilterBiquadTest` (+ engine filter tests) green — no correctness regression from the change.
- ✅ Complete baseline (no GUI-blocked half).
- → **Wave 2 decision recorded above** — measure aggregate EQ-chain cost before committing to the SIMD rewrite.
