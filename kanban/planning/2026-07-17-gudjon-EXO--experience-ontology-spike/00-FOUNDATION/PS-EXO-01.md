---
id: PS-EXO-01
type: problem-statement
prefix: EXO
title: "Agent reasons a legal transition from ontology files alone"
status: open
---

# PS-EXO-01

## EARS
**When** an agent is given only the song/session ontology files for a 3-track set,  
**the system shall** allow it to propose a next-track transition that is  
**harmonically compatible** (Camelot / compatible keys) and **energy-plausible** (from hand-authored curve),  
**without** querying the live engine or RT path.

## acceptance
```yaml
acceptance:
  metric: "fixtures exist; independent evaluator confirms transition proposal cites Camelot compatibility + energy direction"
  measure: |
    Schema + 3 ontology fixtures + session.json under dossier fixtures/
    Written answer in results/TRANSITION-PROOF.md citing keys and energy
    Second agent or human signs P-08 line in 91-LOOP-CLOSURE
  baseline: "no ontology fixtures"
  threshold: "proof file + evaluator sign-off"
```

## Non-goals
Production analyzers; live intent-inbox.
