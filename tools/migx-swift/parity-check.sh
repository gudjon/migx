#!/usr/bin/env bash
# Cross-runtime parity — the Swift binary and the Python one must answer
# --json identically for every command both implement (ADR-009).
#
# This exists because parity was VERIFIED ONCE, by hand. A contract observed
# once is a claim; a contract checked on every run is a contract. As commands
# port one at a time, this is what stops the two binaries drifting apart in a
# way nobody notices until an agent gets two different answers.
#
# If the Swift binary is missing it reports SKIPPED and exits 0 — but it says
# so loudly. A silent pass would mean "parity holds" and "parity was never
# checked" look identical, which is the defect this repo keeps finding (P-34).
set -uo pipefail
cd "$(dirname "$0")/../.."

SWIFT="${MIGX_SWIFT_BIN:-build/migx-swift}"
PY="${MIGX_PY_BIN:-tools/migx-cli/migx}"

# Commands CLAIMED to be at parity. Grows as each one is genuinely ported.
#
# config.show is deliberately absent: the Swift side reads the same file and
# resolves the same library.root, but emits a flattened shape while Python
# nests library/quality/spotify/sources and reports per-key provenance. That is
# a real gap, tracked in ADR-009's migration order -- not something to paper
# over by loosening the comparison.
#
# Listing it here would leave a permanently red check, which trains people to
# ignore red. Omitting it is honest ONLY because the gap is recorded elsewhere;
# a command must never be dropped from this list to make it pass.
COMMANDS=("session.now")

if [ ! -x "$SWIFT" ]; then
  echo "SKIPPED: no Swift binary at $SWIFT — parity NOT checked this run."
  echo "  build it:  swiftc -O tools/migx-swift/Sources/main.swift -o $SWIFT"
  exit 0
fi

fails=0
for cmd in "${COMMANDS[@]}"; do
  sw_out=$("$SWIFT" "$cmd" --json 2>/dev/null); sw_exit=$?
  py_out=$("$PY" "$cmd" --json 2>/dev/null); py_exit=$?

  if [ "$sw_exit" != "$py_exit" ]; then
    echo "FAIL $cmd: exit differs — swift=$sw_exit python=$py_exit"
    fails=$((fails + 1)); continue
  fi
  # Compare parsed JSON, not bytes: key order and whitespace are not contract.
  if ! SW="$sw_out" PY="$py_out" python3 - "$cmd" <<'PYEOF'
import json, os, sys
try:
    sw = json.loads(os.environ["SW"])
    py = json.loads(os.environ["PY"])
except json.JSONDecodeError as exc:
    print(f"FAIL {sys.argv[1]}: not JSON ({exc})"); raise SystemExit(1)
if sw == py:
    raise SystemExit(0)
for key in sorted(set(sw) | set(py)):
    if sw.get(key) != py.get(key):
        print(f"FAIL {sys.argv[1]}: {key} swift={sw.get(key)!r} python={py.get(key)!r}")
raise SystemExit(1)
PYEOF
  then
    fails=$((fails + 1)); continue
  fi
  echo "  ok  $cmd  (exit $sw_exit, identical payload)"
done

if [ "$fails" -gt 0 ]; then
  echo "FAIL: $fails of ${#COMMANDS[@]} command(s) diverge between runtimes"
  exit 1
fi
echo "PASS: ${#COMMANDS[@]} command(s) identical across Swift and Python"
