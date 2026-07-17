---
id: apple-silicon-cleanup-surface
type: knowledge
title: "Legacy / cross-platform surface removable under Apple-Silicon-only (ADR-006)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: "grep/find sweep of src/ + packaging/ + .github/workflows/ at HEAD, 2026-07-17"
---

# Removable surface under ADR-006 (Apple Silicon only)

Quantifies how much legacy/cross-platform code the [ADR-006](../architecture/decisions/ADR-006-platform-scope-apple-silicon.md)
focus lets us delete or de-branch. Feeds [[narrow-platform-to-apple-silicon]] (the execution task).
macOS/Apple-Silicon stays; **Linux drops** (§4); **Windows goes dormant, not deleted** (§3, "later").

## Per-OS preprocessor branching (collapse to single-branch as touched)
| Guard | Files | Disposition |
|---|---|---|
| Windows (`__WINDOWS__` / `_WIN32` / `Q_OS_WIN`) | **51** | Dormant — leave `#ifdef` bodies, stop building/testing them; don't chase deletion (Windows is "later"). |
| Linux/X11 (`__LINUX__` / `Q_OS_LINUX` / `__linux__`) | **30** | **Delete** the Linux branches as files are touched — no audience. |
| Any per-OS branch (`Q_OS_*` / `__(WINDOWS\|LINUX\|APPLE)__`) | **74 files total** | Each simplifies toward a single Apple-Silicon path. |

~93 Windows-guard + ~60 Linux-guard lines mark the branch points; the code *inside* those branches is
the real removable volume (larger). De-branch opportunistically, wave-gated, build-green each step.

## OS deployment floor (the other big cut) — 11.0 → 26.0
Current `CMAKE_OSX_DEPLOYMENT_TARGET=11.0` (buildenv triplet `arm64-osx-min1100`). ADR-006 pins the
floor to **macOS 26.0**. Raising it: (a) lets us **drop pre-26 availability guards / back-compat shims**
across 15 macOS majors, and (b) **unblocks the OS-26 audio frameworks unconditionally** (FOA / AUAudioMix
/ MusicUnderstanding — see [[apple-audio-frameworks-os26-wwdc25]]), no `@available` fallbacks. This is
both a cleanup and a capability unlock — the enabling move for the alignment opportunity.

## Packaging (delete Linux, dormant Windows)
| Path | Size | Disposition |
|---|---|---|
| `packaging/debian/` + `CPackDebInstall.cmake` + `CPackDebUploadPPA.cmake` | ~60K | **delete** (Linux) |
| `packaging/flatpak/` + `.github/workflows/flatpak.yml` | ~128K | **delete** (Linux) |
| `packaging/wix/` | ~2.1M | **dormant** (Windows later — keep, stop building) |
| `packaging/macos/` | keep | the only live packaging path (DMG + notarize) |
| `ios/` seam | keep | **iPad is the sensible next platform** (ADR-006 §2) |

## CI
**15 of the workflow files** reference `ubuntu`/`flatpak`/`windows`/`msvc`. Target end-state: a
macOS-arm64-only CI (build + ctest + benchmark + kanban-discipline). Removing the Linux/Windows legs is
most of the CI wall-clock and flakiness.

## Deeper bet (note, don't overclaim)
Sound I/O currently goes through **PortAudio** (`src/soundio/sounddeviceportaudio.*`) — the
cross-platform abstraction. Apple-Silicon-only *enables* a future CoreAudio-direct path, but that's a
real architectural bet (its own dossier), not part of the mechanical prune.

## Adjacent legacy (audience/tech-debt, not platform)
- Deprecated GL/Qt waveform renderers — `src/waveform/{widgets,renderers}/deprecated/` (~148K) →
  [[retire-deprecated-gl-waveform-renderers]] (untangle-first).
- `src/broadcast/` (Shoutcast/Icecast) — check DJ-audience relevance before investing; possible retire.

## Net
~74 files de-branched toward one platform, ~3 packaging trees + most CI legs gone, plus the adjacent
deprecated-renderer retirement — a large, real reduction in compat/test surface. Sequence it wave-by-wave
under [[narrow-platform-to-apple-silicon]]; never green-over-red (`AP-01`).
