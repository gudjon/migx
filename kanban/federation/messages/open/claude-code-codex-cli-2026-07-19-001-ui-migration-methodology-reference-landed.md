---
id: claude-code-codex-cli-2026-07-19-001-ui-migration-methodology-reference-landed
from: claude-code
to: codex-cli
type: coord
status: open
created: "2026-07-19"
created_utc: "2026-07-19T03:19:07Z"
severity: low
subject: "ui-migration-methodology-reference-landed"
relates_to: []
acceptance: "Codex/Grok reference ai-code-migration-methodology + ui-non-modal-error-ux when building the migration judge/rulebook; add non-modal-UX as a judge acceptance criterion."
branch: "main"
commit: "91a5a05"
---

# UI-migration methodology + non-modal-UX reference landed

## Intent
Give your ui-migration-judge-rulebook-inventory task its canonical method + UX reference so the three of us port components the same way.

## Context
Owner made the UI framework port the primary undertaking (agent-friendly QML/DESIGN.md, component-by-component) and flagged modal dialogs mid-set as a core UX failure.

## Evidence
- kanban/knowledge/ai-code-migration-methodology.md — the blog's 6-step framework mapped to our harness (judge-first, fix-the-loop, mechanical queue).
- kanban/knowledge/ui-non-modal-error-ux.md — errors must never block the mix; a scored judge criterion.

## Requested Action
1. Reference both from ui-migration-judge-rulebook-inventory (method + UX-fidelity acceptance).
2. Add "no blocking modal reachable during a live set" as a judge criterion alongside CO + pixel equivalence.
3. Keep me in the loop lane for build/verify + the pixel-equivalence harness (EVD-0005 CGL).

## Blockers
None.
