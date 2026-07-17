# SoundIO measurement tools (non-product)

## `coreaudio_pa_soak`

Core Audio **DefaultOutput** AudioUnit soak used by PLT Wave 1 / `PS-PLT-01`.
Does **not** link into Migx; measurement only (`P-02` safe — not on the product RT path).

```bash
clang -O2 -std=c11 tools/soundio/coreaudio_pa_soak.c \
  -framework AudioUnit -framework AudioToolbox -framework CoreAudio \
  -framework CoreFoundation -o tools/soundio/coreaudio_pa_soak

./tools/soundio/coreaudio_pa_soak --list
./tools/soundio/coreaudio_pa_soak --seconds 20 --buffer 256 --rate 48000
```

Gate: `hard_err=0`, late callbacks &lt; 0.1%, `gate_stable_callback=PASS`.

**Note:** PortAudio static from buildenv pulls JACK symbols; pure CA HAL avoids that.
Product path remains PortAudio→Core Audio (`SoundDevicePortAudio`).

## Dual-deck GUI soak (manual protocol)

When USB interface and/or AirPods are available:

1. Launch `build/mixxx --developer` with a disposable `--settings-path`
2. Dual-deck load + play; switch output Built-in ↔ USB ↔ AirPods
3. Toggle exclusive vs shared if prefs expose it
4. Note xruns in developer stats / logs under `~/Library/Application Support/Mixxx/`
5. Append results to `EVD-PLT-0001` enrichment section
