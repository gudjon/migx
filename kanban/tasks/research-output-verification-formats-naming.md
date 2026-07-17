---
id: research-output-verification-formats-naming
type: task
title: "Output verification — formats & naming at each stage for agent/downstream consumers"
status: open
owner: gudjon
priority: high
initiative: initiative-ai-djing-product
parent_dossier: ""
depends_on:
  - research-headless-sim-ground-truth-agentic-cli
authored_by: grok-signal
authored_kind: agent
queued_by: gudjon
queued_at: "2026-07-18"
triggered_by: "User 2026-07-18 — from headless sim queue: Output Verification — formats/naming at each stage; downstream services must handle correctly"
created: "2026-07-18"
lastUpdated: "2026-07-18"
related:
  - research-headless-sim-ground-truth-agentic-cli
  - closed-loops-and-tdd-feedback-gaps
  - world-model-experience-ontology
  - P-03
  - P-08
  - P-09
  - P-27
acceptance: |
  A knowledge note (kanban/knowledge/output-verification-formats-naming.md) that:
  1. Maps the **pipeline stages** where Migx (and agent harness) emit artifacts — e.g.:
     - Analyzer / Track metadata
     - FSL Song.migx / ontology.json / session JSON
     - EVD-* evidence files
     - mixxx-test / benchmark stdout + JSON
     - Co-pilot COPILOT-WHY-NEXT.md|json + QML fixture mirror
     - Federation messages (frontmatter schema)
     - Sim/headless mix outputs (proposed: golden WAV, metrics JSON) if SIM proceeds
     - CI logs / ctest JUnit (if any)
  2. For each stage: **format** (JSON schema version, WAV sample rate/channels, markdown sections),
     **naming convention** (paths, ids, schema strings like migx.song-ontology/1),
     **writer** (one owner), **readers/downstream** (tests, QML, peers, CI).
  3. Defines **output verification** contracts: machine-checkable validators (schema, fixture check,
     golden hash, filename regex) so agents cannot invent ad-hoc names that break consumers.
  4. Gap list: where formats are informal, dual, or version-skew-prone (e.g. session edges vocabulary).
  5. Recommendations: SSoT schema homes, versioning rules, CI gate (`just verify-outputs` or similar),
     and how this feeds headless sim + Claude TDD (RED = validator fail).
  6. Explicit non-goal: redesign every format in one PR — inventory + contracts first.
loop_queue: true
scout_topics:
  - artifact contracts for agent pipelines
  - schema versioning (JSON Schema $id)
  - golden file naming in audio test harnesses
seed_existing:
  - "tools/exo/check_fixtures.py — EXO structural check"
  - "fixtures/schema/migx.*.v1.json — song/session ontology"
  - "kanban/federation MSG frontmatter — typed messages"
  - "EVD-* frontmatter conventions"
  - "res/qml/CoPilot/fixture_why_next.json mirror of COPILOT-WHY-NEXT.json"
---

# Research — Output verification (formats & naming)

## Intent (user ask)

From the headless-sim / agentic-CLI thread: also queue **Output Verification** —

> Examine **output formats and naming conventions at each stage**, ensuring **downstream services
> handle them correctly**.

This is the **sensor contract for artifacts**: if Claude or a sim stage writes a file, every consumer
(QML, ctest, federation, co-pilot, future CLI) must agree on **path, name, schema, and version**.

## Why it belongs with sim + TDD

```text
Sim / agent stage N  →  artifact (named, typed)  →  stage N+1 / CI / peer
                              ↑
                     output verification (RED if wrong shape)
```

Without this, headless mode and multi-agent federation invent parallel `_v2` names and break the loop
(`P-11`, `AP-10`).

## Stages to inventory (starter list)

| Stage | Example outputs | Downstream |
|---|---|---|
| Engine / decode | PCM buffers (in-test), optional WAV dump | benches, golden compare |
| Analyzer | Track DB fields, future FSL | library, EXO |
| EXO | `*.ontology.json`, `session-*.json` | copilot, QML, agents |
| Co-pilot | `COPILOT-WHY-NEXT.json`, intent inbox | QML chrome, CO reconciler |
| EVD / dossier | `EVD-*.md` | seal, regression |
| Federation | `messages/{open,ack,closed}/*.md` | peers |
| Sim (proposed) | `scenario-*/out.wav`, `metrics.json` | agent TDD, CI |

## Loop instruction

Advance after or in parallel with `research-headless-sim-ground-truth-agentic-cli` — sim design must
**cite** this note’s naming/format contracts; do not invent sim paths before the inventory.

## Deliverable

`kanban/knowledge/output-verification-formats-naming.md`
