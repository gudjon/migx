# Co-pilot — why next (offline Layer B)

**Generated:** 2026-07-17T14:00:30Z
**Current:** `song-02-peak` (local, 9A)
**UX:** Predict → Ask → Explain

## Proposal: `song-04-spotify-uri-only` (score 102.0)

- relation: **sequence-only**
- source: `spotify` · Camelot `10A`
- multi_deck_allowed: False

### Why

- source policy: local→spotify is sequence-only (no dual Spotify multi-deck; multi_deck cur=True cand=False)
- session edge harmonically-compatible: 9A → 10A Camelot +1; agent ranking only — sequence if SP playback later
- session edge sequence-only: Local→Spotify: no dual Spotify stream; hand off to sequential_spotify or play SP alone after local outro
- Camelot compatible: 9A → 10A (self/±1/mode flip)
- energy lift: tail 0.28 → head 0.38 (Δ+0.10)
- matches planned order (next in session.order)

### Ranked alternatives

- → `song-04-spotify-uri-only` score=102.0 (spotify, 10A, sequence-only)
-   `song-01-deep-intro` score=41.0 (local, 8A, harmonically-compatible)
-   `song-03-cool-down` score=20.0 (local, 7A, planned-transition)

### House physics

- Intent status **proposed** — human must ack before any CO write.
- No RT / network / dual Spotify multi-deck from this tool.
