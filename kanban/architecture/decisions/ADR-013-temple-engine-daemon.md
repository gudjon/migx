---
id: ADR-013
type: decision
title: "Temple Engine is a daemon — its own clock, its own priority, one node contract"
status: proposed
owner: gudjon
created: "2026-08-18"
lastUpdated: "2026-08-18"
supersedes: []
amends: [ADR-011]
related: [ADR-010, ADR-012, P-02, P-11, P-21, P-34]
---

# ADR-013 — the engine is a daemon

**Status: proposed.** The daemon and the node contract are straightforward. **Publishing an SDK is
not** — an ABI other people build against is a promise you cannot take back, and that half needs an
explicit yes.

## Decision

`temple-audio` is a **long-lived background process**, not a child the TUI spawns.

| Property | Consequence |
| --- | --- |
| launchd-managed | starts on demand or at login; survives every client |
| owns the clock | the transport is *its* clock; clients subscribe (`P-21`) |
| owns I/O | master · cue · zone · device hotplug |
| RT priority | `.userInteractive` QoS, audio workgroup, **App Nap disabled** |
| knows nothing | no songs, no crates, no ISRC, no DB, no policy, no agents |

**Why a daemon rather than a subprocess:** it changes what a crash means. A spawned child dies with
its parent, so a TUI restart is a silent gap. A daemon means the TUI can crash, be upgraded, or be
quit — and the music does not stop; the next client **reattaches to the graph that is already
running**. That is the strongest version of the crash law, and it is only available if the engine
outlives its UI.

It also removes a whole class of bug: nothing about resource priority, device selection, or clock
drift depends on which client happened to launch first.

## The Bitwig lesson: one node contract, NOT a patching engine

Bitwig's insight is that *everything is a module with the same interface* — unification, not a cable
UI. Take that:

    node contract:  prepare(format) · render(frames) · params(atomic)
    everything is one:  deck · transition bed · FX · zone · analysis tap

A deck stops being a special case, which is what makes slots (A/B/C/D), a return, and a second-room
zone the same object at different positions rather than three code paths.

**Explicitly not taken: a user-facing modular DSP graph.** A patchable Grid puts a graph compiler and
arbitrary user topology on the audio deadline, and it is a different product — one that competes with
Bitwig rather than with Rekordbox. `P-02` does not bend for a feature. The internal graph is fixed and
small; modularity lives at the **plugin boundary**, out of process, where a crash is survivable
(`ADR-011`).

## The SDK — deliberately unpublished at first

The protocol is already named: `temple.intent/1` in, `temple.taps/1` out, `temple.audio/1` for plugin
buffers. Calling that an SDK adds one thing — **a promise not to break it.**

So: version it from day one, document it, build the first plugins against it *ourselves* — and do not
publish until `AUD` has shipped and the shape has survived contact with a real night. An ABI with
third parties on it cannot be moved, and the fastest way to freeze the wrong design is to publish it
before the second implementation exists.

The reference implementation is the honest test: if `migx-analyze` and a transition player both fit
the plugin contract without special-casing, it is ready. If either needs a private hook, it is not.

## What this does not license

- **Not a DAW.** No arrangement, no piano roll, no user-patchable DSP.
- **Not a service.** No network listener, no LAN trust. Any Link/clock-out is a hostile-network
  surface (`ADR-011`).
- **Not always-on by default.** A daemon that runs when no one is DJing is a battery complaint. It
  starts on demand and idles cheaply, or it is not welcome on a laptop.
- **Not a place for policy.** Permission classes stay on the command table. The engine refuses
  malformed intents; it does not know what an agent is.

## Resolved — one daemon per user, and TWO scopes of authority

**One daemon per OS user.** Not system-wide: everything it owns is already per-user (device selection,
library root, the lock), and a global daemon would have to arbitrate between users for one master
output. Arbitration needs an authority above both — a system service, meaning root, the launchd system
domain, TCC prompts for the music folder, and a new attack surface. Real cost, and it buys nothing:
nobody DJs two sets on one laptop.

The failure it avoids is specific. The daemon owns **hardware** — one device, one master. If two
clients attached, whoever last set the crossfader would win **silently**: no error, just a fader moving
on its own mid-set. That is the `P-34` shape at the worst possible moment.

### The part the question was hiding

*Per user* and *per session* are not the same thing: one user can open two terminals against one
library. So which thing is the lock?

**Two scopes, deliberately not overlapping:**

| Authority | Guards | Exists when | Held by |
| --- | --- | --- | --- |
| **library lock** | Collection mutations — ingest · adopt · rename | always, daemon or not | the lock file (`sessionlock`, built) |
| **playback authority** | decks · master · cue | only while playing | the **daemon itself** |

The daemon does not need a lock file to prove it owns playback — **its existence is the claim**, and
binding to the audio device is the enforcement. Adding a second file that also says "playback is mine"
would be two authorities over one fact, which is exactly the defect the lock was written to prevent.

Equally, the library lock must **not** grant playback, and the daemon must **not** guard ingest. A
prep session mutating the library while nothing plays is legitimate and must not require a daemon; a
running daemon must not block a library command that touches no deck.

### What this changes in already-shipped code

`sessionlock` (pid + start time, stale detectable) is correct and stays — but its **scope narrows to
the library**. Its docstring currently says "one live Migx session per OS user", which under this ADR
over-claims: it guards the library, not the night. Narrow the wording when `AUD` lands, so the two
authorities are named where each is enforced.
