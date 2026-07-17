---
id: arcflow-filesystem-m4
type: knowledge
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: >
  Distilled by reading /Users/gudjon/code/arcflow-core (Rust). Files read:
  crates/arcflow-core/src/worldstore/mmap.rs (read-only mmap store + madvise),
  crates/arcflow-core/src/worldstore/serve/transport/mmap.rs ("don't reinvent the page cache" doctrine),
  crates/arcflow-core/src/worldstore/serve/transport/iouring.rs (io_uring transport, Linux-only),
  crates/arcflow-core/src/worldstore/io/platform.rs (PlatformOps trait: fsync/rename/madvise/unified/direct-io),
  crates/arcflow-core/src/worldstore/io/platform/macos.rs (F_FULLFSYNC, atomic rename, madvise, single-socket),
  crates/arcflow-core/src/worldstore/io/stripe.rs (group-commit, posix_fadvise DONTNEED),
  crates/arcflow-core/src/worldstore/serve/plan.rs (range coalescing, readahead window, deadline mode),
  crates/arcflow-bench/src/bin/iouring_vs_mmap.rs (mmap-vs-uring bench methodology).
---

# arcflow-core → Migx: filesystem / I-O techniques for M4 (APFS + fast NVMe + UMA)

Research input for [[initiative-apple-silicon]], companion to [[arcflow-m4-perf-techniques]].
arcflow-core's storage substrate ("worldstore") is explicitly built around the 2025–26
**mmap-as-storage** convergence (KuzuDB / LanceDB / DuckDB / MLX / llama.cpp). **We take the
technique, not the code.** Migx file-access hot spots: library scan + SQLite (`arch-library-db`),
track decode + `src/engine/cachingreader/` (`arch-sources-decode`), waveform/analysis cache data, and
startup (skin/settings).

**The headline Apple-Silicon lesson**: arcflow's io_uring transport is **Linux-only**; on macOS the
default "blazing fast" transport is **mmap + `madvise` + the kernel page cache**. On an M4 with one
fast internal NVMe and unified memory, you do **not** need io_uring-style batched async I/O to
saturate the disk — `mmap` + readahead hints get you there with far less machinery. So the transfer
list below is dominated by mmap/page-cache/durability techniques, not async-I/O plumbing.

---

## A. The read path — mmap + kernel page cache

### A1 — mmap immutable files as the READ path; a separate writer owns durable writes
- **What arcflow does** (`worldstore/mmap.rs`): reads go through a lazily-created **read-only**
  `memmap2::Mmap` mapped once and reused for the file's lifetime; writes never go through mmap (they
  use `pwrite` + `fsync` + atomic-rename), and any write **invalidates** the cached mapping first. Its
  invariant: `db.close()` == `munmap` + `close(fd)` — **no separate in-RAM copy**; the kernel reclaims
  pages (~500 ms) rather than the app holding a duplicate.
- **Why it fits Apple Silicon / APFS**: mapping an immutable file lets the **unified-memory** page
  cache back the data with zero user-space copy; the app's RSS and the cache are the same pages.
- **Migx target**: `src/engine/cachingreader` and `src/sources` decode input — mmap the (immutable)
  source audio file so the decoder reads from mapped pages instead of `read()`-into-buffer; waveform /
  analysis **cache files** (`.mixxx` analysis blobs) map read-only; SQLite already supports `PRAGMA
  mmap_size` for its read path.
- **Pattern**: **NEW pattern** — *"mmap immutable files for the read path; writers use
  pwrite+fsync+rename and invalidate the mapping."*
- **RT caveat (P-02)**: a page fault on a fresh mmap **blocks** — unacceptable on the audio thread.
  The RT caching-reader must **prefetch** (A3 `WILLNEED` ahead of the playhead) so the audio thread
  only ever touches resident pages, or keep its existing decoded-chunk ring as the RT-facing layer and
  use mmap only in the *worker* that fills it. mmap replaces `read()` in the worker, not the RT tap.

### A2 — Don't reinvent the page cache (arcflow `ANTI-0027`)
- **What arcflow does** (`transport/mmap.rs`): explicitly refuses to build a user-space LRU/LFU over
  mmap. Rationale, verbatim in the doctrine: the kernel page cache is **shared across processes**,
  **NUMA-aware**, and `madvise(WILLNEED)` already schedules optimal async readahead for the device; a
  user-space cache **competes with the page cache for the same RAM**, lowering aggregate hit rate. The
  only sanctioned user-space cache is for genuinely *remote* (S3) blocks — and the page cache still
  sits above it.
- **Migx target**: library scan and analyzer full-file reads should **not** grow a second bespoke
  cache — mmap + page cache is the cache. **Nuance for Migx**: `src/engine/cachingreader` legitimately
  *does* keep its own decoded-PCM chunk cache, because (a) it caches *decoded* samples, not raw file
  bytes, and (b) the RT thread cannot page-fault. That is a different layer than a raw-byte cache and
  stays. The lesson applies to the **non-RT** paths (scan/analyze/waveform read): prefer page cache.
- **Pattern**: reinforces **P-07** (one canonical home per concept) — the page cache is the canonical
  raw-byte cache. Candidate note under the A1 NEW pattern.

### A3 — `madvise` access-pattern hints
- **What arcflow does** (`macos.rs`, `MmapHint`): a thin `madvise` wrapper mapping four hints to
  Darwin advice — `Sequential`→`MADV_SEQUENTIAL`, `WillNeed`→`MADV_WILLNEED` (prefetch),
  `Random`→`MADV_RANDOM`, `DontNeed`→`MADV_DONTNEED` (evict). Best-effort only (never a correctness
  dependency). Darwin's `madvise` tolerates non-page-aligned pointers and clips internally.
- **Why it fits M4**: the hint lets the kernel issue the **right** readahead against the fast internal
  NVMe — big sequential reads for a one-pass scan, aggressive prefetch ahead of a known access point.
- **Migx target**: `src/analyzer` — `MADV_SEQUENTIAL` over a whole track being analysed one-pass;
  `src/engine/cachingreader` worker — `MADV_WILLNEED` on the region **ahead of the playhead** (and on
  seek target) so the RT thread finds resident pages (ties to the A1 RT caveat); waveform generation —
  `MADV_SEQUENTIAL`; `MADV_DONTNEED` after a one-pass read so the scan doesn't evict hot playback data.
- **Pattern**: part of the A1 NEW pattern; hint selection is per-caller.

---

## B. The write path — durability & crash-safety on APFS

### B1 — `F_FULLFSYNC` for true durability (plain fsync is not enough on macOS)
- **What arcflow does** (`macos.rs::fsync_file_durable`): durable commit is `fcntl(fd, F_FULLFSYNC)`,
  not `fsync`. It advertises `durable_fsync: true` only because it uses the full-sync barrier.
- **Why it's Apple-specific**: on macOS/APFS a plain `fsync()` flushes to the drive but does **not**
  force the drive to flush its **write cache** to stable media; only `F_FULLFSYNC` is a true barrier.
  This is *the* classic macOS durability footgun.
- **Migx target**: `arch-library-db` (SQLite) — ensure `PRAGMA fullfsync=ON` (or `checkpoint_fullfsync`)
  for commits that must survive power loss; settings save; analysis/waveform cache persistence.
- **Tradeoff**: `F_FULLFSYNC` is **slow** (waits on the physical drive) — pair with **B3** group-commit
  so you pay it once per batch, not per record.
- **Pattern**: supports **P-27 / P-28** (library DB via versioned migrations + typed DAO — the DAO is
  the right chokepoint to enforce the fullfsync policy).

### B2 — Atomic-rename commit protocol
- **What arcflow does** (`macos.rs::atomic_rename`): commits manifests/segments by
  **write-temp → fsync → `rename(2)`**; `rename(2)` is atomic for a single-target replace on APFS/HFS+.
  A reader always sees either the old file or the fully-written new one, never a torn write.
- **Migx target**: settings/preferences save (write `.tmp`, fsync, rename over the real file); waveform
  and analysis **cache files**; any exported/backup DB. Crash-safe with no half-written config.
- **Pattern**: **NEW pattern** — *"Commit durable state via write-temp + F_FULLFSYNC + atomic
  rename."* (B1 + B2 are one pattern in practice.)

### B3 — Group-commit: batch many writes behind one fsync
- **What arcflow does** (`stripe.rs`): the writer batches append records up to a **group-commit
  window** (`group_commit_bytes`, default 4 MiB) before issuing **one** `fsync`, amortising the
  (expensive, per B1) syscall over many writes; stripes roll at 256 MiB.
- **Migx target**: `arch-library-db` — during a library scan, insert many tracks inside **one
  transaction** and fsync once (SQLite: one `BEGIN…COMMIT` per batch, not per row); batching analysis
  results the same way.
- **Pattern**: supports **P-27 / P-28**; the DAO layer is where batch/commit windows live.

### B4 — Protect the page cache after bulk writes: `posix_fadvise(DONTNEED)`
- **What arcflow does** (`stripe.rs`, `drop_pagecache_on_commit: true`): after committing a stripe it
  tells the kernel to **drop** those just-written pages — the writer won't re-read them, so the page
  cache should be reserved for hot data.
- **Why it fits M4**: keeps the shared page cache holding *hot playback/waveform* data instead of
  cold, write-once scan output. macOS equivalent: `fcntl(F_NOCACHE)` on the fd or `madvise(DONTNEED)`
  on a mapped region.
- **Migx target**: library scan and analyzer writing large cache files — don't let the scan evict the
  currently-playing track's resident pages. Startup responsiveness benefit.
- **Pattern**: part of B2's NEW pattern (page-cache hygiene).

---

## C. Read planning — coalescing, deadlines, direct I/O

### C1 — Range coalescing at the kernel readahead window (8 MiB)
- **What arcflow does** (`serve/plan.rs`): a read plan carries a **coalesce threshold** (default
  **8 MiB**) — "ranges within N bytes should be fetched as one." The comment ties 8 MiB to "the S3
  optimal block size **and the kernel's readahead window on macOS/Linux**."
- **Why it fits M4**: merging many small nearby reads into one large sequential read matches the NVMe
  + kernel readahead sweet spot and cuts syscall count.
- **Migx target**: `arch-library-db` scan (batch many small tag/metadata reads); reading multi-section
  analysis blobs; anywhere the code does N small `read()`s from one file.
- **Pattern**: general; relates to B3 (batching).

### C2 — Deadline-over-completeness read mode
- **What arcflow does** (`plan.rs::deadline_at_ms`, its `PAT-0053`): the transport stops issuing
  **new** range fetches at a wall-clock deadline; in-flight reads finish; skipped ranges are reported
  as `missing`/`partial` (explicitly surfaced — **no silent downgrade**).
- **Migx target**: **startup** — load skin/settings within a time budget and fall back to partial/
  deferred load rather than blocking the splash; library-scan responsiveness; progressive waveform
  load. Keep the "this is partial" signal visible per **AP-16** (no silent swallow).
- **Pattern**: **NEW pattern** — *"Bound startup/scan I/O with a deadline; surface partial results
  explicitly."* Relates to **P-18** (tail latency) — a deadline caps p99 startup.

### C3 — Direct I/O / `F_NOCACHE` for streaming-once large reads
- **What arcflow does** (`platform.rs` / `macos.rs`): advertises `direct_io: true` on macOS. Darwin's
  direct I/O is `fcntl(F_NOCACHE)` — bypass the page cache for data read exactly once.
- **Migx target**: `src/analyzer` one-pass full-file decode — reading a whole track once to analyse it
  can use `F_NOCACHE` to avoid polluting the page cache with data that won't be reused (complements
  B4). Use judiciously: only where the data is genuinely single-use.
- **Pattern**: page-cache-hygiene family (with B4).

---

## D. Platform posture (informational, still actionable)

### D1 — Capability probe + runtime dispatch, never silent downgrade
- **What arcflow does** (`platform.rs`): storage capabilities (durable-fsync, atomic-rename,
  punch-hole, madvise, unified-memory, direct-io) are a runtime-probed trait; a platform that can't
  honour a *required* capability is refused at mount rather than corrupting data (`ANTI-0003`). Backend
  choice is **runtime, not compile-time `#ifdef`**.
- **Migx target**: detect whether a track/library lives on a **local APFS volume vs a network/FUSE
  mount** and pick the durability path accordingly (F_FULLFSYNC is meaningless/harmful on some network
  FS); surface degraded modes to the user rather than silently losing the guarantee. Relates to **P-27**.

### D2 — Apple Silicon is single-socket → skip NUMA entirely
- **What arcflow does** (`macos.rs::numa_pin`): a no-op returning `Ok(())` — "macOS / Apple Silicon is
  single-socket; there is no NUMA topology to pin to."
- **Migx target**: don't invest in NUMA-affinity or memory-node pinning for the M4 build — unified
  memory means one node. (Contrast with the P-core/E-core QoS work in [[arcflow-m4-perf-techniques]]
  B1, which **is** worth doing.)

### D3 — io_uring is Linux-only; on macOS mmap+madvise is the fast path
- **What arcflow does** (`transport/iouring.rs` gated `#[cfg(target_os = "linux")]`;
  `iouring_vs_mmap.rs` bench prints "N/A" on non-Linux and runs mmap-only). io_uring's 1.5–4× win
  needs multi-NVMe; on a single-disk box the gap is small.
- **Migx target**: **don't** chase io_uring / kqueue-AIO for Migx on M4 — invest in A1–A3 (mmap +
  madvise + page cache) and B/C instead. This is a scoping decision that saves effort.
- **Bench methodology to reuse** (`iouring_vs_mmap.rs`): warmup + measured iters, report **median**
  and GiB/s throughput, soft regression assertion — a clean template for **P-03 / P-25** I/O benchmark
  contracts, and **P-18** (median/tail, not mean).

---

## Candidate dossiers to seed (each a closed-loop P-03 benchmark dossier)

1. **FS-MMAP-DECODE — "mmap + madvise read path for decode & analysis."** Wire A1–A3 into the
   `src/engine/cachingreader` worker (raw-byte read → mmap; `WILLNEED` ahead of playhead) and
   `src/analyzer` (`SEQUENTIAL` + `DONTNEED` one-pass). Prove the RT thread never page-faults (P-02)
   and benchmark decode/scan throughput on M4. Consumes A1, A2, A3, C3.
2. **FS-DURABLE-COMMIT — "F_FULLFSYNC + atomic-rename + group-commit for DB, settings, caches."** Wire
   B1–B4 through the library DAO (`arch-library-db`, P-27/P-28) and the settings/cache writers.
   Benchmark scan-write throughput and verify crash-safety (kill-during-write leaves old-or-new, never
   torn). Consumes B1, B2, B3, B4, D1.
3. **FS-STARTUP-BUDGET — "deadline-bounded, coalesced startup & scan I/O."** Wire C1 (coalescing) + C2
   (deadline mode) into skin/settings load and the library scan; surface partial state (AP-16).
   Benchmark cold-start p99 (P-18) on M4. Consumes C1, C2, D3 (bench methodology).
