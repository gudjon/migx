---
id: mod-music-management-mode
type: module-contract
title: "MODULE — mod-music-management-mode (ARRANGE / music brain)"
status: draft
owner: gudjon
authored_by: grok-signal
created: "2026-07-21"
lastUpdated: "2026-07-23"
defers_to:
  - kanban/knowledge/nextgen-music-management-mode.md
  - kanban/knowledge/nextgen-modes-library-multideck.md
  - kanban/knowledge/nextgen-community-signal-data-sourcing.md
  - kanban/knowledge/nextgen-cognitive-load-perform-arrange-library.md
  - kanban/knowledge/nextgen-bakeoff-deck-strip-copilot.md
  - kanban/knowledge/nextgen-agent-dj-shadow-product.md
related:
  - nextgen-music-management-mode
  - nextgen-cognitive-load-perform-arrange-library
  - initiative-ui-modernization
  - initiative-ai-djing-product
---

# MODULE — `mod-music-management-mode`

**Job:** Full-screen **music brain** for a busy-club DJ — recognize tracks, see tags/crates/playlist membership, read **cached** community heat chips, stage 1–5 next tracks, load **only** to an explicitly free playable deck, return to PERFORM in one gesture. Audio never stops; mode is not a modal.

**Product names:** Music-management mode · ARRANGE (modes map). PERFORM deck strip remains the literacy surface (`nextgen-bakeoff-deck-strip-copilot`).

---

## 1. Acceptance (machine-consumable)

```yaml
acceptance:
  module: mod-music-management-mode
  host: qml-nextgen   # Surface A; no WebView required for hot path
  network_hot_path: false
  modal: false
  single_writer: true   # P-06 — load/queue only via documented CO writers
  fixtures:
    min_tracks: 50
    min_tags: 8
    min_playlists: 4
    community_signal_stub_coverage: ">=0.6"  # fraction of tracks with ≥1 chip stub
  checks:
    - id: nextgen-ui-rulebook
      cmd: "tools/ng-judge nextgen-ui lint --path res/qml/nextgen --assert-token-only --assert-no-blocking-modal"
      expect: exit 0
    - id: fixture-load
      cmd: "tools/ng-judge music-mode fixture-load --fixture fixtures/music-mode-50/"
      expect: exit 0
    - id: search-stable
      cmd: "tools/ng-judge music-mode search --q 'peak' --expect-ids id:03,id:11,id:27"
      expect: exit 0
    - id: filter-key-compatible
      cmd: "tools/ng-judge music-mode filter --key-compat free-deck --expect-count-range 3,12"
      expect: exit 0
    - id: cards-render
      cmd: "tools/ng-judge music-mode cards --require art,bpm,key,energy,tags,playlists,chips"
      expect: exit 0
    - id: mode-switch-preserves-play
      cmd: "tools/ng-judge music-mode switch-roundtrip --assert-playhead-continues"
      expect: exit 0
    - id: queue-then-load-free
      cmd: "tools/ng-judge music-mode stage-and-load --track id:07 --deck free --require-ack"
      expect: exit 0
    - id: no-load-busy-deck
      cmd: "tools/ng-judge music-mode load --track id:07 --deck busy --expect-reject"
      expect: exit 0
    - id: missing-signal-degrades
      cmd: "tools/ng-judge music-mode cards --track id:no-signal --assert-no-modal --assert-chip-empty-ok"
      expect: exit 0
    - id: no-network
      cmd: "tools/ng-judge music-mode offline-box --deny-net --run fixture-load,search-stable,cards-render"
      expect: exit 0
    - id: layout-no-overlap
      cmd: "tools/ng-judge music-mode screenshot --sizes laptop-1440x900,wide-1920x1080 --assert-no-text-overlap"
      expect: exit 0
  thresholds:
    mode_switch_ms_p95: 100   # UI only; audio independent
    search_ms_p95: 50         # fixture in-memory
```

**P-08:** Author of the module does not sole-grade — Codex/judge binary runs the frozen checks above.

### 1.1 Judge v0 landed

Codex landed the first offline judge on 2026-07-23:

- `tools/ng-judge` owns the `music-mode` acceptance checks above.
- `fixtures/music-mode-50/` is the frozen v0 data pack: 51 tracks, 9 tags, 5 playlists, 31 cached community-signal rows, free/busy deck state, and layout guard metadata.
- `tools/ng-judge nextgen-ui lint` fails QML below `res/qml/nextgen` on hardcoded visual literals or blocking modal patterns.
- `just ng-music-judge` runs the full acceptance list in one command, including `just ng-ui-lint`.

This is a fixture judge, not the final visual/CO parity judge. It exists so the ARRANGE module can be
built against a stable contract before real sidecar enrichment, UI screenshots, and ControlObject load
writers are wired in.

---

## 2. Surfaces & mode shell

```text
┌─ MODE BAR ──────────────────────────────────────────────────────────────┐
│  [ PERFORM ]  [ ARRANGE ● ]  [ LIBRARY ]     hotkey / pad / edge        │
└─────────────────────────────────────────────────────────────────────────┘
┌─ NOW RIBBON (always visible in ARRANGE/LIBRARY) ────────────────────────┐
│  A: title · bars left · BPM/key   B: …   free decks: 2   target: auto  │
├─ SEARCH / FILTER CHIPS ─────────────────────────────────────────────────┤
│  q · crate · tag · key-compat · energy · played-tonight · heat band    │
├─ CANDIDATE FIELD (grid or dense list) ──────────────────────────────────┤
│  TrackCard × N (virtualized)                                           │
├─ STAGE QUEUE (1…5 cards) ───────────────────────────────────────────────┤
│  ordered next · load free · dismiss                                    │
└─ ACTION RAIL ───────────────────────────────────────────────────────────┘
   Stage · Load free · Why · Return PERFORM
```

| Control | Semantics |
|---|---|
| PERFORM ↔ ARRANGE | One keystroke; no focus trap; ribbon keeps room awareness |
| Stage | Adds to stage queue; **not** a playable deck (no RT cost) |
| Load free | Requires free playable deck + explicit Ack; writes CO load path only |
| Return PERFORM | Instant; stage queue preserved |

---

## 3. Track card (atomic unit)

| Field | Required | Source |
|---|---|---|
| title, artist, remixer | yes | library / FSL |
| artwork or waveform thumb | yes (placeholder ok) | local |
| bpm, key, energy | yes | analyzer / EXO |
| tag chips | yes (may be empty) | local taxonomy |
| playlist / crate chips | yes (may be empty) | local |
| community chips | optional | FSL `community_signal` cache |
| candidate reason | optional | co-pilot / EXO |
| Stage / Load free / Why | yes | actions |

---

## 4. Community signal chip schema (from sourcing research)

**SSoT feasibility:** `nextgen-community-signal-data-sourcing.md`.

### 4.1 Principles

1. **Cached only** on hot path — PREP/offline enrich writes sidecar; booth reads.  
2. **Honest labels** — never show “N sets” for Beatport chart rank or SC plays.  
3. **Confidence-gated** — omit chip if `match_confidence` < threshold (default 0.7).  
4. **Stale is grey** — show number + age; do not block UI.  
5. **Never sole ranker** — co-pilot weights community secondary to key/tempo/energy/local crates.

### 4.2 Machine shape (FSL / EXO sidecar)

```yaml
# per track — tools/exo or .migx sidecar
community_signal:
  schema: "migx.community_signal.v1"
  fetched_at: "2026-07-21T00:00:00Z"   # ISO8601 UTC
  identity:
    isrc: null | string
    mbid: null | string
    match_method: "isrc" | "mbid" | "beatport_id" | "youtube_id" | "string" | "manual"
    match_confidence: 0.0..1.0
  chips:                          # UI iterates this list only
    - kind: youtube_views
      label: "YT"                 # short glyph family
      display: "12M"              # pre-formatted for booth
      value_num: 12400000
      unit: views
      source_id: "dQw4w9WgXcQ"    # videoId
      match_confidence: 0.85
      observed_at: "2026-07-20T12:00:00Z"
      stale_after_hours: 168
    - kind: beatport_chart
      label: "BP"
      display: "Melodic #4"
      value_num: 4
      unit: chart_rank
      meta: { genre: "Melodic House & Techno", window: "daily" }
      source_id: "bp:12345"
      match_confidence: 0.95
      observed_at: "2026-07-21T00:00:00Z"
      stale_after_hours: 48
    - kind: soundcloud_plays
      label: "SC"
      display: "890k"
      value_num: 890000
      unit: plays
      source_id: "sc:456"
      match_confidence: 0.8
      observed_at: "2026-07-19T00:00:00Z"
      stale_after_hours: 168
    - kind: setlist_appearances   # v2 only — null chips until feed exists
      label: "TL"
      display: "48 sets · 90d"
      value_num: 48
      unit: set_appearances
      meta: { window_days: 90, unique_djs: 31, feed: "1001tracklists" }
      source_id: "tl:…"
      match_confidence: 0.9
      observed_at: "2026-07-21T00:00:00Z"
      stale_after_hours: 72
    - kind: local_plays
      label: "you"
      display: "6×"
      value_num: 6
      unit: local_plays
      match_confidence: 1.0
      observed_at: "2026-07-21T00:00:00Z"
      stale_after_hours: 8760
```

### 4.3 Kind allowlist (v1 vs v2)

| `kind` | v1 fixture | Live enrich | Forbidden claim |
|---|---|---|---|
| `youtube_views` | stub OK | YT Data API offline | “sets” |
| `beatport_chart` | stub OK | BP charts API | “DJ set count” |
| `soundcloud_plays` | stub OK | SC track API | “set appearances” |
| `local_plays` | from fixture history | always | — |
| `setlist_appearances` | stub optional | **blocked** until licensed feed | inventing MC/SC/BP set totals |
| `mixcloud_sets` | **not in v1** | only if sampled crawl + honest “sample” label | global Mixcloud N |

### 4.4 UI rendering rules

```text
chip := [label][display]  e.g.  YT 12M · BP Melodic #4 · SC 890k · you 6×
long-press / Why → source + observed_at + match_confidence + stale?
stale (now - observed_at > stale_after_hours) → muted token, still tappable
missing chips → no placeholder noise (empty is fine)
```

### 4.5 Co-pilot feature vector (optional weights — open assumption)

```text
score = w_key * key_fit
      + w_tempo * tempo_fit
      + w_energy * energy_arc
      + w_crate * local_crate_boost
      + w_community * f(chips)     # small; never dominates
```

`f(chips)` must ignore `setlist_appearances` until v2 feed is real. Do not use raw YT views as the only community term (wedding-banger bias).

---

## 5. Fixture contract (`fixtures/music-mode-50/`)

Minimum files:

```text
fixtures/music-mode-50/
  library.jsonl          # >=50 tracks: id, title, artist, remix, bpm, key, energy, art_stub
  tags.jsonl             # tag_id, name, color
  track_tags.jsonl       # track_id, tag_id
  playlists.jsonl        # playlist_id, name
  playlist_tracks.jsonl  # playlist_id, track_id, position
  community_signal/      # cached chip stubs (>=60% coverage)
    index.jsonl
  history.jsonl          # local plays for "you" chips
  free_decks.json        # playable deck pool state for load tests
  layout.json            # non-modal/no-network/viewport-overlap metadata
```

**Judge v0 uses only this tree** — no network, no live YT/SC/BP. Later visual/CO judges may add
in-process QML.

---

## 6. ControlObject / load boundary

| Action | Allowed writer | Notes |
|---|---|---|
| Stage queue mutate | UI / mode controller | Local queue model; not engine |
| Load track → free deck | **One** documented load path (same as classic library load) | P-06; never mid-set silent |
| Play/pause/cue | Existing deck CO writers | Mode must not steal |
| Community fetch | Offline worker only | Never from `process*()` |

Staging ≠ playable deck. Playable cap (4–6) is engine policy; stage list is UI-virtual.

---

## 7. Out of scope (this module)

- Full dual-deck waveform parity (bake-off strip owns literacy).  
- Live multi-platform scrape in booth.  
- AI silent setlist / auto-load without Ack.  
- WebView-only library.  
- Claiming unified “Mixcloud+SoundCloud+Beatport set counts” without a real reverse index.

---

## 8. Build order (Claude)

1. Mode shell + ribbon + hotkey PERFORM↔ARRANGE (mock cards).  
2. Fixture loader + search/filter — include **function/role crates** (opener, peak, bridge, reset, closers) per cognitive-load research.  
3. TrackCard with tags/playlists + chip renderer (schema §4).  
4. Stage queue + load-free Ack path.  
5. Judge scripts wired to acceptance YAML.  
6. Wire real offline enrich later (tools/) — not blocking UI dogfood.

**Cognitive-load probes (when judge exists):** time-to-stage under play; mode-switch preserves L1 SA ribbon; no-network; see `nextgen-cognitive-load-perform-arrange-library.md` §5.

---

## 9. Claims

| Claim | Confidence |
|---|---|
| MODULE acceptance above is sufficient for first dogfood of music mode | med |
| Chip schema matches sourcing research (YT/BP/SC/local; setlist v2) | high |
| No network + no modal + free-deck-only load are non-negotiable for club path | high |
