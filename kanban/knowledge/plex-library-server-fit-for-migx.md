---
id: plex-library-server-fit-for-migx
type: knowledge
title: "Plex (and peer media servers) — features that fit Migx libraries & EXO"
status: active
owner: gudjon
created: "2026-07-18"
lastUpdated: "2026-07-18"
task: kanban/tasks/research-plex-library-server-features-for-migx.md
related:
  - world-model-experience-ontology
  - spotify-dj-integration-landscape-2026
  - filesystem-driven-architecture
  - ADR-005
  - ADR-006
sources:
  - "https://www.plex.tv/blog/important-2025-plex-updates/ (remote playback; music/photos often exempt)"
  - "https://support.plex.tv/articles/requirements-for-remote-playback-of-personal-media/"
  - "https://support.plex.tv/articles/201638786-plex-media-server-url-commands/"
  - "https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/"
  - "https://support.plex.tv/articles/201105738-creating-and-managing-server-shares/"
  - "https://developer.plex.tv (official PMS API docs, JWT era)"
  - "https://www.plex.tv/blog/plex-pro-week-25-api-unlocked/ (API unlock, short-lived tokens)"
  - "https://python-plexapi.readthedocs.io/ (community client; audio/track models)"
  - "https://www.plexopedia.com/plex-media-server/api/ (community endpoint catalogue)"
  - "Peer landscape: Jellyfin, Navidrome/OpenSubsonic, Emby (2025–26 field)"
note: >
  Research pass for Migx library expansion. Separates browse/index from decode/playback.
  Does not authorize any RT multi-deck stream from Plex without separate rights analysis.
---

# Plex library/server features → Migx fit

**Question:** What does Plex offer that could fit Migx — especially **connecting to known servers for libraries** — without repeating the Spotify multi-deck trap?

**Answer in one line:** Treat Plex (and peers) as a **household media index + optional file path resolver** that plugs into Migx the way **iTunes/Serato/Rekordbox external library features** already do — not as a second RT decoder until paths/rights are clear.

---

## 1. Product model (what Plex is)

```text
┌──────────────────── plex.tv account ────────────────────┐
│  Auth · device tokens · list of servers you own/share   │
└──────────────────────────┬──────────────────────────────┘
                           │ resources / “known servers”
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   Your PMS (LAN)    Friend’s PMS      Shared library ACL
   :32400            remote relay*     section-level shares
         │
         ▼
   Library sections: Movies | TV | Music | Photos | …
         │
         ▼
   Artists → Albums → Tracks  + playlists/collections
```

\*Remote video often needs **Plex Pass** or **Remote Watch Pass** (2025–26). **Music/photos to Plexamp/Photos apps are largely exempt** from those video remote paywalls — important for library prep vs gig playback.

---

## 2. Feature inventory → Migx mapping

### 2.1 Connect to known servers (highest fit)

| Plex surface | What it does | Migx fit | Layer |
|---|---|---|---|
| **Account-linked server list** | After sign-in, clients see servers you own or were invited to | Prefs: “Plex servers” list; pick one or more for library features | B/C |
| **LAN discovery** | Find PMS on local network (GDM / known host:32400) | Gig laptop ↔ NAS same Wi‑Fi — primary path | A/B |
| **Direct host:port** | Manual `http://ip:32400` | Power users; offline LAN without cloud | B |
| **Shared libraries** | Owner grants section-level access to other Plex users | Optional “friend crate”; privacy sensitivity high | B |
| **X-Plex-Token / JWT auth** | Token on every PMS API call; plex.tv moving to short-lived JWT | Worker-only token store; never RT; rotate | B |

**Migx UX sketch (doable):**  
Settings → Library → **Add media server** → sign-in or paste token → select **Music** sections → import/index.

### 2.2 Music libraries & metadata

| Surface | Notes | Migx fit |
|---|---|---|
| **Music library section** | Artist / album / track hierarchy; ratings; play counts | Map tracks → Mixxx `Track` / library DB rows |
| **Metadata / agents** | Tag + agent enrichment; custom metadata agents (Plex roadmap + API docs) | Prefer **file tags + path**; agents as optional enrichment |
| **Sonic Analysis** (Plex Pass) | Music analysis for mixes/DJ-ish features in Plexamp | **Do not depend** — Migx has AnalyzerBeats/Key; EXO owns experience |
| **Playlists & collections** | User playlists; smart filters | Import as Mixxx playlist/crate **or** EXO session `order[]` |
| **On deck / history** | Continuity features | Low priority for DJ prep |

### 2.3 API & integration (implementation substrate)

| Surface | Notes | Migx fit |
|---|---|---|
| **PMS HTTP API** (`:32400`) | e.g. `/library/sections`, section contents, item metadata | **Read-only importer** on worker thread |
| **Official developer.plex.tv** | Documented API push (2025 Pro Week “API Unlocked”) | Prefer official docs over reverse-only |
| **Token auth** | `X-Plex-Token=…` query/header | Keychain-backed settings |
| **python-plexapi / community clients** | Mature client models for Track/Album/Artist | Reference for endpoint shapes; product code stays C++/Qt |
| **Transcode sessions** | Server-side transcode | **Avoid for DJ RT** — want original file path or direct play |

### 2.4 Playback (carefully)

| Surface | Notes | Migx fit |
|---|---|---|
| **Direct play file path** | When library is on a mount Migx can see (same NAS share) | **Best path:** resolve Plex item → absolute path → existing Mixxx file open |
| **Stream URL via token** | HTTP stream from PMS | Possible sequential preview; **not** multi-deck RT without underrun/rights analysis |
| **Plexamp** | Dedicated music client UX | Steal UX patterns only (server picker, library browse) |
| **Remote Watch Pass / Plex Pass** | Video remote gated; music remote freer | Gig prep at home OK; venue may be LAN-only |

### 2.5 Features that look cool but are poor Migx fits

| Surface | Why low fit |
|---|---|
| Free ad-supported Plex TV / Live TV | Not DJ crate material |
| Discover / universal availability | Catalog discovery ≠ local set prep |
| Skip intro / movie extras | Video product |
| Common Sense Media | Parenting, not DJ |
| Server as exclusive audio device | Competes with Core Audio instrument path |

---

## 3. Hard boundary: index vs decode (Spotify lesson)

Same architecture as EXO hybrid / Spotify paste-import:

| Mode | Allowed | Forbidden without partner/rights work |
|---|---|---|
| **Browse & index** tracks from Plex Music section | ✅ | |
| **Import metadata** into Mixxx library + EXO (`source: plex`) | ✅ | |
| **Resolve to local/NAS file path** and load into engine | ✅ if path exists on Mac | |
| **Dual-deck mix** of two pure Plex HTTP streams | | ❌ default — glitch + ToS risk |
| **Transcode-on-the-fly** as RT source | | ❌ underrun / P-02 risk |

**Rule:** Plex row with a **reachable file path** = first-class local track.  
Plex row that is **stream-only** = EXO **sequence-only / prep** (like Spotify URI).

---

## 4. Peer comparison (known-server library pattern)

| System | Auth / discovery | Music strength | API | Migx note |
|---|---|---|---|---|
| **Plex** | Account + LAN; shares | Good; Plexamp | PMS HTTP + official docs push | Highest “already owned” install base among DJs with NAS |
| **Jellyfin** | Self-host; no mandatory cloud account | OK music; less client polish | Open REST | Good open alternative; Quick Connect UX |
| **Navidrome / OpenSubsonic** | Host:port + user | **Music-first** | Subsonic-compatible (huge client ecosystem) | Best pure-music server API to also support |
| **Emby** | Similar to Plex model | OK | Proprietary API | Lower priority than Plex + Subsonic |
| **Apple Music / MusicKit** | Apple ID | Catalog + user library | MusicKit | Catalog rights — separate from self-host |
| **Local folders / Browse** | Path | Full file control | Filesystem | Already in Migx (`BrowseFeature`) |

**Recommendation:** Design a **generic “Media server library feature”** with two backends later:

1. **Plex** (household default)  
2. **OpenSubsonic** (Navidrome etc.) — same product problem, cleaner OSS API  

Do **not** hard-code only Plex if the abstraction is free.

---

## 5. Where it plugs into Migx code (evidence)

Existing external-library pattern (already ships):

| Feature | Path | Pattern |
|---|---|---|
| iTunes | `src/library/itunes/` | `BaseExternalLibraryFeature` |
| Serato | `src/library/serato/` | same |
| Rekordbox | `src/library/rekordbox/` | same |
| Traktor / Rhythmbox / Banshee | respective dirs | same |
| Browse folders | `src/library/browse/` | filesystem walk |

**Natural home for Plex:**  
`src/library/plex/` (or `mediaserver/`) subclassing **`BaseExternalLibraryFeature`** — sidebar section, import as playlist/crate, load track if path resolvable.

**Not home:** `src/engine/**` RT paths; analyzer callback; SoundIO.

**EXO hybrid:** extend `source` enum with `plex` | `subsonic` | `jellyfin` alongside `local` / `spotify` (session schema already has hybrid policy).

---

## 6. Layer mapping (ADR-005)

| Layer | Role of Plex integration |
|---|---|
| **A Instrument** | Only if resolved **file path** loads through existing SoundSource; no new RT backend required for v1 |
| **B Agent seams** | Server list, library feature, EXO identity, prep cues, co-pilot “crate includes NAS music” |
| **C Intelligence** | Optional: rank Plex crate with EXO energy/harmonic (same as local) |

---

## 7. Recommended next steps (doable)

### Step 0 — Contract (done by this note)
Acceptance criteria for research task met.

### Step 1 — Spike prefs + list servers (1–2 days)
- Settings panel: Plex account token **or** manual host + token  
- Call plex.tv resources / PMS identity; show server name + connection (LAN vs remote)  
- **No** library scan yet  
- Worker thread only; token in Keychain

### Step 2 — Music section index → external library feature (2–4 days)
- List music library sections; page tracks  
- Map into temporary external tables or import to Mixxx library with `location` = resolved path when available  
- Sidebar: **Plex** like iTunes/Serato  
- EXO optional: write `source: plex`, `external_ids.plex_rating_key`

### Step 3 — Path resolution policy
- If track `Media.Part.file` is on a mounted volume → treat as local  
- Else mark `playback.mode: prep_only` / sequence-only in EXO  
- Never invent dual-stream multi-deck

### Step 4 (optional) — OpenSubsonic backend
- Same UI; different connector  
- Captures Navidrome users without second product

### Explicit non-goals (v1)
- Plexamp clone  
- Plex Live TV / Discover  
- Remote video features  
- Sonic Analysis as Migx analyzer replacement  
- Transcode-as-deck  

---

## 8. Risks & house physics

| Risk | Mitigation |
|---|---|
| Token leak | Keychain; never log token; never commit |
| Network on RT | All PMS HTTP on **worker** only (`P-02`) |
| Library DB spam | Batch import; typed DAO (`P-27`/`P-28`) |
| Path lies (Windows path on Mac) | Detect mount; fall back to prep-only |
| ToS / remote streaming paywalls | Prefer LAN for gigs; document Pass requirements |
| Scope creep into media center | Stay music-library-only |

---

## 9. Comparison to Spotify path (relations)

| | Spotify (Octave path) | Plex path |
|---|---|---|
| Identity | `spotify:track:…` | `plex://{server}/{ratingKey}` or path |
| Multi-deck | Forbidden without partner | Only if **file path** multi-deckable |
| Best use | Prep / sequence / hybrid crate | **Home library** on NAS already ripped |
| API | Web API + ToS | PMS API + token |
| EXO edge | `sequence-only` common | `local`-like when path works |

Together: **Spotify = commercial catalog identity**; **Plex = self-hosted file index**. Both feed the same hybrid crate / EXO graph.

---

## 10. Acceptance checklist (task)

- [x] Inventory Plex surfaces (servers, music lib, API, remote, shares, Plexamp)  
- [x] Map to Migx layers A/B/C + library/EXO/FSL  
- [x] Separate browse/index vs decode  
- [x] Peer compare (Jellyfin, Navidrome/Subsonic, Emby, MusicKit, folders)  
- [x] 0–3 doable steps + out-of-scope  
- [x] Primary citations  

---

## 11. Suggested federation handoff (when implementing)

**To Claude:** “Implement Step 1–2 as `LibraryFeature` spike under `src/library/plex/` (or generic mediaserver), worker-only, path-resolve policy, no RT. EXO `source: plex` optional fixture.”  
**To Codex:** “Verify no RT/network on callback; token not logged; import uses DAO migrations if schema changes.”  
**Grok:** continue field watch on PMS API/JWT changes and OpenSubsonic client ecosystem.
