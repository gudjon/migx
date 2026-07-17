# AGENTS.md — vinylcontrol/ (timecode-vinyl signal → deck control)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-vinylcontrol.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
Turns a timecode-vinyl (or CDJ) input signal into deck rate and position. `VinylControlProcessor`
receives the control-vinyl input buffers on the **audio callback thread**, decodes timecode via
`VinylControlXwax`, smooths it with `SteadyPitch`, and writes the resulting pitch/scratch back to the
engine deck through `ControlObject`s. Enable/mode/lead-in are GUI-thread config.

## Key files
- `vinylcontrolmanager.cpp/.h` — GUI-side lifecycle; binds inputs to processors.
- `vinylcontrolprocessor.cpp/.h` — RT-side input consumer; drives the per-deck `VinylControl`.
- `vinylcontrol.cpp/.h` — abstract per-deck decode → rate/position.
- `vinylcontrolxwax.cpp/.h` — the xwax timecode DSP implementation.
- `steadypitch.cpp/.h` — pitch smoothing / steady-state estimation.
- `vinylcontrolsignalwidget.cpp/.h` — GUI signal-quality scope (off-RT).

## Invariants you MUST respect
- **RT thread (hard):** the input-callback path (`VinylControlProcessor` →
  `VinylControl::analyzeSamples`) — **no** alloc, **no** mutex, **no** I/O, **no** blocking. `P-02`, `AP-02`.
- **Cross-thread out via ControlObject:** decoded pitch/position reach the engine deck through the
  lock-free `ControlObject` bus — never a shared lock or synchronous slot. `P-16`.
- **Object lifetime off the RT thread:** processors/decoders are created/destroyed by
  `VinylControlManager` on the GUI thread; never `new`/`delete` on the callback. `P-17`.
- **Single writer:** vinyl is the authoritative writer of the deck rate control only while engaged; it
  must not race the engine's own rate writer. `P-06`, `AP-03`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R VinylControl` (GoogleTest; tests in `src/test/`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Any allocation, lock, or blocking call on the `VinylControlProcessor`/`analyzeSamples` input path.
- Blocking the engine's rate writer, or making vinyl a second writer that races it (`AP-03`).
- Doing timecode DSP or `SteadyPitch` smoothing anywhere other than the RT input path it belongs on.

## Cross-references
Upstream: `src/soundio/AGENTS.md` (input callback), `src/control/AGENTS.md` (config controls).
Downstream: `src/engine/AGENTS.md` (deck rate/position it drives). Card:
`kanban/architecture/ddd/bounded-contexts/arch-vinylcontrol.md`.
