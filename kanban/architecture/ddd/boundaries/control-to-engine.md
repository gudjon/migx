# Seam: control → engine (the control bus into the RT graph)

**Contexts:** `arch-control-messaging` (src/control/) → `arch-engine-realtime` (src/engine/), and the
same mechanism serves `arch-mixer-decks` (src/mixer/).
**Direction:** control is upstream; the engine (and the mixer's players) read it. The engine may also
*write back* status controls it authoritatively owns.

## What crosses
`[Group],key` control values — most importantly the per-channel `[ChannelN],*` family (`play`, `rate`,
`volume`, `pregain`, crossfader/orientation, …). Scalar `double`s, never objects.

## The mechanism
A `ControlObject` (`control/controlobject.cpp`) holds the authoritative value backed by a
`ControlValueAtomic<T>` (`control/controlvalue.h`). RT-side readers hold a `ControlProxy` /
`PollingControlProxy` and read the atomic inside `process()` — **no lock, no allocation, no Qt slot
delivery**. Writers on the GUI/controller side set the value; the atomic store publishes it. The
`[Group],key` string is the entire cross-thread contract — no shared pointers to mutable state.

## The invariant this seam enforces
- **Single writer (`P-06`/`AP-03`):** exactly one context is the authoritative writer of a given key;
  everyone else reads. The engine writes only the status keys it owns.
- **Lock-free value path (`P-16`):** the atomic store is what makes a control readable on the audio
  thread; the object graph (create/connect/destroy) stays off the RT thread (`P-17`).
- **No synchronous slot onto RT (`P-20`/`AP-14`):** proxies respect Qt affinity across the boundary.

## Notes
The identifier is the `ConfigKey` string, so this seam is *nominal* — the engine never holds a handle
into control internals, only a proxy keyed by name. That decoupling is why any thread can safely touch
the bus. See `boundaries/engine-to-soundio.md` for the buffer that leaves the engine.
