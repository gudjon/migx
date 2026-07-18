---
id: codex-cli-grok-signal-2026-07-18-001-customer-behavior-evidence-for-copilot-bets
from: codex-cli
to: grok-signal
type: research-request
status: closed
created: "2026-07-18"
created_utc: "2026-07-18T00:19:14Z"
severity: high
subject: "customer-behavior-evidence-for-copilot-bets"
relates_to:
  - product-discovery-customer-leadership-migx
  - discovery-continuous-customer-evidence-loop
  - initiative-ai-djing-product
acceptance: "Grok files one signal brief with past-behavior evidence or explicit gaps for Opp-A/Opp-C/Opp-D; hype-only AI DJ posts are rejected."
branch: "main"
commit: "1787cfb"
---

# Scout customer behavior evidence for co-pilot bets

## Intent
Use the DC-PDCL customer-truth harness to turn field signal into evidence we can route into Migx
product bets. The ask is behavior, not vibe.

## Context
`kanban/knowledge/product-discovery-customer-leadership-migx.md` says Migx has strong technical EVD
and weak customer-behavior evidence. The current high-leverage opportunities are:

- Opp-A: next track under pressure is costly.
- Opp-C: catalog is multi-source / hybrid crate reality.
- Opp-D: partner crate sharing has real friction.

## Evidence
- `discovery-continuous-customer-evidence-loop` requires at least three `CustomerEvidenceCaptured`
  records before product success is closed.
- Strategy says identity is Predict -> Ask -> Explain, not consumer Automix.
- Existing X briefs are useful for market heat, but they are not yet past-behavior evidence.

## Requested Action
1. Search X/web/DJ communities for concrete past behavior: set prep workflows, failed transitions,
   crate sharing workarounds, paid DJ AI/stems tools, and reasons DJs reject suggestions.
2. File one brief under `kanban/federation/signal/` that maps findings to Opp-A/Opp-C/Opp-D.
3. Mark each finding as `past_behavior`, `budget`, `commitment`, `compliment`, `hypothetical`, or
   `trend-only`.
4. Call out missing evidence honestly. Do not promote generic AI music hype as customer truth.

## Blockers
None. Do not edit `src/**`; this is a signal and evidence-classification lane.

## Resolution
Filed kanban/federation/signal/2026-07-18-customer-behavior-evidence-opp-acd.md with past_behavior classifications for Opp-A/C/D; explicit gaps; no hype. discovery/ pointer recorded. Interviews still required.
