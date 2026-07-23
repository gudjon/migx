# justfile — Migx task orchestrator.
#
# A THIN command layer over the existing build (CMake) + quality gates (pre-commit) — NOT a build
# system and NOT a restructure. Migx is an upstream-tracking fork of Mixxx; this file is additive and
# touches no upstream-owned file (see kanban/architecture/decisions/ADR-001-task-orchestrator.md).
#
# The Turborepo-transferable idea is the *explicit task graph*, not the JS tooling:
#   configure ─▶ build ─┬─▶ test ─▶ bench
#                       └─▶ bench
#   lint / lint-frontend / kanban-lint  (independent, fast)
#   ci = lint + test + kanban-lint
#
# Requires: `just` (brew install just). First build needs the toolchain — see
# kanban/runbooks/build-setup-macos-m4.md (run `tools/macos_buildenv.sh setup` first).

build_dir := "build"
jobs := `/usr/sbin/sysctl -n hw.ncpu 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 8`

# List recipes
default:
    @just --list

# ---- C++ pipeline (heavy; the FAST loop is `just lint-changed`, not this) ----
# Configure arm64-native macOS 26+ (ADR-006) + compile_commands.json for clangd (P-26) + tests + bench.
configure:
    cmake -S . -B {{build_dir}} -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON -DBUILD_BENCH=ON \
      -DCMAKE_OSX_ARCHITECTURES=arm64 \
      -DCMAKE_OSX_DEPLOYMENT_TARGET=26.0
    ln -sf {{build_dir}}/compile_commands.json compile_commands.json

build: configure
    cmake --build {{build_dir}} --parallel {{jobs}}

test: build
    ctest --test-dir {{build_dir}} --output-on-failure

# Google-benchmark suite (BUILD_BENCH → the mixxx-benchmark target = mixxx-test --benchmark).
# Pin baselines per P-03 / P-25; gate on p99/max not mean (P-18).
bench: build
    cmake --build {{build_dir}} --target mixxx-benchmark --parallel {{jobs}}
    {{build_dir}}/mixxx-test --benchmark {{bench_filter}}
bench_filter := ""

# ---- Run the app: build latest + a runnable (un-sandboxed, ad-hoc) bundle + Desktop launcher ----
# `just app` builds the current source, installs dist/migx.app, refreshes
# ~/Desktop/Migx.app -> it, and launches. Re-run any time to get the latest.
# Un-sandboxed via BundleInstall.cmake.in (dev builds), so it can write settings
# + read your music library (the App Sandbox is App-Store-only).
app:
    cmake -S . -B {{build_dir}} -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DMACOS_BUNDLE=ON -DMACOS_BUNDLE_NAME=migx -DMACOS_BUNDLE_IDENTIFIER=com.gudjon.migx \
      -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_OSX_DEPLOYMENT_TARGET=26.0
    cmake --build {{build_dir}} --target mixxx --parallel {{jobs}}
    rm -rf dist/migx.app
    cmake --install {{build_dir}} --prefix "$PWD/dist"
    xattr -dr com.apple.quarantine dist/migx.app 2>/dev/null || true
    ln -sfn "$PWD/dist/migx.app" ~/Desktop/Migx.app
    @echo "Launching Migx (also on your Desktop as Migx.app)…"
    open dist/migx.app

# ---- Run the NextGen shadow shell (ADR-007): the new agent-first UI on the shared engine ----
app-ng: app
    @echo "Launching Migx NextGen shell (--nextgen)…"
    open dist/migx.app --args --nextgen

# ---- Fast quality gate (CLAUDE.md mandates this before commit) ----
lint:
    pre-commit run --all-files
lint-changed:
    pre-commit run --files `git diff --name-only HEAD`

# ---- Frontend as a first-class workspace (qmllint/qmlformat are stages:[manual] — hidden today) ----
lint-frontend: lint-qml lint-js lint-qss
lint-qml:
    pre-commit run qmllint --all-files --hook-stage manual
fmt-qml:
    pre-commit run qmlformat --all-files --hook-stage manual
lint-js:
    pre-commit run eslint --all-files
lint-qss:
    pre-commit run qsscheck --all-files

# ---- Agent-harness discipline (mirrors .github/workflows/kanban-discipline.yml) ----
kanban-lint:
    python3 kanban/scripts/lint-dossier-frontmatter.py
    python3 kanban/scripts/verify-prefix-registry.py
    python3 kanban/scripts/lint-naming-conventions.py
    python3 kanban/scripts/verify-ps-citations.py
    python3 kanban/scripts/verify-sealed-dossier-has-closure.py
    python3 kanban/architecture/lint/verify-owns-paths-exist.py
    python3 kanban/architecture/lint/verify-agents-md-present.py
    python3 .claude/architecture/lint/verify-skill-grounding.py
    python3 kanban/scripts/gen-pattern-index.py --check
    python3 kanban/architecture/ddd/gen-index.py --check

# ---- Fleet federation (multi-peer Claude/Codex/Grok; AGY paused) ----
# Rank open+ack mail; write scratchpad nudge (gitignored).
fleet:
    python3 kanban/scripts/migx-fleet-conductor.py --nudge-file

# Conductor + Codex seal-class drains (EXO P-08 evaluate & close).
fleet-drain:
    python3 kanban/scripts/migx-fleet-conductor.py --nudge-file --drain-codex

fed-list:
    ./kanban/scripts/migx-fed list --status all

fed-sync:
    ./kanban/scripts/migx-fed sync

fed-sync-json:
    ./kanban/scripts/migx-fed sync --json

fed-audit:
    ./kanban/scripts/migx-fed audit

# Usage: just fed-poll SIDE=codex-cli
fed-poll SIDE:
    @side="{{SIDE}}"; side="${side#SIDE=}"; ./kanban/scripts/migx-fed poll --to "$side"

# Codex long listener (Ctrl-C to stop). Usage: just fed-listen SIDE=codex-cli INTERVAL=900
fed-listen SIDE INTERVAL="900":
    @side="{{SIDE}}"; side="${side#SIDE=}"; interval="{{INTERVAL}}"; interval="${interval#INTERVAL=}"; ./kanban/scripts/migx-fed listen --to "$side" --interval "$interval"

# Long federation harness: sync + audit + poll every interval.
fed-harness SIDE="codex-cli" INTERVAL="900":
    @side="{{SIDE}}"; side="${side#SIDE=}"; interval="{{INTERVAL}}"; interval="${interval#INTERVAL=}"; ./kanban/scripts/migx-fed harness --to "$side" --interval "$interval"

fed-harness-smoke SIDE="codex-cli":
    @side="{{SIDE}}"; side="${side#SIDE=}"; ./kanban/scripts/migx-fed harness --to "$side" --interval 1 --cycles 1

# Design-token bridge (DUI)
theme-check:
    python3 tools/design/gen_theme_from_design.py --check

# NextGen token/modal rulebook for QML below Theme.
ng-ui-lint:
    tools/ng-judge nextgen-ui lint --path res/qml/nextgen --assert-token-only --assert-no-blocking-modal

# NextGen ARRANGE / music-management module judge (offline fixture; no network).
ng-music-judge: ng-ui-lint
    tools/ng-judge music-mode fixture-load --fixture fixtures/music-mode-50/
    tools/ng-judge music-mode search --q peak --expect-ids id:03,id:11,id:27
    tools/ng-judge music-mode filter --key-compat free-deck --expect-count-range 3,12
    tools/ng-judge music-mode cards --require art,bpm,key,energy,tags,playlists,chips
    tools/ng-judge music-mode switch-roundtrip --assert-playhead-continues
    tools/ng-judge music-mode stage-and-load --track id:07 --deck free --require-ack
    tools/ng-judge music-mode load --track id:07 --deck busy --expect-reject
    tools/ng-judge music-mode cards --track id:no-signal --assert-no-modal --assert-chip-empty-ok
    tools/ng-judge music-mode offline-box --deny-net --run fixture-load,search-stable,cards-render
    tools/ng-judge music-mode screenshot --sizes laptop-1440x900,wide-1920x1080 --assert-no-text-overlap

# EXO: paste Spotify URIs → prep-only ontology stubs (no network / no playback)
exo_paste := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/import/sample-paste.txt"
exo_import_songs := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/songs/imported"
exo_import_session := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sessions/session-paste-import-demo.json"

exo-spotify-import:
    python3 tools/exo/spotify_uri_import.py \
      --paste {{exo_paste}} \
      --out-dir {{exo_import_songs}} \
      --session-out {{exo_import_session}} \
      --session-id session-paste-import-demo
    python3 tools/exo/spotify_uri_import.py \
      --paste {{exo_paste}} \
      --out-dir {{exo_import_songs}} \
      --check

# Structural check of EXO song/session fixtures (incl. hybrid + paste-import)
exo-fixtures-check:
    python3 tools/exo/check_fixtures.py

# Offline Layer B co-pilot: why-next over hybrid or demo session (no engine / no network)
exo_session_hybrid := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sessions/session-hybrid-prep-demo.json"
exo_mirror := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/dogfood/session-mirror.v1.json"
exo_why_md := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/results/COPILOT-WHY-NEXT.md"
exo_why_json := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/results/COPILOT-WHY-NEXT.json"
exo_intent := "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/dogfood/intent-inbox.v1.json"

exo_qml_fixture := "res/qml/CoPilot/fixture_why_next.json"
exo_sidecar_out := "/private/tmp/migx-exo-sidecar-demo"

exo-copilot-why:
    python3 tools/exo/copilot_why_next.py \
      --session {{exo_session_hybrid}} \
      --current song-02-peak \
      --md-out {{exo_why_md}} \
      --json-out {{exo_why_json}} \
      --write-intent {{exo_intent}}
    mkdir -p res/qml/CoPilot
    cp {{exo_why_json}} {{exo_qml_fixture}}

exo-copilot-why-mirror:
    python3 tools/exo/copilot_why_next.py \
      --mirror {{exo_mirror}} \
      --md-out {{exo_why_md}} \
      --json-out {{exo_why_json}} \
      --write-intent {{exo_intent}}

# Real-library bridge smoke: FSL track sidecars -> EXO song ontologies -> co-pilot proposal.
exo-sidecar-ontology:
    python3 tools/exo/ontology_from_sidecar.py \
      --sidecars \
      kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sidecars/deep-house-am-126.migx/track.json \
      kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sidecars/prog-house-em-128.migx/track.json \
      kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sidecars/tech-house-dm-124.migx/track.json \
      kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/fixtures/sidecars/dnb-em-174.migx/track.json \
      --out-dir {{exo_sidecar_out}}
    python3 tools/exo/copilot_why_next.py --session {{exo_sidecar_out}}/session.json

# Set-level co-pilot: audit a planned set and optionally propose a smoother order.
exo-set-audit:
    python3 tools/exo/set_planner.py --session {{exo_session_hybrid}} --audit

exo-set-plan START="song-02-peak":
    @start="{{START}}"; start="${start#START=}"; python3 tools/exo/set_planner.py --session {{exo_session_hybrid}} --audit --plan --start "$start"

exo-tool-tests: exo-fixtures-check
    python3 tools/exo/test_copilot_tempo.py
    python3 tools/exo/test_ontology_from_sidecar.py
    python3 tools/exo/test_set_planner.py
    python3 -m py_compile tools/exo/copilot_why_next.py tools/exo/ontology_from_sidecar.py tools/exo/set_planner.py

# PLT Wave 1: Core Audio HAL soak (measurement only — not product RT path).
# Defaults: 20s · 256 frames · 48 kHz. Override via env:
#   SOAK_SECONDS=30 SOAK_BUFFER=128 SOAK_RATE=44100 just soundio-soak
soundio-soak:
    @test -x tools/soundio/coreaudio_pa_soak || clang -O2 -std=c11 tools/soundio/coreaudio_pa_soak.c -framework AudioUnit -framework AudioToolbox -framework CoreAudio -framework CoreFoundation -o tools/soundio/coreaudio_pa_soak
    ./tools/soundio/coreaudio_pa_soak --seconds "${SOAK_SECONDS:-20}" --buffer "${SOAK_BUFFER:-256}" --rate "${SOAK_RATE:-48000}"

# Night tick (log-only; safe for cron)
night-loop:
    bash kanban/scripts/migx-night-loop.sh
    @echo "log: /tmp/migx-night-loop.log"

# ---- Meta ----
ci: lint test kanban-lint
doctor:
    @for t in just cmake ninja ccache pre-commit clang-format qmllint; do \
      printf "%-14s %s\n" "$t" "$(command -v $t || echo MISSING)"; done
    @echo "Qt: `brew list --versions qt qt@6 2>/dev/null || echo 'MISSING — run tools/macos_buildenv.sh setup'`"
clean:
    rm -rf {{build_dir}}
