---
id: prep-set-research-harness
type: knowledge
title: "PREP set-research harness — enrich portable track packages from field sets"
status: draft
owner: gudjon
authored_by: grok-signal
created: "2026-08-08"
lastUpdated: "2026-08-08"
defers_to:
  - kanban/knowledge/track-as-skill-portable-package.md
  - kanban/knowledge/nextgen-community-signal-data-sourcing.md
  - kanban/knowledge/arrange-nexttrack-copilot-scoring.md
  - kanban/knowledge/session-coaching-multimodal-agent.md
  - kanban/knowledge/agent-filesystem-hooks-integration.md
related:
  - tools/migx-cli/migx_cli/lastfm.py
  - fixtures/music-mode-50/transitions.json
  - kanban/tasks/lastfm-signal-layer.md
  - initiative-ai-djing-product
note: >
  Pre-session (PREP) long harness: research public/licensed setlists and charts,
  mine before/after context and heat, write into per-song portable packages.
  Never on RT; never invent sources; offline cache only in booth.
---

# PREP set-research harness — iterate the song package data layer

## One sentence

Before a gig, a **long offline harness** researches how the world is *actually*
playing tracks in your crate (and near-neighbours), then **writes structured
priors into each song’s portable package** — so Arrange / `set.plan` / the coach
open with field-informed edges, not empty taste folders.

This is **prep intelligence**, not live Automix and not mid-set networking.

## Why this is the right product moment

| Phase | Human job | Harness job |
| --- | --- | --- |
| **PREP (hours/days before)** | pick crate, energy arc, bootleg policy | long research, graph enrich, trend chips |
| **ARRANGE (booth, glance)** | choose next | rank using **cached** co-occurrence + mixability |
| **PERFORM** | hands on decks | no network; packages already loaded |
| **COACH (during/after)** | floor judgment | overwrite/append **local truth** on top of field priors |

Field priors answer: *what are other DJs doing with this record?*  
Your night’s `track.feedback` answers: *what did **this** room do?*  
Local floor always outranks stale global heat when both exist.

## What you already have (compose, don’t restart)

| Piece | Status | Role in this harness |
| --- | --- | --- |
| Portable track package idea | research | write target: `graph/`, `taste/`, `community/` |
| Community-signal sourcing brief | research | honest per-platform capabilities + ToS |
| Arrange scoring layers | active | `w_cooc`, `w_trend` consume cache only |
| Fixture `transitions.json` | landed | schema + judge path for co-occurrence |
| Last.fm client | code | **your** play-next corpus (personal transition memory) |
| Spotify playlist pull | code | mirror crates / “what was on lists” — not set order |
| Session coach + feedback | shipped | night harvest into packages after the gig |

## The closed loop (P-01)

```text
Trigger    →  PREP started for crate / Collection slice / “gig folder”
Capture    →  setlists, charts, blogs, your scrobbles (paced APIs / imports)
Intelligence → match to ISRC/path; mine A→B edges; theme clusters; heat
Adjustment →  write package layers + rebuild offline cooc index
Re-check   →  set.plan / Arrange chips differ; fixture/judge still green
```

Long harness = this loop unattended for hours (Grok overnight / Claude research
wave / scheduled job), with **disk contracts** not chat logs as the result.

---

## Inputs — what each source is *honestly* good for

Reuse the sourcing matrix; labels must never lie:

| Source | Good for | Not good for | Package fields |
| --- | --- | --- | --- |
| **Your Last.fm** | *your* A→B transitions, play counts | global “trending” | `graph/personal_pairs`, `taste/local_plays` |
| **Your Spotify mirrors / crates** | inventory, “on which lists” | real DJ order | `community/list_membership` |
| **Mixcloud** (API, paced, user follows / URL list) | long-form show **sections** → consecutive pairs when tagged | global set count without a crawl corpus | `graph/field_pairs` (source=mixcloud), notes |
| **SoundCloud** | promo/stream heat | “# of DJ sets” | `community/sc_plays` |
| **Beatport** | chart/genre heat, identity (ISRC) | setlists | `community/bp_chart` |
| **YouTube** (cached video ids) | view heat | setlists | `community/yt_views` |
| **1001Tracklists-class** | real “played in N sets” / who played it | free scrape (ToS) | `community/set_appearances` **only if licensed/partner** |
| **DJ blogs / 1001 writeups / RA** | theme language, “peak anthem”, narrative | structured pairs (NLP weak) | `notes/field.md`, theme tags with low confidence |
| **Shazam / set ID** (future) | live identification of what was played | — | later |

**Default dogfood path (legal + useful):**

1. Personal Last.fm consecutive scrobbles → pair edges.  
2. User-supplied Mixcloud cloudcast URLs + official API sections → pair edges.  
3. Beatport/YT **offline batch** heat chips.  
4. Optional: licensed setlist feed when available.  

Do **not** ship a “scrape Mixcloud/1001TL” job as product core.

---

## Outputs — how the portable package grows

Per track (Shape A package beside audio):

```text
Title.migx/
  MANIFEST.md                 # refresh description if themes stabilize
  community/
    summary.json              # { fetched_at, sources[], chips[] }
    sources/
      lastfm.json
      mixcloud_sample.json
      beatport.json
      youtube.json
  graph/
    field_after.jsonl         # { to_isrc|to_key, count, window, sources[] }
    field_before.jsonl
    personal_after.jsonl      # from your scrobbles
    pairs/                    # optional deep notes for strong edges
  taste/
    themes.json               # inferred + human-confirmed
    placement_hints.json      # opener/mid/peak from set position histograms
  notes/
    field.md                  # agent prose: "often after melodic openers in …"
  history.jsonl               # untouched by research (floor only) OR separate
```

### What the harness is allowed to write

| Allowed | Forbidden |
| --- | --- |
| Append/update **sourced** counts with `fetched_at` + `match_confidence` | Invent “48 sets” without counting |
| Propose themes with `confidence: low` until human confirms | Overwrite human `policy: bootleg-special` |
| Add pair edges with source tags | Delete local floor feedback |
| Refresh MANIFEST description **proposal** file | Auto-rewrite MANIFEST without review in v1 |
| Recompute offline `transition_priors` index | Touch RT / mid-set network |

Human confirmation pattern (skill-like): harness writes
`taste/themes.proposed.json`; coach or PREP TUI promotes to `themes.json`.

---

## Algorithm sketch (offline)

### 1. Scope

```text
targets = Collection tracks in selected crate OR whole Collection
        OR “tracks with empty graph/” first (cold packages)
```

### 2. Identity resolve (once, cached)

```text
path → ISRC / MBID / normalized (artist, title, remix)
store in identity.json; refuse community attach if confidence < threshold
```

### 3. Mine edges

```text
for each setlist document (cloudcast sections / scrobble stream / licensed TL):
  for consecutive (A, B) in time order:
    if both resolve to library (or B is external neighbour):
      edge[A→B] += 1
      record set_meta: dj, city?, date, source_url
```

External neighbours (not in library) become **gap candidates** or soft edges
“people play *X* after your track” for discovery — not forced into set.plan until
owned.

### 4. Aggregate per track

```text
for track T in targets:
  field_after  = top K B by count from edges T→*
  field_before = top K A by count from edges *→T
  position_hist = { opener, mid, peak } from index-in-set
  co_djs        = who played T (if source has DJ id)
  theme_cluster = bag-of-tags from co-occurring tracks’ genres/labels
```

### 5. Write packages + global index

```text
write Title.migx/graph/*.jsonl
write Title.migx/community/summary.json
merge into library-level:
  Application Support/Migx/cache/transition_priors.json  # or FSL
  (schema already stubbed: migx.transition_priors.v1)
```

### 6. Re-check

```text
migx set.plan --json          # edges should surface in why/score later
# Arrange chips: "TL·12 after" only when source honest
# judge: fixture + optional live package schema check
```

---

## Long harness shape (agent / overnight)

Fits Grok long harness + Claude implementer split:

```text
Wave 0  Scope crate; list cold packages; identity resolve batch
Wave 1  Ingest sources (Last.fm pages, Mixcloud URL list, BP/YT cache)
Wave 2  Build edge table (ISRC×ISRC counts, 90d + all-time windows)
Wave 3  Write packages (atomic); rebuild priors index
Wave 4  Report: top new edges, top trending-in-crate, unresolved matches
Wave 5  Optional: propose MANIFEST description diffs for human accept
```

**Disk contract for the run:**

```text
~/Library/Application Support/Migx/research/
  runs/2026-08-08T12Z-prep/
    scope.json
    sources_manifest.json
    edges.jsonl
    write_receipts.jsonl
    report.md
```

Agent may be interrupted; receipt file is the SSoT of what got written
(same discipline as engine bridge receipts).

CLI surface (target):

```bash
migx research.prep --crate "Night - Club X" --sources lastfm,mixcloud-urls
migx research.prep --track "Feel It" --deep
migx research.status --json
migx research.apply --run <id>          # or auto-apply with --write
migx track.package show "Feel It" --json
```

---

## How Arrange / plan consume it (never invert weights)

From `arrange-nexttrack-copilot-scoring`:

```text
score = mixability          # always first
      + crate context
      + personal edges      # your Last.fm / your nights
      + field co-occurrence # research harness
      + trend heat          # capped secondary chip
      + floor feedback bias # retire/weak/worked (shipped)
```

**Clash still sorts last.** Trend never overrides “unmixable.”

---

## Relationship to coaching and the gig night

```text
PREP research  →  packages have field priors
      ↓
you arrange / set.plan with eyes open
      ↓
PERFORM + coach  →  local feedback appends history
      ↓
post-gig harvest →  floor truth updates taste/ + personal graph
      ↓
next PREP research  →  field layer refreshes; does not wipe floor
```

Two writers, two layers: **`community/` + `graph/field_*`** vs **`taste/` +
`graph/personal_*` + feedback**. Merge at read time with explicit precedence.

---

## Risks and non-goals

| Risk | Mitigation |
| --- | --- |
| ToS / scrape | Official APIs, user-supplied URLs, licensed feeds only |
| Wrong match (remix chaos) | confidence threshold; no chip if low |
| Trend dominates taste | cap `w_trend`; mixability first |
| Network mid-set | PREP-only; booth reads cache |
| Package bloat | progressive disclosure; summary.json always small |
| Silent empty research | report.md must list failures (P-34) |
| Automix identity | research **informs** order; human/armed load only |

**Wont-do:** claim multi-platform “N sets” without counting; RT research;
executable code inside packages; auto-load decks from research.

---

## Build order

| # | Deliverable | Acceptance |
| --- | --- | --- |
| 1 | Package dirs + schema for `community/` + `graph/field_*` | validate empty package ok for play |
| 2 | Last.fm → personal edges → packages | edges from real scrobbles on dogfood user |
| 3 | `transition_priors` rebuild from packages + fixture judge | schema green |
| 4 | Mixcloud URL list ingest → sections → edges | paced; receipts |
| 5 | BP/YT offline heat into `community/` | honest chip labels |
| 6 | `research.prep` long harness CLI + run dir | overnight report |
| 7 | Arrange/set.plan consume field edges | score delta fixture |
| 8 | Licensed 1001TL-class feed (if/when) | only then “set appearances” chip |

---

## Bottom line

**Yes** — pre-session long research that mines **who plays what before/after**,
**heat**, and **themes**, then **iterates the portable package** around each song,
is exactly the PREP closed loop that makes track-as-skill packages alive.

It is not a new product identity: it is the **field layer** of the package, fed by
honest sources, consumed offline by Arrange, and always **overridable by your
floor** the night of the gig.
