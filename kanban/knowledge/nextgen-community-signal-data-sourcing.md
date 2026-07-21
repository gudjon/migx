---
id: nextgen-community-signal-data-sourcing
type: knowledge
title: "NextGen — community-signal data sourcing (YT views + DJ-set heat)"
status: research
owner: gudjon
authored_by: grok-signal
created: "2026-07-21"
lastUpdated: "2026-07-21"
defers_to:
  - kanban/knowledge/nextgen-modes-library-multideck.md
  - kanban/knowledge/world-model-experience-ontology.md
related:
  - nextgen-modes-library-multideck
  - nextgen-music-management-mode
  - initiative-ai-djing-product
sources:
  - "YouTube Data API v3 quota (developers.google.com) — videos.list=1u, search.list=100u, default 10k/day + 100 search/day"
  - "SoundCloud API Guide + Rate Limits (developers.soundcloud.com) — OAuth 2.1 PKCE; play stream 15k/24h; metadata not globally capped"
  - "Mixcloud API (mixcloud.com/developers) — URL-shaped REST; search; cloudcast sections; rate limits with Retry-After"
  - "Beatport API v4 docs (api.beatport.com/v4) — catalog/charts/search; no public setlist graph"
  - "1001Tracklists — track total_plays / set appearances; anti-scrape; third-party Parse.bot wrappers exist; no official open API"
---

# Community-signal data sourcing — field brief

**Question (Claude → grok-signal mail):** Can NextGen show per-track (a) YouTube play counts and (b) DJ-set appearance counts (Mixcloud / SoundCloud / Beatport) with real APIs, ToS, quotas, coverage, matching — and what pipeline should we ship?

**Verdict in one line:** **(a) YouTube views: yes, feasible offline if video IDs are cached.** **(b) “Appears in N DJ sets” as stated on Mixcloud+SoundCloud+Beatport: not feasible as a clean multi-platform count — use 1001Tracklists (or licensed setlist data) as the set-appearance proxy; Beatport = chart heat, not setlists; Mixcloud/SC = partial/expensive.**

UI implication (already in modes doc): chips are **sourced + dated**, secondary to local mixability; never rank only on YT views.

---

## 1. Source matrix

| Source | Per-track signal obtainable? | Official API? | ToS / ops reality | Coverage (DJ library) | Matching key | Cost / rate |
|---|---|---|---|---|---|---|
| **YouTube** | **Yes — `statistics.viewCount`** (likes, etc.) | Data API v3 `videos.list` | Google Cloud key; default **10 000 units/day** for non-search; **search.list 100 units + separate 100/day bucket** | High for popular/mainstream; weak for white-label/tool tracks with no official upload | Best: stable **videoId**; resolve once via search or user link | **Cheap once ID known:** up to 50 IDs / call @ 1 unit → ~500k stats/day theoretical. **Expensive to discover:** search burns quota |
| **SoundCloud** | **Plays/likes on a SC track** (`playback_count` etc. on track resource) — **not** “# of DJ sets containing this song” | Yes — OAuth 2.1 PKCE; app registration (Artist Pro path for keys) | Rate: **stream plays 15k/24h**; aggregate metadata **not currently globally capped**; reuse tokens | Strong for promo/underground SC-first releases; weak for label-only Beatport IDs | title+artist search → track id; fragile for remixes | Feasible for **track heat** batch; **not** setlist co-occurrence without crawling all playlists/mixes |
| **Mixcloud** | **Cloudcast metadata + `sections` (tracklist)** on known shows; search cloudcasts | Yes — simple REST (`api.mixcloud.com` URL mirror); OAuth for write/me | **Rate limits on all actions**; `403` + `Retry-After`; limits “still tweaking” (no public SLA numbers) | Good for **tagged** long-form DJ shows; many uploads lack accurate sections | Artist/song strings in sections — no ISRC | **Set appearance count requires indexing many cloudcasts** then string-matching sections → slow, incomplete, ToS-sensitive if aggressive |
| **Beatport** | **Catalog metadata + chart position / hype** | API v4 exists (`/catalog/tracks`, `/catalog/charts`, search) — developer portal login | Partner/commercial access typical; not a free setlist firehose | Excellent for **electronic retail** identity (ISRC, release, genre chart) | **ISRC / Beatport track id** best in class | **Chart heat, not “played in N sets.”** Do not claim setlist count from BP |
| **1001Tracklists** | **Yes — total tracklist appearances / recent plays** (site charts; track pages) | **No public first-party open API** | Explicit **anti-scrape** (datacenter/VPN blocks); community scrapes exist; third-party scrapers/APIs (e.g. Parse.bot marketplace) = vendor risk + ToS | **Best coverage for “DJs actually played it”** in EDM | Title/artist/mix string; sometimes ISRC-adjacent via labels | **Right product metric**, **wrong legal posture** for naive scrape. Prefer partnership or licensed third party |
| **MusicBrainz / AcousticBrainz / Discogs** | Identity layer (ISRC, MBID, release) — **not community heat** | Yes (MB rate-friendly with UA) | Fine for matching | Variable | **ISRC / MBID** | Use as **join key**, not chip source |
| **Spotify / Apple** | Popularity / playlist counts (platform-specific) | Partner APIs | Strict ToS; not booth-core | Mainstream | ISRC | Optional later; not in owner ask |

---

## 2. Feasibility verdicts

### (a) YouTube play counts — **FEASIBLE (batch offline)**

| Piece | Recommendation |
|---|---|
| Stats fetch | `GET videos?part=statistics&id=id1,...,id50` — 1 quota unit |
| ID discovery | **Do not** `search.list` every library track every day. Prefer: user pastes link, MusicBrainz/YouTube Music URL tags, one-time search + cache `videoId`, or optional “official video” field in FSL |
| Storage | FSL sidecar / EXO property: `community_signal.youtube = { video_id, view_count, fetched_at, match_confidence }` |
| Booth | Read-only cache; grey if stale > N days |
| Failure mode | No video match → omit chip (never invent 0) |

### (b) DJ-set appearance counts on Mixcloud / SoundCloud / Beatport — **NOT FEASIBLE AS STATED**

| Platform | Why not “set appearance count” |
|---|---|
| **Beatport** | Charts + sales catalog. No setlist graph in public developer surface. |
| **SoundCloud** | Track **playback_count** is stream heat, not set membership. Building “N mixes include track X” means crawling playlists/mixes globally — no endpoint for reverse setlist index. |
| **Mixcloud** | Closest: cloudcasts have **sections** (artist/song). There is **no** “give me all shows containing track X by ISRC.” You must search/crawl → parse sections → fuzzy match. Rate-limited; incomplete tagging. |

**Closest real proxy for “how many DJ sets”:**

1. **1001Tracklists-class setlist index** (`total_plays` / unique DJs / windowed charts) — product-correct, partnership or licensed feed preferred.  
2. **Secondary:** Mixcloud **sampled** corpus (genre tags, followed DJs, user-supplied cloudcast URLs) for **personal network heat**, not global N.  
3. **Tertiary:** SoundCloud **playback_count** + likes as **promo heat**, labelled as such (not “sets”).  
4. **Beatport chart rank / genre position** as **retail heat**, labelled as such.

Product copy should never say “48 Mixcloud sets” unless the pipeline actually counted Mixcloud sections with a documented match rate.

---

## 3. Matching risk (local track → external entity)

| Key | Strength | Notes |
|---|---|---|
| **ISRC** | Highest | Often in Beatport/purchase tags; rare in SC/Mixcloud sections; not on YT |
| **MusicBrainz recording MBID** | High | Good bridge once resolved |
| **Beatport track id** | High (electronic) | Chart + catalog |
| **YouTube videoId** | High once known | Wrong video = wrong view count (live vs official vs DJ rip) |
| **title + artist + remixer** | Medium | Normalize (feat., VIP, extended); Camelot irrelevant here |
| **Duration + BPM** | Weak disambiguator | Helps reject wrong hit |
| **Audio fingerprint (Chromaprint/AcoustID)** | High for identity | Offline prep; use to attach ISRC/MBID before community fetch |

**Rules for chips:**

- Store `match_confidence` + `matched_as` (isrc | mbid | string | manual).  
- UI: only show numeric heat if confidence ≥ threshold; else “YT linked” without count or hide.  
- Never auto-attach first YouTube search hit without confirmation in PREP mode (booth mid-set: use cache only).

---

## 4. Recommended pipeline (v1 → v2)

### Principles

- **Offline / PREP only** — never on RT thread or mid-set network.  
- **Sidecar cache** into FSL / EXO `community_signal` (stale-ok).  
- **Local crates + key/energy first**; community is secondary chip (modes doc §5).  
- **Honest labels** per source (views ≠ sets ≠ chart rank).

### v1 (ship chips without lying)

```text
Local library track
    → resolve identity (ISRC / MBID / AcoustID offline)
    → Beatport: chart position + genre (if id/ISRC)     → chip "BP Melodic #4"
    → YouTube: cached videoId → videos.list statistics  → chip "YT 12M"
    → SoundCloud: optional track id → playback_count    → chip "SC 890k plays"
    → Local play history                                 → chip "you · 6×"
    ✗ Do not claim "N sets" yet unless 1001TL (or peer) feed exists
```

**Quota posture:** nightly batch per active library (or on PREP enrich). Cap YT search to new/unmatched tracks only (e.g. ≤80/day → leave headroom). Batch `videos.list` 50-wide.

### v2 (true setlist heat)

```text
Licensed setlist feed (1001Tracklists partnership / commercial API / own corpus)
    → map setlist track rows → ISRC/MBID/string
    → aggregate appearances_90d, unique_djs_90d
    → chip "TL 48 sets · 90d"
Optional: Mixcloud follow-graph sample for "your scene" heat
```

Without a license, **do not scrape 1001TL from product** — anti-scrape + ToS risk.

### Explicit non-goals (v1)

- Real-time multi-platform scrape from booth.  
- Silent AI re-rank by YT views.  
- Claiming Mixcloud+SC+Beatport “set counts” as one number.  
- Client-side API keys that hit Google/SC from every DJ install (use optional user keys **or** Migx-hosted enrich with consent + quota — product decision).

---

## 5. EXO / FSL sketch (machine-consumable)

```yaml
# sidecar — not RT
community_signal:
  fetched_at: "2026-07-21T00:00:00Z"
  identity:
    isrc: "…"
    mbid: "…"
    match_confidence: 0.92
  youtube:
    video_id: "…"
    view_count: 12400000
    match_confidence: 0.85
  beatport:
    track_id: 123
    chart: { genre: "Melodic House & Techno", rank: 4, window: "daily" }
  soundcloud:
    track_id: 456
    playback_count: 890000
  setlist:                    # null until v2 feed
    source: null              # "1001tracklists" | "mixcloud_sample" | …
    appearances_90d: null
    unique_djs_90d: null
```

Co-pilot may use these as **features** with weights; UI always shows source glyph.

---

## 6. Coverage honesty (what DJs will see)

| Library slice | Likely chip density |
|---|---|
| Chart / Beatport purchases | High BP + often YT |
| Promo SoundCloud drops | SC plays; weak BP/YT |
| White labels / edits | Often **no** external heat — local crates dominate (correct) |
| Classics / festival IDs | High YT + high setlist (v2) |

Empty heat is OK — **recognition UI still has art, tags, crates**.

---

## 7. Claims (tagged)

| Claim | Confidence | Evidence |
|---|---|---|
| YT `videos.list` yields viewCount; batch 50 IDs @ 1 unit | high | Official quota calculator + 2026 quota writeups |
| YT search is the bottleneck (100 units; ~100 search/day default) | high | Google default allocation notes |
| SC API gives track plays, not reverse setlist index | high | SC API guide (tracks/search/playlists); no set-appearance endpoint |
| Mixcloud can expose sections but not global reverse index | high | Mixcloud developers docs |
| Beatport is charts/catalog, not setlists | high | API v4 catalog/charts surface |
| True “DJ set count” ≈ 1001Tracklists-class data; scrape is hostile | med–high | Site anti-scrape FAQ; third-party scraper APIs; industry use |
| Offline FSL sidecar is the only house-safe path | high | RT physics + modes doc §5 |

---

## 8. Recommended next steps

| Who | Action |
|---|---|
| **Owner** | Value call: partner/license setlist data vs ship v1 without “N sets” chip |
| **Claude** | EXO property + FSL sidecar schema; ARRANGE card chips (mock data OK) |
| **Codex / tools** | Optional `tools/` enrich job skeleton: YT batch + Beatport chart pull behind feature flag |
| **Grok** | Closed this mail; no further handoff unless owner picks v2 path |

**Acceptance for this research:** met — sources, feasibility, ToS/quota, matching, pipeline (v1 feasible signals + honest proxy for set heat).
