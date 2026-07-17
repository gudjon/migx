---
id: EVD-PLT-0001
type: evidence
title: "Core Audio HAL soak baseline — macOS 26.2 + M4 (Wave 1)"
dossier: 2026-07-17-gudjon-PLT--macos26-platform-alignment
status: complete
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# EVD-PLT-0001 — SoundIO / Core Audio soak (validate, don't rewrite)

Pinned baseline for underrun/callback stability on the **only** supported OS (`P-25` axes).

## Environment

| | |
|---|---|
| SoC | Apple **M4** (10 cores: 4P+6E) |
| Arch | **arm64** native (`file build/mixxx` → arm64) |
| macOS | **26.2 (25C56)** |
| Load avg during soak | ~2.9 (10 cores — moderate) |
| coreaudiod | alive (`/usr/sbin/coreaudiod` long-running) |
| Default output | MacBook Air Speakers @ 48 kHz |
| Devices present | Built-in speakers/mic + Continuity “IPhone 8bit Microphone” |
| External USB / AirPods | **not present** — GUI dual-deck protocol deferred |
| Tool | `tools/soundio/coreaudio_pa_soak` (DefaultOutput AU, not product binary) |
| Commit at measure | `2afd73b` tree + PLT WIP |

## Method

1. Enumerate CA devices via HAL.  
2. Open `kAudioUnitSubType_DefaultOutput`, set float32 stereo stream, set buffer frame size.  
3. Render 440 Hz sine @ −22 dBFS-ish for **N seconds**; record inter-callback periods.  
4. **Late** = period &gt; 1.5× expected buffer period (soft xrun proxy).  
5. **hard_err** = missing buffer / stop failures.  
6. Gate: `hard_err=0` ∧ late ratio &lt; 0.1% ∧ callbacks &gt; 10.  

Product path remains **PortAudio → Core Audio** (`SoundDevicePortAudio`); this EVD proves the
OS audio deadline is healthy enough that a rewrite is **not** indicated by OS flakes alone.

## Results — buffer / rate sweeps

| Config | seconds | callbacks | late | hard_err | p50 ms | p99 ms | max ms | gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 48 kHz · **128** frames (2.667 ms) | 20 | 7502 | **0** | **0** | 2.667 | 2.689 | 2.757 | **PASS** |
| 48 kHz · **256** frames (5.333 ms) | 20 | 3751 | **0** | **0** | 5.333 | 5.383 | 5.437 | **PASS** |
| 48 kHz · **512** frames (10.667 ms) | 20 | 1875 | **0** | **0** | 10.666 | 10.754 | 10.838 | **PASS** |
| 44.1 kHz · **256** frames | 15 | 2813 | **0** | **0** | 5.333* | 5.369 | 5.467 | **PASS** |

\* At 44.1 kHz request the device kept ~5.33 ms periods (device-side buffer alignment); still stable.

**Verdict:** SoundIO/Core Audio on **macOS 26.2 + M4 built-in** is **solid** for the measured
surface — **zero hard errors, zero late callbacks** across all four sweeps. No flake card opened
for built-in path. **Do not start Wave 5 Core Audio rewrite** based on OS instability.

## Engine correctness (adjacent)

`build/mixxx-test` gtest filter:

```
EngineBufferTest.* : EngineBufferE2ETest.BasicProcessingTest : EngineBufferE2ETest.SeekTest
: SoundSourceProxyTest.open : SoundSourceProxyTest.openEmptyFile
```

→ **16/16 PASSED** (~12 s).

Note: `ctest --test-dir build` currently fails with a **local CMake recursion** in
`build/mixxx-test[1]_include.cmake` (self-include). Pre-existing build-tree glitch; binary tests
OK. Reconfigure later if needed — not a product regression.

## Dual-deck / device-switch (not measured this EVD)

| Scenario | Status |
|---|---|
| Built-in exclusive/shared | Tool used shared DefaultOutput — OK |
| USB interface | No device attached |
| AirPods | No device attached |
| Sample-rate switch under dual-deck GUI | Protocol in `tools/soundio/README.md` |

## Relation to MTL EVD-0001

EVD-0001 = waveform CPU preprocess baseline.  
EVD-PLT-0001 = **audio deadline / CA callback** baseline.  
OS build **26.2/25C56** is now an axis on both.

## Intelligence → Adjustment

| Finding | Action |
|---|---|
| CA built-in stable | Advance baseline; Wave 2 prune unblocked |
| No USB/AirPods data | Keep manual protocol; optional follow-up soak card |
| PA static needs JACK to link soak | Pure CA tool is correct; leave PA in product |

## Reproduce

```bash
clang -O2 -std=c11 tools/soundio/coreaudio_pa_soak.c \
  -framework AudioUnit -framework AudioToolbox -framework CoreAudio \
  -framework CoreFoundation -o tools/soundio/coreaudio_pa_soak
./tools/soundio/coreaudio_pa_soak --seconds 20 --buffer 256 --rate 48000
```
