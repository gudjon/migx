---
description: "How to build, test, and lint Migx — the real commands"
---

# Rule — build, test, lint

SSoT for the substance: `CONTRIBUTING.md` + repo-root `AGENTS.md`. This rule is the fast index.

## Build (heavy — not the fast loop)
```
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON   # configure once (also feeds clangd — P-26)
cmake --build build --parallel $(sysctl -n hw.ncpu)      # macOS; use nproc on Linux
```
Every commit must build (bisectability). On Apple Silicon, build **native arm64** (`P-24`) so
Accelerate/vDSP and the right `-mcpu` tuning are available — never x86_64/Rosetta for perf work.

## Test
```
ctest --test-dir build                 # all GoogleTest suites
ctest --test-dir build -R <Filter>     # e.g. -R Engine
```
Or run the `mixxx-test` binary directly under a debugger. Tests live in `src/test/`.

## The fast quality gate — pre-commit (use this, not a full build, for feedback)
```
pip install pre-commit && pre-commit install && pre-commit install -t pre-push
pre-commit run --files <changed-files>     # clang-format 19.1.3, clang-tidy, qmllint, cmake lint, ...
SKIP=clang-format git commit ...           # skip a hook when justified
```
GUI changes need before/after screenshots (see CONTRIBUTING.md).

## Benchmarks (the perf loop — north-star)
Migx links `benchmark::benchmark`. Add benchmarks in the GoogleTest tree; run the bench binary /
`ctest`. Pin the baseline to a commit + record the M4 core config; measure deltas against it (`P-03`,
`P-25`); gate on p99/max + zero underruns (`P-18`), never the mean.

## Verification ladder (cheapest sufficient check first — playbook ch.03)
pre-commit lint → `ctest -R <targeted>` → benchmark delta → full build → adversarial subagent review.
For a perf claim the benchmark delta is the load-bearing rung; for correctness it's the test.
