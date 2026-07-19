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

## Readiness status (2026-07-19) — **buildable; use bundle binary**

| Check | Status |
|---|---|
| Host macOS 26+ arm64 | ✅ |
| `build/` Ninja + RelWithDebInfo + arm64 + deploy 26.0 | ✅ |
| Qt6 via `buildenv/mixxx-deps-…/arm64-osx-min1100` | ✅ |
| `build/migx.app/Contents/MacOS/migx` arm64 exists | ✅ fresh after `just build` / `cmake --build build --target mixxx` |
| `build/mixxx` arm64 exists | ⚠️ legacy standalone path; may be stale in this bundle build |
| `compile_commands.json` → `build/` | ✅ |
| Prefer | `just build` / `just test` (see root `justfile`) |

If configure fails (missing buildenv): `source tools/macos_buildenv.sh setup` then `just configure`.

## Get running (Claude / implementer DRI)

```bash
cd /Users/gudjon/code/migx   # main checkout — not migx-grok/codex worktrees for first rebuild
git pull --ff-only
just build                   # configure (idempotent) + parallel build
file build/migx.app/Contents/MacOS/migx | grep arm64
build/migx.app/Contents/MacOS/migx --version
open build/migx.app          # GUI dogfood from an interactive macOS session
build/mixxx-test --gtest_filter='TrackDAOTest.*:EngineBufferTest.*'
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
- [ ] **Fresh** binary at current HEAD: `file build/migx.app/Contents/MacOS/migx | grep arm64` after rebuild.
- [ ] CLI smoke: `build/migx.app/Contents/MacOS/migx --version` exits 0.
- [ ] Focused smoke: `build/mixxx-test --gtest_filter='TrackDAOTest.*:EngineBufferTest.*'`.
- [ ] Broad `ctest --test-dir build -R 'Engine|Track'` only after the focused gate; this pattern is not cheap and can select controller/track-adjacent tests.
- [ ] `benchmark::benchmark` / `just bench` when measuring (`P-03`).
- [ ] `pre-commit` on changed files before commit.

**Handoff:** `kanban/federation/signal/2026-07-19-get-running-macos-build-claude.md`

## Dev launch recipe (avoid false first-run fails)

```bash
# From repo root after just build:
mkdir -p /tmp/migx-dogfood
open build/migx.app --args --developer \
  --settings-path /tmp/migx-dogfood \
  --resource-path "$(pwd)/res"
```

- **Bundle path**: use `build/migx.app/Contents/MacOS/migx` or `open build/migx.app`; `build/mixxx` can be stale.
- **`--resource-path`**: keeps skins/keyboard/maps resolving from repo `res/` during local dogfood.
- **`--settings-path`**: isolates dogfood from a bad `~/Library/Application Support/Mixxx` DB.
- **JACK `dlopen` errors**: ignore unless you need JACK (Core Audio is the AS default path).
- Logs: `$settings-path/mixxx.log` — grep Critical/Error after any dialog.
- Known bug: keyboard fallback misses `keyboard/` subdir (see signal 2026-07-19-launch-failure-analysis).

See also: `kanban/federation/signal/2026-07-19-launch-failure-analysis-for-claude.md`
