# AGENTS.md — mixer/ (deck/sampler/player lifecycle owner; straddles RT + GUI)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-mixer-decks.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The lifecycle owner of the playback objects. `PlayerManager` creates every `Deck`, `Sampler`,
`PreviewDeck`, `Microphone`, and `Auxiliary`, wires each to its `EngineChannel` and audio I/O, and
loads tracks. It **straddles two thread domains**: players are GUI-owned QObjects, but each one's engine
node processes on the RT thread. The ownership handoff is the whole job — the RT-safe processing lives
in `src/engine/`.

## Key files
- `playermanager.cpp/.h` — creates/owns all players; maps `[ChannelN]`/`[SamplerN]` groups to objects.
- `baseplayer.cpp`, `basetrackplayer.cpp` — `BasePlayer` / `BaseTrackPlayer` / `BaseTrackPlayerImpl`:
  shared player base, track load and engine wiring.
- `deck.cpp` — a playback `Deck`; `sampler.cpp` — a `Sampler` slot (both `BaseTrackPlayerImpl`).
- `previewdeck.cpp` — library preview player.
- `microphone.cpp`, `auxiliary.cpp` — mic / aux input players (`BasePlayer`).
- `samplerbank.cpp` — save/restore of sampler slot state. `playerinfo.cpp` — current-track lookup.

## Invariants you MUST respect
- **Parent before parented_ptr:** every player QObject gets a parent before its `parented_ptr`
  destructs; `PlayerManager` is the object-tree owner. Create/teardown is GUI-thread only. `P-19`, `AP-13`.
- **Lifetime off the RT thread:** a player's `EngineChannel` is constructed/destroyed on the GUI thread
  and handed to the engine by pointer — never `new`/`delete` a player on the callback. `P-17`.
- **Thread affinity:** players are GUI QObjects; the RT engine touches their channel processing state,
  not the QObject. No synchronous slot delivery across the RT boundary. `P-20`, `AP-14`.
- **Single writer per channel control:** the player owning `[ChannelN]` is the authoritative writer of
  its state controls; other contexts read via proxy. `P-06`, `AP-03`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "Player|Sampler"` (GoogleTest; e.g. `playermanager_test`,
  `samplerbank_test` in `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Constructing or destroying a player / `EngineChannel` on a `process()`-reachable path.
- Creating a player QObject without a parent, or destructing before it has one (`AP-13`).
- Adding a second writer to a `[ChannelN]` state control owned by another player.

## Cross-references
Downstream: `src/engine/AGENTS.md` (the `EngineChannel` nodes players create). Upstream:
`src/control/AGENTS.md` (channel state controls), `src/library/` (`TrackPointer` loads),
`src/soundio/AGENTS.md` (I/O registration). Seam: `kanban/architecture/ddd/boundaries/control-to-engine.md`.
