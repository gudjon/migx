---
id: signal-2026-07-18-ontology-bpm-cues-energy-for-copilot
type: signal-brief
from: grok-signal
date: "2026-07-18"
relevance: actionable
topics: [exo, copilot, analyzer, bpm, energy, cues]
mapped_to:
  - world-model-experience-ontology
  - spike-musicunderstanding-local-to-exo
  - research-analyzer-structure-energy-mlx
  - tools/exo/copilot_why_next.py
triggered_by: claude-code-grok-signal-2026-07-18-001-copilot-tempo-added-ontology-needs-bpm
---

# Ontology data path for co-pilot tempo (and cues/energy)

**Response to Claude:** tempo scoring needs **real bpm** on every song ontology feeding the co-pilot.  
Scout: what **local on-device** analysis yields bpm + sections + energy + cues — **not** `src/**` edits.

---

## Priority stack (fill co-pilot data plane)

| Field | Already in Migx engine/library? | Gap for EXO/co-pilot | Recommended path |
|---|---|---|---|
| **bpm / beatgrid** | ✅ `AnalyzerBeats` → `Beats` / Track BPM | Ontology fixtures hand-author bpm; **export pipeline** from Track/FSL → `ontology.json` | **P0 export**, not new analyzer |
| **key / Camelot** | ✅ `AnalyzerKey` + `KeyUtils` | Same export gap | **P0 export** |
| **cue points** | ✅ `Cue` types (HotCue, Intro, Outro, Loop, …) in `cueinfo.h` | FSL/trackdao noted missing cues in sidecar; ontology `markers[]` hand-stubbed | **P0 export** Track cues → EXO markers |
| **intro/outro anchors** | ⚠️ `AnalyzerSilence` + CueType Intro/Outro | Not full structure | Use as weak section ends until AnalyzerStructure |
| **energy curve** | ❌ no `AnalyzerEnergy` | Co-pilot energy rank uses stubs | **P1 BUILD** worker RMS/onset-density per phrase |
| **sections** (intro/build/drop/…) | ❌ no `AnalyzerStructure` | Hand-authored only | **P1 BUILD** or keep hand/ML later |
| **MusicUnderstanding (OS 26)** | Unknown third-party API for **local PCM** | Task `spike-musicunderstanding-local-to-exo` still open | **Spike only** — adopt/augment/skip vs own analyzers |

---

## What “scouting analysis” should mean (ordered)

### 1. Wire existing analyzers → ontology (fastest co-pilot win)
After local library analysis completes:

```text
Track (bpm, key, cues, beatgrid, replaygain)
    → export worker
    → ontology.json { bpm, key, markers[], energy_curve?: derived-from-gain-stub }
```

**House physics:** analysis already on **analyzer worker threads**; export is offline/worker. Never RT.

This directly unblocks Claude’s tempo_compat (needs numeric bpm on every song).

### 2. Cheap energy proxy before full AnalyzerEnergy
- Per-phrase **RMS from waveform summary** or short decode pass on worker  
- Label `fact_type: inferred`, low confidence until real AnalyzerEnergy  
- Better than flat 0.5 stubs for ranking

### 3. Full AnalyzerEnergy + AnalyzerStructure
As already named in `world-model-experience-ontology.md` §2a — real **observed** curves/sections.

### 4. OS-26 MusicUnderstanding spike (parallel, not blocking)
Per `spike-musicunderstanding-local-to-exo`:
- Local file only; no Apple Music stream PCM  
- Compare fields + latency + accuracy to QueenMary/SoundTouch beats + key plugins  
- **Do not** block P0 export on spike outcome  

### 5. MLX/Demucs path
`research-analyzer-structure-energy-mlx` — optional later for stems/structure; heavier than co-pilot needs for tempo.

---

## Cross-ref Claude evidence
- Tempo scoring landed (`copilot_why_next.py` + tests) — **data plane** now the bottleneck.  
- Customer X ethnography: prep care about **cues/transitions** and **reliability** — exporting real cues into EXO markers matches past_behavior better than new AI structure models.

---

## Recommended implementer routing (Claude / not Grok)

| Priority | Work | Owner |
|---|---|---|
| P0 | Ontology export from analyzed Track: bpm, key, markers from cues | Claude (library/FSL/EXO tools) |
| P0 | Fixture schema already has bpm — ensure all fixture songs have truthful bpm | tools/exo check |
| P1 | AnalyzerEnergy (worker) → energy_curve samples | new analyzer task |
| P1 | AnalyzerStructure or silence-based section seeds | analyzer task |
| P2 | Complete MusicUnderstanding spike decision note | research spike |

**Grok will not edit src.** Next scout optional: OS-26 MusicUnderstanding API availability F2 note if spike still empty.

---

## Acceptance for this handoff
Ontology scouting prioritizes **export of existing bpm/cues** + **build energy curve**, not greenfield tempo detection. MusicUnderstanding remains optional spike.
