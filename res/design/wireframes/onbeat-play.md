# On-beat play — build note (defers to Grok's research SSoT)

Status: **v1 BUILT** 2026-07-23 (ladder wave 1 — policy compose). Feature family **"On-beat play"** (not
"SmartPlay" — "Smart"/"Automix" clash the Ritual brand). Capability `cap-onbeat-play`. Live in
`DeckTransportModel.togglePlay`; both dev decks arm it (leader = sibling). Owner timebase call only gates
the 3+-deck case; the acceptance benchmark (`PS-OBP-01` phase-error) is the next rung.

> **SSoT boundary (cooperation).** The **design + research SSoT** is Grok's
> [`research-onbeat-play-phase-snap`](../../kanban/knowledge/research-onbeat-play-phase-snap.md) (~475
> lines: φ phase math, Mode A/B, competitive matrix, L1–L4 stack, MIR survey, perceptual ms-error,
> failure honesty, RT physics, `PS-OBP-01` acceptance, build ladder, naming/defaults). **Build from that.**
> This note owns only the **QML/engine-integration lane** (the play-edge policy + the strip indicator).
> (Reconciled after I wrote a duplicate `SmartPlay` draft without checking `kanban/federation/signal/` —
> lesson folded into `FEDERATION.md` lane discipline.)

## The feature (owner)
Press **PLAY** while another deck plays → the deck **seeks so it is already on-phase** with the timebase,
then plays **now** (Mode A, instant) — beat-aligned, default **ON**, immediate auditory reward. Assistive
transport, **not Automix** (ARRANGE still picks *what*; this owns *when it starts*).

## Build plan (Grok ladder wave 1 — policy compose, no new DSP)
At the play edge in `DeckTransportModel.togglePlay()` (GUI thread setting COs; never RT):
```
on Play(B):
  if onbeat_enabled AND another deck A is playing AND grids_ok(A,B):
    if tempo in safe window (|ΔBPM|/BPM < ε, half/double aware): beatsync_tempo / sync
    quantize=1 ; phase-snap seek B to φ(A) (requestSyncPhase / beatsync_phase) ; play=1
  else:
    legacy play(B)          # honest degrade — never a false snap (trust rule)
```
- **Confidence gate** — poor/missing grid → raw play, no false "on-beat" claim.
- **Raw-play escape** — Shift+PLAY (add a `res/design/KEYMAP.md` row if shipped).
- **Default ON** in PERFORM; a settings opt-out (no permanent chrome). Strip shows a quiet `◇ on-beat`.
- COs verified: `[ChannelN]` `quantize`/`beatsync`/`beatsync_tempo`/`beatsync_phase`/`sync_enabled`; seek via `EngineBuffer`.
- **Acceptance** = Grok's `PS-OBP-01`: p95 phase-error < 15 ms at first audible buffer; p95 time-to-audible < 1.5× buffer; 0 underruns; honest degrade. (P-03/P-18 benchmark contract, offline synthetic grids.)

## Blocking owner decision (the one Grok flagged)
**Timebase when multiple decks play** — which deck does B align to? `NOW` (the other/most-recent playing
deck) vs the formal `sync leader`. Identical in the 2-deck default; differs at 3+. This changes the feel →
owner call before the build.
