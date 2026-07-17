---
id: P-10
type: pattern
title: "Promote an audio-behaviour change offline → shadow → live"
status: active
severity: MUST
domain: engine
related: [P-08, P-14, P-09, AP-06]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-10 — Promote an audio-behaviour change offline → shadow → live

## Statement
A change to audio behavior is promoted through three stages: **offline** (bench on real signal, no
engine), then **shadow** (runs inside the app but does *not* drive the audio output — its result is
compared, not heard), then **live**. Each stage passes the frozen contract (`P-09`) before the next.

## Why
The audio path is unforgiving: a bug there is an audible glitch in front of an audience, and RT
constraints (`P-02`) mean you can't just attach a debugger. Staged promotion buys observation without
risk — offline proves the candidate beats the current path (`P-14`); shadow proves it behaves
correctly under real engine timing and load *while the old path still drives sound*; only then does it
go live. It turns "sounds smoother, ship it" (`AP-06`) into a loop with a sensor at every stage.

## How to apply
- **Offline:** the `P-14` bench — real signal, tail metrics, correctness vs golden, off the RT thread.
- **Shadow:** wire the candidate into the engine computing its result alongside the live path via a
  lock-free handoff (`P-16`); log/diff its output against the authoritative path, but the old path is
  what's audible. Watch for RT-safety regressions (`P-32`) under real load.
- **Live:** flip the candidate to authoritative only after shadow passes the frozen contract, judged by
  an independent evaluator (`P-08`).
- Keep the old path retrievable (`P-12`) until live is proven.

## Example — wrong
> New EQ curve wired straight to the master output on `main`; judged live by ear in one session
> (`AP-06`).

## Example — right
> EQ candidate: offline bench green (`EVD-*`); run in shadow for a week diffing against the current EQ,
> 0 RT-safety regressions; independent evaluator confirms the contract; then promoted to live.

## Detection
Review: an audio-behavior change that went from branch to live with no shadow stage, or whose shadow
run drove the actual output; promotion without an independent verdict.

## Cross-references
Offline stage is `P-14`; each gate runs `P-09`, judged by `P-08`; shadow crosses via `P-16` and is
watched by `P-32`. Skipping the stages is `AP-06`.
