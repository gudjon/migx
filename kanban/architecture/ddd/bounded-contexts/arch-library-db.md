---
id: arch-library-db
type: ddd-bounded-context
title: "library-db — the track collection, SQLite schema and typed DAO layer"
owns:
  - src/library/                # TrackCollection, Library, LibraryTableModel, dao/, features, playlists/crates, scanner
  - src/database/               # MixxxDb, SchemaManager — the SQLite connection and migrations
exclude: []
thread_domain: gui + worker
rt_safety: none
subdomain: supporting
upstream: [arch-track-model, arch-sources-decode]
downstream: [arch-mixer-decks, arch-track-model, arch-analyzer]
maturity: operational
fork_delta: upstream-tracking
agents_md: src/library/AGENTS.md
last_audited: "2026-07-17"
---

# library-db — bounded context

The persistent music collection and everything that reads it. `MixxxDb` owns the SQLite connection and
`SchemaManager` runs its versioned migrations; the `dao/` layer (`TrackDAO`, `PlaylistDAO`, `CueDAO`, …)
is the only typed gateway to those tables. Above it, `TrackCollection`/`TrackCollectionManager` and the
`LibraryTableModel` family expose the collection to the GUI table views. It is GUI/worker-thread code
(`rt_safety: none`) — nothing here runs on the audio callback. Pointers, never copies — `src/library/`
+ `src/database/` are the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `TrackCollection` | `library/trackcollection.cpp` | in-process front of the DB; owns the DAOs |
| `TrackCollectionManager` | `library/trackcollectionmanager.cpp` | internal + external collections, save orchestration |
| `Library` | `library/library.cpp` | root of features, models, sidebar |
| `LibraryTableModel` | `library/librarytablemodel.cpp` | the main track table (`BaseSqlTableModel`) |
| `BaseSqlTableModel` | `library/basesqltablemodel.cpp` | SQL-backed Qt table model base |
| `TrackDAO` | `library/dao/trackdao.cpp` | typed CRUD for the tracks table |
| `PlaylistDAO` / `CueDAO` / `AnalysisDAO` | `library/dao/` | typed access to playlists, cues, analysis |
| `TrackLoader` | `library/trackloader.cpp` | worker-thread track load for models/preview |
| `MixxxDb` | `database/mixxxdb.cpp` | the SQLite connection factory |
| `SchemaManager` | `database/schemamanager.cpp` | forward-only schema version migrations |

## Invariants (an agent MUST respect these)
- **All DB access goes through a DAO (`P-28`):** no raw `QSqlQuery` scattered through features/models;
  the typed `dao/` layer is the single gateway to the schema.
- **Schema changes are forward-only migrations (`P-27`):** bump the version and add a migration through
  `SchemaManager`; never mutate the live schema ad hoc or edit a shipped migration.
- **The DB is a derived store, not the canonical track (`P-07`):** the authoritative `Track` lives in
  arch-track-model / the file tags; the DB caches it. Reconcile, don't fork the source of truth.
- **Off the RT thread (`P-17`):** loads/scans run on worker threads and hand `TrackPointer`s to players;
  library code is never reachable from `process()`.

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `library` | the persisted track collection + its UI | the RT audio "buffer" library |
| `track` (row) | a DB record / model row for a track | the in-memory `Track` aggregate (arch-track-model) |
| `DAO` | a typed table gateway (`*DAO`) | a QML model proxy (arch-qml-ui) |
| `feature` | a sidebar source (`LibraryFeature`) | an audio feature / analysis result (arch-analyzer) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | `TrackPointer` for load | arch-mixer-decks | `TrackLoader` / `TrackCollection` | — |
| in/out | `Track` persistence | arch-track-model | `TrackDAO` ↔ `GlobalTrackCache` | — |
| out | tracks to analyze | arch-analyzer | scheduler pulls collection rows | — |
| in | tag/metadata on import | arch-sources-decode | `SoundSourceProxy` / metadata sources | — |

## Key patterns (cited, not restated)
`P-27`, `P-28`, `P-07`, `P-17` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`. The DAO gateway
(`P-28`) and forward-only migrations (`P-27`) are the load-bearing rules for any schema-touching change.
