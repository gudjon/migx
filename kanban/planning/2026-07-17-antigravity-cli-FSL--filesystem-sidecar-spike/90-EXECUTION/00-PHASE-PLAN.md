# Phase plan — FSL

## Wave 1 — additive sidecar export
- [x] Add `TrackDAO::saveTrack()` sidecar export hook.
- [x] Write `<track-location>.migx/track.json` with bpm / key / replaygain / peak.
- [x] Keep SQLite DB path in place; no runtime SSoT flip.
- [x] Verify build and library/track/dao tests per PS-FSL-01 note.

**Gate:** arm64 build green and 95/95 library/track/dao tests green.

## Wave 2 — harden file I/O before seal
- [ ] Gate export to only-on-change; avoid redundant write work on every `saveTrack()`.
- [ ] Add classified logging for open/write failures (`P-34`).
- [ ] Add or update focused unit coverage if a stable hook exists.

**Gate:** focused library/dao tests pass; no RT-thread path touched.

## Wave 3 — EXO handoff boundary
- [ ] Decide whether `ontology.json` extension stays in FSL or moves to an EXO successor.
- [ ] Update `kanban/knowledge/filesystem-driven-architecture.md` only if code reality changes.
- [ ] Draft 91-LOOP-CLOSURE with follow-on owner.

**Gate:** every open end has a task or successor dossier.
