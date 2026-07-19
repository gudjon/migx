---
id: runbook-build-setup-macos-m4
type: runbook
title: "Build setup + readiness — macOS 26+ Apple Silicon (M4)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-19"
defers_to:
  - CONTRIBUTING.md
  - kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md
  - kanban/knowledge/claude-code-capabilities.md
  - justfile
---

# Build setup & readiness — macOS 26+ · Apple Silicon only

**Product floor (ADR-006):** **macOS 26.\*+** on **Apple Silicon (arm64)** only.  
Intel / Rosetta / Windows / Linux / iOS shipping targets are **unsupported**.

The reference machine profile (also the baseline hardware for every `EVD-*` benchmark record — `P-25`)
and the steps to get Migx build-ready before executing any dossier.

## Machine profile (this laptop)
| | |
|---|---|
| SoC | Apple **M4** — 10 cores (**4 performance + 6 efficiency**) |
| Arch | `arm64` (native — no Rosetta; `P-24`) |
| OS | **macOS 26.2** (build 25C56) — **minimum product OS is 26.0** |
| CMake | Homebrew (`/opt/homebrew/bin/cmake`) |
| Ninja / ccache | present |
| Compiler | Apple clang (via `/usr/bin/c++`) |
| clangd | present — needs root `compile_commands.json` symlink (`P-26`) |

## Readiness status (2026-07-19) — **buildable; binary may be stale**

| Check | Status |
|---|---|
| Host macOS 26+ arm64 | ✅ |
| `build/` Ninja + RelWithDebInfo + arm64 + deploy 26.0 | ✅ |
| Qt6 via `buildenv/mixxx-deps-…/arm64-osx-min1100` | ✅ |
| `build/mixxx` arm64 exists | ✅ but **rebuild if HEAD moved** (e.g. after FSL cues/energy) |
| `compile_commands.json` → `build/` | ✅ |
| Prefer | `just build` / `just test` (see root `justfile`) |

If configure fails (missing buildenv): `source tools/macos_buildenv.sh setup` then `just configure`.

## Get running (Claude / implementer DRI)

```bash
cd /Users/gudjon/code/migx   # main checkout — not migx-grok/codex worktrees for first rebuild
git pull --ff-only
just build                   # configure (idempotent) + parallel build
file build/mixxx | grep arm64
./build/mixxx                # GUI dogfood
ctest --test-dir build -R 'Engine|Track' --output-on-failure
```

Manual equivalent:
```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON -DBUILD_BENCH=ON \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=26.0
ln -sf build/compile_commands.json compile_commands.json
cmake --build build --parallel $(sysctl -n hw.ncpu)
```

## Readiness checklist (gate before executing a perf dossier)
- [x] Host is **macOS ≥ 26.0** on **Apple Silicon** (`sw_vers`; `uname -m` → `arm64`).
- [x] buildenv/Qt present; `cmake` configure succeeds.
- [x] `build/compile_commands.json` exists and is symlinked at repo root.
- [ ] **Fresh** binary at current HEAD: `file build/mixxx | grep arm64` after rebuild.
- [ ] `ctest --test-dir build` smoke (Engine/Track) on current HEAD.
- [ ] `benchmark::benchmark` / `just bench` when measuring (`P-03`).
- [ ] `pre-commit` on changed files before commit.

**Handoff:** `kanban/federation/signal/2026-07-19-get-running-macos-build-claude.md`
