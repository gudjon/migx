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

## What Octave actually proposes (not “hack the DRM”)

The June concept doc is explicit about the hard limit:

> True multi-track mixing from DRMed services like Spotify is a **no-go**.

Its **doable** Spotify design is:

| Layer | Octave approach | Legal / product meaning |
|---|---|---|
| **Auth + metadata** | Local agent OAuth → Web API metadata → knowledge graph | Allowed under Dev Mode / quotas (constrained) |
| **Playback** | Client embeds **official Web Playback SDK**; agent **never proxies audio bytes** | Official path; single stream per Connect session |
| **“DJ” for Spotify** | **Simulated transitions**: sequential, beat-matched crossfade *feel*, two-deck UI for prep | One stream at a time — not §III.7 multi-overlap of Spotify audio |
| **True multi-deck** | Only **local / non-DRM** (and future Artist Server) | Real Mixxx/Migx engine territory |
| **Prep station** | Cues, order, tags, export later to Serato/rekordbox | High value without stream decode |
| **Grey-zone** | Opt-in **modules** with disclaimers, not core product | Boundary only — core stays “squeaky clean” |
| **Offline “Focus-List”** | For DRM: SDK/license-bound cache only; no re-encode/re-host | Do **not** design a Spotify rip-cache in core |

So “hack our way” in the Octave sense means **architecture that works around the multi-deck DRM wall**, not reverse-engineering partner SDKs or ripping streams.

Partner multi-deck (djay/Serato/rekordbox) remains a separate BD path — see landscape note.

---

## Reality check for Migx

| Constraint | Implication |
|---|---|
| Spotify Dev Policy **§III.7** (no mix/overlap Spotify content) | No public-API multi-deck of two Spotify tracks |
| Mixxx/Migx is a **native RT audio engine** | Web Playback SDK is browser/Connect-class; not a drop-in `SoundSource` |
| House physics `P-02` | Network/decode never on RT callback |
| 2026 Dev Mode (Premium, 5 users, org-only extended quota) | Metadata experiments stay small until entity/quota |
| User expectation | Must label “Spotify mode” honestly: sequence + FX, not Serato-class dual stream |

---

## The honest product split (Octave → Migx)

```text
┌─────────────────────────────────────────────────────────┐
│  UNIFIED LIBRARY (metadata)                             │
│  Local files + Spotify playlists/URIs + (later) others  │
│  EXO / FSL / crates                                     │
└───────────────┬─────────────────────┬───────────────────┘
                │                     │
     ┌──────────▼──────────┐  ┌───────▼──────────────────┐
     │  TRUE ENGINE DECKS  │  │  SPOTIFY PREP + LISTEN    │
     │  Local / open audio │  │  Sequential “Automix-lite”│
     │  Full multi-deck    │  │  Official player surface  │
     │  stems/record OK    │  │  Cues as session metadata │
     └─────────────────────┘  └──────────────────────────┘
```

This is the **only simple path** that is both doable and not a legal time bomb.

---

## Stepped plan (smallest reversible unit each time)

### Step 0 — Freeze the contract (0.5 day, no code) — **DONE**

**Landed:** `kanban/tasks/spotify-octave-step0-contract.md`

1. **In-scope Spotify:** metadata sync + prep UX + sequential playback (if any).  
2. **Out-of-scope (core):** dual Spotify streams, stems on Spotify, offline rip, record of Spotify.  
3. **Grey-zone:** never in core; if ever explored, isolated opt-in only with explicit user risk — **do not schedule in v1**.  
4. Success metric for Step 3–4 is **UX + ToS posture**, not “sounds like Serato dual deck.”

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

**Pros:** No RT engine entanglement; ToS-aligned if single stream.  
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

**Do not schedule:** unofficial multi-deck decode, libspotify-era hacks, or DRM cache re-host (Octave Chapter 12 DRM download language is **not** a green light without partner legal).

---

### Step 5 — True multi-deck only where it’s free (ongoing)

| Work | Detail |
|---|---|
| Engine | Existing Mixxx decks for local files |
| EXO co-pilot | Best transitions among **analyzable** tracks |
| Source badge | Clear `LCL` vs `SP` on every row (Octave “Live-Link Badges”) |

**Product rule:** If user drops two Spotify tracks on A/B → UI offers **sequence Automix**, not silent fail or illegal dual stream.

---

### Step 6 — Optional “grey-zone module” boundary (architecture only)

Octave’s “Grey-Zone = Extension” is a **product boundary**, not a roadmap item to implement circumvention.

For Migx:

- Core = squeaky clean (Steps 1–5).  
- Extension API (future) = capability flags + user consent.  
- **No** core dependency on grey-zone for v1 acceptance.

---

## Suggested first closed loop (1 week of real work)

| Day | Deliverable | Acceptance |
|---|---|---|
| 1 | Contract doc (Step 0) in a short task or `STR` research note | In/out scope frozen |
| 2–3 | Step 1 fixtures + EXO URI fields | `ctest`/fixture green |
| 4–5 | Step 2 OAuth + playlist list in library UI **or** skip OAuth and ship paste-import if quota friction | User can see Spotify playlists offline after one sync |
| 6–7 | Step 3 hybrid crate + cue notes on URI tracks | Prep a 10-track set with mix of local + Spotify IDs without playback |

**Defer** Step 4 until Step 3 feels good — prep station is the Octave insight that works without fighting DRM.

---

## Mapping Octave chapters → Migx artifacts

| Octave | Migx home |
|---|---|
| Local Agent + KG | EXO + library DB + optional sidecar process (not full Memgraph day one) |
| Spotify Module (metadata) | Worker + prefs OAuth; no RT |
| Web Playback SDK | Lane A sidecar / Connect — not `SoundSource` |
| Simulated DJ for DRM | Automix-lite queue UI |
| True mix | Existing engine + local files |
| Focus-List offline | Local files only first; Spotify = online sequential |
| Grey-zone modules | Future; out of core |

---

## What we will not call “simple / doable”

- Reverse-engineering Serato/djay Spotify stream  
- Dual-deck overlap of two Spotify tracks via public APIs  
- Offline full-track locker for Spotify in core  
- Recording Spotify mixes  
- Training models on full Spotify audio without license  

Those are either partner-only or ToS/legal failures — not “hacks,” just blocked paths.

---

## One-sentence strategy

**Be the agentic prep + local multi-deck cockpit; treat Spotify as a first-class metadata and sequential-listen source until (if ever) a partner deal exists.**

That is Octave’s actual Spotify plan, sized to Migx.
