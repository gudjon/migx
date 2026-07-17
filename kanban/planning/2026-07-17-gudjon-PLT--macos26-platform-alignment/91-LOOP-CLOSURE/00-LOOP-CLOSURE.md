---
id: loop-closure-plt
type: loop-closure
dossier: 2026-07-17-gudjon-PLT--macos26-platform-alignment
verdict: partial
sealed: false
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# Loop closure — PLT (partial)

## Verdict

**partial** — Waves 1–3 **execution contracts met** on the build host; not sealed because:

1. USB/AirPods dual-deck GUI soak not run (no devices).  
2. CI change not yet observed green on GitHub Actions.  
3. Waveform visual dogfood not signed (matrix is HOLD gate, not full UIX retirement).

## Forecast vs actual

| Forecast | Actual |
|---|---|
| CA may flake on 26.x | Built-in path **stable** (0 late, 0 hard_err) |
| Need rewrite soon | **No** — Wave 5 not indicated |
| CI multi-OS slow | Matrix collapsed to 1 job |
| Risk of GL delete | Held with explicit matrix |

## 5-pass retro (short)

1. **What worked:** pure CA soak tool; clear EVD; CI prune without touching engine.  
2. **What hurt:** PA static + JACK; broken local ctest includes.  
3. **Surprise:** Continuity iPhone mic appears as HAL device.  
4. **Would redo:** start with pure CA not PA.  
5. **Learning to re-home:** OS build is soak axis; matrix before delete — already in arch map.

## What feeds back (must land before seal)

| Learning | Home | Landed? |
|---|---|---|
| CA 26.2/M4 built-in solid | EVD-PLT-0001 + this dossier | yes |
| CI mac-only | build.yml + ADR-006 practice | yes |
| GL delete HOLD deps | WAVEFORM-PARITY-MATRIX + task | yes |
| Soak tool path | tools/soundio/README | yes |

## Successor

- Manual dual-deck soak card when USB/AirPods available (enrich EVD-PLT-0001).  
- UIX dossier for real retirement after visual dogfood.  
- Watch first GH Actions run of macOS arm64-only matrix.

**Do not seal** until GH Actions green **or** owner accepts local-only gate.
