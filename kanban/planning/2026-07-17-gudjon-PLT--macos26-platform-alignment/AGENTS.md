---
id: dossier-plt-macos26-platform-alignment
type: dossier
prefix: PLT
title: "macOS 26+ AS platform alignment (SoundIO soak · CI prune · waveform parity)"
status: open
sealed: false
owner: gudjon
facilitator: gudjon
initiative: initiative-apple-silicon
created: "2026-07-17"
lastUpdated: "2026-07-17"
ps:
  - PS-PLT-01
defers_to:
  - kanban/knowledge/architecture-apple-silicon-macos26-refactor-map.md
  - kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md
  - AGENTS.md
---

# PLT — agent entry

## Intent routing

| Intent | Read first |
|---|---|
| Why / acceptance | `00-FOUNDATION/PS-PLT-01.md` |
| Waves / gates | `90-EXECUTION/00-PHASE-PLAN.md` |
| Soak results | `results/EVD-PLT-0001-soundio-soak.md` |
| Waveform parity | `results/WAVEFORM-PARITY-MATRIX.md` |
| Narrative log | `JOURNAL.md` |

## House physics (always)

- No RT alloc/lock (`P-02`) — Wave 1 is **measurement only**  
- One writer per CO (`P-06`)  
- Perf gates p99/max + zero underruns (`P-03`/`P-18`)  
- No green-over-red (`AP-01`); no bulk GL delete until parity (`P-11`)
