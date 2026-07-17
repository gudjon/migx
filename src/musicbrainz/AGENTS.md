# AGENTS.md — musicbrainz/ (online metadata lookup; async HTTP in src/network/)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-musicbrainz.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
Identifies a track online and fills in its tags. `TagFetcher` fingerprints the audio with `ChromaPrinter`
(AcoustID/Chromaprint), runs an `AcoustidLookupTask` then a `MusicBrainzRecordingsTask`, and returns
candidate metadata to the tag dialogs. `src/network/` is the reusable async plumbing — `WebTask`/
`JsonWebTask` wrap `QNetworkAccessManager` request/reply into signalled task objects. Network/worker
code, never on the audio path.

## Key files
- `tagfetcher.cpp/.h` — orchestrates fingerprint → lookup → recordings.
- `chromaprinter.cpp/.h` — Chromaprint acoustic fingerprint.
- `web/acoustidlookuptask.cpp`, `web/musicbrainzrecordingstask.cpp`, `web/coverartarchivelinkstask.cpp`
  — the lookup tasks.
- `musicbrainzxml.cpp` — parses the MB XML response.
- `../network/webtask.cpp`, `../network/jsonwebtask.cpp`, `../network/networktask.cpp` — async HTTP task base.

## Invariants you MUST respect
- **Fully async, off the RT thread:** every request is a non-blocking `WebTask` on the network thread;
  nothing here blocks a UI or audio thread waiting on I/O. `P-17`, `P-20`.
- **Fail loud:** network/lookup errors are reported to the caller (dialog/log), not swallowed into an
  empty result that looks like "no match". `AP-16`.
- **Results are proposals, not writes:** fetched metadata is offered to the user/`Track`; this context
  does not silently overwrite the canonical track record. `P-07`.
- **Qt affinity:** tasks are QObjects delivering results via queued signals on their owning thread; no
  cross-thread synchronous slot into GUI/RT. `P-20`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "MusicBrainz|WebTask|TagFetcher"` (GoogleTest; `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Making a blocking/synchronous network call instead of a `WebTask` (`P-17`, `P-20`).
- Swallowing a lookup/network error into an empty "no match" result (`AP-16`).
- Silently overwriting the canonical `Track` metadata instead of proposing it (`P-07`).

## Cross-references
Upstream: `src/track/AGENTS.md` (audio + existing tags). Downstream: `src/library/AGENTS.md` (persist
accepted metadata), `src/track/AGENTS.md`. Card:
`kanban/architecture/ddd/bounded-contexts/arch-musicbrainz.md`.
