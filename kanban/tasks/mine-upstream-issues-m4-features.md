---
id: mine-upstream-issues-m4-features
type: task
title: "Mine mixxxdj/mixxx GitHub issues for macOS-M4-relevant features & capability uplifts"
status: done
owner: gudjon
priority: high
initiative: initiative-apple-silicon
parent_dossier: ""
depends_on: []
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon request 2026-07-17 — do a round on features relevant to the macOS M4 version from https://github.com/mixxxdj/mixxx/issues"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A distilled findings note at kanban/knowledge/upstream-issues-m4-features.md that:
  - surveys open mixxxdj/mixxx issues (via `gh issue list`) relevant to macOS / Apple Silicon /
    performance / Metal / audio latency / waveform rendering / CoreAudio,
  - buckets them: (a) macOS/M4 bugs to fix, (b) performance/GPU/DSP uplifts, (c) features worth
    implementing in Migx, (d) upstream work we should track (fork_delta),
  - for each high-value item records: issue #, title, one-line summary, which Migx subsystem/DDD
    context it touches, and whether it maps to an existing initiative dossier (MTL/DSP/ASI) or warrants
    a new one,
  - ranks the top ~10 candidates by (M4 relevance × user value × tractability),
  - names which become dossiers vs backlog tasks.
---

# Mine upstream issues for M4-relevant features

Survey `https://github.com/mixxxdj/mixxx/issues` for what's relevant to our macOS Apple-Silicon (M4)
Migx build — bugs, performance uplifts, and features to implement or track. Feeds
[[initiative-apple-silicon]] and the broader Migx roadmap.

**Method (a research subagent / later loop iteration):**
- `gh issue list --repo mixxxdj/mixxx --state open --limit 100 --search "macOS OR "Apple Silicon" OR Metal OR performance OR latency OR CoreAudio OR waveform"` (and label filters).
- Read the top candidates; cross-reference against our DDD map (arch-waveform-render, arch-audio-io,
  arch-rendergraph, arch-analyzer, arch-engine-realtime) and patterns.
- Distill into `kanban/knowledge/upstream-issues-m4-features.md` per the acceptance block.

Research input, not implementation — produces the prioritized backlog the optimization/feature dossiers
draw from. Keep the issue→Migx-subsystem→dossier mapping concrete.
