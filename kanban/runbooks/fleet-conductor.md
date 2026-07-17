---
id: runbook-fleet-conductor
type: runbook
title: "Fleet conductor + Codex drain (autonomous multi-peer loop)"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
defers_to:
  - kanban/knowledge/fleet-operating-model.md
  - kanban/federation/FEDERATION.md
---

# Fleet conductor + Codex drain

## What it is
A thin **conductor** over `migx-fed` that:

1. Loads **open + ack** federation mail  
2. **Scores** by severity, subject (P-08/eval first), peer tie-break (Codex → Claude → Grok; AGY paused)  
3. Prints **NEXT DRI** + shell commands  
4. Optionally writes `kanban/federation/scratchpad/conductor/LATEST.md`  
5. Optionally runs **`migx-codex-drain.py`** for seal-class work (EXO P-08 today)

It does **not** auto-start Claude/Grok/Codex (avoids surprise compile load). You or cron start the DRI.
Antigravity is **paused** (no tokens) — conductor will not recommend it as NEXT.

## Commands

```bash
cd ~/code/migx   # or any worktree

# Rank queue + print next peer
python3 kanban/scripts/migx-fleet-conductor.py

# + write nudge file for peers / night loop
python3 kanban/scripts/migx-fleet-conductor.py --nudge-file

# + run Codex drains only when matching Codex mail is open/ack (EXO P-08 evaluate & close)
python3 kanban/scripts/migx-fleet-conductor.py --nudge-file --drain-codex

# JSON for tooling
python3 kanban/scripts/migx-fleet-conductor.py --json

# Codex drain only
python3 kanban/scripts/migx-codex-drain.py
python3 kanban/scripts/migx-codex-drain.py --dry-run
python3 kanban/scripts/migx-codex-drain.py --force-eval  # refresh artifact without active mail

# Codex long listen (manual peer)
export MIGX_FED_SIDE=codex-cli
./kanban/scripts/migx-fed listen --to codex-cli --interval 900 --cycles 0
```

## just recipes
```bash
just fleet            # conductor + nudge file
just fleet-drain      # conductor + codex drain + nudge
just fed-list         # open mail
just fed-poll SIDE=codex-cli
```

## Night loop (launchd / cron example)

```bash
# every 30 minutes while machine is awake — drain seal-class + refresh nudge
*/30 * * * * cd /Users/gudjon/code/migx && python3 kanban/scripts/migx-fleet-conductor.py --nudge-file --drain-codex >> /tmp/migx-fleet-conductor.log 2>&1
```

Or launchd: `kanban/runbooks/fleet-conductor.plist.example` (copy to `~/Library/LaunchAgents/` and customize paths).

## Peer duty after conductor says NEXT
1. Open the named CLI in the right worktree  
2. `migx-fed poll --to $SIDE`  
3. Act → close with Resolution  
4. Re-run `just fleet`  

## EXO P-08 drain (what automates)
When open/ack mail id/subject matches `exo-p08` / `evaluate-transition` and is addressed to
`codex-cli`:

- Validates fixture JSON  
- Camelot adjacency (same ring ±1)  
- Energy story (peak > outro, peak ≥ cool-down)  
- Proof recommends song-02; session order starts 01→02  
- Writes `…/results/P08-EVAL-codex.md`  
- Closes mail as **codex-cli**  

If no matching mail is active, the drain is a no-op. Use `--force-eval` to refresh the artifact
manually without closing mail.

## Safety
- No RT code executed  
- No force-push  
- Scratchpad nudges are gitignored under `federation/scratchpad/`  
- Generator never self-seals: drain is a **separate script** from the EXO author path  
