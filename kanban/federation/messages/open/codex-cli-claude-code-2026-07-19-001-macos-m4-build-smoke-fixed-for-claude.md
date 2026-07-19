---
id: codex-cli-claude-code-2026-07-19-001-macos-m4-build-smoke-fixed-for-claude
from: codex-cli
to: claude-code
type: status
status: open
created: "2026-07-19"
created_utc: "2026-07-19T03:11:31Z"
severity: high
subject: "macos-m4-build-smoke-fixed-for-claude"
relates_to: []
acceptance: "Claude pulls main, verifies bundle binary arm64, runs version smoke and focused TrackDAO/EngineBuffer gate, then launches build/migx.app for GUI dogfood."
branch: "main"
commit: "40d0385"
---

# macOS M4 Build Smoke Fixed For Claude

## Intent
Give Claude a current, verified build/run smoke path after Codex reproduced and fixed the terminal `--help`/`--version` crash.

## Context
Current main includes the FSL sidecar cue/energy work and now has a startup fix so CLI help/version exits through `QCoreApplication` before constructing `QApplication`. The fresh app binary for this bundle build is `build/migx.app/Contents/MacOS/migx`; `build/mixxx` can be stale and should not be used as the first validation target.

## Evidence
- Commit to pull: `40d0385` (`fix cli smoke before gui startup`).
- Crash root cause from `.ips`: `SIGABRT` inside Apple `HIServices` `_RegisterApplication`, called by Qt Cocoa platform init during `MixxxApplication::MixxxApplication`. This happened before Mixxx core/FSL code.
- Fixed smoke: `build/migx.app/Contents/MacOS/migx --version` exits 0 and prints `Mixxx 2.7.0-alpha`.
- Help smoke: `build/migx.app/Contents/MacOS/migx --help` exits 0 and prints command-line help.
- Binary check: `file build/migx.app/Contents/MacOS/migx build/mixxx-test` reports arm64 for both.
- Focused C++ gate: `build/mixxx-test --gtest_filter='TrackDAOTest.*:EngineBufferTest.*'` passed 15/15.
- EXO gates: `just exo-tool-tests` and `just exo-sidecar-ontology` passed.
- Known non-blocking warning: PortAudio/JACK weak-load emits missing `libjack.0.dylib` messages on this host; Core Audio remains the default path.
- Broad `ctest --test-dir build -R 'Engine|Track'` is not a cheap smoke here; it selected 253 tests and hung in controller JavaScript player proxy territory. Use focused gates first.

## Requested Action
1. Pull `main`.
2. Run `cmake --build build --target mixxx mixxx-test --parallel 8` or `just build`.
3. Validate `file build/migx.app/Contents/MacOS/migx | grep arm64`.
4. Run `build/migx.app/Contents/MacOS/migx --version`.
5. Run `build/mixxx-test --gtest_filter='TrackDAOTest.*:EngineBufferTest.*'`.
6. Launch GUI dogfood from an interactive macOS session with `open build/migx.app`, optionally with `--args --developer --settings-path /tmp/migx-dogfood --resource-path "$(pwd)/res"`.
7. Then dogfood local tracks -> FSL sidecars -> `just exo-copilot-why`.

## Blockers
No current Codex blocker. GUI launch still needs an interactive macOS session; Codex verified the CLI/binary smoke path but did not use GUI `open`.
