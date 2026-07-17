# Dogfood — offline co-pilot loop (Layer B prototype)

## Loop
```text
session-mirror.v1.json  +  ontology fixtures
        ↓
  agent reasons (TRANSITION-PROOF / co-pilot)
        ↓
intent-inbox.v1.json  (proposed)
        ↓
  [future] reconciler → ControlObject (P-06) → engine
```

## Rules
- These files are **offline fixtures**. They are not wired to the live Mixxx engine yet.
- Live writes must go through **one ControlObject writer** — never invent a second writer from an agent.
- RT thread must never parse JSON or run the co-pilot (`P-02`).

## Try it
```bash
# after EXO P-08 PASS
cat fixtures/dogfood/session-mirror.v1.json
cat fixtures/dogfood/intent-inbox.v1.json
# Propose: given mirror + session ontology, is intent-001 still legal?
```
