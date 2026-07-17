# P-08 independent evaluation — EXO transition proof

**Evaluator:** codex-cli drain (`migx-codex-drain.py`) — not the fixture author  
**Verdict:** **PASS**

## Method
- Parse song/session JSON fixtures
- Camelot adjacency: same ring letter, number ±1 (mod 12), or same number major/minor
- Energy: peak track max section energy > track1 outro; peak ≥ cool-down peak
- Proof text must recommend song-02 / 9A; session order must start song-01 → song-02

## Detail
```
keys: song-01-deep-intro=8A, song-02-peak=9A, song-03-cool-down=7A
camelot_adjacent(8A,9A)=True
camelot_adjacent(8A,7A)=True
energy outro1=0.2 intro2=0.35 peak2=0.95 peak3=0.7
VERDICT: PASS — 8A→9A adjacent; energy lift coherent; session order matches proof
```

## Sign-off
Automated structural + harmonic/energy check. Human may still enrich; seal EXO only with this PASS
(or a human override recorded in JOURNAL).
