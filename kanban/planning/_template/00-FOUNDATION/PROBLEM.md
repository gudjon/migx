# Problem

*Prose. Why this bet exists — the reader should finish knowing what's wrong, for whom, and what
"done" looks like. The machine-checkable spec lives in the `PS-<PFX>-*.md` files; this is the human
framing.*

## What's wrong today
<The current-reality gap. For a perf dossier: what is slow, on what hardware, measured how, versus
what it should be.>

## Who feels it
<The user/persona, or the subsystem. E.g. "a DJ scrubbing a loaded waveform on an M4 MacBook sees
dropped frames.">

## What "done" means (the bet)
This dossier is a bet with three parts (MG-1 / MG-5):
1. **The problem is real** — <evidence: a baseline benchmark `EVD-*`>.
2. **The approach works** — <the hypothesis>.
3. **The gates catch failure** — <the benchmark/test that would fail if we regressed>.

## Non-goals
<What this dossier explicitly does NOT do — keeps scope full-capability but bounded.>

## Inheritance
<Patterns/ADRs/prior dossiers this builds on, by typed ID. Cite, don't restate (MG-3).>
