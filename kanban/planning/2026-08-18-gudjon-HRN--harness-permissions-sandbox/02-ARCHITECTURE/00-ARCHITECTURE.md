# Architecture

*The chosen design and its edges. If this pins a path (not just a recommended approach), also write
an ADR in `kanban/architecture/decisions/` and cite it here.*

## The design
<The approach in enough detail to implement. Diagrams as ASCII/mermaid if useful.>

## Touched subsystems & the RT/GPU boundary
<Which of src/engine, src/waveform, src/rendergraph, src/shaders, src/mixer, etc. change. Call out
explicitly where the change sits relative to the real-time audio thread and the GPU boundary — a
change on the RT path must not allocate or lock (MG-6).>

## Patterns & decisions cited
| ID | How this design uses it |
|---|---|
| `P-NN` | |
| `ADR-NNN` | |

## Data journey
<How data flows through the changed path — where copies happen (and on a unified-memory SoC, where
they can be eliminated), where the hot loop is.>

## Risks
<Link `AP-NN` antipatterns this could trip, and how the plan avoids them. Detailed risk log in
`../RISKS.md` if it grows.>

## Verifiability
<How we will prove it works — the benchmark/test that becomes the `90-EXECUTION` gate and the
`91-LOOP-CLOSURE` verdict.>
