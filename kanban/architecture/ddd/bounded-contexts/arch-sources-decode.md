---
id: arch-sources-decode
type: ddd-bounded-context
title: "sources-decode — audio file decode and encode off the RT thread"
owns:
  - src/sources/                # SoundSource*, SoundSourceProxy, provider registry, AudioSource, metadata sources
  - src/encoder/                # Encoder*, format-specific encoders/settings (broadcast/record)
exclude: []
thread_domain: worker
rt_safety: none
subdomain: supporting
upstream: [arch-track-model]
downstream: [arch-engine-realtime, arch-analyzer]
maturity: operational
fork_delta: upstream-tracking
agents_md: src/sources/AGENTS.md
last_audited: "2026-07-17"
---

# sources-decode — bounded context

The codec layer: it turns a file on disk into `CSAMPLE` frames and back. `SoundSourceProxy` picks a
provider from the `SoundSourceProviderRegistry` and opens a `SoundSource` (FFmpeg, CoreAudio, FLAC, MP3,
Opus, …) exposing an `AudioSource` the engine's caching reader pulls from. The `src/encoder/` half is
the reverse — `Encoder*` writes MP3/Opus/FLAC/WAV for recording and broadcast. All of it runs on
**worker threads**, never the audio callback (`rt_safety: none`); the RT-safe hand-off into playback is
the caching reader in arch-engine-realtime. Pointers, never copies — `src/sources/` + `src/encoder/`
are the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `SoundSourceProxy` | `sources/soundsourceproxy.cpp` | selects a provider and opens a source for a `Track` |
| `SoundSource` | `sources/soundsource.cpp` | abstract decoder base; `AudioSource` producer |
| `SoundSourceProviderRegistry` | `sources/soundsourceproviderregistry.cpp` | registered providers, ranked per file type |
| `SoundSourceFFmpeg` | `sources/soundsourceffmpeg.cpp` | FFmpeg-backed decoder |
| `SoundSourceCoreAudio` | `sources/soundsourcecoreaudio.cpp` | macOS CoreAudio decoder |
| `AudioSource` | `sources/audiosource.cpp` | the pull interface consumed downstream |
| `MetadataSourceTagLib` | `sources/metadatasourcetaglib.cpp` | tag/metadata read-write via TagLib |
| `Encoder` | `encoder/encoder.cpp` | abstract encoder base |
| `EncoderFfmpegCore` | `encoder/encoderffmpegcore.cpp` | FFmpeg-backed encode core |

## Invariants (an agent MUST respect these)
- **Never on the RT thread (`P-17`):** decode/encode is worker-thread work; the RT engine consumes
  decoded frames only through the caching reader's lock-free hand-off, never by calling a `SoundSource`.
- **Fail loud, not silent (`AP-16`):** a decode error surfaces (logged / propagated) — it is never
  swallowed into silence that looks like a working track.
- **Provider selection is data-ranked:** file → provider is decided by the registry ranking, not by
  hard-coded per-caller `if` chains.
- **Metadata edits are transactional against the file:** `MetadataSource*` owns the tag round-trip; the
  library DB holds the derived copy (`P-07`).

## Ubiquitous language
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `source` | a `SoundSource` decoder for one file | a `SoundDevice` audio interface (arch-audio-io) |
| `provider` | a codec plugin registered for file types | an effects backend (arch-effects-chain) |
| `AudioSource` | decoded-frame pull interface | `AudioSource` engine-registered device sink (arch-audio-io) |
| `metadata` | file tags (artist, title, cues) | library DB columns derived from them (arch-library-db) |

## Boundaries (edges by id)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| out | decoded `AudioSource` frames | arch-engine-realtime | caching reader worker pull | — |
| out | decoded frames for analysis | arch-analyzer | `SoundSourceProxy` open on worker | — |
| in | which `Track` / file to open | arch-track-model | `TrackPointer` | — |

## Key patterns (cited, not restated)
`P-17`, `P-07`, `AP-16` — see `kanban/patterns/`. Root house rules: `/AGENTS.md`. This context feeds the
engine but is deliberately *off* the RT thread; the RT-safety line is drawn at the caching-reader seam.
