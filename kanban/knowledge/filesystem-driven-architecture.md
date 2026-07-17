---
id: filesystem-driven-architecture
type: knowledge
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: >
  https://vercel.com/blog/how-to-build-agents-with-filesystems-and-bash (fetched 2026-07-17) +
  kanban/knowledge/claude-code-capabilities.md +
  Migx architecture: kanban/architecture/ddd/bounded-contexts/arch-library-db.md, arch-track-model.md,
  arch-sources-decode.md; kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md;
  kanban/tasks/analyse-world-model-experience-ontology.md; kanban/knowledge/arcflow-filesystem-m4.md.
  Source evidence read directly: src/library/dao/trackdao.cpp, src/library/dao/cuedao.cpp,
  src/library/dao/analysisdao.cpp, src/database/mixxxdb.cpp, res/schema.xml, src/track/serato/.
related: [analyse-filesystem-driven-architecture, world-model-experience-ontology, arcflow-filesystem-m4,
  claude-code-capabilities, arch-library-db, arch-track-model, arch-sources-decode]
---

# A filesystem-driven architecture for the Migx library (sidecar metadata next to audio)

**Question this note resolves:** should Migx's DJ library be more **filesystem-driven** — audio files
with **sidecar metadata files** (cues, beatgrid, key, gain, waveform cache, tags, the experience
ontology) living *next to* the audio — making the library agent-readable/writable, versus (or alongside)
the central SQLite DB? And which is the **source of truth**?

**Bottom line up front:** Yes — introduce a greppable **per-track sidecar** as the *human/agent-facing
authoring surface and the portable source of truth for musical metadata*, but keep `mixxxdb.sqlite` as a
**rebuildable index/cache** for queries the filesystem can't serve fast (search, sort, crates, joins).
That is **sidecar-as-SSoT, DB-as-derived-index**, phased in behind ADR-002's build+test gate. Migx is
*already* a partial hybrid today (see §2) — this proposal completes and inverts that arrangement rather
than inventing it.

---

## 1. Why the filesystem is a powerful agent substrate

Distilled from the Vercel blog and `claude-code-capabilities.md`:

- **The model already speaks Unix.** LLMs have seen `grep`, `cat`, `find`, `awk` "billions of times
  during training." Filesystem navigation is a *native* capability, not a learned tool schema. The
  blog's thesis: *"The best agent architecture is already sitting in your terminal."*
- **Discovery beats prompt-stuffing.** Rather than pre-loading everything (token-limited) or
  approximating with vector search (imprecise), structured files let the model **discover context
  on-demand** with familiar primitives. `grep` returns *exact* matches, not ranked candidates —
  "precision over approximation."
- **Structure is self-documenting.** Domain hierarchies map directly to directories; relationships are
  preserved instead of being flattened into embeddings. A track's cues live *in the track's file*, the
  way a function's tests live next to the function.
- **Durability & tool-agnosticism.** Files persist independently of any API; there is "less code to
  maintain," and the same tree is readable by Claude Code, Codex, Grok, a shell script, `jq`, or a human.
  This is exactly Migx's **MG-2 "everything is code"** posture and the tool-agnostic `AGENTS.md`
  convention (`claude-code-capabilities.md` "How the Migx harness uses this").
- **Debuggability & auditability.** Every agent action leaves a diffable trace on disk. `git` gives you
  history, blame, and rollback for free — the co-pilot's writes to a live session (§6) become reviewable.
- **Convention over API.** No RPC surface to version; the "interface" is a filename and a text format.
  Future model improvements in code understanding *automatically* benefit the agent (blog: "Scalability").

The composing perf layer is `arcflow-filesystem-m4.md`: mmap + `madvise` + the kernel page cache make
many-small-file reads cheap on M4/APFS, and write-temp → `F_FULLFSYNC` → atomic-rename (B1/B2) is the
crash-safe way to commit a sidecar. Filesystem-driven does **not** mean slow if it rides that substrate.

---

## 2. How Migx persists track metadata **today** (file:line evidence)

The canonical store is a **single, central** SQLite file, not per-track. `src/database/mixxxdb.cpp:29`
— `kDefaultFileName = "mixxxdb.sqlite"` — one DB in the settings dir for the whole collection. All access
goes through the typed `dao/` layer (`arch-library-db`, invariants P-27/P-28). Current schema version is
**40** (`res/schema.xml`).

Where each metadata fact lives now:

| Metadata | Storage today | Evidence |
|---|---|---|
| Beatgrid | `beats` **BLOB** + `beats_version`/`beats_sub_version` columns on the `library` row | `trackdao.cpp:475-477,524-526,671-673`; `Beats::toByteArray()` at `:661`; schema `res/schema.xml:289-290` (v25 added `beats BLOB`) |
| Key | `keys` **BLOB** + `keys_version`/`keys_sub_version` columns | `trackdao.cpp:479,528-530,681-683`; `schema.xml:351-352` |
| BPM / ReplayGain | scalar columns `bpm`, `replaygain`, `replaygain_peak` on `library` | `schema.xml:169,420`; `trackdao.cpp` bind block |
| Cues / hotcues / loops | dedicated `cues` table, one row per cue | `CueDAO` INSERT/UPDATE at `cuedao.cpp:161,174` |
| Waveform / analysis (overview + detail) | **hybrid already**: `track_analysis` table holds `(id, type, description, version, data_checksum)` as an index; the **actual blob is a file on disk** | `analysisdao.cpp:12,35,135`; blob path `getAnalysisStoragePath()` → `<settingsPath>/analysis/<id>` (`analysisdao.cpp:173,259`) |
| File tags (artist/title/comment + **Serato** cues & beatgrid) | round-tripped **into the audio file's own container tags** | `MetadataSourceTagLib` (`sources/metadatasourcetaglib.cpp`); Serato import/export in `src/track/serato/` (`markers.cpp`, `markers2.cpp`, `beatgrid.cpp`, `cueinfoimporter.cpp`, `beatsimporter.cpp`) |

Two facts make the sidecar proposal *incremental, not radical*:

1. **Migx already writes analysis/waveform blobs to the filesystem** — just in a *central, opaque*
   directory keyed by a numeric DB `id` (`<settings>/analysis/12345`), so it is neither greppable nor
   next-to-audio. The DB row is already the *index* over a file blob. The pattern exists; it's pointed
   at the wrong location and an opaque format.
2. **Migx already round-trips real DJ metadata through the file itself** — Serato markers/beatgrid are
   read from and written to the audio container. There is already a "the file is the source of truth"
   path for interop; it's just limited to what Serato's binary tag formats encode.

Doctrine today (the tension we're resolving): `arch-library-db` invariant — *"The DB is a derived store,
not the canonical track (P-07): the authoritative `Track` lives in arch-track-model / **the file tags**;
the DB caches it."* Migx's own architecture already **declares the file, not the DB, as canonical** — but
in practice the durable home for Migx-specific structure (Migx beatgrid version, hotcue colors, future
ontology) is the DB BLOB, because file tags can't hold it. A sidecar closes exactly that gap.

---

## 3. The proposal — a per-track sidecar

### 3a. Format & layout

A **sidecar directory** next to each audio file, not a single blob file, so large/binary caches don't
bloat the greppable part:

```
Song.flac
Song.migx/
├── track.toml          # human-authored + agent-authored musical metadata (SSoT)
├── ontology.json       # the World-Model experience timeline + property-graph edges (§6)
└── cache/
    ├── waveform.bin     # derived render cache (regenerable; not SSoT)
    └── analysis.bin     # derived DSP blobs (regenerable)
```

- **`track.toml`** (or JSON — TOML for hand/agent editing, comments, diff-friendliness) holds the
  **greppable source of truth**: `bpm`, `key` (Camelot + classical), `replaygain`/`peak`, the
  **beatgrid** as *structured* anchors (not an opaque `Beats::toByteArray()` blob — emit
  down-beat/anchor + tempo segments so `grep`/`jq` and an agent can read it), and **cues** as a list of
  `{ position, type, label, color }`. One `<track>.migx/track.toml` ↔ one `Track` aggregate
  (`arch-track-model`).
- **`ontology.json`** is the sidecar home for `world-model-experience-ontology` — sections
  (intro/build/drop/outro), energy curve, harmonic journey, phrase structure, and the node/edge graph
  the live co-pilot reasons over. Keeping it a sibling of `track.toml` is precisely the "where does the
  ontology live on disk" question that task defers to this note.
- **`cache/`** holds **derived, regenerable** binary (waveform, analysis) — the mmap-friendly perf blobs
  from `arcflow-filesystem-m4.md`. These are explicitly **not** source of truth and are `.gitignore`-able.
- **Fallback for read-only/networked volumes** (P-01/D1 in `arcflow-filesystem-m4.md`): when the audio
  dir isn't writable, mirror the same `.migx/` tree under `<settings>/sidecars/<hash>/` — the DB index
  records which location won. Never fail silently (AP-16).

Why a `.migx/` dir over a single `Song.flac.migx.json`: keeps the audio folder tidy (one entry per
track), lets binary caches sit apart from the text SSoT, and gives the ontology room to grow without
rewriting one giant file on every cue edit (write-amplification, §4).

### 3b. The source-of-truth question — three options

| Model | SSoT | DB role | Verdict |
|---|---|---|---|
| **A. Sidecar-as-SSoT, DB-as-index** | `.migx/track.toml` | rebuildable cache for search/sort/crates/joins | **Recommended** |
| **B. DB-as-SSoT, sidecar-export** | `mixxxdb.sqlite` | canonical; sidecar is a read-only mirror | Weakest for the agent thesis |
| **C. Dual-write** | both, "kept in sync" | co-equal | Reject as the steady state |

**Recommendation: Option A — sidecar is the source of truth for musical metadata; the DB is a derived,
rebuildable index.** Rationale:

- It is the **only** option that makes the library genuinely agent-*writable*: an agent (or `git`, or
  another DJ tool) edits `track.toml`, and the DB reconciles *from* it. Under B, an agent write to the
  sidecar is a second-class copy the DB can clobber — that kills the co-pilot use case.
- It **matches Migx's already-stated invariant** (P-07: "the file is canonical, the DB caches it") and
  extends today's analysis-blob-on-disk + Serato-in-tags reality to *all* structure, in a greppable form.
- "Rebuildable index" is a strong property: if `mixxxdb.sqlite` is deleted or corrupt
  (`mixxxdb.cpp:95` already warns on corruption), Migx **re-derives** it by scanning sidecars — the DB
  stops being precious. Backup = copy the music folder.
- **Reject dual-write (C) as a steady state**: two authoritative writers is a P-06 single-writer
  violation and an unbounded consistency-reconciliation problem. Dual-write appears only *transiently* in
  the migration (§5) with a clear SSoT flag, never as the destination.

The DB stays because the filesystem is bad at what a DB is good at: "give me all 120–124 BPM tracks in
7A added this month, sorted by energy" is one indexed query vs. `grep`-ing 10k files. So: **write path →
sidecar; query path → DB index**. The DAO layer (`TrackDAO`) becomes the reconciler between them.

---

## 4. Benefits vs. risks

**Benefits**
- **Agent-friendly / greppable** — the co-pilot reads cues/energy/graph with `cat`/`grep`/`jq`; no DB
  driver, no query API to version (§1). Directly enables `world-model-experience-ontology`.
- **Portable / backup-trivial** — metadata travels *with* the audio on copy/move; backing up the music
  folder backs up the library. No "export your Mixxx DB" ritual.
- **Interop** — a text sidecar is readable by other tools and CLI; complements the existing
  Serato-tag interop (`src/track/serato/`) with an open, documented format.
- **Version-controllable** — `git` history/blame/rollback over a crate; every agent write to a live set
  is diffable and revertible (auditability, §1).
- **Resilient** — DB corruption is recoverable by re-scan; the DB is no longer a single point of loss.

**Risks & mitigations**
- **Perf vs. indexed DB** — filtering/sorting 10k+ tracks by scanning files is a non-starter → *keep the
  DB index; the FS is the write path, not the query path.* Reads ride mmap + page cache
  (`arcflow-filesystem-m4.md` A1–A3).
- **Consistency / sync** — sidecar and DB can drift → single reconciler in `TrackDAO`, a
  content hash/mtime in the DB row to detect staleness, re-derive on mismatch. One writer (sidecar),
  one deriver (DB) — not two writers.
- **Scale (10k+ libraries)** — 10k×3 small files. Mitigate with the `.migx/` dir (text SSoT small; heavy
  binary caches separate and `DONTNEED`-hinted, `arcflow-filesystem-m4.md` B4/C3), and coalesced reads
  (C1) on scan. Cold-scan bounded by a startup deadline (C2).
- **Write-amplification** — editing one cue must not rewrite a huge file → split text SSoT (`track.toml`,
  small) from binary caches; commit via write-temp + `F_FULLFSYNC` + atomic-rename (B1/B2), group-commit
  batches during scan (B3).
- **Conflicts** — two writers to one sidecar (agent + human) → last-writer-wins is unacceptable for a
  live set; use atomic-rename commits and, where it matters, `git`-style 3-way on the text file. The
  co-pilot writes through the same guarded API, respecting P-06/P-20 (§6).
- **Upstream divergence** — this deepens the fork away from Mixxx's DB-centric model. Under **ADR-002**
  (true hard fork, no upstream merge) this is *sanctioned*, not a cost: `fork_delta` records heritage
  only. Every step lands behind the build+test gate (ADR-002 §3).
- **Read-only media / streaming sources** — a track on a read-only mount or a non-file source has no
  place for a sidecar → settings-dir mirror fallback (§3a), DB index still covers it.

---

## 5. Coexistence & migration path (don't rip out the DB day one)

The DB and sidecar coexist permanently (index + SSoT); the migration is about **inverting authority**
gradually, each stage gated on build+test (ADR-002).

1. **Stage 0 — Export-only (shadow, no behavior change).** On `TrackDAO` save, *also* emit
   `.migx/track.toml` from the already-in-memory `TrackRecord`/`Beats`/`Cues`/`Keys`. DB remains SSoT
   (Option B, transient). Zero risk; produces a real corpus of sidecars to validate the format and let
   the ontology/co-pilot work start reading real files.
2. **Stage 1 — Read-back & reconcile.** On track load, if a sidecar is newer than the DB row (mtime/hash),
   import it and reconcile into the DB. Now edits made by an agent/`git`/hand *flow into Migx*. This is
   the transient dual-write window — carry an explicit `ssot=sidecar|db` marker per track; no silent
   last-writer-wins.
3. **Stage 2 — Flip SSoT to sidecar (Option A).** New/edited tracks are sidecar-canonical; the DB row is
   rebuilt from the sidecar on save. Add a **"rebuild index from sidecars"** maintenance path (re-derive
   `mixxxdb.sqlite` by scanning `.migx/`), proving the DB is now disposable.
4. **Stage 3 — Relocate the derived caches.** Move `AnalysisDao`'s central `<settings>/analysis/<id>`
   blobs (`analysisdao.cpp:259`) into per-track `.migx/cache/`, making waveform/analysis travel with the
   track too. Optional; highest write-amplification scrutiny.

Nothing forces a Stage; each is independently valuable and reversible. Migx can ship at Stage 1 (agent
can read *and* affect the library) and decide later whether to flip authority.

---

## 6. Recommendation — spike dossier, composing with the ontology + live co-pilot

**Recommend: a spike dossier (not yet a standing initiative), sequenced *before/with* the World-Model
ontology work.** Reasons:

- The **source-of-truth question is now answered** (Option A), which is what
  `world-model-experience-ontology` explicitly waits on ("Resolve storage — sidecar vs DB vs graph — with
  the filesystem-driven analysis first"). The `ontology.json` sibling in §3a *is* that resolution: the
  experience graph lives in the sidecar, next to the audio and the cues it annotates.
- It is **de-risked and incremental** — Stage 0 is a pure additive export with a build+test gate, and it
  rides an already-scoped perf substrate (`arcflow-filesystem-m4.md`). No RT-path involvement
  (`arch-library-db`/`arch-sources-decode` are `rt_safety: none`).
- It is **load-bearing for the differentiator.** ADR-002 frames Migx's headline divergence as
  *"agent access to live session state woven into the core."* A greppable, agent-writable sidecar is the
  concrete substrate that makes the **live co-pilot** (`world-model-experience-ontology` "killer use
  case") real: an agent reads deck/position/cues/upcoming crate as files, and **writes** a cue or
  reorders the queue by editing a sidecar — while honoring house physics (never on the RT thread; any
  change that reaches the engine is marshalled via ControlObject, P-06/P-20). The filesystem mirror is
  the read/write surface; ControlObject remains the *only* RT-affecting write path.

**Proposed spike (register a prefix, e.g. `FSL` — filesystem-library):**
- **FSL-01** — Define + document the `.migx/` format (`track.toml` schema for bpm/key/gain/beatgrid/cues).
- **FSL-02** — Stage 0 export from `TrackDAO`; validate round-trip fidelity (DB → sidecar → re-import ==
  identity) as the acceptance contract (independent evaluator, generator≠evaluator).
- **FSL-03** — Stage 1 read-back + reconcile with an SSoT marker; prove an out-of-band edit (agent/`git`)
  reaches a loaded `Track`.
- **FSL-04** (composes with the ontology spike) — add `ontology.json`; prove an agent reasons a
  transition from two sidecars (hands off to `world-model-experience-ontology`'s EXO/WLD spike).

Keep it research+spike until FSL-02 proves the format and fidelity; promote to an initiative only if the
export corpus and the co-pilot read-path pay off.
