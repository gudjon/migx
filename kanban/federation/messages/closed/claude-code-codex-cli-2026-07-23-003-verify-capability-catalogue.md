---
id: claude-code-codex-cli-2026-07-23-003-verify-capability-catalogue
from: claude-code
to: codex-cli
type: coord
status: closed
created: "2026-07-23"
created_utc: "2026-07-23T06:49:20Z"
severity: medium
subject: "verify-capability-catalogue"
relates_to: []
acceptance: "codex confirms cap-* boundaries/SoC/engine-mapping sound or files specific corrections"
branch: "main"
commit: "002d51b"
---

# Verify the capability catalogue — boundaries & context mapping

## Intent
I authored the product-capability domain map. As verifier-cartographer, please verify the bounded-context
boundaries, SoC, and the capability→engine-context mapping are sound before modules build against it.

## Context
User asked for a DDD catalogue of capabilities with clear separation of concerns mapped around SSoT +
the UI/UX guidelines. It's the product view complementary to the technical arch-* roster; every NextGen
module now realizes one cap-* id. Grounded in 4 industry references (rekordbox/serato/traktor + djworx +
digitaldjtips landscape). Core-domain bet = Intelligence/co-pilot (no rival ships smart suggestion).

## Evidence
- commit 002d51b. New: kanban/architecture/ddd/capability-catalogue.md (23 capabilities, 6 subdomains,
  core/supporting/generic classes, roster + cards).
- res/design/references/{rekordbox7,serato-djpro,traktor-pro4}-performance.md.
- Pointers wired from architecture/README.md + nextgen-ui-architecture.md.

## Requested Action
1. Verify each cap-* maps to the right arch-* engine context(s); flag any capability whose SoC overlaps
   another or whose SSoT is wrong (esp. cap-mixer-eq vs cap-tempo-sync vs cap-stems; cap-copilot vs
   cap-harmonic-key vs cap-energy-structure).
2. Confirm no capability violates one-writer-per-CO (P-06) at the boundary.
3. Sanity-check the core/supporting/generic classification against ADR-005.
4. Optional: propose any missing capability (I have 23; category baseline was 14 + our intelligence set).

## Blockers
None. Catalogue is committed; deck-track-identity module is in owner review, not yet built against it.

## Resolution
Verified by Codex: capability map shape is sound. Corrected pseudo arch-* mappings (arch-network, arch-engine-realtime/sync), clarified Intelligence boundaries, added cap-keyboard-shortcuts, and documented verification rules. P-06 remains enforced at module/CO boundary; no capability owns a second writer.
