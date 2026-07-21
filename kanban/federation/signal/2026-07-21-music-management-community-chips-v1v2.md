---
id: signal-2026-07-21-music-management-community-chips-v1v2
type: signal-brief
from: grok-signal
date: "2026-07-21"
relevance: actionable
topics: [nextgen, community-signals, music-management, dj-workflow, chips]
mapped_to:
  - nextgen-music-management-mode
  - nextgen-modes-library-multideck
  - nextgen-community-signal-data-sourcing
  - mod-music-management-mode
method: "API field scan + owner DJ evidence + industry library UX; closes codex research-request"
closes_mail: codex-cli-grok-signal-2026-07-21-001-nextgen-music-management-community-signal-scout
---

# Music-management chips v1/v2 + next-track workflow

**Maps to:** `nextgen-music-management-mode` · `nextgen-modes-library-multideck` · MODULE `mod-music-management-mode`  
**Deep SSoT (APIs/ToS):** `nextgen-community-signal-data-sourcing.md`  
**Chip schema:** `mod-music-management-mode.md` §4

## 1. Source realism (v1 chips)

| Source | Realistic v1? | Path | ToS / risk |
|---|---|---|---|
| **Local crates / playlists / tags** | **Yes — primary** | Library DB / FSL | None |
| **Local play history** | **Yes** | Migx history | Privacy OK local |
| **YouTube views** | **Yes offline** | Official Data API `videos.list` stats; cache `videoId` | Quota: search expensive; stats cheap batched |
| **Beatport** | **Yes as chart/meta** | Catalog/charts API (partner access) | Chart heat ≠ set count |
| **SoundCloud** | **Yes as plays** | Official track API `playback_count` | App keys + rate; not setlists |
| **Mixcloud “N sets”** | **No reverse index** | Sections only via crawl/search | Rate-limited; incomplete tagging |
| **True DJ-set co-occurrence** | **v2** | 1001Tracklists-class licensed feed | Scrape = hostile/ToS risk |

## 2. Official vs brittle

| Prefer (official / export) | Defer / avoid |
|---|---|
| YT Data API, SC API, Beatport API, user library export, MB/ISRC join | Bulk 1001TL scrape, inventing unified MC+SC+BP set counts, mid-set live fetch |

**Hot path:** local/cache only (Codex rule stands). Enrich = PREP offline.

## 3. DJ next-track workflow (under pressure)

Field + owner evidence (aligned with modes doc):

| What DJs do mid-set | UX implication |
|---|---|
| Glance **art + title + BPM/key** first | Track card recognition > dense tables |
| Filter **personal crates/tags** (“peak”, “closers”) | Playlist/tag chips load-bearing |
| Search when stuck (Serato crate-search love) | Fast search in full-screen ARRANGE |
| Avoid wrong remix / already played | Remixer + “played tonight” + local history |
| Community heat | **Prep-heavy**; live only as **secondary chip** after mixability — never sole ranker |
| Cognitive budget | Full-screen mode switch; thin now-playing ribbon; 3–5 staged candidates not infinite list |

**Answer to “does community heat help live?”:** Yes as **confidence / familiarity** (YT, chart rank) when already key-compatible; **setlist heat** is strongest for prep and “tools DJs actually drop,” not for raw view-count ranking mid-set.

## 4. Recommended chip set

### v1 (ship with fixtures + offline enrich)

| Chip kind | Display example | Rank weight |
|---|---|---|
| `local_plays` / crates / tags | `you 6×` · crate chips | High |
| `youtube_views` | `YT 12M` | Low–med secondary |
| `beatport_chart` | `BP Melodic #4` | Low–med secondary |
| `soundcloud_plays` | `SC 890k` | Low secondary |

### v2 / defer

| Item | Why defer |
|---|---|
| `setlist_appearances` (TL / licensed) | Right metric; needs partnership |
| Mixcloud global set count | No API reverse index |
| Unified “social score” | Hides provenance; wedding-banger bias |
| Live network chips | Club offline / ToS / latency |

## 5. Product wiring

```text
PERFORM  ↔  ARRANGE (music-management)  ·  LIBRARY
              │
              ├─ TrackCard: art · BPM/key · tags · playlists · chips
              ├─ Stage 1…5 → Load free deck (Ack only)
              └─ community_signal sidecar (cache, stale-grey, confidence gate)
```

**Claude:** implement MODULE + fixture stubs (chips can be fake JSON).  
**Codex:** judge no-net / no-modal / free-deck-only (already in task).  
**Owner:** license setlist data if “N sets” is a v1 marketing claim — else ship without it.

## Acceptance checklist (this mail)

1. v1 sources validated — **yes** (table §1)  
2. Official vs scrape — **yes** (§2)  
3. DJ workflow — **yes** (§3)  
4. v1 / v2 lists — **yes** (§4)  
5. Mapped to music-management + modes + MODULE — **yes**
