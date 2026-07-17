# AGY.md — Migx (Antigravity CLI entry) — **PAUSED**

> **2026-07-17:** Antigravity is **out of the active agent mix** — no tokens on this box.  
> Do not start `agy` sessions or send new federation mail to `antigravity-cli`.  
> Re-enable: restore tokens → set `peers.yaml` `antigravity-cli.status: active` → unpause this file.  
> Active fleet: **Claude Code** · **Codex CLI** · **Grok** (`kanban/federation/peers.yaml`).

---

Thin routing for **Antigravity CLI (`agy`)** sessions (dormant until tokens return). State each rule
once in its home — this file only points.

Default side id: **`antigravity-cli`** (autonomous co-implementer) — **paused**.

```bash
# Only when re-enabled:
export MIGX_FED_SIDE=antigravity-cli
./kanban/scripts/migx-fed poll --to antigravity-cli
```

- **Role charter:** [`kanban/federation/roles/antigravity-cli.md`](kanban/federation/roles/antigravity-cli.md) (status: paused)
- **Federation:** [`kanban/federation/FEDERATION.md`](kanban/federation/FEDERATION.md)
- **Peers SSoT:** [`kanban/federation/peers.yaml`](kanban/federation/peers.yaml)
- **Tool:** `agy` 1.1.3+ (prefer `/opt/homebrew/bin/agy` if PATH conflicts)

## While paused — who does the work?

| Former AGY domain | Current owner |
|---|---|
| QML / UI product slices | `claude-code` (or Gudjon) |
| EXO / ontology / sidecars | `claude-code` + Grok for research |
| Non-RT product waves | `claude-code` |
| RT / engine | still `claude-code` only |
| Verify / P-08 | `codex-cli` |
| Field signal | `grok-signal` |

## Re-enable checklist

1. Confirm Google Ultra / Antigravity login works: `agy -p "OK"`  
2. `peers.yaml`: `antigravity-cli.status: active` (remove paused_reason)  
3. Role charter + this file: `status: active`  
4. Restore multi-agent runbook Terminal 4 block  
5. Optional worktree: `git worktree add ../migx-agy -b agy/work`  
