---
id: copilot-product-assumptions
type: knowledge
title: "Co-pilot product assumptions — declared open (technical-green ≠ product-closed)"
status: active
owner: gudjon
created: "2026-07-18"
lastUpdated: "2026-07-18"
related:
  - product-discovery-customer-leadership-migx.md
  - tasks/discovery-continuous-customer-evidence-loop.md
  - closed-loops-and-tdd-feedback-gaps.md
gate: "codex-cli→claude-code product-discovery-gate-for-capability-uplift"
---

# Co-pilot product assumptions — declared open

The `tools/exo/` co-pilot capabilities shipped this cycle (tempo scoring, sidecar→ontology bridge,
set planner) are **technically green** — tests pass, demos run on real-shaped data. They are **not
product-closed**: every one rests on an untested **desirability** assumption about how DJs actually mix
(DC-PDCL-2.8 / 2.11 / 6.4). No real DJ has evaluated a single suggestion. The rule (per the Codex gate):
`fixture green != product bet closed`. This note is the explicit open-assumption flag those closures
require. Revisit trigger for all of them: the **first real DJ evidence** captured via
`discovery-continuous-customer-evidence-loop`.

| # | Assumption (as-built) | Why it may be false (bad news, DC-PDCL-1.11) | How to test it |
|---|---|---|---|
| A1 | Tempo gaps >15% should be hard-penalized as un-mixable | Some DJs bridge tempo with loops, stems, hard cuts, or halftime rolls; the penalty may be too harsh for DnB/footwork/edits | 10 suggested transitions rated by a real DJ; or accept/override telemetry on proposed transitions |
| A2 | Camelot ±1 harmonic compatibility is a primary constraint (+25) | Many DJs mix by energy/vibe/phrasing, not key; some genres ignore key; key detection is often wrong | DJ evidence on whether flagged "harmonic" transitions actually sound good |
| A3 | DJs want a **proposed re-order** (plan_order) | DJs may want to keep their creative order and only get **warnings** (audit_order), not a machine re-sort | Which mode real DJs use / trust — audit vs plan |
| A4 | "Next track / set order" is the useful co-pilot job | The real friction may be **transition timing / cue points** ("where do I mix out?"), not track selection | DJ interview: what they actually want the agent to do mid-set |
| A5 | Harmonic + tempo + energy is enough signal | Ignores vocal clashes, phrasing/bar alignment, intra-track key drift, crowd read — things DJs weight heavily | DJ evidence on rejected-but-"compatible" suggestions |
| A6 | Learning transitions from a corpus of real setlists (+ trending) improves the pick over local scoring — the [[copilot-transition-intelligence]] bet | DJs prize originality (crowd picks may feel derivative); corpus coverage of an individual crate may be low; setlist-corpus licensing/ToS unresolved; trending can push untested tracks | Real-DJ accept/override on transition-driven vs mixability-only picks; Grok feasibility on obtainable ordered-setlist corpora |

**Scoring posture:** these co-pilot commits are recorded as **technical progress with product
assumptions open**, not product wins. When the customer-evidence loop produces its first captures, this
table gets re-ranked and the co-pilot weights (`score_candidate`, `tempo_compat`) recalibrated against
real DJ behavior — that is the closure, not the passing tests.
