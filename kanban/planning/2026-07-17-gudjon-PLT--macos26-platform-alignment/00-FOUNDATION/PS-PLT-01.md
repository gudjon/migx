---
id: PS-PLT-01
type: problem-statement
title: "Platform surface must match ADR-006 with proven SoundIO stability and no premature GL delete"
status: open
severity: MUST
ears_class: state-driven
dossier: 2026-07-17-gudjon-PLT--macos26-platform-alignment
prefix: PLT
resolves: []
risks: [AP-01, AP-02, AP-11]
related: []
acceptance:
  - "Wave1: Core Audio HAL soak on macOS 26.x + M4 records EVD-PLT-0001 with hard_err=0 and late-callback ratio <0.1% for buffer sweeps {128,256,512}@48k and 256@44.1k (tools/soundio/coreaudio_pa_soak); engine ctest -R 'EngineBuffer|SoundSourceProxyTest' green"
  - "Wave2: .github/workflows/build.yml matrix ships only macOS arm64 product job; packaging/{debian,flatpak} marked DORMANT; PIPEWIRE remains default OFF; local cmake --build + ctest still green on this host"
  - "Wave3: results/WAVEFORM-PARITY-MATRIX.md lists allshader vs deprecated feature rows + live #include deps; zero files deleted from deprecated/"
verified_against_code: "2afd73b / 2026-07-17"
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# PS-PLT-01 — Align platform to ADR-006 with measured SoundIO trust

**EARS statement:**
> While Migx ships only for **macOS 26.\*+ on Apple Silicon**, the system shall (1) prove Core Audio I/O stability with a recorded soak EVD on the target host, (2) stop CI/packaging from promising unsupported OSes, and (3) refuse waveform GL retirement until an explicit parity matrix is signed — without removing any Mac DJ feature.

## Context

- Floor already landed: ADR-006, CMake deployment `26.0`, arm64 refuse (Wave 0).  
- Open tasks: `tahoe-m4-soundio-soak-rebaseline`, `narrow-platform-to-apple-silicon`, `retire-deprecated-gl-waveform-renderers` (HOLD — live base classes in `deprecated/`).  
- Host: **M4 · macOS 26.2 (25C56) · arm64** — actionable now.  
- RT origin today: `SoundDevicePortAudio` → Core Audio host API (`src/soundio/sounddeviceportaudio.cpp`).  

## Acceptance contract

| Wave | Measure | Threshold |
|---|---|---|
| 1 | `tools/soundio/coreaudio_pa_soak` + `ctest -R EngineBuffer\|SoundSourceProxyTest` | hard_err=0; late&lt;0.1%; ctest green |
| 2 | `build.yml` matrix + packaging READMEs | single mac arm64 product path; no Mac feature loss |
| 3 | parity matrix file | complete rows; **0 deletes** |

**Guard:** no edit to `process*` RT paths; no `deprecated/` deletion.

## Out of scope

Native Core Audio `SoundDevice` rewrite; Accelerate DSP; QML skin parity; Spotify; full dual-deck GUI soak with USB/AirPods (protocol documented; hardware optional).
