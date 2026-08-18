# Research

*Prior art and options, so the architecture choice is defensible. Cite sources by path/URL; cite
patterns by `P-NN`.*

## Upstream (Mixxx) changelog scan
<What upstream already does here. Migx forks Mixxx — check whether the capability exists upstream,
is in-flight, or was rejected, before building it. Link commits/PRs.>

## Prior art
<How comparable software / the Qt/Metal/Accelerate ecosystem solves this. For perf work: known
techniques, their tradeoffs on Apple Silicon (unified memory, P/E cores, NEON, Metal RHI vs raw
Metal).>

## Options considered
| Option | Pros | Cons | Verdict |
|---|---|---|---|
| `<A>` | | | |
| `<B>` | | | |

## Baseline measurement (the trigger/capture for MG-1)
<Record the baseline benchmark BEFORE any change, as an `EVD-*` in `../results/`. Name the exact
command, the hardware (M4 core config), and the number. This is what every later delta measures
against — pin the commit.>

## Open questions
<Anything unresolved that architecture must decide.>
