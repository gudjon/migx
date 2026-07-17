# Execution — phase plan

*Ordered phases (waves). Each wave ends at a verifiability gate — a check that must pass before the
next wave starts. Waves are executed under `/loop`; commit per wave.*

## Waves

| # | Wave | Deliverable | Verifiability gate |
|---|---|---|---|
| 1 | `<name>` | `<what lands>` | `<pre-commit clean · ctest -R <x> green · benchmark ≥ baseline>` |
| 2 | | | |
| 3 | | | |

## Gate definitions (the `02-VERIFIABILITY-GATES` detail)
For each gate, name the exact command and threshold:
- **Wave 1 gate:** `<cmd>` → `<pass condition>`

## House-physics guardrails (apply to every wave — MG-6)
- No allocation / no lock added on the RT audio thread.
- Qt object ownership via `parented_ptr`/`make_parented`; no leaks.
- `pre-commit run --all-files` clean (clang-format/tidy, qmllint, cmake lint).
- Every commit builds (bisectability).

## Rollback
<How to back out a wave if its gate fails — the base commit to reset to.>

## Loop discipline (when running unattended)
Decide at forks with confidence ≥ 0.4 or flag-and-skip; never stop to ask unless irreversible or a
value judgment. Record decisions in `../JOURNAL.md`. Always leave the loop closed.
