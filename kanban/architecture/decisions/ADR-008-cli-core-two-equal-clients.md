---
id: ADR-008
type: decision
title: "CLI core as the product spine — one command surface, two equal clients (DJ UI + agents)"
status: accepted
owner: gudjon
created: "2026-08-07"
lastUpdated: "2026-08-07"
supersedes: []
amends: []
related: [ADR-005, ADR-006, ADR-007, arch-cli-commands, arch-control-messaging, arch-qml-ui, headless-sim-ground-truth-agentic-cli, output-verification-formats-naming, P-06, P-07, P-11, P-27]
---

# ADR-008 — CLI core as the spine, two equal clients

## Context

The owner set the direction (2026-08-07): Migx is architected so the **UI is built
on top of a powerful CLI layer**, and that layer serves **two consumers equally** —
(a) the DJ human interface, (b) the agentic interface (Claude Code, Codex, Grok).
Neither may be a second-class client.

Two things on disk pointed the other way and are reconciled here:

1. `headless-sim-ground-truth-agentic-cli.md` §7 recommends **deferring** the
   product CLI to "W4 / optional", treating it as a dev sensor behind a test
   harness. That phasing is superseded for the *command surface* (the sim
   scenario harness recommendation stands on its own merits).
2. The 16 bounded contexts all map 1:1 onto inherited Mixxx `src/` directories.
   Nothing covered `tools/`, so a CLI had **no home in the map** and would have
   grown ad hoc by default.

The grain already existed: ADR-007 invariant #2 mandates that QML views are dumb
and emit *intent*, binding the engine only through typed proxies over the
ControlObject bus. This ADR extends that one layer down and makes the intent
surface first-class and addressable.

## Decision

1. **The command surface is the product spine.** The DJ UI/TUI and agents are two
   **adapters** over one command layer. A capability reachable from the UI must be
   expressible as a command, and vice versa.

2. **The CLI is not a new domain.** It is an application/interface layer over the
   existing 16 contexts. It gets exactly one bounded context today
   (`arch-cli-commands`, owning `tools/migx-cli/`). No context is invented for code
   that does not exist yet.

3. **Four interface kinds.** Every command is exactly one of:

   | Kind | Semantics | Naming | Example |
   | --- | --- | --- | --- |
   | `command` | mutates state; routed through a single writer | `<noun>.<verb>` imperative | `playlist.pull` |
   | `query` | pure read, no side effect | `<noun>.<verb>` | `library.missing` |
   | `event` | engine → client push, subscription | `<noun>.<past-participle>` | `deck.loaded` |
   | `capability` | introspection of the surface itself | — | `system.capabilities` |

   `capability` is what makes the agent a first-class client rather than an
   afterthought: the UI ships with hardcoded knowledge of the API, an agent must
   **discover** it. Without this kind, "fits both equally" is false on day one.

4. **Nouns come from ubiquitous language, not invention.** The `<noun>` in a
   command id MUST appear in some bounded context's ubiquitous-language table.
   The namespace maps to a **context**, never to a `src/` path, so it survives
   refactors. Inventing a parallel vocabulary beside the DDD one is two truths
   (MG-3) and is already forbidden for agents by `P-11`.

5. **Schemas extend the existing artifact convention.** `migx.<artifact>/<N>`, as
   established in `output-verification-formats-naming.md`
   (`migx.song-ontology/1`, `migx.sim-scenario/1`). The API surface is versioned
   as a whole (`api_version`), not per command.

6. **Single writer survives the second client (`P-06`).** The UI and the CLI must
   not both `set()` the same `[Group],key`. Both route through one command handler
   that owns the write. Two adapters, one writer.

7. **The CLI never touches the audio callback.** Commands cross to the engine
   lock-free (`P-16`); nothing in the command path may allocate, lock, or block on
   the RT thread (`P-02`).

8. **Machine output on stdout, human prose on stderr**, and `--json` accepted on
   either side of the subcommand — so an agent can pipe stdout without filtering.

9. **Audio location is a resolver interface.** A resolver answers where the
   audio for an identity lives; output **always** passes the quality gate —
   no resolver self-certifies. Core ships `local-files`. See
   `tools/migx-cli/README.md`.

10. **Quality is a contract on the file.** True 320 CBR or lossless is eligible
    for the library index by default; anything else needs an explicit override
    (DJ stretch/EQ needs solid masters).

## Consequences

**Good.** Agents and the UI cannot drift, because they consume one surface.
`system.capabilities` means a new command is immediately usable by Codex/Grok
with no prompt update. Schemas are diffable, so the acceptance contract for a
command is machine-checkable (`P-09`).

**Cost.** Every UI capability now needs a command id and a schema — real
discipline, and it will feel slow the first few times. The vocabulary lint
(below) will reject convenient-but-wrong names.

**Risk.** Without enforcement, "equally" decays to UI-first within two sprints.
Mitigated by the closed loop:

- `kanban/architecture/lint/verify-command-vocabulary.py` fails when a command
  noun appears in no ubiquitous-language table, or when a command declares an
  unknown kind.
- The manifest is generated from the code, so it cannot describe a command that
  does not exist.

**Deliberately deferred.** The `event` kind is specified but unimplemented — there
is no push channel yet. The C++-side application layer (where `P-06` single-writer
routing will actually live) is not built; today's CLI reads metadata and touches
no ControlObject. When it lands it becomes a second context, not a rename of this
one.

## Alternatives rejected

- **Thin CLI shell directly over ControlObject.** Cheapest, but agents inherit a
  flat untyped `double` bus designed for widgets: no discovery, no schemas, no
  multi-key atomic intent. The agentic client would be second-class by
  construction — exactly what the owner ruled out.
- **Separate agent RPC beside the UI's path.** Two control planes, guaranteed
  drift, and a direct `P-06` violation.
- **Deferring the CLI behind the sim harness** (the prior §7 phasing). Rejected as
  the ordering for the command surface: the UI would be built first and the CLI
  retrofitted, which is how the second client becomes second-class.
