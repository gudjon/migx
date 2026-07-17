# Research — PLT Waves 1–3

## Prior art

| Source | Takeaway |
|---|---|
| `architecture-apple-silicon-macos26-refactor-map.md` | Wave order 1→2→3; risk register; 100% aligned criteria |
| `apple-audio-frameworks-os26-wwdc25.md` | Tahoe field risks (coreaudiod, caulk SIGILL); soak first |
| EVD-0001 (MTL) | Baseline axis = commit + M4 config + **OS build** |
| `retire-deprecated-gl-waveform-renderers` task | Live includes of `deprecated/glwaveformrenderer*.h` |
| PortAudio buildenv static lib | Links JACK symbols — pure CA HAL soak preferred for tool |

## Host inventory (2026-07-17)

| | |
|---|---|
| SoC | Apple M4 (10 cores) |
| Arch | arm64 native |
| macOS | **26.2 (25C56)** |
| Default output | MacBook Air Speakers @ 48 kHz |
| Default input | MacBook Air Microphone @ 48 kHz |
| Other | "IPhone 8bit Microphone" (Continuity-style) |
| External USB / AirPods | **not attached** at soak time — protocol notes them as follow-on |

## Options considered

| Option | Decision |
|---|---|
| Full dual-deck GUI soak only | Insufficient for unattended gate; keep as manual protocol |
| PortAudio soak binary | Blocked by JACK unresolved symbols in buildenv static lib |
| **Core Audio DefaultOutput AU soak** | **Chosen** for Wave 1 automated gate |
| Delete packaging trees wholesale | Risk CMake/CPack references; **mark DORMANT** + remove CI legs first |
| GitHub `macos-15` arm64 native job | Preferred over cross-compile from `macos-15-intel` |
