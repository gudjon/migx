---
description: "Single source of truth — one canonical home per fact; derive don't restate; cite don't copy"
---

# Rule — single source of truth (MG-3)

Every load-bearing fact has exactly **one canonical home**. Everything else points at it.

- **Derive, don't restate.** Never store a value another file/query/git can derive. No hand-maintained
  status a lint could compute. Dossier `phase`/`sealed` are derived from git, not trusted from a field.
- **Cite, don't copy.** A doc that depends on another declares `defers_to:` and links — it does not
  duplicate the text. Two copies of a rule is two truths that drift.
- **Reference by typed ID, never prose.** Cite `P-02`, `PS-ASI-01`, `ADR-003`, `arch-engine-realtime` —
  never "the audio-thread thing." Prose references can't be lint-checked and rot silently.
- **Anchor vs. name.** `P-NN`/`AP-NN` are immutable anchors used in code/commits/grep; human names are
  display-only aliases. Never invent your own anchor number.

## The homes (where each fact lives)
| Fact kind | Home |
|---|---|
| House code physics | repo-root `AGENTS.md` |
| Operating doctrine | `kanban/AGENTS.md` + `kanban/playbook/` |
| A recurring approach / named failure | `kanban/patterns/` (`P-NN`/`AP-NN`) |
| A path-pinning decision | `kanban/architecture/decisions/` (ADR) |
| A bounded context / its invariants | `kanban/architecture/ddd/` + `src/<domain>/AGENTS.md` |
| Durable technical/product research or synthesis | `kanban/knowledge/` |
| A unit of work | a dossier in `kanban/planning/` |
| Chronology / history | `git log` (no ledger files) |

## The deletion test
For any artifact ask: *would removing it make the team faster with no loss of safety?* If yes, delete
it or fold its substance into a surface that already exists. Memory decays, it does not only grow.
