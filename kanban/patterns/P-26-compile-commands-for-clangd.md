---
id: P-26
type: pattern
title: "Emit compile_commands.json for clangd and agents"
status: active
severity: SHOULD
domain: build
related: [P-15, P-24]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-26 — Emit compile_commands.json for clangd and agents

## Statement
The build emits a `compile_commands.json` compilation database (`CMAKE_EXPORT_COMPILE_COMMANDS=ON`) at
a stable path, so clangd and code-navigating agents resolve includes, macros, and types the way the
compiler actually does. *(Not generated today — this is the target state.)*

## Why
Without a compilation database, clangd and any tool doing semantic navigation fall back to guessing
include paths and defines. In a codebase this size — Qt moc, per-target defines, generated headers —
guessing is wrong often enough that "go to definition" and cross-reference break, which is exactly the
capability `P-15` (trace-before-refactor) depends on. A correct compile_commands.json makes tracing
call paths deterministic for both humans and agents, and lets clang-tidy run with the real flags.

## How to apply
- Set `CMAKE_EXPORT_COMPILE_COMMANDS=ON` in the CMake configure (cache var or preset); the file lands
  in the build dir.
- Symlink or point clangd at it from the repo root (a `.clangd`/`compile_commands.json` at a known
  path) so editors and agents find it without per-user setup.
- Keep it regenerated as part of configure so it never goes stale against `CMakeLists.txt` changes.
- Treat it as build output, not a checked-in artifact.

## Example — wrong
> Agents grep for symbols and read headers by hand because there's no compile database; include
> resolution is inconsistent and clang-tidy can't run with real flags.

## Example — right
> `cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON …` emits `build/compile_commands.json`, linked from repo
> root. clangd resolves the full engine graph; `P-15` traces are exact.

## Detection
Review: no `compile_commands.json` produced by configure; clangd diagnostics dominated by unresolved
includes; tooling that can't find the compile database.

## Cross-references
Enables the exact call-path tracing `P-15` requires; part of the build hygiene alongside `P-24`.
