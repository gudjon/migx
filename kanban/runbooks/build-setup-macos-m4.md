---
id: runbook-build-setup-macos-m4
type: runbook
title: "Build setup + readiness on Apple Silicon (M4)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - CONTRIBUTING.md
  - kanban/knowledge/claude-code-capabilities.md
---

# Build setup & readiness — macOS Apple Silicon (M4)

The reference machine profile (also the baseline hardware for every `EVD-*` benchmark record — `P-25`)
and the steps to get Migx build-ready before executing any dossier.

## Machine profile (this laptop)
| | |
|---|---|
| SoC | Apple **M4** — 10 cores (**4 performance + 6 efficiency**) |
| Arch | `arm64` (native — no Rosetta; `P-24`) |
| OS | macOS 26.2 (build 25C56) |
| CMake | 4.1.2 (`/opt/homebrew/bin/cmake`) |
| Compiler | Apple clang 17.0.0 |
| clangd | present (`/usr/bin/clangd`) — symbol navigation ready once `compile_commands.json` exists |

## Readiness status (2026-07-17) — NOT yet buildable
Missing prerequisites (the build will not configure without Qt):
- **Qt6** — not installed (no `brew qt`/`qt@6`, `QTDIR`/`CMAKE_PREFIX_PATH` unset). **Blocker.**
- `ninja`, `ccache` — missing (recommended generator + compile cache).
- `clang-format`, `clang-tidy` — missing (the pre-commit gate needs clang-format 19.1.3).
- `pre-commit` — missing.

## Get build-ready (run these — some need the user; `!` prefix runs a command in this session)
1. **Bootstrap deps (installs Qt6 + libs via homebrew):**
   `source tools/macos_buildenv.sh setup`
2. **Dev tools:** `brew install ninja ccache llvm` (llvm gives clang-format/clang-tidy) and
   `pip install pre-commit`, then `pre-commit install && pre-commit install -t pre-push`.
3. **Configure (arm64-native, emit compile_commands for clangd — `P-26`):**
   ```
   cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
     -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DQT6=ON -DCMAKE_OSX_ARCHITECTURES=arm64
   ln -sf build/compile_commands.json compile_commands.json   # clangd looks at repo root
   ```
4. **Build:** `cmake --build build --parallel 10`  (heavy — the fast loop is `pre-commit`, not this).
5. **Test:** `ctest --test-dir build` (target `mixxx-test`; `BUILD_TESTING` on when GTest is found).

## Readiness checklist (gate before executing a perf dossier)
- [ ] `source tools/macos_buildenv.sh setup` completed; `cmake` configure succeeds.
- [ ] `build/compile_commands.json` exists and is symlinked at repo root (clangd resolves symbols).
- [ ] Build is `arm64` (`file build/mixxx | grep arm64`); NOT x86_64/Rosetta (`P-24`).
- [ ] `ctest --test-dir build` runs; at least the engine + waveform suites pass on a clean checkout.
- [ ] `benchmark::benchmark` bench binary builds/runs (needed for `P-03` contracts).
- [ ] `pre-commit run --all-files` is green (or known-baseline) so the fast gate works.

Until the first two boxes are checked, dossier **execution** is blocked (design/scaffolding is not).
