---
id: spotify-octave-style-doable-steps
type: knowledge
title: "Spotify via Octave-style architecture — realistic steps for Migx"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
progress:
  step0: done
  step1: done
  step1b_paste_import: done
  step2: open
  note: "paste-import via tools/exo + just exo-spotify-import; OAuth still optional"
defers_to:
  - kanban/knowledge/spotify-dj-integration-landscape-2026.md
  - kanban/Strategy-Current.md
sources:
  - "Octave Music Platform - June Concept Doc (external)"
  - "https://www.spotify.com/us/dj-integration/"
  - "https://developer.spotify.com/policy"
---

# Spotify the Octave way — simple, realistic steps for Migx

## What Octave proposes (platform shape)

The June concept doc treats Spotify as a **metadata + sequential listen** source; true multi-track
mixing of catalog streams is outside the public Web API / Playback SDK model.

| Layer | Octave approach | Migx meaning |
|---|---|---|
| **Auth + metadata** | OAuth → Web API → knowledge graph | Dev Mode / quotas apply |
| **Playback** | Official Web Playback / Connect; client does not re-host stream bytes | Single stream per session |
| **“DJ” for Spotify** | Sequential / simulated transitions; prep UI | One catalog stream at a time (API §III.7) |
| **True multi-deck** | Local / open audio (and future Artist Server) | Migx RT engine |
| **Prep station** | Cues, order, tags, export | High value without stream decode |
| **Offline crates** | Local files first; streaming offline is player/SDK-bound | Local Collection is the offline path |

Partner multi-deck (djay/Serato/rekordbox) is a separate BD path — see landscape note.

---

## Reality check for Migx

| Constraint | Implication |
|---|---|
| Spotify Dev Policy **§III.7** (no mix/overlap Spotify content) | Public API is not dual-deck of two catalog streams |
| Mixxx/Migx is a **native RT audio engine** | Web Playback is browser/Connect-class; not a drop-in `SoundSource` |
| House physics `P-02` | Network/decode never on RT callback |
| 2026 Dev Mode (Premium, 5 users, org-only extended quota) | Metadata experiments stay small until entity/quota |
| UX clarity | Label Spotify mode as sequence/prep unless partner streaming exists |

---

## Product split (Octave → Migx)

```text
┌─────────────────────────────────────────────────────────┐
│  UNIFIED LIBRARY (metadata)                             │
│  Local files + Spotify playlists/URIs + (later) others  │
│  EXO / FSL / crates                                     │
└───────────────┬─────────────────────┬───────────────────┘
                │                     │
     ┌──────────▼──────────┐  ┌───────▼──────────────────┐
     │  TRUE ENGINE DECKS  │  │  SPOTIFY PREP + LISTEN    │
     │  Local / open audio │  │  Sequential / Automix-lite│
     │  Full multi-deck    │  │  Official player surface  │
     │  stems/record OK    │  │  Cues as session metadata │
     └─────────────────────┘  └──────────────────────────┘
```

Wave-1 engineering targets **metadata + prep + local multi-deck**. Streaming dual-deck waits on
platform/partner capability.

---

## Stepped plan (smallest reversible unit each time)

### Step 0 — Freeze the contract (0.5 day, no code) — **DONE**

**Landed:** `kanban/tasks/spotify-octave-step0-contract.md`

1. **In-scope Spotify:** metadata sync + prep UX + sequential playback (if any).  
2. **Deferred for public API:** dual catalog streams, stems/record of streams.  
3. **Offline:** local Collection files; streaming offline is app/SDK-bound.  
4. Success metric for Step 3–4 is **prep UX + hybrid session graph**, not dual-stream parity.

---

### Step 1 — Spotify as **identity in EXO/FSL** (1–2 days) — **DONE**

**Landed under EXO dossier** (`2026-07-17-gudjon-EXO--experience-ontology-spike`):

| Artifact | Path |
|---|---|
| Schema | `fixtures/schema/migx.song-ontology.v1.json` (`source`, `external_ids`, `playback`) |
| Session prep | `fixtures/schema/migx.session-ontology.v1.json` (`prep`, `policy`, `sequence-only`) |
| SP-only song | `fixtures/songs/song-04-spotify-uri-only.ontology.json` |
| Hybrid session | `fixtures/sessions/session-hybrid-prep-demo.json` |
| Proof | `results/PREP-STATION-PROOF.md` |

**Verify:** fixture parse + hybrid policy checks green (zero network).  
**Value:** co-pilot can reason over Spotify IDs + local tracks with honest sequence constraints.

---

### Step 1b — Paste-import (no OAuth) — **DONE**

Offline dogfood path before Dev Mode OAuth:

```bash
just exo-spotify-import    # sample paste → songs/imported + session
just exo-fixtures-check    # structural + policy gates
```

| Artifact | Path |
|---|---|
| Tool | `tools/exo/spotify_uri_import.py` |
| Check | `tools/exo/check_fixtures.py` |
| Task | `kanban/tasks/spotify-octave-step1b-paste-import.md` |

Line format: `uri_or_url | title | artist | bpm | camelot`

---

### Step 2 — OAuth + **metadata-only** connector (2–4 days, optional Dev Mode app) — **OPEN**

**Goal:** Read library/playlists into Migx library DB or a sidecar index.

| Work | Detail |
|---|---|
| OAuth | PKCE app; tokens in OS keychain / secure prefs — never log tokens |
| Sync | Liked songs + user playlists → track rows with source=`spotify` |
| UI | QML list: browse playlists; **no load-to-deck** yet |
| Limits | Dev Mode: ≤5 users; document org/MAU wall for anything public |

**Verify:** refresh token rotation; disconnect deletes local tokens + optional purge.  
**House physics:** all network on worker thread; CO only for “sync status.”

**Do not** implement playback here.

---

### Step 3 — **Prep station** (the high-ROI Octave move) (3–5 days)

**Goal:** Migx is the best place to **prepare** sets that include Spotify tracks, without needing dual stream.

| Work | Detail |
|---|---|
| Session state | Cue points, notes, order, key/BPM **annotations** on Spotify URI rows (local-only state) |
| Hybrid crate | Local file tracks + Spotify URI tracks in one list |
| Export later | Optional: M3U/CSV of URIs + local paths for human use; **not** partner USB |
| EXO | Transition suggestions: “next track” ranked over hybrid list using local twins / metadata |

**Verify:** offline prep works with no Spotify network after sync.  
**Honest UX copy:** “Prepare here; dual-deck mix is for local files / partner apps.”

This is where Migx + AI co-pilot wins **without** partner SDK.

---

### Step 4 — Sequential Spotify listen path (choose **one** lane)

Octave uses Web Playback SDK in a web client. Migx is Qt/native. Pick the **simplest** lane:

#### Lane A — **Sidecar player** (simplest, most realistic)

| Work | Detail |
|---|---|
| Surface | Small QML/webview or external “Spotify Connect target” helper process |
| Behavior | One track play/pause/seek via **Connect / Web Playback** |
| Migx role | Queue + Automix-lite **commands** the sidecar; library stays Migx |
| Engine | Migx engine continues local decks; Spotify is **not** a deck channel |

**Pros:** No RT engine entanglement; fits single-stream Playback/Connect.  
**Cons:** Not “Spotify on Channel 1.”

#### Lane B — **Simulated Automix** (Octave’s “feels like a mix”)

| Work | Detail |
|---|---|
| Queue | Ordered hybrid playlist |
| Transition | On track end / user “next”: smart gap + optional FX on **local** buffer only if local; for Spotify, request next track on Connect with timed fade in Spotify’s player if API allows |
| UI | Two “prep decks” for **next/current** metadata + waveform **placeholders** (analysis only if legal preview/local twin) |

**Pros:** Matches Octave § “simulated transitions.”  
**Cons:** Easy to over-promise; keep “sequential” in the product name.

#### Lane C — Partner path (not engineering-first)

BD for official DJ integration. Parallel, long, no code commitment until contract.

**Partner streaming path:** BD track for official DJ integration — long, parallel to engineering.

---

### Step 5 — True multi-deck on local audio (ongoing)

| Work | Detail |
|---|---|
| Engine | Existing Mixxx decks for local files |
| EXO co-pilot | Best transitions among **analyzable** tracks |
| Source badge | Clear `LCL` vs `SP` on every row (Octave “Live-Link Badges”) |

**UX rule:** two Spotify catalog tracks on A/B → offer **sequence Automix / prep** until dual-stream
capability exists on a supported path.

---

### Step 6 — Extension surface (future)

Optional later modules hang off a capability flag + explicit enablement. Wave-1 acceptance does not
depend on them.

---

## Suggested first closed loop (1 week of real work)

| Day | Deliverable | Acceptance |
|---|---|---|
| 1 | Contract doc (Step 0) in a short task or `STR` research note | In/out scope frozen |
| 2–3 | Step 1 fixtures + EXO URI fields | `ctest`/fixture green |
| 4–5 | Step 2 OAuth + playlist list in library UI **or** skip OAuth and ship paste-import if quota friction | User can see Spotify playlists offline after one sync |
| 6–7 | Step 3 hybrid crate + cue notes on URI tracks | Prep a 10-track set with mix of local + Spotify IDs without playback |

**Defer** Step 4 until Step 3 feels good — prep station is the high-ROI path.

---

## Mapping Octave chapters → Migx artifacts

| Octave | Migx home |
|---|---|
| Local Agent + KG | EXO + library DB + optional sidecar process (not full Memgraph day one) |
| Spotify Module (metadata) | Worker + prefs OAuth; no RT |
| Web Playback SDK | Lane A sidecar / Connect — not `SoundSource` |
| Simulated sequential DJ | Automix-lite queue UI |
| True mix | Existing engine + local files |
| Focus-List offline | Local Collection first; Spotify = online sequential |

---

## Harder / later paths (not wave-1 “simple”)

- Reverse-engineering closed partner stream clients  
- Dual-deck overlap of two Spotify catalog tracks via public APIs alone  
- Building offline stream re-host as a v1 dependency  
- Model training on full-catalog audio without a rights package  

---

## One-sentence strategy

**Be the agentic prep + local multi-deck cockpit; treat Spotify as first-class metadata (and sequential
listen when wired) while multi-deck streaming waits on platform/partner capability.**

That is Octave’s actual Spotify plan, sized to Migx.
