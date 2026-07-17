# AGENTS.md — sources/ (audio file decode; encode lives in src/encoder/)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-sources-decode.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The codec layer: turn a file on disk into `CSAMPLE` frames and back. `SoundSourceProxy` picks a provider
from the registry and opens a `SoundSource` (FFmpeg, CoreAudio, FLAC, MP3, Opus, …) exposing an
`AudioSource` the engine's caching reader pulls from. `src/encoder/` is the reverse — `Encoder*` writes
MP3/Opus/FLAC/WAV for recording and broadcast. All of it runs on **worker threads**, never the callback.

## Key files
- `soundsourceproxy.cpp/.h` — selects a provider and opens a source for a `Track`.
- `soundsource.cpp/.h` — abstract decoder base; `audiosource.cpp/.h` — the pull interface consumed downstream.
- `soundsourceproviderregistry.cpp/.h` — registered providers, ranked per file type.
- `soundsourceffmpeg.cpp`, `soundsourcecoreaudio.cpp`, `soundsourceflac.cpp`, `soundsourcemp3.cpp`,
  `soundsourceopus.cpp`, … — per-codec decoders.
- `metadatasourcetaglib.cpp` — tag/metadata read-write via TagLib.
- `../encoder/encoder.cpp`, `../encoder/encoderffmpegcore.cpp`, `../encoder/encoderopus.cpp`, … — encoders.

## Invariants you MUST respect
- **Never on the RT thread:** decode/encode is worker-thread work; the RT engine consumes decoded frames
  only through the caching reader's lock-free hand-off, never by calling a `SoundSource`. `P-17`.
- **Fail loud, not silent:** a decode error surfaces (logged/propagated) — never swallowed into silence
  that looks like a working track. `AP-16`.
- **Provider selection is data-ranked:** file → provider is decided by the registry ranking, not
  hard-coded per-caller `if` chains.
- **Metadata edits are transactional against the file:** `MetadataSource*` owns the tag round-trip; the
  library DB holds the derived copy. `P-07`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R "SoundSource|Encoder|Metadata"` (GoogleTest; tests in `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Calling a `SoundSource` decode from a `process()`-reachable path instead of via the caching reader.
- Swallowing a decode/encode error into an empty-but-successful-looking result (`AP-16`).
- Hard-coding file-type → provider selection outside the registry ranking.

## Cross-references
Upstream: `src/track/AGENTS.md` (`TrackPointer` to open). Downstream: `src/engine/AGENTS.md` (caching
reader), `src/analyzer/AGENTS.md` (decode for analysis). Card:
`kanban/architecture/ddd/bounded-contexts/arch-sources-decode.md`.
