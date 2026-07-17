# AGENTS.md — control/ (the cross-thread string-keyed control bus)

> DDD card: `kanban/architecture/ddd/bounded-contexts/arch-control-messaging.md`
> House rules (SSoT): repo-root `/AGENTS.md` · Build/style: `/CONTRIBUTING.md` · Patterns: `kanban/patterns/`
> This charter cites those; it does not restate them. Tool-agnostic (Claude Code / Codex / Grok).

## Purpose
The value bus every other component talks through. A `[Group],key` (`ConfigKey`) names one atomic
`double` with a single authoritative writer and any number of readers. The GUI, controllers, and the
real-time engine exchange state through it **without sharing locks** — the atomic value store is what
makes a control safe to read on the audio thread.

## Key files
- `controlobject.cpp/.h` — the authoritative value for one `ConfigKey`; the writer's handle.
- `control.cpp/.h` — `ControlDoublePrivate`, the shared refcounted backing behind every object/proxy.
- `controlvalue.h` — `ControlValueAtomic<T>`: atomic for lock-free T, ring buffer otherwise.
- `controlproxy.cpp/.h` — reader/notifier handle; `pollingcontrolproxy.h` — signal-free polling reader.
- `controlpushbutton.cpp`, `controlpotmeter.cpp` (+ `controllinpotmeter`, `controllogpotmeter`,
  `controlaudiotaperpot`) — behaviour specialisations of a ControlObject.
- `controlobjectscript.cpp` — proxy exposed to the controller QJSEngine.
- `controlmodel.cpp`, `controlsortfiltermodel.cpp` — the developer control picker (GUI/debug).

## Invariants you MUST respect
- **Single writer:** each `[Group],key` has exactly one authoritative writer. Adding a second is the
  named antipattern — introduce a new key or route through the owner. `P-06`, `AP-03`.
- **Read via a proxy:** cross-context readers hold a `ControlProxy`/`PollingControlProxy`; they never
  take ownership of the `ControlObject`.
- **Value path lock-free, object graph is not:** reading/writing the atomic value is RT-callable
  (`P-16`); create/connect/destroy of the object graph is GUI/worker-thread only. `P-17`.
- **Qt affinity:** proxies are QObjects — connect/emit respect thread affinity; no synchronous
  `Qt::DirectConnection` delivery onto the RT thread. `P-20`, `AP-14`.

## Build / test entry points
- Build: `cmake --build build --parallel $(sysctl -n hw.ncpu)` (configure once with
  `cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON`; see `/CONTRIBUTING.md`).
- Tests: `ctest --test-dir build -R Control` (GoogleTest; control tests live in `src/test/`, e.g.
  `controlobject_test`, `controlobjectaliasing_test`).
- Fast gate before commit: `pre-commit run --files <changed>` (clang-format/tidy).

## Forbidden edits
- Adding a second writer to an existing `ControlObject`.
- Allocating, locking, or constructing/destroying a control on a `process()`-reachable path.
- Making the atomic value store block or allocate (it is read on the audio thread).

## Cross-references
Downstream consumers: `src/engine/AGENTS.md` (RT reads `[ChannelN],*`), `src/mixer/AGENTS.md`
(player state), `src/controllers/` (scripted controls), `src/skin/`+`src/qml/` (widget bindings).
Seam: `kanban/architecture/ddd/boundaries/control-to-engine.md`.
