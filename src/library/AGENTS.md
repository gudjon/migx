# AGENTS.md — library/ (track collection, models; DB schema in src/database/)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-library-db.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The persistent music collection and everything that reads it. `MixxxDb` owns the SQLite connection and
`SchemaManager` runs its versioned migrations; the `dao/` layer is the only typed gateway to those
tables. Above it, `TrackCollection`/`TrackCollectionManager` and the `LibraryTableModel` family expose
the collection to the GUI table views. GUI/worker-thread code — nothing here runs on the audio callback.

## Key files
- `trackcollection.cpp/.h`, `trackcollectionmanager.cpp/.h` — in-process front of the DB; owns the DAOs.
- `library.cpp/.h` — root of features, models, sidebar.
- `librarytablemodel.cpp`, `basesqltablemodel.cpp`, `basetracktablemodel.cpp` — SQL-backed table models.
- `dao/trackdao.cpp`, `dao/playlistdao.cpp`, `dao/cuedao.cpp`, `dao/analysisdao.cpp` — typed table gateways.
- `trackloader.cpp` — worker-thread track load for models/preview.
- `../database/mixxxdb.cpp` — the SQLite connection factory; `../database/schemamanager.cpp` — migrations.

## Invariants you MUST respect
- **All DB access goes through a DAO:** no raw `QSqlQuery` scattered through features/models; the typed
  `dao/` layer is the single gateway to the schema. `P-28`.
- **Schema changes are forward-only migrations:** bump the version and add a migration through
  `SchemaManager`; never mutate the live schema ad hoc or edit a shipped migration. `P-27`.
- **The DB is a derived store, not the canonical track:** the authoritative `Track` lives in `src/track/`
  / the file tags; the DB caches it — reconcile, don't fork the source of truth. `P-07`.
- **Off the RT thread:** loads/scans run on worker threads and hand `TrackPointer`s to players; library
  code is never reachable from `process()`. `P-17`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "Library|TrackDAO|Playlist|SearchQuery"` (GoogleTest; `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Issuing raw SQL from a feature/model instead of through a `dao/` gateway (`P-28`).
- Editing a shipped migration or mutating the live schema outside `SchemaManager` (`P-27`).
- Treating a DB row as the canonical track and overwriting the `Track`/file source of truth (`P-07`).

## Cross-references
Upstream: `src/track/AGENTS.md` (canonical `Track`), `src/sources/AGENTS.md` (import metadata).
Downstream: `src/mixer/AGENTS.md` (`TrackPointer` loads), `src/analyzer/AGENTS.md`. Card:
`kanban/architecture/ddd/bounded-contexts/arch-library-db.md`.
