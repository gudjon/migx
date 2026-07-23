# Reference analysis — Serato DJ Pro, Performance view (+ djworx critique)

Second industry reference for the NextGen design gate. Serato is the other market leader; its philosophy
differs sharply from rekordbox — **performance-first, cleaner, less analytical clutter**. Includes the
djworx interface critique (Mark Settle), a respected DJ-tech source, which **directly validates our
low-cognitive-load thesis**.

## What's on the screen
- **Top bar** — deck-layout selector (Vertical / 2·4-deck), REC, FX, SP-6 (sampler), master gain + meter,
  MIDI, SETUP, clock.
- **Deck headers** — deck# · **title** (large) · **artist** · **BPM** · time (elapsed / remaining) ·
  Edit Grid. Note: classic Serato is **BPM-first** — KEY is not prominent in this layout (added later).
- **Signature: vertical parallel RGB waveforms** (center) — the two decks run *vertically side-by-side* so
  the DJ aligns transients visually. Beatmatch-first visual philosophy (vs rekordbox/Traktor horizontal).
- **Big skeuomorphic platters** — virtual vinyl circles with BPM/pitch/elapsed-remaining.
- **Numbered + colour-coded hot cues (1–8)** + loop split (8 cues / 8 loops / mixed).
- **SP-6 sample player** (4 slots × banks A–D), then the mixer row.
- **Browser** — song · artist · album · **bpm** · bitrate · length. Simpler than rekordbox.

## Adopt
- **RGB frequency-coloured waveforms** — Serato pioneered spectrum colouring (low/mid/high). Now table
  stakes; our future waveform module inherits it.
- **Clean, flat aesthetic** — djworx praises "monochrome + Helvetica Bold, flat, no drop shadows /
  vignettes / funky animations." This is exactly our token-driven, un-skeuomorphic discipline.
- **Flexible hot-cue/loop split** — 8 cues / 8 loops / mixed. Adopt configurability for the hotcue module.
- **Track-identity anchor** — deck# · title · artist · BPM · time. Same universal head as rekordbox.

## Reject / diverge — and the djworx critique (cited, and it backs our thesis)
Mark Settle (djworx, "Serato DJ interface — our thoughts"):
- **"A bit busy"** — interface duplicates controller feedback on-screen.
- **Big white platters + oversized BPM are "ill-placed"** and waste screen real estate, "especially on
  13–15\" laptops where real estate is breaking point."
- **No modularity** — commenters want to "build up their own GUI" instead of one-size-fits-all.
- **Core recommendation: "smarter ways to use screen real estate," prioritise vital info over redundant
  hardware duplication.**

Our stance (this is validation, not just critique):
- **Drop the skeuomorphic platter entirely.** A fake jog wheel on a laptop is hardware duplication that
  the djworx piece explicitly calls wasteful. The DJ reads the **waveform + clock**, not a fake vinyl.
- **Modular / composable by design** — our mode-scoped, token-driven, agent-composed layout *is* the
  "build your own GUI, smarter real-estate" answer djworx asks for.
- **Vertical-vs-horizontal waveform** is a deliberate future waveform-module choice; Serato's vertical is
  the beatmatch-first option worth prototyping.
