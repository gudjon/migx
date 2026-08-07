---
id: ADR-008
type: decision
title: "TUI-first product spine - one command core for humans, CLI, and agents"
status: accepted
owner: gudjon
created: "2026-08-07"
lastUpdated: "2026-08-07"
supersedes: []
amends: []
related: [ADR-005, ADR-006, ADR-007, arch-cli-commands, arch-control-messaging, arch-qml-ui, tui-first-agentic-dj-workstation, headless-sim-ground-truth-agentic-cli, output-verification-formats-naming, P-02, P-06, P-07, P-09, P-11, P-16, P-27]
---

# ADR-008 - TUI-first product spine, one command core

## Context

The owner set the direction on 2026-08-07: Migx is a **TUI-first DJ workstation**.
Its application command surface serves the rich human TUI, conventional CLI,
machine-readable automation, and external agents such as Claude Code and Codex.
None may be a second-class client, and none may create a parallel control plane.

Two things on disk pointed the other way and are reconciled here:

1. `headless-sim-ground-truth-agentic-cli.md` §7 recommends **deferring** the
   product CLI to "W4 / optional", treating it as a dev sensor behind a test
   harness. That phasing is superseded for the *command surface* (the sim
   scenario harness recommendation stands on its own merits).
2. The 16 bounded contexts all map 1:1 onto inherited Mixxx `src/` directories.
   Nothing covered `tools/`, so a CLI had **no home in the map** and would have
   grown ad hoc by default.

The grain already existed: ADR-007 invariant #2 mandates that views are dumb and
emit *intent*, binding the engine only through typed proxies over the
ControlObject bus. This ADR makes that intent surface first-class and addressable.
Interaction and visual direction live in
`kanban/knowledge/tui-first-agentic-dj-workstation.md`.

## Decision

1. **The TUI is the primary human product.** `migx` with no command starts or
   resumes the terminal workspace. A later graphical UI is another adapter, not
   the definition of product behavior.

2. **The command core is the product spine.** TUI actions, direct CLI commands,
   JSON automation, agent requests, and future graphical actions route through
   the same application handlers. A capability reachable from one first-class
   adapter must be addressable from the others unless the manifest declares a
   presentation-only concern.

3. **The public adapter contract is pinned.** The intended surfaces are:

   | Invocation | Consumer | Contract |
   | --- | --- | --- |
   | `migx` | human DJ | interactive TUI workspace |
   | `migx <noun>.<verb> ...` | human/script | deterministic CLI |
   | `migx <noun>.<verb> ... --json` | automation | one-shot structured result |
   | `migx --agent` | external agent | long-lived JSONL request/event/receipt stream |
   | `migx mcp-server` | Claude Code/Codex-compatible tools | optional adapter over the same core |

   The final MCP and local transport implementation may evolve. It may not fork
   command semantics or bypass the application handler.

4. **The CLI is not a new business domain.** It is an application/interface layer over the
   existing 16 contexts. It gets exactly one bounded context today
   (`arch-cli-commands`, owning `tools/migx-cli/`). No context is invented for code
   that does not exist yet.

5. **Four interface kinds.** Every surface entry is exactly one of:

   | Kind | Semantics | Naming | Example |
   | --- | --- | --- | --- |
   | `command` | mutates state; routed through a single writer | `<noun>.<verb>` imperative | `playlist.pull` |
   | `query` | pure read, no side effect | `<noun>.<verb>` | `library.missing` |
   | `event` | engine → client push, subscription | `<noun>.<past-participle>` | `deck.loaded` |
   | `capability` | introspection of the surface itself | — | `system.capabilities` |

   `capability` is what makes the agent a first-class client rather than an
   afterthought: the UI ships with hardcoded knowledge of the API, an agent must
   **discover** it. Without this kind, "fits both equally" is false on day one.

6. **Capability discovery is mandatory.** `system.capabilities` is the machine
   entry point for both the TUI and agents. The manifest exposes IDs, kinds,
   arguments, emitted schemas, authority requirements, and current availability.
   An agent must not need source inspection or a prompt update to discover a
   newly shipped capability.

7. **Agent mode is structured and streaming.** `--agent` uses line-delimited JSON
   for requests, accepted/rejected state, events, completion, cancellation, and
   receipts. Every request carries a correlation ID. Human prose never contaminates
   the machine stream. Record/replay uses the same envelopes.

8. **Every mutation returns a receipt.** A receipt identifies the command,
   requester, validated preconditions, outcome, affected entities, and recovery
   or undo information when available. The TUI renders receipts; agents consume
   them. Neither invents its own audit format.

9. **Authority is explicit.** Adapters operate in `observe`, `prepare`, `perform`,
   or `autonomous` mode. Live authority requires deliberate arming, command-level
   preconditions, immediate human takeover, and safe continuation when an agent
   disconnects. Autonomous is observable agent operation, not opaque Automix.

10. **Nouns come from ubiquitous language, not invention.** The `<noun>` in a
   command id MUST appear in some bounded context's ubiquitous-language table.
   The namespace maps to a **context**, never to a `src/` path, so it survives
   refactors. Inventing a parallel vocabulary beside the DDD one is two truths
   (MG-3) and is already forbidden for agents by `P-11`.

11. **Schemas extend the existing artifact convention.** `migx.<artifact>/<N>`, as
   established in `output-verification-formats-naming.md`
   (`migx.song-ontology/1`, `migx.sim-scenario/1`). The API surface is versioned
   as a whole (`api_version`), not per command.

12. **Single writer survives every adapter (`P-06`).** TUI, CLI, agent, MCP, and
   future GUI clients never `set()` the same `[Group],key` themselves. All route
   through one application handler that owns the write.

13. **Agents decide; Migx executes in real time.** Agents may select tracks, plan
   transitions, and schedule intents on musical boundaries. They never operate
   per buffer. Commands cross to the engine lock-free (`P-16`); nothing in any
   adapter or agent path may allocate, lock, or block on the RT thread (`P-02`).

14. **Machine output on stdout, human prose on stderr**, and `--json` accepted on
   either side of the subcommand — so an agent can pipe stdout without filtering.

15. **Acquisition stays out of core, behind a resolver interface.** A resolver
   answers one question (where is the audio for this identity) and its output
   **always** passes the quality gate — no resolver self-certifies. Core ships
   `local-files` only. See `tools/migx-cli/README.md`.

16. **Quality is a contract on the file, not the pipeline.** True 320 CBR or
    lossless is eligible for the library index; anything else needs an explicit
    override. This makes the engineering line and the licensing line the same
    line, because the sources that cut legal corners cannot produce true 320 CBR.

## Consequences

**Good.** Agents and human interfaces cannot drift, because they consume one surface.
`system.capabilities` means a new command is immediately usable by Codex/Grok
with no prompt update. Schemas are diffable, so the acceptance contract for a
command is machine-checkable (`P-09`).

**Cost.** Every product capability now needs a command id and a schema - real
discipline, and it will feel slow the first few times. The vocabulary lint
(below) will reject convenient-but-wrong names.

**Risk.** Without enforcement, the TUI or agent adapter can grow private behavior.
Mitigated by the closed loop:

- `kanban/architecture/lint/verify-command-vocabulary.py` fails when a command
  noun appears in no ubiquitous-language table, or when a command declares an
  unknown kind.
- The manifest is generated from the code, so it cannot describe a command that
  does not exist.

**Current truth and deliberately deferred work.** Today's Python CLI implements a
library/preparation subset, one-shot `--json`, and a multi-mode stdlib curses TUI
launched by `tools/migx-cli/migx-tui`. The TUI reads a pure snapshot and is tested
without a terminal; its Library/Arrange/Prep/Track views include analyzed metadata,
cues, notes, sparklines, a track heatmap, and Deck transition support. The no-command `migx` launch,
three-column workspace, `--agent`, events, receipts, MCP adapter, and C++
application/engine bridge are not built. Documents must call those planned until
code and gates exist. Deterministic simulation is the gate for live engine
authority, not a reason to defer the TUI or public command surface.

## Alternatives rejected

- **Thin CLI shell directly over ControlObject.** Cheapest, but agents inherit a
  flat untyped `double` bus designed for widgets: no discovery, no schemas, no
  multi-key atomic intent. The agentic client would be second-class by
  construction — exactly what the owner ruled out.
- **Separate agent RPC beside the UI's path.** Two control planes, guaranteed
   drift, and a direct `P-06` violation.
- **Graphical UI first, CLI later.** Rejected because it makes automation and
  external agents retrofit presentation behavior instead of sharing the core.
- **Embedded-model-only intelligence.** Rejected because Claude Code, Codex,
  Grok, scripts, and future agents must be able to operate the public surface.
- **Deferring the CLI behind the sim harness** (the prior §7 phasing). Rejected as
  the ordering for the command surface: the UI would be built first and the CLI
  retrofitted, which is how the second client becomes second-class.
