# Transition proof (files only) — session-3track-demo

**Evaluator note (P-08):** Author wrote fixtures + this proof. Independent sign-off still required
from `codex-cli` or Gudjon before sealing EXO dossier.

## Question
Given only the ontology files, what should play **after** `song-01-deep-intro`?

## Answer
**Next: `song-02-peak`**

## Why (harmonic)
| Track | Camelot | Chromatic |
|---|---|---|
| song-01-deep-intro | **8A** | Am |
| song-02-peak | **9A** | Em |
| song-03-cool-down | **7A** | Dm |

Camelot wheel neighbor rule (also `KeyUtils::getCompatibleKeys` / Lancelot): **8A → 9A** is a
classic +1 energy step (same outer ring, adjacent).  
**8A → 7A** is also adjacent the other way (energy down).  
For a set that should climb, **9A** is preferred.

## Why (energy)
- song-01 outro energy ~**0.2–0.25** (mixable outro).  
- song-02 intro ~**0.35** then climb to **0.95** peak — natural lift.  
- song-03 peaks only ~**0.7** and cools — better **after** the peak track.

## Mix guidance from sections
- Leave song-01 on **outro** (mixable).  
- Enter song-02 on **intro** (mixable).  
- Do not open song-02 on its main drop while song-01 drop is still hot.

## Rejected
Leading with song-03 after song-01: harmonically OK (8A↔7A) but **energy story goes flat** for a
three-track demo that wants a mid-set peak.

## Independent evaluation (P-08)
**Verdict: PASS** — `codex-cli` independently evaluated the fixtures on 2026-07-17.

- `song-01-deep-intro` (`8A`, Am) -> `song-02-peak` (`9A`, Em) is Camelot-adjacent on the minor ring.
- The energy story is coherent: song-01 exits at low outro energy (~0.2), song-02 enters mixably at
  moderate intro energy (~0.35), then climbs to the highest peak in the three-track set (~0.95).
- Schema/data gap: `session-3track-demo.json` labels the later `song-02-peak` -> `song-03-cool-down`
  edge as `harmonically-compatible` while its own note says `9A -> 7A` is not strict-adjacent. That
  does not invalidate the requested `song-01` -> `song-02` proof, but the session edge vocabulary
  should distinguish strict compatibility from planned narrative/cool-down transitions.

## Commands (reproduce listing)
```bash
ls kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/songs/
cat kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sessions/session-3track-demo.json
python3 -c "import json, pathlib; base=pathlib.Path('kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures'); files=list(base.glob('songs/*.json'))+list(base.glob('sessions/*.json'))+list(base.glob('schema/*.json')); [json.load(p.open()) for p in files]; print('json ok', len(files), 'files')"
```
