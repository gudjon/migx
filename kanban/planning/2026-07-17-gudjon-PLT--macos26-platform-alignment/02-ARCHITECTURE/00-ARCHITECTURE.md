# Architecture — PLT platform alignment

## Chosen design

```text
Wave 1  measure CA deadline origin (tool outside mixxx binary)
           tools/soundio/coreaudio_pa_soak  →  EVD-PLT-0001
Wave 2  collapse portability tax at CI/packaging edge only
           build.yml matrix → macOS arm64
           packaging/{debian,flatpak} → DORMANT README
           CMake PIPEWIRE already OFF
Wave 3  parity matrix SSoT before any waveform delete
           WAVEFORM-PARITY-MATRIX.md  (no code delete)
```

## Edges

| Touches | Does not touch |
|---|---|
| `.github/workflows/build.yml` (+ related callouts) | `src/engine/**` process paths |
| `packaging/*` dormancy markers | Live SoundDevicePortAudio rewrite |
| `tools/soundio/*` measurement | Product default renderer selection |
| dossier results/ | Bulk `git rm` of deprecated/ |

## Patterns / ADRs

- ADR-006 platform floor  
- `P-03` / `P-18` / `P-25` soak baseline axes  
- `P-11` no parallel `_v2`; touch-local ifdef collapse only  
- `AP-01` no green-over-red  
- Risk: premature GL delete → Wave 3 HOLD  

## Feature-preservation (Mac DJ)

All deck/mix/controller/library/waveform **features stay**. Only unsupported-OS *promises* leave.
