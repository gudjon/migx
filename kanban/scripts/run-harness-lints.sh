#!/usr/bin/env bash
# run-harness-lints — the ONE list of harness discipline lints (MG-3).
#
# Both callers run this script rather than keeping their own copy:
#   - `just kanban-lint`              (the operator surface)
#   - .github/workflows/migx-ci.yml   (the gate)
#
# Two hand-maintained copies of this list is two truths, and they drift
# silently: kanban-discipline.yml and migx-ci.yml already diverged on whether
# to install PyYAML, which made the lints report the OPPOSITE verdict in CI
# from local (see _kanban_lint.parse_yaml_lite). Adding a lint should mean
# editing exactly one file — this one.
#
# Runs every lint even after one fails, so a single run reports the whole
# picture. An autonomous loop that has to re-run the gate once per hidden
# failure burns a cycle per finding.
#
# Requires PyYAML (the registry parsers refuse to guess without it).

set -uo pipefail
cd "$(dirname "$0")/../.."

LINTS=(
  "kanban/scripts/lint-dossier-frontmatter.py"
  "kanban/scripts/verify-prefix-registry.py"
  "kanban/scripts/lint-naming-conventions.py"
  "kanban/scripts/verify-ps-citations.py"
  "kanban/scripts/verify-sealed-dossier-has-closure.py"
  "kanban/architecture/lint/verify-owns-paths-exist.py"
  "kanban/architecture/lint/verify-agents-md-present.py"
  "kanban/architecture/lint/verify-tui-keys-documented.py"
  "kanban/architecture/lint/verify-command-vocabulary.py"
  ".claude/architecture/lint/verify-skill-grounding.py"
  "kanban/scripts/gen-pattern-index.py --check"
  "kanban/architecture/ddd/gen-index.py --check"
)

failed=()
for lint in "${LINTS[@]}"; do
  # shellcheck disable=SC2086 -- the --check suffix is intentionally split
  if ! python3 $lint; then
    failed+=("$lint")
  fi
done

if [ ${#failed[@]} -gt 0 ]; then
  echo
  echo "FAIL: ${#failed[@]} of ${#LINTS[@]} harness lint(s) failed:"
  printf '  - %s\n' "${failed[@]}"
  exit 1
fi

echo
echo "PASS: all ${#LINTS[@]} harness lints"
