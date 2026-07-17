---
id: signal-2026-07-17-metal-waveform-render-scout
type: signal-brief
from: grok-signal
date: "2026-07-17"
relevance: actionable
topics: [metal, waveform, allshader, rhi, apple-silicon, uma, p-21, p-22]
mapped_to:
  - kanban/planning/2026-07-17-gudjon-MTL--waveform-scrub-regime/
  - EVD-0003
  - initiative-apple-silicon
  - P-21
  - P-22
  - PLT Wave 3 HOLD (deprecated GL)
triggered_by: claude-code-grok-signal-2026-07-17-002-redirect-scout-dsp-to-metal-render
sources:
  - "X AS UMA coherence: CPU/GPU negotiate buffers without discrete VRAM copy tax (field 2025–26)"
  - "Apple TBDR / mobile GPU constraint patterns (custom BVH/TBDR work on M-series, Jul 2026)"
  - "MTL dossiers EVD-0001/0002/0003 + coreservices OpenGL force for offscreen"
---

# Signal — Metal / allshader waveform render (post–DSP NO-GO redirect)

## Mandate update
Claude parked **DSP-EQ SIMD** (EVD-DSP-01: EQ ≪ RT budget). Grok **holds** further DSP-EQ
scouting. North-star field focus: **M4 Metal + allshader / Qt RHI → Metal** waveform path.

## Field synthesis (actionable for MTL)

### 1. Unified memory is the product advantage
Apple Silicon field consensus: **CPU↔GPU buffer sharing is cheap** vs discrete GPUs that reserve
VRAM pools. For Migx this reinforces **P-22 zero-copy**: keep waveform geometry in GPU-visible
buffers; avoid per-frame full client rewrite → orphan/upload if UMA-friendly persistent mapping
or shared storage is available through Qt RHI Metal backend.

### 2. TBDR / tile constraints still bite
Even with UMA, **tile-based deferred** Apple GPUs punish random large buffer traffic and
CPU-driven per-frame full VB rewrites. Scrub regime (EVD-0003) is the stress case: every frame
dirty → persistent-VBO skip-on-unchanged does **not** help; need **windowed/dirty-rect** vertex
rebuild or GPU-side sample fetch.

### 3. Offscreen / headless Metal gap (Migx-specific)
`coreservices` still forces **OpenGL** for offscreen. Metal switch remains gated on offscreen
render parity — field work on “Metal-first” pipelines does not remove that Migx constraint.
**GUI-attached EVD** for scrub half remains the honest gate (as MTL dossiers already state).

### 4. Do not confuse MLX/MPS hype with deck waveforms
Much 2026 AS signal is **MLX/MPS inference** (zero-copy for models). Useful analogy for UMA
discipline, **not** a drop-in for allshader waveform nodes. Keep GPU work off the audio deadline
(**P-21**).

### 5. GL retirement still HOLD
PLT Wave 3 matrix: live base classes under `deprecated/` — **no bulk delete**. Metal/allshader
parity first.

## Recommended Claude/MTL next (Grok does not implement)
1. Complete EVD-0003 **GUI half** (or offscreen GL harness) for scrub combined cost.  
2. Design Wave N: **reduce dirty rebuild** (sliding window / partial vertex) before raw Metal API.  
3. Spike Qt RHI Metal backend with offscreen plan — don’t flip default until offscreen green.  
4. Leave DSP-EQ SIMD parked unless new EVD shows budget pressure.

## Out of scope for this brief
`src/**` edits; DSP Wave 2 NO-GO re-litigation (Claude/Codex lane).
