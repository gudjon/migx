# transitions.json — setlist co-occurrence priors (ARRANGE)

**Schema:** `migx.transition_priors.v1`  
**File:** `transitions.json`  
**Consumers:** ARRANGE next-track list, `cap-copilot-suggestion`, offline judge.

## Purpose

Stub the owner idea: **“what DJs play *after* this track”** without live network.

| Field | Meaning |
|---|---|
| `edges[].from` → `to` | Ordered pair observed in synthetic setlists |
| `edges[].count` | Appearance count in window (higher = stronger prior) |
| `edges[].display` | Booth chip fragment e.g. `48 after` |
| `inbound_totals` | Total times a track was the *destination* (aggregate heat) |

## QML / ViewModel use

```text
NOW deck track id = nowId
for candidate c in selected_crate:
  cooc = edges where from==nowId and to==c.id
  display chip: cooc.display or hide
  score += w_cooc * normalize(cooc.count)
mixability always ranks above cooc (see arrange-nexttrack-copilot-scoring.md)
```

## Rules

- **Offline only** — never fetch on booth hot path.  
- **Synthetic** — `source: fixture_synthetic`; not real 1001Tracklists.  
- Labels: `TL · N after` or chip kind `setlist_appearances` with honest `meta.feed`.  
- Clash mixability still sorts last even if cooc is high.

## Related

- `kanban/knowledge/arrange-nexttrack-copilot-scoring.md`  
- `community_signal/index.jsonl` — aggregate `setlist_appearances` chips derived from inbound_totals  
