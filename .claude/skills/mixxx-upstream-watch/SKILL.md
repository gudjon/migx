---
name: mixxx-upstream-watch
description: "Fire when the user wants to check upstream mixxxdj/mixxx for new development to learn from
  — phrasings like 'what's new in mixxx / upstream', 'any upstream fixes worth porting', 'check
  upstream', or a scheduled/cadence run of this watch. Migx has NO git link to mixxxdj/mixxx (fresh
  history, hard fork — ADR-002); this is the sanctioned channel to pull upstream signal and propose
  RE-IMPLEMENTED ports, never a git merge or remote."
disable-model-invocation: false
user-invocable: true
allowed-tools: [Bash, Read, Write, Edit]
defers_to:
  - kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md
  - kanban/knowledge/upstream-issues-m4-features.md
  - kanban/knowledge/upstream-easy-issues-triage.md
  - kanban/tasks/upstream-mixxx-watch-skill.md
audit_gate: "advisory — produces a dated log section + task cards; any accepted port is build+test-gated when executed as a task/dossier (P-03 for perf)."
verifiable_output_shape: "A new dated `## <YYYY-MM-DD>` section appended to kanban/knowledge/upstream-mixxx-watch-log.md, plus zero or more kanban/tasks/ port-candidate cards."
metadata:
  cites_patterns: []
---

# mixxx-upstream-watch — pull upstream signal without re-coupling

Migx is a hard fork with **fresh git history and no remote link** to mixxxdj/mixxx
([ADR-002](../../../kanban/architecture/decisions/ADR-002-hard-fork-no-upstream-merge.md)). You learn
from upstream by **querying the public repo via `gh` and re-implementing** what's worth having — never
by adding a git remote, cherry-picking across ancestry, or merging.

## Procedure

1. **Find the last-checked date.** Read the newest `## <date>` heading in
   `kanban/knowledge/upstream-mixxx-watch-log.md`. If the file doesn't exist, use 30 days ago as the
   floor. Call this `SINCE`.

2. **Query upstream since `SINCE`** (public repo, read-only):
   ```
   gh pr list   --repo mixxxdj/mixxx --state merged --search "merged:>SINCE" --limit 60 \
                --json number,title,mergedAt,labels
   gh release list --repo mixxxdj/mixxx --limit 5
   gh issue list --repo mixxxdj/mixxx --state open --label easy --limit 30 --json number,title,labels
   ```

3. **Triage against Migx subsystems.** Keep only items relevant to our surfaces — **engine/RT**,
   **waveform/render** (Apple-Silicon north-star), **controllers**, **library/DB**, **audio I/O**.
   Drop packaging/CI/Windows/Linux-only noise. Flag anything Apple-Silicon-relevant.

4. **Write the log.** Prepend a `## <today>` section to `kanban/knowledge/upstream-mixxx-watch-log.md`
   with a table: `#PR/issue | title | Migx subsystem | port verdict (port / watch / skip) | why`.
   The section heading date becomes the next run's `SINCE` marker — keep it incremental.

5. **Propose ports as tasks, not merges.** For each `port` verdict, scaffold a
   `kanban/tasks/<slug>.md` card (see `kanban/tasks/` for the shape) describing the change to
   **re-implement** into Migx, with a build+test acceptance gate. Perf-relevant ports cite `P-03`.
   Do NOT open a git remote or attempt a cross-repo merge.

6. **Report** the shortlist (top ~5 port candidates) and the log path. Ports execute later as their own
   tasks/dossiers — this skill only surfaces and records; it does not implement.

Complements the one-shot research notes it defers to (`upstream-issues-m4-features`,
`upstream-easy-issues-triage`) by making the check **repeatable and incremental**.
