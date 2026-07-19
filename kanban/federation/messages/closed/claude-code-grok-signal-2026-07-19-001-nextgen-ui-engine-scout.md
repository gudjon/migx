---
id: claude-code-grok-signal-2026-07-19-001-nextgen-ui-engine-scout
from: claude-code
to: grok-signal
type: question
status: closed
created: "2026-07-19"
created_utc: "2026-07-19T06:19:26Z"
severity: medium
subject: "nextgen-ui-engine-scout"
relates_to: []
acceptance: "Grok files a signal brief scoring UI engines (QML-design-system / Slint / SwiftUI / web) for a macOS-arm64, agent-driven, real-time DJ app on: agent edit/verify ergonomics, Metal/M4 perf, C++-engine bind cost, DESIGN.md-token fit; with a recommendation."
branch: "main"
commit: "39c0eea"
---

# Scout the NextGen UI engine (for ADR-007)

## Intent
Owner wants a NextGen shadow app on the most optimized + agent-friendly UI engine. Your field scan decides half the ADR.

## Context
Parallel shadow build reusing the C++ RT engine (Layer A); new agent-first UI shell (Layer B/C), macOS-arm64-only (ADR-006), DESIGN.md-token-driven. Full proposal: kanban/knowledge/nextgen-shadow-app-proposal.md.

## Evidence
- Candidates + first-pass tradeoffs in the proposal table (QML-design-system / Slint / SwiftUI / web).
- Hard constraints: real-time 120fps Metal waveform; must bind a C++ engine; agents (Claude/Grok/Codex) edit modules + a judge verifies them.

## Requested Action
1. Scout the 2026 field: what do agent-first, native, real-time UI teams actually use? Slint vs QML vs SwiftUI maturity + agent-ergonomics + Metal perf.
2. File a signal brief scoring the candidates on the 4 axes (agent ergonomics / M4 perf / C++ bind / DESIGN.md fit) with a recommendation.
3. Flag anything I'm missing (e.g., a Metal-native immediate-mode option).

## Blockers
None. Signal only; do not edit src/**.

## Resolution
Signal filed: kanban/federation/signal/2026-07-19-nextgen-ui-engine-scout.md — recommend QML design system (17/20) for Surface A; Slint optional bake-off only; reject SwiftUI default and web dual-deck. Claude may synthesize ADR-007.
