---
id: migx-ddd-context-map
type: context-map
title: "Migx context map — the RT signal chain and the control bus that crosses everything"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/architecture/README.md
  - kanban/architecture/DDD-BUILDOUT-PLAN.md
---

# Context map — the RT signal chain

Migx's load-bearing axis is the **real-time audio boundary**, so the context map reads as a signal
chain, not a deployment topology. One clock originates it; one bus crosses every context.

```
                 arch-control-messaging  (src/control/, thread_domain: any)
                 the string-keyed [Group],key bus — crosses EVERY context below
          ┌───────────────┬───────────────┬───────────────┬──────────────┐
          │ (lock-free    │               │               │              │
          ▼  atomic read) ▼               ▼               ▼              ▼
 arch-sources ─► arch-mixer-decks ─► arch-engine-realtime ─► arch-audio-io ─► device
   -decode        (src/mixer/)         (src/engine/)          (src/soundio/)
  (worker)     creates EngineChannel   process() graph      SoundManager callback
                nodes for the engine   mixes master buffer   ORIGINATES the RT thread
                                              │
                                              └─► arch-waveform-render (src/waveform/)
                                                  lock-free VisualPlayPosition tap,
                                                  rendered on the DISPLAY clock
```

## The RT clock originates in soundio, not engine
`arch-audio-io`'s `SoundManager` opens the device and its backend callback (`callbackProcess`) is the
**deadline source**. The engine's `EngineMixer` registers as an `AudioSource`; the callback *pulls* the
master `CSAMPLE` buffer from it. So `process()` runs *inside* the audio callback — data flows engine→
soundio, but the clock flows soundio→engine. Seam: `boundaries/engine-to-soundio.md`.

## The mixer straddles the boundary
`arch-mixer-decks`'s `PlayerManager` constructs every `Deck`/`Sampler`/`PreviewDeck`/`Microphone`/
`Auxiliary` on the **GUI thread** (Qt object tree, `parented_ptr`) and hands each one's `EngineChannel`
to the engine by pointer. Player lifecycle is GUI; channel processing is RT. This is where Qt ownership
(`P-19`) and the RT-lifetime rule (`P-17`) meet — the hardest ownership seam in the codebase.

## The control bus crosses every context
`arch-control-messaging` is `thread_domain: any` because a `[Group],key` is just an atomic `double`.
The GUI/controllers write; the RT engine reads the `[ChannelN],*` family lock-free inside `process()`.
The identifier is the *string*, so no context ever holds a mutable handle into another — that nominal
coupling is what makes the bus thread-safe. Single-writer (`P-06`) is the invariant that keeps it sane.
Seam: `boundaries/control-to-engine.md`.

## The render tap is deliberately one-way
`arch-waveform-render` samples engine state through a lock-free `VisualPlayPosition` double-buffer and
renders on the **display clock**, never the audio clock. A stalled GPU frame can never gate the audio
deadline — dropping a video frame is fine, dropping an audio buffer is not (`AP-02`). Seam:
`boundaries/engine-to-waveform.md`.

## Why this shape
The two ways a change silently breaks Migx are (1) violating the audio deadline and (2) botching Qt
ownership. Every seam above is drawn to make one of those two failure modes *visible*: the RT contexts
are `rt_safety: hard`, their edges are lock-free handoffs, and object lifetime is pushed off the
callback. Full roster and status: `kanban/architecture/README.md`.
