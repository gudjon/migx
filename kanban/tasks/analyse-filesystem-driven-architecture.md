---
id: analyse-filesystem-driven-architecture
type: task
title: "Analyse a filesystem-driven architecture for Migx (agent-friendly audio + sidecar metadata)"
status: done
owner: gudjon
priority: medium
initiative: initiative-apple-silicon
parent_dossier: ""
related: [learn-arcflow-filesystem-m4, design-md-ui-modernization]
authored_by: claude-code
authored_kind: agent
triggered_by: "gudjon request 2026-07-17 — learn from CLI codegen tools (Claude Code, Codex) + Vercel 'agents with filesystems and bash'; make Migx more filesystem-driven for audio files + sidecar metadata"
created: "2026-07-17"
lastUpdated: "2026-07-17"
acceptance: |
  A proposal note (kanban/knowledge/filesystem-driven-architecture.md) that:
  - distills WHY CLI codegen agents (Claude Code, Codex) use the filesystem + bash as their substrate,
    from https://code.claude.com/docs/en/how-claude-code-works, .../changelog, and
    https://vercel.com/blog/how-to-build-agents-with-filesystems-and-bash (the filesystem as a durable,
    greppable, tool-agnostic interface; sidecar files; convention over API),
  - maps the pattern onto Migx's DJ domain: local on-disk audio files + SIDECAR METADATA (cues, beatgrids,
    key, gain, waveform cache, tags) living as greppable files NEXT TO the audio, complementing (not
    necessarily replacing) the SQLite library (arch-library-db, arch-track-model),
  - assesses benefits: agent-friendliness, portability/backup, interop with other DJ tools + CLI, version
    control, and resilience; and risks: perf vs DB, consistency, sync, scale (10k+ track libraries),
    conflict with upstream Mixxx's DB-centric model (fork_delta),
  - proposes a concrete sidecar format + where it sits vs the DB (source of truth question), and a
    migration/coexistence path,
  - recommends whether this is a spike dossier, an initiative, or research-only for now.
---

# Analyse a filesystem-driven architecture for Migx

CLI codegen tools (Claude Code, Codex) are powerful because the **filesystem + bash is their substrate**:
durable, greppable, tool-agnostic, convention-over-API. This is the same "everything is code" (MG-2) the
Migx harness runs on. **Question:** should Migx's DJ library be more filesystem-driven — audio files with
**sidecar metadata files** (cues/beatgrid/key/gain/waveform/tags) next to them — making the library
agent-friendly, portable, and CLI-accessible, versus (or alongside) the SQLite DB?

References to distill: the two Claude Code docs (already summarized in
`kanban/knowledge/claude-code-capabilities.md`) + https://vercel.com/blog/how-to-build-agents-with-filesystems-and-bash.
Touches `arch-library-db`, `arch-track-model`, `arch-sources-decode`. Relates to
[[learn-arcflow-filesystem-m4]] (fast I/O) and [[design-md-ui-modernization]] (markdown-as-SSoT for UI).
Research/architecture analysis — resolve the source-of-truth (DB vs sidecar) question before any dossier.
