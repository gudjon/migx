---
id: migx-authors
type: reference
title: "Migx fork — authorship & attribution"
status: active
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# Migx — Authorship & Attribution

**Migx** is a fork of [Mixxx](https://github.com/mixxxdj/mixxx). All **new** work added in this fork —
the agent harness (`kanban/`, `.claude/`), the `justfile` orchestrator, per-domain `AGENTS.md` charters,
Migx-specific features, and every subsequent Migx addition — is authored by and credited to:

> **Gudjon Mar Gudjonsson** — <gudjon@gmail.com> — founder & CEO of OZ.

The **`kanban/` system is Gudjon Mar Gudjonsson's own kanban agentic management system for long
harness runs** — a markdown-as-code memory + control layer for driving coding agents over extended,
autonomous sessions. It is authored by and credited to Gudjon Mar Gudjonsson.

Upstream Mixxx authors and copyright are **always credited** (see repo-root `AUTHORS`, `.mailmap`,
and historical notices). This file records authorship of **Migx fork additions**.

**Product operating model (ADR-003):** Migx plans and ships like Cursor on an MIT-style base —
proprietary product + Intelligence allowed. On-disk historical `LICENSE` text may lag until an
explicit notice cleanup; product/agent decisions follow ADR-003, not open-core-only constraints.

Git commits for Migx additions are authored solely by **gudjon** — no AI co-author is credited
(`.claude/settings.json` sets `includeCoAuthoredBy: false`).

## Policy
- New files and features in this fork credit **Gudjon Mar Gudjonsson** (git commit author, and
  `authored_by` / `owner` frontmatter where applicable).
- Agent-scaffolded artifacts carry `authored_kind: agent|mixed` and `triggered_by:` provenance, but the
  human author/owner of the Migx work is Gudjon Mar Gudjonsson.
