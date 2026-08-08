---
id: ctest-four-failures-first-real-run
type: task
title: "4 ctest failures surfaced by the first real run of the C++ suite"
status: open
owner: gudjon
priority: medium
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
| 618 | `AdjustReplayGainTest.AdjustReplayGainUpdatesPregain` | **SEGFAULT** — the one to triage first |
| 781 | `SoundSourceProxyTest.firstSoundTest` | `soundproxy_test.cpp:876` expected 2270, got 2318 |
| 946 | `BulkMappings/MappingTestFixture.LoadMapping/Traktor_Kontrol_S4_MK3_bulk_xml` | mapping load |
| 965 | `HidMappings/MappingTestFixture.LoadMapping/Dummy_Device_Screen_hid_xml` | mapping load |

## Reading them
- **618 is the real one.** A segfault in a test is a segfault in shipping code paths until proven
  otherwise, and replay-gain touches pregain — audible. Triage before the other three.
- **781** is a 48-sample first-sound offset. This class of test is sensitive to the decoder build
  (FFmpeg 7.1 / CoreAudio 26.2 here); it is likely an environment expectation rather than a defect, but
  *likely* is not *verified* — confirm which before writing it off, and do not adjust the constant to
  make it green (`AP-01`).
- **946 / 965** are controller-mapping XML loads. Cheapest to check; possibly upstream mappings we
  inherited and do not use.

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
