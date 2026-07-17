---
id: ADR-001
type: decision
title: "A top-level justfile orchestrates tasks; the upstream C++ tree is not restructured"
status: accepted
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
supersedes: []
---

# ADR-001 — Task orchestrator (`justfile`), and no restructuring of the upstream tree

## Context
Migx is an **upstream-tracking fork** of Mixxx (the Cursor-from-VS-Code model). A structure review
(against modern-CMake / large-Qt-app references, with Turborepo-inspired framing for the QML/JS
frontend) found the layout already sound and matching best practice: domain-oriented `src/`, isolated
`lib/` vendored deps, partitioned `res/` frontend assets, a rich `.pre-commit-config.yaml`, and ccache/
sccache already wired in CMake. The real gap is **orchestration**: no single entry point, and some
frontend linters (`qmllint`/`qmlformat`) are `stages: [manual]` so a normal `pre-commit run` skips them.

The forcing constraint: **anything that moves or restructures upstream-owned files (the `src/` layout,
the monolithic `CMakeLists.txt`, `res/`, `lib/`, config files, `tools/`, `packaging/`) creates merge
conflicts against every future upstream pull** — destroying the fork's most valuable property
(`fork_delta` tracking). So improvements must be **additive**.

## Decision
1. Add a **top-level `justfile`** as a thin command layer over the existing build (CMake) and quality
   gates (pre-commit). It is NOT a build system (CMake is) and adds no competing dependency/cache
   engine. It encodes the task graph: `configure → build → {test, bench}`; independent `lint`,
   `lint-frontend`, `kanban-lint`; `ci = lint + test + kanban-lint`.
2. Surface the **frontend as a first-class workspace** via `just lint-qml/lint-js/lint-qss/fmt-qml`
   recipes that call the already-configured tools (no new config).
3. Choose **`just` over Taskfile/Make**: `just` is a command runner (terse, Make-like) appropriate for
   wrapping an existing build; Taskfile's checksum/watch engine would duplicate ccache + CMake's own
   dependency tracking.
4. **Do NOT** impose an `include/`+`src/` header split, rename subsystem dirs, move `lib/`→`third_party/`,
   reorganize `res/`, or split the monolithic CMake wholesale. These are explicit non-goals.

## Consequences
- One memorable entry point (`just build`/`test`/`lint`/`kanban-lint`/`ci`); hidden frontend linters
  become discoverable and runnable locally, closing the loop before CI.
- Caching is unchanged and already optimal (ccache/sccache for C++, pre-commit's own hook cache) — the
  `justfile` documents/surfaces it (`just doctor`) rather than adding infra.
- Zero upstream-merge risk: every change is a new root/`kanban`/`.claude` file. The only future
  collision would be upstream itself adopting `just` (unlikely).

## Alternatives considered
- **Taskfile.yml** — rejected: duplicates CMake/ccache with its own engine (structure review, cited refs).
- **Makefile** — rejected: upstream may use `make` semantics; a `just` file avoids ambiguity and is terser.
- **A full dossier** — rejected: a `justfile` + docs changes no runtime behavior and has no benchmark to
  pin, so a dossier (with EARS PSes + verifiability gates) would be ceremony. An ADR is the right home.

## Deferred / needs owner sign-off (not decided here)
- Splitting Migx-specific CMake test/bench targets into an `include()`d file (touches the build — med risk).
- Adding frontend lint to a **CI** workflow (vs the local recipe) — CI policy.
- A `.editorconfig` — only if upstream doesn't own one.

SSoT for the orchestrator: `/justfile`. Structure review provenance: the prep round, 2026-07-17.
