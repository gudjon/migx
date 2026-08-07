#!/usr/bin/env bash
# migx-night-loop — overnight tick: fleet coordination, and (opt-in) the gate.
#
# Two stages, because they run at different cadences:
#
#   default        fleet tick only — conductor + codex drain + theme check.
#                  Cheap enough to run every 15 min (TR-grok-long-harness-wave).
#   --verify       ALSO builds incrementally and runs the gate (`just verify`).
#                  Once a night: a full ctest pass is minutes, not seconds.
#
# Why the gate belongs here at all: MG-1 says shipping without a loop attached
# is not shipping. An overnight loop that writes code but never runs the suite
# is an open loop -- it produces commits nobody has verified. The gate is the
# "Intelligence" step of Trigger -> Capture -> Intelligence -> Adjustment.
#
# It stays OPT-IN rather than always-on so the 15-minute fleet tick does not
# trigger a build; a loop that is too expensive to run gets switched off, and a
# switched-off loop verifies nothing.
#
# Safe by construction: no force-push, no destructive git, no auto-commit. It
# reports a verdict; acting on it is the operator's or the next session's call.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
LOG="${MIGX_NIGHT_LOG:-/tmp/migx-night-loop.log}"

VERIFY=0
[ "${1:-}" = "--verify" ] && VERIFY=1

{
  echo "=== migx-night-loop $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo "HEAD $(git rev-parse --short HEAD) on $(git rev-parse --abbrev-ref HEAD)"

  python3 kanban/scripts/migx-fleet-conductor.py --nudge-file --drain-codex || true
  python3 tools/design/gen_theme_from_design.py --check || echo "WARN theme-check failed"

  if [ "$VERIFY" = "1" ]; then
    echo "--- gate ---"
    # Build first: `just verify` deliberately does not depend on `build`, so it
    # would otherwise verify a stale tree. Failing the build is a real verdict.
    if just build; then
      if just verify; then
        echo "GATE: PASS"
      else
        echo "GATE: FAIL (verify) — see $LOG"
      fi
    else
      echo "GATE: FAIL (build) — see $LOG"
    fi
  else
    echo "gate skipped (pass --verify to build + run it)"
  fi

  echo "NEXT peer: see kanban/federation/scratchpad/conductor/LATEST.md"
  echo "Optional: start Grok scout if research-request mail open (manual / separate tmux)"
  echo "=== done ==="
} >>"$LOG" 2>&1
