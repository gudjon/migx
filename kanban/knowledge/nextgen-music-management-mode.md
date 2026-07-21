---
id: nextgen-music-management-mode
type: knowledge
title: "NextGen music management mode — arrangement, recognition, and next-queue decisions"
status: active
owner: gudjon
authored_by: codex-cli
authored_kind: agent
created: "2026-07-21"
lastUpdated: "2026-07-21"
defers_to:
  - kanban/knowledge/nextgen-shadow-app-proposal.md
  - kanban/knowledge/nextgen-dj-needs-and-leader-ui-map.md
  - kanban/knowledge/nextgen-dj-ux-modes-and-signal.md
  - kanban/knowledge/nextgen-modes-library-multideck.md
  - kanban/knowledge/mod-music-management-mode.md
  - kanban/knowledge/nextgen-community-signal-data-sourcing.md
  - kanban/knowledge/nextgen-bakeoff-deck-strip-copilot.md
  - kanban/knowledge/product-discovery-customer-leadership-migx.md
  - kanban/runbooks/ai-ui-migration-loop.md
related:
  - initiative-ui-modernization
  - initiative-ai-djing-product
  - nextgen-agent-dj-shadow-product
  - dj-shared-library-capability
  - filesystem-driven-architecture
---

# NextGen music management mode

## Owner refinement

NextGen is not only a new dual-deck skin. The hard DJ problem is often **arrangement and music
management under pressure**: quickly recognizing the right next song, seeing why it fits, staging it,
and loading it without increasing cognitive load in a busy club.

This should become a first-class **full-screen mode** the DJ can switch into and out of quickly. It
must preserve the playing state and never behave like a blocking dialog.

## Product decision

Treat music management as a **mode**, not a table:

```text
Performance mode:  active decks, mixer, waveform trust surface
Music mode:        crate/map/search/arrangement surface for next-queue decisions
```

The two modes share the same data plane and deck load path. Performance mode keeps the DJ safe while
tracks are playing. Music mode helps the DJ make the next selection faster and with less recall burden.
For the broader field/signal treatment of PERFORM/ARRANGE/LIBRARY modes, vertical multi-deck, and
community heat chips, defer to `nextgen-modes-library-multideck.md`; this note owns the Codex-readable
product contract and judge.
For the first-hand owner-DJ evidence capture, defer to `nextgen-dj-ux-modes-and-signal.md`. For the
draft machine contract and chip schema, defer to `mod-music-management-mode.md`.

## Cognitive-load rules

| Rule | Product meaning |
|---|---|
| Recognition beats recall | Track cards need cover art, mini-waveform, key/BPM/energy, cue/vocal markers, tags, and playlist memberships |
| Show a small decision set | Live focus should surface 3 to 5 strong candidates, not a giant ranked dump |
| Deck state stays visible | Full-screen music mode still needs compact now-playing/free-deck context |
| Fast escape matters | One key/controller action returns to performance mode without changing playback |
| Every action is explicit | Queue, pin, audition, or load to a free deck requires a visible user action |
| Degraded is allowed | Missing external signal becomes a quiet badge, never a modal |

## Multi-deck model

Technology can support flexible vertical deck/staging capacity, but the product should separate:

- **Playable decks:** bounded by UI, audio routing, and controller trust. Initial working cap should be
  explicit, likely 4 to 6 even if the architecture can represent more.
- **Staging lanes:** effectively unbounded next-candidate or arrangement lanes. These are not audio
  engines until the DJ loads one into a real deck.

This keeps the product open to vertical deck workflows without turning every candidate into a live
engine burden.

## Track-recognition card

Minimum useful track card:

| Field | Why it exists |
|---|---|
| Title, artist, remix, version | Avoid wrong-version loads |
| Cover art or stable visual fingerprint | Recognition in a dark, high-pressure setting |
| Mini waveform and phrase/vocal markers | Structure at a glance |
| BPM, key, energy, length | Mix compatibility |
| User tags and crates | The DJ's own memory system |
| Playlist memberships | "Where have I used this before?" |
| Last played and set history | Avoid accidental repeats |
| Candidate reason | Explain why it is suggested now |
| Confidence/provenance | Prevent fake certainty |

## Community and market signal

External/community signal should enrich recognition and confidence, but it must not be a live
dependency.

**Feasibility SSoT (2026-07-21):** `nextgen-community-signal-data-sourcing.md`.  
**Chip schema + MODULE:** `mod-music-management-mode.md` §4.

| Signal | Useful if it answers | v1 reality |
|---|---|---|
| YouTube listens/views | Is this familiar to the room or broadly known? | **Feasible offline** (`videos.list` + cached videoId) |
| Beatport charts/store metadata | Genre / chart placement | **Chart heat** — not setlist count |
| SoundCloud plays/likes/reposts | Promo / underground activity | **playback_count** — not “N sets” |
| Mixcloud / true DJ-set appearances | Do DJs actually put this in sets? | **Not** reverse-indexable via MC/SC/BP; use **1001Tracklists-class** feed as v2 `setlist_appearances` |
| Internal Migx set history | Has this DJ used it successfully? | Always available locally (`local_plays`) |

Store as optional FSL/EXO `community_signal.chips[]` with `kind`, `display`, `value_num`,
`match_confidence`, `observed_at`, `stale_after_hours`. Hot path reads cache only. **Honest labels:**
never render SC plays or BP rank as “sets.”

## Mode anatomy

```text
┌─ compact now-playing context ──────────────────────────────────────────────┐
│ Deck A/B/C/D status · free deck target · key/BPM/energy context            │
├─ search and crate map ─────────────────────────────────────────────────────┤
│ query · filters · tags · playlists · source · recent set packs             │
├─ visual track field ───────────────────────────────────────────────────────┤
│ cards/lanes grouped by crate, energy arc, playlist membership, or signal   │
├─ next queue / staging lanes ───────────────────────────────────────────────┤
│ pinned candidates · planned order · audition notes · load target           │
└─ action rail ──────────────────────────────────────────────────────────────┘
  Queue · Load free deck · Pin · Dismiss · Explain · Return to Performance
```

## Architecture

- Build this in QML first so it shares the performance shell, `Theme.qml`, and CO load semantics.
- It is Surface B-like in information density, but it must drive Surface A deck loads directly.
- Rich web/shadcn experiments may inform prototypes, but the live mode should not depend on WebView
  or network calls.
- EXO/FSL should be the local data plane for BPM, key, cues, energy, and candidate reasons.
- External platform signals should be imported/prepared before the set and displayed with provenance.

## Judge

Minimum machine-checkable judge for `mod-music-management-mode`:

```text
1. fixture library loads with at least 50 tracks and multiple tags/playlists
2. search/filter returns stable results within the fixture
3. track cards render identity, BPM/key/energy, tags, playlist memberships, and signal chips
4. mode switch preserves current deck play state
5. queue/load action only targets an explicitly selected free deck
6. missing external signal shows a non-modal degraded state
7. no network is required during live-mode judge
8. screenshot/pixel gate proves no text overlap at laptop and wide desktop sizes
```

## Discovery questions

Use the product-discovery harness before overfitting the UI:

1. Last time you struggled to find the next track mid-set, what happened?
2. What visual cue makes you recognize a song fastest in your current software?
3. Which tags, crates, or playlist memberships do you actually use under pressure?
4. Do community signals change your decision, or only prep discovery?
5. What would make you distrust an AI next-track recommendation even if it looked compatible?

## Federation split

| Agent | Strong lane |
|---|---|
| Claude Code | Build feasibility, QML shell/mode scaffold, module contracts, launch smoke |
| Grok signal | Current DJ/community signal sources, API/ToS feasibility, X/community pain around library/search |
| Codex | Engine boundary, judge design, claim rules, P-08 review, no-modal/CO invariants |

**Bottom line:** NextGen needs a dual/multi-deck performance surface, but the product wedge may be the
music-management mode that helps a working DJ decide what to queue next. Build it as a mode with
cached signals, explicit actions, and a mechanical judge.
