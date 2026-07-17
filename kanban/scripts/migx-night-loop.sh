#!/usr/bin/env bash
# migx-night-loop — thin overnight fleet tick (conductor + codex drain + optional scout reminder)
# Safe: no builds, no force-push. Logs to /tmp by default.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
LOG="${MIGX_NIGHT_LOG:-/tmp/migx-night-loop.log}"
{
  echo "=== migx-night-loop $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  python3 kanban/scripts/migx-fleet-conductor.py --nudge-file --drain-codex || true
  python3 tools/design/gen_theme_from_design.py --check || echo "WARN theme-check failed"
  echo "NEXT peer: see kanban/federation/scratchpad/conductor/LATEST.md"
  echo "Optional: start Grok scout if research-request mail open (manual / separate tmux)"
  echo "=== done ==="
} >>"$LOG" 2>&1
