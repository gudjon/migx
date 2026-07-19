---
id: signal-2026-07-19-get-running-macos-build-claude
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [build, macos, arm64, claude-code, dogfood, exo]
mapped_to:
  - kanban/runbooks/build-setup-macos-m4.md
  - ADR-006
  - P-24
  - P-26
method: "Repo readiness audit + prior X product signals; handoff to Claude implementer"
---

# Get Migx running — macOS M4 build handoff (Claude)

**Shift:** signal loops → **compile, run, dogfood**. Claude owns the heavy C++ build on main checkout.

---

## Machine (already green)

| | |
|---|---|
| Host | macOS **26.2** · **Apple M4** · `arm64` |
| Cores | 10 (`sysctl -n hw.ncpu`) |
| CMake / Ninja / ccache | present under Homebrew |
| Configure cache | `build/` exists: **Ninja**, `RelWithDebInfo`, `arm64`, deploy **26.0** |
| Qt6 | via `buildenv/mixxx-deps-…/arm64-osx-min1100` (not brew qt — OK) |
| Binary | fresh bundle binary is `build/migx.app/Contents/MacOS/migx`; legacy `build/mixxx` can be stale |

**Do not** reconfigure unless cache is broken. **Do** incremental rebuild against current `main`.

---

## Recipe (Claude — main checkout only)

```bash
export MIGX_FED_SIDE=claude-code
cd /Users/gudjon/code/migx
git pull --ff-only origin main
git status -sb   # leave peer dirt alone if any; clean preferred

# If configure ever needed (first-time or wiped build/):
# just configure
# or: source tools/macos_buildenv.sh setup   # only if Qt/buildenv missing

just build       # configure (idempotent) + cmake --build -j$(sysctl -n hw.ncpu)
# Or without just:
# cmake --build build --parallel $(sysctl -n hw.ncpu)

# Smoke
file build/migx.app/Contents/MacOS/migx | grep arm64   # P-24 — fail if x86_64
build/migx.app/Contents/MacOS/migx --version           # CLI smoke; exits before GUI init
build/mixxx-test --gtest_filter='TrackDAOTest.*:EngineBufferTest.*'
open build/migx.app                                    # GUI dogfood from interactive macOS session
# Broad later: ctest --test-dir build --output-on-failure
# Full later: just test
```

### Best practices (house + field)

| Practice | Why |
|---|---|
| **Native arm64 only** (`CMAKE_OSX_ARCHITECTURES=arm64`) | `P-24` — Accelerate/vDSP; never Rosetta for perf |
| **Deploy target 26.0** | ADR-006 floor; unlocks OS-26 frameworks later |
| **Ninja + RelWithDebInfo** | Fast rebuilds + usable backtraces |
| **`CMAKE_EXPORT_COMPILE_COMMANDS=ON`** + symlink root | `P-26` clangd |
| **ccache** if not already wired | Field default for large C++ on AS |
| **Parallel = `hw.ncpu`** | M4 10 cores |
| **pre-commit on changed files only** before commit | Fast gate; full build not every edit |
| **No RT edits casually** | House physics; dogfood path is library/UI/EXO first |

X trend (supporting, not blocking): native macOS agent skills emphasize CLI build recipes + native patterns — we already have `just` + runbook; **use them**, don’t invent a second build path.

---

## After green binary — dogfood order (product reality)

Codex already shipped **FSL cues + energy** (`a03a250`). Build enables:

1. **Launch** Migx GUI → load a few local tracks → confirm analysis writes sidecars.  
2. **EXO path:** `just exo-copilot-why` / sidecar recipes → co-pilot with **real** bpm/key/cues/energy (no flat 0.50).  
3. **Settings → Co-Pilot** QML panel dogfood.  
4. Only then: optional session-mirror / live Layer B (still assumption-open per discovery).

### Open research — do **not** block first run

| Item | Priority after green build |
|---|---|
| Dogfood co-pilot on real library | **P0** |
| MusicUnderstanding local-file spike | P1 research (macOS 26 present) |
| AnalyzerEnergy full DSP (if waveform-band energy insufficient) | P2 |
| Discovery live interviews | parallel, not build |
| Spotify OAuth step2 | after dogfood |
| prune-legacy / CI mac-only | opportunistic |

---

## Worktree hygiene

| Tree | Role |
|---|---|
| `/Users/gudjon/code/migx` `main` | **Claude build here** |
| `migx-grok` / `migx-codex` | signal / verify — do not steal Claude’s main dirt |

Claim `build/` surface only if multi-agent collision risk; prefer single Claude DRI for first green rebuild.

---

## Done when (acceptance)

1. `just build` (or cmake build) succeeds at current HEAD.  
2. `file build/migx.app/Contents/MacOS/migx` → `arm64`.
3. `build/migx.app/Contents/MacOS/migx --version` exits 0; GUI launch or dogfood documented separately.
4. Short note in federation status or EXO JOURNAL: commit SHA + wall time + any configure fixes.  
5. Focused `TrackDAOTest.*:EngineBufferTest.*` green; broader `ctest` can follow once the GUI/control-test hang is isolated.

Grok will not edit `src/**` or own the compile; next wave polls for your status.
