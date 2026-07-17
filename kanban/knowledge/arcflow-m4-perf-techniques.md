---
id: arcflow-m4-perf-techniques
type: knowledge
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: >
  Distilled by reading /Users/gudjon/code/arcflow-core (Rust). Files read:
  crates/arcflow-core/src/accelerate_batch.rs (Accelerate/AMX batch matmul),
  crates/arcflow-runtime/src/cpu_qos.rs (P-core QoS on Rayon pool),
  crates/arcflow-runtime/src/morsel.rs (morsel-driven atomic dispatch),
  crates/arcflow-runtime/src/algo_dispatch.rs (CPU-vs-accelerator routing / cost model),
  crates/arcflow-runtime/src/metal/mod.rs (Metal UMA / pipeline cache / heap / residency / counters),
  crates/arcflow-core/src/partition/hot_state.rs (cache-line alignment, false sharing),
  crates/arcflow-core/src/worldgraph/nodes/dense_store.rs + worldgraph/topology/csr.rs (SoA/columnar),
  crates/arcflow-core/src/vector/quantization.rs (precompute-invariants / ADC),
  Cargo.toml (release profile: LTO fat + codegen-units=1 + panic=abort + strip),
  ARCHITECTURE-RUST-STRATEGIES.md.
---

# arcflow-core → Migx: M4 / Apple-Silicon compute & dispatch techniques

Research input for [[initiative-apple-silicon]], companion to [[arcflow-filesystem-m4]].
arcflow-core is a Rust graph/vector database with an explicit "Wave F / PS-MM4" Apple-Silicon
tuning line. **We take the technique, not the code** — every row below maps a distilled method to a
concrete Migx subsystem (`src/engine` DSP, `src/analyzer`, `src/rendergraph`) and to a Migx pattern
(existing `P-NN` or a proposed **NEW**).

The single most important framing arcflow uses (its `ANTI-0003` "lane-explicit" rule): **keep the
routing decision — CPU vs accelerator — separate from the kernel.** Once "run on CPU" is chosen,
*which* CPU path (scalar / AMX / SME) executes is opaque to the router. Migx should mirror this: the
"does this run on the audio thread / a worker / Metal" decision is a policy layer above the DSP
kernels, not baked into them.

---

## A. SIMD / linear-algebra kernels

### A1 — Route batchable math through Accelerate (AMX/SME), not hand-written NEON
- **What arcflow does** (`accelerate_batch.rs`): batch dot-product and cosine-similarity are one
  `cblas_sgemm` call linked against `Accelerate.framework`. That single call dispatches the matmul
  onto the M-series **AMX coprocessor (M1+)** and **SME instructions (M4+)** automatically.
- **Why it's fast on Apple Silicon**: the open AMX ISA is undocumented and `core::arch::aarch64`
  (NEON intrinsics) exposes *neither* AMX nor SME. Accelerate's BLAS/vDSP is the only supported path
  to those silicon blocks, and it is hand-tuned per core generation by Apple. On an M4 the AMX/SME
  units deliver several times the FMA throughput of the NEON pipes for the shapes that amortise the
  framework-call overhead (arcflow notes ~256×768 f32 is where AMX starts winning). Behaviour is
  bit-close (fp reordering only), so it is a drop-in for a scalar loop.
- **Migx target**: `src/analyzer` — key detection and beat detection are FFT- and filterbank-heavy;
  route FFTs through **vDSP** (`vDSP_fft_zrip`) and windowing/magnitude through vDSP vector ops
  instead of scalar loops. `src/engine` DSP — biquad EQ banks, the resampler/scaler, and gain stages
  are matmul/convolution-shaped and can use vDSP (`vDSP_deq22`, `vDSP_vsmul`, `cblas_sgemm` for
  filter banks). Waveform overview downsampling (min/max/RMS reduction) maps to `vDSP_maxmgv` /
  `vDSP_rmsqv`.
- **Pattern**: extends **P-24** (build native arm64 with tuned flags). Warrants a **NEW pattern**:
  *"Prefer Accelerate/vDSP for batchable DSP math over hand-vectorised NEON"* — the NEON intrinsics
  route never reaches AMX/SME and is more code to maintain.
- **RT caveat (P-02)**: Accelerate calls may allocate/lock internally — **not** audio-thread safe.
  Use on `src/analyzer` workers and offline/prepare paths, or precompute coefficients off-thread and
  run a fixed, allocation-free vDSP call on the RT path only after proving it never allocates.

### A2 — Precompute query-independent invariants outside the inner loop
- **What arcflow does** (`precompute_norms_f32`; the ADC `TODO(perf)` in `quantization.rs`): row L2
  norms are computed once and cached because they are query-independent; the planned Asymmetric
  Distance Computation builds one distance table per query so each candidate becomes O(m) lookups
  instead of O(dims) work (~16× per-distance speedup at m=8, dims=128).
- **Why it's fast**: hoists O(M·K) work out of the hot loop; turns recomputation into a table lookup.
- **Migx target**: `src/engine` — window functions, filter coefficients, resampler polyphase tables,
  twiddle factors computed once at rate/param change, never per-buffer. `src/analyzer` — per-track
  constants (sample-rate-derived tables) computed once per track, not per frame.
- **Pattern**: general algorithmic hygiene; no new pattern, but reinforces **P-14** (prove the
  candidate beats the current path).

### A3 — Partial selection (top-K heap) instead of full sort
- **What arcflow does** (`top_k_f32`): a size-K min-heap gives the top-K in **O(M·log K)** vs the
  **O(M·log M)** of a full sort (~100× cheaper at M=1M, K=100).
- **Migx target**: `src/analyzer` peak/candidate picking (beat-grid candidate scoring, key histogram
  top-N), and library search ranking. Small but free wins wherever code sorts-then-truncates.
- **Pattern**: none; general algorithm-choice technique.

---

## B. Concurrency / dispatch to cores & lanes

### B1 — Place non-RT compute workers on P-cores via QoS class
- **What arcflow does** (`cpu_qos.rs`): the Rayon global pool is built with a `start_handler` that
  tags every worker thread on macOS with `QOS_CLASS_USER_INITIATED` (0x19) via
  `pthread_set_qos_class_self_np`. Called once, as early as possible, first-builder-wins (OnceLock).
- **Why it's fast on Apple Silicon**: the macOS scheduler chooses **P-cores vs E-cores** from a
  thread's QoS class. Default QoS for non-main threads is `UTILITY` or lower, which pins compute to
  **E-cores** on a busy host and forfeits most of the M4-Pro's throughput. `USER_INITIATED` asks for
  P-cores (kernel may still spill to E-cores under P-core pressure).
- **Migx target**: `src/analyzer` worker threads (`analyzerthread.cpp`), the caching-reader decode
  worker (`src/engine/cachingreader/cachingreaderworker.cpp`), and any `QThreadPool`/`std::thread`
  doing DSP-heavy prep. On macOS set `pthread_set_qos_class_self_np(QOS_CLASS_USER_INITIATED, 0)` in
  each worker's thread-start, or set `QThread::start` priority + a QoS shim.
- **RT caveat (P-02, P-18)**: **do not** apply `USER_INITIATED` to the audio callback thread — that
  thread must run under CoreAudio's **realtime workgroup / `QOS_CLASS_USER_INTERACTIVE`+time-
  constraint** policy, which is stronger and RT-scheduled. `USER_INITIATED` is for *workers*, not the
  RT lane. Mixing them up is an AP-14-shaped regression.
- **Pattern**: **NEW pattern** — *"Tag non-RT compute workers with a P-core QoS class on macOS."*
  Relates to **P-18** (tail latency: E-core placement is a p99 killer).

### B2 — Morsel-driven parallelism with a lock-free atomic dispatcher
- **What arcflow does** (`morsel.rs`): input is split into fixed-size "morsels" (4096 units, sized for
  L2). Workers claim the next morsel with a single `AtomicUsize::fetch_add(1, Relaxed)` — each worker
  reads one cache line, no lock. Dynamic claiming load-balances skewed work far better than a static
  N/threads partition; `reset()` re-uses the dispatcher for the next stage.
- **Why it's fast**: lock-free claim = no contention; morsel sized to L2 keeps the working set hot;
  dynamic steal-like behaviour tolerates uneven per-item cost (exactly the analyzer's profile — some
  tracks/blocks cost far more than others).
- **Migx target**: `src/analyzer` batch analysis across many tracks and across blocks within a track;
  waveform generation over a track's block grid. Replace "chunk = total/threads" static splits with a
  shared atomic cursor.
- **Pattern**: relates to **P-16** (lock-free handoff) and **P-18**. Candidate **NEW pattern**:
  *"Dispatch parallel worker batches via a lock-free morsel cursor sized to L2."*

### B3 — Size-gated CPU-vs-accelerator routing with a cost model (decision ≠ kernel)
- **What arcflow does** (`algo_dispatch.rs`): a router picks CPU vs GPU by input size and a cost
  model (e.g. H2D transfer bandwidth vs compute saved), with an **env-var escape hatch** and a
  **load-aware device pool** that uses atomic in-flight counters (no background thread, no NVML). The
  kernel implementations are unaware of the decision.
- **Why it lands**: small inputs never pay accelerator setup cost; the router is cheap (atomics) and
  the decision layer stays testable and overridable.
- **Migx target**: `src/rendergraph` / `src/waveform` — decide CPU vs Metal for waveform rendering by
  visible-sample count; `src/analyzer` — decide vDSP-CPU vs (future) Metal compute by track length.
- **Pattern**: mirrors **P-21** (GPU work must not gate the audio deadline) — the router is where you
  enforce "offload only when it pays and never on the RT deadline." Candidate **NEW pattern**:
  *"Gate accelerator offload behind a size/cost model, keep it out of the kernel."*

### B4 — Cache-line-align concurrent hot state to kill false sharing
- **What arcflow does** (`hot_state.rs`): per-shard hot atomics (`monotonic_seq`, `pending_writes`,
  `visible_seq`, …) are packed into one `#[repr(C, align(64))]` struct so adjacent shards never share
  a 64-byte line; a compile-time assert fails the build if size/alignment regresses. Its comment: the
  false-sharing trap "turns a 4-shard speedup into a 1.5× disappointment."
- **Why it's fast on Apple Silicon**: **64 bytes is the correct cache-line size on Apple M-series**
  (same as x86-64); aligning per-writer atomics to a line boundary removes cross-core cache-line
  ping-pong on the write path.
- **Migx target**: `src/engine` per-deck / per-channel atomic state written by the RT thread and read
  by GUI/waveform; `src/control` hot ControlObject counters; `src/analyzer` per-thread progress
  counters. Align each writer's hot atomics to 64 bytes (`alignas(64)`).
- **Pattern**: relates to **P-16** and **P-32** (engine tests assert house physics — add a
  false-sharing/TSan check). Candidate **NEW pattern**: *"Align concurrently-written hot atomics to a
  64-byte cache line."*

---

## C. Memory layout

### C1 — Struct-of-Arrays / columnar layout for cache-friendly scans
- **What arcflow does** (`dense_store.rs`, `csr.rs`): a Dense Property Store in **struct-of-arrays**
  form (5–8× memory reduction, node footprint from ~300–500 B to ~40–80 B); a compact 40-byte record
  with a hard "any field growth is a halt — split into a side table" invariant; an 8-property inline
  fast-path proven to cut cache misses; CSR topology extracted as three SoA columns in a single pass.
- **Why it's fast**: sequential columnar scans stream through cache with high line utilisation and
  perfect hardware-prefetcher behaviour; SoA is also the layout that **NEON/vDSP want** (contiguous
  same-type lanes), so it compounds with A1.
- **Migx target**: `src/engine` sample buffers — prefer **planar (SoA) over interleaved** for
  multi-channel DSP so vDSP/NEON operate per-channel contiguously; `src/waveform` data (already
  column-ish min/max/RMS); `src/analyzer` feature buffers. Keep per-item hot structs small and
  fixed-size.
- **Pattern**: candidate **NEW pattern**: *"Hold DSP hot data as planar/SoA, keep hot records small."*

---

## D. GPU / Metal (Apple-Silicon unified memory)

These are `src/rendergraph` targets and pair directly with **P-21 / P-22 / AP-12**. arcflow's
`metal/mod.rs` is a compact catalogue of Metal-on-Apple-Silicon wins:

### D1 — UMA zero-copy via `MTLResourceStorageModeShared`
- **What/why**: on unified memory the CPU and GPU address the same pages — buffers created
  `StorageModeShared` need **no upload/download**. No DMA copy, no staging buffer.
- **Migx target**: waveform sample/summary data → GPU. Write the waveform data once into a Shared
  buffer and let the shader read it in place. **Directly satisfies P-22** (waveform data stays in GPU
  buffers) and kills **AP-12** (GPU↔CPU copy in the render hot path).

### D2 — Persist compiled pipelines: `MTLBinaryArchive` cache
- **What/why**: arcflow persists compiled pipeline state across process boots; cold-start kernel
  compile drops from **~250–310 ms to <15 ms** on a cache hit.
- **Migx target**: `src/rendergraph` / `src/shaders` — cache the compiled RHI/Metal pipeline for the
  waveform shaders to disk so first-frame-after-launch isn't a multi-hundred-ms shader compile. Big
  **startup** win. Relates to **P-21** (don't let first-frame compile stall anything time-critical).

### D3 — Pool GPU buffers: `MTLHeap` transient sub-allocation
- **What/why**: a pre-allocated 128 MiB shared heap; sub-allocation costs **~1 µs** vs **~80–150 µs**
  for `device.newBuffer`; falls back to `newBuffer` on heap exhaustion.
- **Migx target**: `src/rendergraph` per-frame waveform/scope buffers — allocate from a pool, never
  `newBuffer` per frame. Reinforces **P-22** and keeps GPU setup off any per-frame critical path.
- **Pattern**: candidate **NEW pattern**: *"Pool GPU buffers from a pre-allocated heap; never
  per-frame device allocation."*

### D4 — Pin hot buffers: `MTLResidencySet`
- **What/why**: (macOS 15+, Apple8+) the driver elides per-encode residency checks for set members,
  saving ~100 µs × iterations on multi-pass work.
- **Migx target**: persistent waveform/texture buffers that live across frames — pin them once. Pairs
  with **P-22**.

### D5 — Per-dispatch GPU timing telemetry feeds an adaptive router
- **What/why**: `MTLCounterSampleBuffer` records per-dispatch GPU time, which feeds the cost router
  (B3) so offload decisions are data-driven.
- **Migx target**: `src/rendergraph` render-time telemetry feeding the CPU-vs-Metal decision (B3);
  aligns with **P-18** (measure the tail) and **P-25** (pin baselines).

---

## E. Build / benchmark discipline (supporting)

- **Whole-program optimisation** (`Cargo.toml [profile.release]`): `lto = "fat"`,
  `codegen-units = 1`, `panic = "abort"`, `strip = "symbols"`. The C++ analogue for Migx perf builds
  is **LTO/IPO on + `-mcpu=apple-m1`/native + no-exceptions on hot TUs where feasible**. Maps to
  **P-24**.
- **Bench methodology** (`iouring_vs_mmap.rs`): warmup iters + measured iters, report **median** and
  derived throughput, plus a soft regression assertion. Clean template for **P-03 / P-25** benchmark
  contracts (warmup, median-not-mean per **P-18**, pinned baseline).

---

## Candidate dossiers to seed (each a closed-loop P-03 benchmark dossier)

1. **DSP-ACCEL — "Accelerate/vDSP batch math for analyzer + engine DSP."** Wire A1 (+A2) into
   `src/analyzer` (FFT/filterbank via vDSP) and one `src/engine` filter/gain kernel. Benchmark vs the
   scalar baseline on M4; assert RT-safety unchanged (P-02) for any engine-path use. Consumes A1, A2,
   A3, C1.
2. **MTL-WAVEFORM-PIPELINE — "Zero-copy + cached-pipeline + pooled-buffer waveform render."** Wire
   D1 (UMA Shared buffers), D2 (pipeline cache → startup), D3 (heap pool) into `src/rendergraph`
   waveform path. Assert P-21/P-22, kill AP-12, measure first-frame and per-frame GPU time (D5).
   Consumes D1–D5, B3.
3. **ASI-WORKER-POOL — "P-core QoS + morsel dispatch for the analyzer/decode workers."** Wire B1
   (QoS) + B2 (morsel cursor) + B4 (cache-line alignment) into `src/analyzer` and
   `src/engine/cachingreader` workers. Benchmark throughput and p99 (P-18) on M4; verify the RT audio
   thread's QoS is untouched (P-02/AP-14). Consumes B1, B2, B4.
