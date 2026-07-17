# PLT — macOS 26+ Apple Silicon platform alignment

**Prefix:** `PLT` · **Date:** 2026-07-17 · **Owner:** gudjon  
**Initiative:** `initiative-apple-silicon`  
**Map:** `kanban/knowledge/architecture-apple-silicon-macos26-refactor-map.md` Waves **1–3**

## Scope

Execute the immediate platform-alignment program **without** feature amputation:

| Wave | Deliverable | Status |
|---|---|---|
| **1** | SoundIO / Core Audio soak baseline on M4 + macOS 26.2 | in progress |
| **2** | CI + packaging prune → macOS arm64 only story | in progress |
| **3** | Waveform parity matrix **before any GL delete** | prep only — no delete |

## Non-goals

- Native `SoundDeviceCoreAudio` rewrite (Wave 5 — only if Wave 1 fails)
- Bulk delete of `src/waveform/**/deprecated/` (HOLD — live base-class deps)
- iPad / Windows / Linux product work

## Success (dossier-level)

1. **EVD** for CA/SoundIO soak on 26.2/M4 with p99 callback period + zero hard fail gate  
2. **CI matrix** ships one macOS-arm64 product path; foreign packaging dormant  
3. **Waveform parity matrix** signed; retire-GL task remains blocked until parity  

## Closed loop

Trigger: ADR-006 floor locked · Capture: soak EVD + CI green · Intelligence: delta vs risks · Adjustment: flake cards or advance baseline  

## Tasks folded in

- `kanban/tasks/tahoe-m4-soundio-soak-rebaseline.md` → Wave 1  
- `kanban/tasks/narrow-platform-to-apple-silicon.md` → Wave 2  
- `kanban/tasks/retire-deprecated-gl-waveform-renderers.md` → **parity prep only** (Wave 3)
