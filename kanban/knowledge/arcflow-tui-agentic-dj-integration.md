---
id: arcflow-tui-agentic-dj-integration
type: knowledge
title: "ArcFlow as the local world-model substrate for TUI-first Migx"
status: active
owner: gudjon
authored_by: codex-cli
created: "2026-08-07"
lastUpdated: "2026-08-08"
defers_to:
  - kanban/Strategy-Current.md
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
related:
  - tui-first-agentic-dj-workstation
  - world-model-experience-ontology
  - headless-sim-ground-truth-agentic-cli
  - kanban/planning/00-PORTFOLIO/capability-gap-matrix.md
  - kanban/tasks/arcflow-distinct-playlist-count-semantics.md
  - ADR-005
  - P-02
  - P-06
  - P-07
  - P-09
  - P-16
---

# ArcFlow for TUI-first Migx

## Decision frame

ArcFlow is a candidate **local-first world-model and derived-state substrate** behind Migx. Its hidden
value is not any single graph algorithm. It is the composition of durable state, graph/time queries,
incremental views, events, workflows, algorithms, and provenance behind the same human and agent
surface.

ArcFlow does **not** become the DJ application core, the ControlObject bus, an audio transport, or a
second writer. Migx owns DJ vocabulary, validation, authority, and real-time execution. ArcFlow remains
a generic engine; Migx injects the music/session domain from outside its repository.

```text
human TUI | CLI/JSON | --agent/MCP | future graphical adapter
                         |
               Migx application command core
          validate | authorize | single writer | receipt
                    /                         \
       query/event/proposal                  engine intent
                 /                               \
       ArcFlow local daemon                 ControlObject boundary
  world model | live views | workflows             |
                                              audio engine RT
```

The audio callback never calls, waits on, or depends on ArcFlow. ArcFlow work runs off the real-time
thread. A derived result is a proposal until the Migx application handler validates and executes it.

## Verified local baseline

Evidence captured on 2026-08-07 from the installed macOS command:

| Check | Observed result | Claim boundary |
| --- | --- | --- |
| Installation | `arcflow` resolves via `~/.local/bin/arcflow` to `~/.arcflow/bin/arcflow` | Available to Claude Code, Codex, Grok, and shells using the user PATH |
| Release | `arcflow v0.11.9`; identity source revision `6168ed04322040c7735473093b625e5dc20d18bd` | This is the runtime evaluated here, not the current `arcflow-core` checkout |
| Local workspace | `workspace init`, persistence, content-addressed snapshot IDs | Suitable for isolated prototypes; not yet a Migx production store |
| Migx-shaped proof | Three `Track` nodes, two `COMPATIBLE_WITH` edges, ordered JSON query | World Graph + Query Engine are directly useful now |
| Mirror loader | `tools/migx-cli/mirrors-to-graph` maps Track/Artist/Playlist and BY/ON edges | Full corpus completed against the patched ArcFlow branch |
| Query/runtime surface | `db.capabilities()` reported CPU backend, delta engine, e-graph rules, and Z-set operators | Confirms a substantial shipped query/incremental surface, not production performance |
| Service boundary | Daemon help exposes Unix-socket JSON-RPC plus optional HTTP/SSE and durability controls | Unix socket is the preferred first integration seam |
| Health ambiguity | `doctor --json` returned `status: ok` but `workspace_valid: false` after init | Must be resolved before relying on doctor as a release gate |

The real loader exposed four ArcFlow `v0.11.9` defects. Query-cache normalization
advanced byte by byte and could stop inside a Unicode scalar; the shared
REPL/PG-wire statement splitter also split semicolons inside quoted strings;
grouped `count(DISTINCT ...)` omitted its aggregate; and plain-variable
`WITH DISTINCT` could discard every grouping row after the first. Ranking then
found a second UTF-8 byte-boundary panic in `ORDER BY` temporal probing.

All four are fixed with Rust/Python/CLI regressions through ArcFlow commit
`ef944443` on `codex/arcflow-distinct-playlist-count`. The complete series is in
ArcFlow PR [`#27`](https://github.com/ozinc/arcflow-core/pull/27), with
protected-branch auto-merge enabled. The patched build preserves `Ysée`,
`trentemøller`, and `Chicane;Máire Brennan`, and ranks `RÜFÜS DU SOL` and
`Röyksopp` without panic. The published release still lags those source fixes,
so Migx must pin an identified patched build until a release containing them
exists.

Verification reported for that branch: 1,942 runtime tests, scoped CLI suites,
Clippy, formatting, and the complete Migx corpus load passed. Full TCK was not
rerun. Two later isolated rebuild attempts were terminated with exit 143 during
dependency compilation; those are incomplete rebuilds, not test failures.

The installed binary, `agent-context`, `paths`, source README, and procedure catalogue report different
crate/procedure/algorithm counts. The current `arcflow-core` checkout is also ahead of the installed
release. Treat the binary's behavior and identity as shipped truth. Treat source-only documentation as
design evidence until the corresponding runtime command is demonstrated.

## Full corpus proof

The patched loader completed 16,248 statements in about 12 seconds:

| Graph element | Count |
| --- | ---: |
| `Track` | 3,720 |
| `Artist` | 2,962 |
| `Playlist` | 83 |
| `BY` | 5,067 |
| `ON` | 4,416 |

The first queries already expose product value. CamelPhat and UNKLE occur
across 12 distinct playlists; NTO, Gui Boratto, and ANNA span 11. `No Goodbye`,
`Spektrum`, `Your Loving Arms`, and `Dark Is The Night For All` each span six.
The strongest five-playlist co-occurrences include the
Spektrum/Magic/Chemical cluster and `Your Loving Arms` with
`Dark Is The Night For All`.

These native findings now match an independent set-based reference. There are
4,300 distinct track/playlist memberships; the other 116 `ON` relationships are
repeated placements within a playlist. Raw `count()` still correctly measures
placements, so product rankings must use `count(DISTINCT p.id)` or first project
`WITH DISTINCT t, p`. Both forms return identical track rankings on the full
corpus. Group by stable `Track.key`, not title alone, because distinct recordings
can share a display title.

The supported canonical form is:

```gql
MATCH (t:Track)-[:ON]->(p:Playlist)
WITH t.key AS key, t.title AS track, count(DISTINCT p.id) AS playlists
RETURN key, track, playlists
ORDER BY playlists DESC, track, key
```

The distinct-playlist blocker is closed in
`kanban/tasks/arcflow-distinct-playlist-count-semantics.md`. Rankings remain
derived evidence, not playback authority.

## Value by ArcFlow layer

| ArcFlow layer | Migx product value | Initial use | Current evidence boundary |
| --- | --- | --- | --- |
| **World Store** | Durable local history of analysis artifacts, playlist snapshots, set/session state, agent receipts, and provenance | Store small structured artifacts and references; keep hot PCM/audio outside initially | Persistence and snapshot IDs verified; Migx schema and retention not designed |
| **Perception Lake** | Normalize analyzer, controller, community, catalog, and session observations with source time, confidence, and provenance | Design an observation envelope; do not make it a dependency yet | ArcFlow source describes this layer as reserved/transitional |
| **World Graph** | Typed `Track`, `Artist`, `Release`, `Crate`, `SetSession`, `Deck`, `Transition`, `Cue`, and `Source` relationships | Extend the proven library graph with observations and sessions | Full Track/Artist/Playlist graph verified; session schema not built |
| **Query Engine** | Answer "what next and why?", as-of session questions, conflict/missing-data queries, and agent inspection | JSON queries through the local daemon, with bounded templates owned by Migx | Direct and distinct grouped queries verified on the full corpus; production latency remains open |
| **Live Surface** | Incrementally maintain next-track candidates, queue conflicts, energy arc, and health as observations change | Drive synthetic session events and compare live results with full recomputation | Delta/Z-set capability reported; Migx standing views not proved |
| **Event Bus** | One replayable observation/event feed for TUI and agent subscribers | Bridge non-RT Migx domain events through a local durable topic | Procedure/daemon surface exists; delivery, replay, and backpressure need a spike |
| **Behavior Engine** | Durable off-RT prepare/analyze/resolve/plan/post-set workflows | Orchestrate preparation jobs and generate proposals with receipts | Behavior/workflow procedures are discoverable; no Migx workflow proved |
| **Algorithm Library** | Hybrid retrieval, graph ranking, community, temporal decay, causal explanation, contradiction, and entity resolution | Benchmark candidate selection and identity resolution against simple baselines | CPU procedures are discoverable; Metal was not active in this install |

## The product advantage

Without a shared world substrate, the TUI, an external agent, and later graphical clients tend to
recompute context independently and explain decisions after the fact. ArcFlow can make these one
inspectable loop:

1. Migx records an observation with source, clock, confidence, and correlation ID.
2. ArcFlow persists it, links it into the music/session graph, and updates derived views.
3. The TUI and agent read the same candidate set and supporting evidence.
4. An agent proposes a typed Migx command.
5. Migx validates authority and engine preconditions, executes through the single writer, and emits a
   receipt.
6. The outcome returns as another observation, so later rankings can learn from accepted, rejected,
   completed, and interrupted transitions.

This creates observable agent DJing rather than opaque Automix: human and agent share state, the
reason for a proposal is queryable, and every mutation remains attributable.

## Domain model boundary

Migx owns the initial vocabulary and schemas. ArcFlow stores and computes over them but must not gain
DJ-specific types in `arcflow-core`.

| Entity / relation | Purpose |
| --- | --- |
| `Track`, `Artist`, `Release`, `Recording` | Resolved music identity and provenance |
| `Analysis`, `Observation`, `Source` | Measured/inferred values with clock, confidence, and origin |
| `Crate`, `PlaylistSnapshot`, `SetSession` | Preparation and historical context |
| `Deck`, `Cue`, `Transition`, `CommandReceipt` | Session state and attributable action history |
| `COMPATIBLE_WITH` | Evidence-backed harmonic, tempo, structure, or energy compatibility |
| `PLAYED_AFTER`, `ACCEPTED`, `REJECTED`, `INTERRUPTED` | Learning signal with session/time context |
| `DERIVED_FROM`, `OBSERVED_BY`, `CONTRADICTS` | Provenance and disagreement, never silent overwrite |

Observed, inferred, and predicted values remain distinct. A predicted BPM, key, or transition score
must never overwrite a measured or source-supplied fact without provenance.

## Integration contract

Use the existing one-process REPL loader only for the offline A0 corpus proof;
ArcFlow `v0.11.9` rejects the bulk forms the loader needs, so spawning one process
per statement is not viable. For ongoing product integration, prefer the local
daemon over a Unix socket once the patched runtime and daemon contract are proved.
That gives the Python TUI/CLI process isolation while preserving the option of a
native Rust/C++ integration later.

- Migx defines versioned request, event, observation, proposal, and receipt schemas.
- Migx publishes domain events only after its authoritative state transition is accepted.
- ArcFlow may return queries, live deltas, workflow status, and proposals; it never writes a
  ControlObject or calls an engine object.
- `--agent` remains a Migx protocol. ArcFlow MCP may expose read/query tools, but playback tools route
  through Migx capabilities and authority modes.
- Every message carries stable entity IDs, schema version, correlation ID, source clock, and
  provenance.
- Backpressure or ArcFlow failure degrades intelligence and history, never playback continuity.
- An agent disconnect or ArcFlow restart cannot revoke local human control or stop a playing deck.

## Build horizons

### A0 - contract proof (loader and distinct semantics complete)

The Track/Artist/Playlist loader and full UTF-8 corpus proof are complete against
the patched branch. Distinct-playlist aggregation is fixed and independently
checked. Finish A0 by pinning the merged runtime identity, adding the remaining
bounded queries, and proving snapshot export/rebuild. Then extend the graph with
the minimal `Observation`/`SetSession` mapping. No engine connection.

**Gate:** the achieved 83-mirror/3,720-track/2,962-artist load stays green; all
ranking queries count distinct playlists correctly in the engine; one JSON query
returns ranked candidates with evidence; rebuild produces the same semantic result.

### A1 - PREP workspace world model

Project current mirror, resolution, quality, ingest, crate, and analysis outputs into ArcFlow. The TUI
inspector shows provenance and query evidence. ArcFlow remains a derived index; existing files and
Migx data stay authoritative.

**Gate:** deleting/rebuilding the ArcFlow workspace loses no source truth; TUI and `--json` return the
same candidate IDs and evidence.

### A2 - live synthetic session

Feed deterministic simulation events into Event Bus/Live Surface. Maintain next-track, energy-arc,
conflict, and health views incrementally. Compare every live result with a full recomputation.

**Gate:** delta and recomputed views agree; cancellation/replay/backpressure are tested; no RT path is
reachable.

### A3 - behaviors and algorithms

Run off-RT preparation workflows and compare ArcFlow ranking/resolution algorithms with simple Migx
baselines. Adopt an algorithm only when it improves a pinned quality or latency metric and preserves
explanation/provenance.

**Gate:** deterministic fixtures, quality metric, latency budget, failure fallback, and receipt exist.

### A4 - guarded engine bridge

Expose simulation-proven deck/mixer commands through the Migx command core. ArcFlow proposals and
external agents use the same authority and receipt contract as the TUI.

**Gate:** single-writer test, deterministic scenario evidence, zero RT allocations/locks added,
disconnect takeover, and audio-underrun acceptance all pass.

## Do not build yet

- No audio blobs or sample-by-sample telemetry in the graph hot path.
- No ArcFlow call from the engine callback.
- No second playback RPC that bypasses `system.capabilities` and Migx authority.
- No dependence on Perception Lake until its shipped contract is demonstrated.
- No Metal performance claim until the installed backend reports and benchmarks Metal.
- No generic "AI memory" abstraction before the first Track/Observation/SetSession fixture closes a
  real PREP query loop.

## Next concrete dossier

The next implementation dossier should remain **A0 only**: pin the merged
runtime identity, add the remaining bounded queries, prove export/rebuild, and
decide whether the Unix-socket daemon contract is stable enough for A1. It must
not touch the audio engine or ControlObjects.
