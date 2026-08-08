---
id: ctest-four-failures-first-real-run
type: task
title: "4 ctest failures surfaced by the first real run of the C++ suite"
status: open
owner: gudjon
priority: high
initiative: initiative-apple-silicon
authored_by: claude-code
authored_kind: agent
triggered_by: "Fixing `just configure` (it never sourced the buildenv) produced
  mixxx-test for the first time; the suite had 1298 tests where ctest had only
  ever reported a mixxx-test_NOT_BUILT placeholder"
created: "2026-08-08"
lastUpdated: "2026-08-08"
---

# 4 ctest failures surfaced by the first real run

## What happened
`just build` / `just test` had never worked: on macOS `CMakeLists.txt:116` hard-fails with
`BUILDENV_URL not specified` unless the buildenv is sourced, and the `configure` recipe never sourced it.
So `mixxx-test` was never produced and ctest reported a single `mixxx-test_NOT_BUILT` placeholder — the
C++ suite has been **ungated for the life of the fork**.

With the recipe fixed (`84e4e8c`), the first real run is **1294 run / 4 failed** on `ed8aab0` + `0bdc518`,
arm64 native, RelWithDebInfo, macOS 26.

**These are pre-existing.** No C++ source was touched in the commits that surfaced them; they were simply
never executed. This card exists so the finding has a home rather than dying in a scrollback — a gate whose
failures nobody files is only marginally better than no gate (`P-01`).

## The four

| # | Test | Symptom |
|---|---|---|
| 618 | `AdjustReplayGainTest.AdjustReplayGainUpdatesPregain` | **SEGFAULT**, ~40% of runs — worker-thread race, triaged below |
| 781 | `SoundSourceProxyTest.firstSoundTest` | `soundproxy_test.cpp:876` expected 2270, got 2318 |
| 946 | `BulkMappings/MappingTestFixture.LoadMapping/Traktor_Kontrol_S4_MK3_bulk_xml` | mapping load |
| 965 | `HidMappings/MappingTestFixture.LoadMapping/Dummy_Device_Screen_hid_xml` | mapping load |

## Reading them
- **618 is the real one** — triaged below: a genuine worker-thread race in `EngineBuffer`, not a flaky
  expectation. It reproduces ~40% of the time and hides under a debugger.
- **781** is a 48-sample first-sound offset. This class of test is sensitive to the decoder build
  (FFmpeg 7.1 / CoreAudio 26.2 here); it is likely an environment expectation rather than a defect, but
  *likely* is not *verified* — confirm which before writing it off, and do not adjust the constant to
  make it green (`AP-01`).
- **946 / 965** — triaged below: both are missing QML modules in the buildenv, not code defects.

## Triage of 618 (done 2026-08-08) — a real thread race, not a flaky expectation

**It is non-deterministic: 2 of 5 direct runs segfault** (exit 139), and it *passes every time under
lldb* (5.6 s vs 1.5 s) — the classic signature of a timing-dependent race that the debugger's slowdown
hides. It crashes inside the test body, not teardown (`[ RUN ]` with no `[ OK ]`).

macOS crash report (`EXC_BAD_ACCESS`, `KERN_INVALID_ADDRESS at 0x30d202c2a7589a11` — a garbage pointer,
so a dangling/corrupted object) gives the faulting stack:

```
EngineBuffer::notifyTrackLoaded(shared_ptr<Track>, shared_ptr<Track>)
CachingReader::trackLoaded(...)
CachingReaderWorker::trackLoaded(...)
CachingReaderWorker::loadTrack(...)
libsystem_pthread  _pthread_start        <-- a WORKER thread, not the engine thread
```

The wiring is deliberate upstream: `src/engine/cachingreader/cachingreader.cpp:86` connects
`CachingReaderWorker::trackLoaded` with **`Qt::DirectConnection`**, so the slot body executes *on the
reader's worker thread*. `EngineBuffer::notifyTrackLoaded` (`src/engine/enginebuffer.cpp:677`) says so
itself: `// Note: we are still in a worker thread.` From there it iterates `m_engineControls`, calls
`pControl->setFrameInfo(...)` / `trackLoaded(...)`, and does Qt `connect`/`disconnect` on the `Track`
object — all off the engine thread.

Note the ordering is *not* the naive culprit: `m_iTrackLoading = 0` is set **after** `notifyTrackLoaded`
returns, and `isTrackLoaded()` is `m_pCurrentTrack && m_iTrackLoading.loadAcquire() == 0`
(`enginebuffer.cpp:1614`), so the fixture's spin-wait in `src/test/signalpathtest.h:173` does not return
early for that deck. The race is between this worker-thread call and the main thread's `ProcessBuffer()`
/ the *other* deck's worker — the test loads the **same TrackPointer into both decks**
(`replaygaintest.cpp:168-169`), so two reader threads touch one `Track`'s connection list.

**Not patched deliberately.** This is engine threading on the audio path; a speculative fix here is how
`AP-02` happens, and a race "fixed" by reordering until the test stops failing is not fixed. It needs an
owner, a decision on whether the DirectConnection contract still holds for Migx, and a stress harness
(run the test in a loop, ideally under TSan) as the acceptance gate — not a one-shot green run, since
the thing passes 3 times in 5 while broken.

Worth checking whether upstream Mixxx carries the same race before designing a fix.

## Triage of 946 / 965 (done 2026-08-08) — two QML modules missing from the buildenv

Both fail for the same reason, and it is not the mapping XML. The controller *screen* QML fails to load:

```
res/qml/TraktorKontrolS4MK3Screens.qml:9:1: module "Qt5Compat.GraphicalEffects" is not installed
res/qml/TraktorKontrolS4MK3Screens.qml:-1:  module "QtQuick.Controls.macOS"    is not installed
```
→ `src/test/controller_mapping_validation_test.cpp:278: Failure — testLoadMapping(mappingPath)`

Confirmed absent from the dependency bundle (`mixxx-deps-2.6-arm64-osx-aa78b5a`): neither
`installed/*/qml/Qt5Compat` nor `installed/*/qml/QtQuick/Controls/macOS` exists. Of the 164
`MappingTestFixture.LoadMapping` cases, exactly these 2 — the ones with device screens — fail.

**This is a build-environment gap, not dead upstream weight, and it is worth fixing rather than
excluding.** Two reasons: a user with a Traktor Kontrol S4 MK3 would hit the same missing module at
runtime, not just in a test; and Migx is committing to a QML shell (`ADR-007`), so a buildenv that
cannot resolve stock Qt QML modules will bite the product UI well beyond controller screens.

Fix direction: add the two modules to the vcpkg buildenv (or confirm they ship in a newer bundle and
bump it) — `tools/macos_buildenv.sh` is the single home for which bundle this arch pulls. Do **not**
silence these by excluding the mappings from the fixture; that converts a real dependency gap into a
green test (`AP-01`).

## Next step
Run each alone for a clean signal (the suite takes ~25 min; a single test is seconds):

```bash
ctest --test-dir build -R AdjustReplayGainUpdatesPregain --output-on-failure
```

Then either fix, or record why a failure is environmental — with evidence, not assertion. Until each is
resolved or explained, `just verify` is red, which is the correct state: it is reporting something true.

## Related
- `P-34` — a gate that cannot fail is not a gate (this suite could not fail, because it never ran)
- `AP-01` — green-over-red closure: do not tune expectations to make these pass
