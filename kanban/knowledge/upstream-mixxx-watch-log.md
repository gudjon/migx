---
id: upstream-mixxx-watch-log
type: knowledge
title: "Upstream mixxxdj/mixxx watch — incremental log"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
source: "Produced by the .claude/skills/mixxx-upstream-watch skill (gh against mixxxdj/mixxx). Newest ## date = next run's SINCE marker."
---

# Upstream mixxx watch — log

Incremental record of upstream mixxxdj/mixxx development, produced by
[`mixxx-upstream-watch`](../../.claude/skills/mixxx-upstream-watch/SKILL.md). Migx has **no git link**
to upstream (fresh history, hard fork — ADR-002); items worth having are **re-implemented** as Migx
tasks, never merged. The newest `##` date below is the marker the next run reads as `SINCE`.

## 2026-07-17

First run — establishes the baseline marker. Scanned the 15 most-recent merged PRs + latest releases.

| # | Title | Migx subsystem | Verdict | Why |
|---|---|---|---|---|
| #16717 | Fix QML slider bar settings | UI / QML | **already in-tree** | Present at Migx's fork point; no action. |
| #16712 | Improve SoundDevice & Channel naming (Sound HW prefs) | audio I/O / prefs | **already in-tree** | Present at Migx's fork point (port-name/channel split); no action. |
| #16713 | Opt out of PipeWire build by default | Linux audio | skip | Linux-only; N/A on macOS/Apple-Silicon. |
| #16720 | Flatpak: update soundtouch to 2.4.1 | packaging (Linux) | skip | Flatpak/Linux packaging noise. |
| #16709/25/31/32/… | 2.5→2.6 merge-syncs, deps bumps, CI | infra | skip | No Migx-relevant code. |

**Net:** nothing new to port this run — the two code-relevant PRs are already in Migx's base, the rest
is Linux/packaging/CI/deps. Upstream latest release is **2.5.6** (2.6 is their dev line). Migx is
current with the recent relevant fixes.

**Next run:** set `SINCE = 2026-07-17`; watch for engine/RT, waveform/render, controller, and library
changes on the 2.6 line — those are the port-worthy surfaces.
