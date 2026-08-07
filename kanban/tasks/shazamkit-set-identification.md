---
id: shazamkit-set-identification
type: task
title: "ShazamKit set identification — DJ set audio to timestamped ISRC tracklist"
status: open
owner: gudjon
priority: medium
initiative: initiative-ai-djing-product
authored_by: claude-code
authored_kind: agent
triggered_by: "Gudjon asked whether ShazamKit can identify tracks in a DJ set
  mp3/wav; deferred to roadmap while the individual-song path lands first"
created: "2026-08-07"
lastUpdated: "2026-08-07"
acceptance: |
  `set.identify <audio-file>` emits migx.setlist/1 with one entry per matched
  track carrying isrc, title, artist, matchOffset (seconds into the set) and
  confidence; the output feeds `library.missing` unchanged so an identified
  set produces an ISRC-keyed want-list. Verified against a real mixed set with
  at least one pitched track.
---

# ShazamKit set identification

Deferred, not rejected: the individual-song path (Spotify identity → mirror →
want-list) lands first. This card exists so the API research is not re-done.

## Why it fits Migx specifically

`ADR-006` pins the platform to **Apple Silicon / macOS 26+**, so a macOS-only
framework carries no cross-platform cost here. Verified against the SDK headers
on this box (macOS 26.2, `MacOSX.sdk`), not from documentation:

| Need | API | Availability |
| --- | --- | --- |
| Identify from a **file**, no mic | `SHSignatureGenerator.generateSignatureFromAsset:` | macOS 13+ |
| Stream buffers instead | `SHSession matchStreamingBuffer:atTime:` | macOS 12+ |
| **ISRC** on the match | `SHMediaItem.isrc` | macOS 12+ |
| **Where** in the set | `SHMatchedMediaItem.matchOffset` | macOS 12+ |
| Confidence score | `SHMatchedMediaItem.confidence` | macOS 15.4+ |
| **Pitch/tempo deviation** | `SHMatchedMediaItem.frequencySkew` | macOS 12+ |
| Match against *your own* library offline | `SHCustomCatalog` | macOS 12+ |

`frequencySkew` is the reason this is viable for DJ sets rather than only for
radio: it reports how far the matched audio was pitched, which is exactly what
a DJ does to a track. `matchOffset` is what turns a match list into a
*timestamped* tracklist.

## Why it is the right shape for the product

It is identification, not acquisition — no audio is copied or redistributed, so
it sits cleanly on the legitimate side of the line the CLI already draws
(`tools/migx-cli/README.md`). Output is ISRC-keyed, so it feeds the existing
`migx.want-list/1` path with no new plumbing: *set → tracklist → what I don't
own → buy*.

It also feeds the co-pilot moat directly (`kanban/Strategy-Current.md`): a
corpus of what good DJs actually play together is stronger signal than the
audio files themselves.

## Open questions before building

- **Account service**: catalog matching requires the ShazamKit App Service
  enabled on the Apple Developer account, plus its terms. Confirm commercial
  terms before this becomes a shipped feature rather than a local tool.
- **Bridging**: ShazamKit is ObjC/Swift; Migx is C++/Qt. Needs a small
  ObjC++/Swift helper. Decide binary-shelled-out (matches the stdlib-only CLI
  posture) vs linked into the app.
- **Accuracy on real mixes**: layered/EQ'd/pitched tracks and long blends are
  the hard case. Measure hit rate on a known set before promising it.
- **Rate/latency** for a 2-hour set: chunking strategy, and whether one
  signature per N seconds beats one signature for the whole asset.

## Related

- `tools/migx-cli/README.md` — the loop this plugs into
- `kanban/knowledge/spotify-octave-style-doable-steps.md` — the line on
  acquisition vs identification
- `ADR-006` — Apple Silicon / macOS platform floor that makes this cheap
