---
id: plex-library-server-fit-for-migx
type: knowledge
title: "DJ shared libraries — what Plex-style server sharing means for Migx"
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
sources:
  - "Plex Manage Library Access / server shares (section-level invite to other accounts)"
  - "Plex known-server list after account auth (own + shared-with-me)"
  - "Plex remote vs LAN; music often freer than video (2025–26 Remote Watch Pass context)"
  - "Migx: BaseExternalLibraryFeature, EXO hybrid crates, sequence-only policy"
note: >
  Scoped to DJ use case: DJs sharing libraries with each other — not Plex as a TV box.
  Index/browse/share identity ≠ multi-deck stream rights.
---

# DJ shared libraries — Plex pattern → Migx

**Use case only:** DJs want to **share crates/libraries** with other DJs (bandmate, residency partner,
friend’s collection, “play off my NAS for the night”) — not run a home cinema.

Plex is interesting here because it already solves one product problem well:

> **I have a library on a machine I control. I invite people I trust. Their client lists my server as a
> known library source.**

That is the pattern Migx should learn from — not Plexamp UX, not Live TV, not Discover.

---

## 1. What “DJs share libraries” actually means

| Scenario | Real need | Playback reality |
|---|---|---|
| **A. Same gig, same LAN** | Friend’s laptop/NAS is the crate; I load tracks onto my decks | Need **file path or low-latency local stream** on LAN |
| **B. Prep at home for a shared set** | See partner’s collection, plan order, export cues | Need **browse + metadata + EXO/session graph** — not dual-deck over WAN |
| **C. Shared residency crate** | One owner hosts; several DJs read the same music section | Need **stable identity + ACLs** (“who can see this crate”) |
| **D. Hand off a set** | “Here’s the playlist I prepped” | Need **playlist/order share** (EXO session / crate export) more than full server |

**Not the use case:** random internet streaming of a buddy’s rip collection as two RT decks over bad Wi‑Fi.

---

## 2. What Plex already does that matches this

Only the **share-relevant** surfaces:

| Plex mechanism | DJ translation |
|---|---|
| **Known servers** after sign-in | “Libraries I can use” = servers I own **or** was invited to |
| **Library Access / shares** | Owner picks **which libraries** (e.g. Music only) a friend account can see |
| **Section-level ACL** | Share the **music crate**, not movies/photos |
| **Friend sees server in their app** | One click: connect → browse shared Music section |
| **LAN when possible** | Same venue / same house → direct to PMS; no cloud middleman for bits if local |
| **Remote as second class** | Prep from hotel; video remote often paid — **music remote freer**, still not a gig guarantee |

**Ignore for this use case:** Live TV, Discover, Skip Intro, Common Sense Media, free ad movies, Sonic Analysis as product core, Plexamp-as-Migx-replacement.

---

## 3. How that maps into Migx (product)

```text
DJ A (host)                         DJ B (guest)
─────────────                       ─────────────
Owns library (NAS / disk)           Opens Migx
  │                                   │
  │  invite / share token             │  “Add shared library”
  │  or “known server” id             │
  ▼                                   ▼
Media server (Plex today;             Migx Library sidebar:
 later: Migx-native share)              Shared crates
  │                                   │
  └──── Music section ────────────────┤ browse / search
        playlists optional            │ pull into session
                                      │ EXO: source=shared
                                      ▼
                               Load only if path/stream
                               policy allows (LAN first)
```

### Layer fit (ADR-005)

| Layer | Shared-library role |
|---|---|
| **A Instrument** | Play only when audio is **reachable with RT-safe policy** (local path or proven LAN direct play) |
| **B Agent seams** | Shared crate identity, EXO hybrid session (`source: shared` / `plex`), prep cues, co-pilot over **union of crates** |
| **C Intelligence** | Rank “what fits next” across **my crate + partner’s shared crate** |

### EXO / hybrid crates (already in our ontology)

Same pattern as Spotify hybrid:

| Track kind | In shared crate | Multi-deck |
|---|---|---|
| Host file path mounted on guest Mac | `source: shared` + path | ✅ like local |
| Guest can only stream over network | `sequence-only` / prep | ❌ default (or LAN-only experimental) |
| Spotify URI in a shared session export | identity | sequence-only (existing policy) |

**Co-pilot win:** “Suggest next from *our* shared residency crate” using harmonic + energy edges over both libraries.

---

## 4. Two product paths (pick later; both valid)

### Path 1 — **Connect to Plex as the share plane** (faster for users who already Plex)

- Migx is a **client** of PMS: list known servers, open **shared Music** sections.  
- Host keeps using Plex for ACLs and invites.  
- Migx only implements: auth, server list, music browse, path resolve, import to crate/session.  
- Fits existing `BaseExternalLibraryFeature` (iTunes/Serato-shaped).

**Best when:** DJs already run Plex on a NAS and invite each other today.

### Path 2 — **Migx-native shared crates** (long-term product moat)

- Host Migx (or a tiny “crate server” on Mac/NAS) exposes a **music library share** with invite links/tokens.  
- Protocol can be Subsonic-compatible or custom EXO/FSL sync.  
- Plex is then optional; lesson is the **product pattern**, not the vendor.

**Best when:** we want “Cursor for AI-DJing” ownership of the share graph, not Plex account dependency.

**Practical sequencing:** Path 1 spike teaches UX + policy; Path 2 reuses the same sidebar/EXO model without Plex branding.

---

## 5. Doable steps (shared-library scoped only)

1. **UX contract** — “Shared libraries” sidebar: list *servers/crates I’m allowed to see* (mock with 2 accounts / 2 fixtures first).  
2. **Read-only connect** — one known host (Plex or fixture) → list tracks + playlists; no RT.  
3. **Import into session** — selected tracks enter EXO hybrid session with `source` + share provenance.  
4. **Play policy** — if file path visible on this machine → load; else mark prep/sequence-only and show why.  
5. **Invite story (docs)** — host checklist: share Music only; prefer LAN at venue; guest Migx pulls index.

**Out of scope for this use case:**  
video libraries, remote multi-deck over cellular, replacing FSL/sidecars, building full Plexamp.

---

## 6. Risks specific to DJ sharing

| Risk | Mitigation |
|---|---|
| Guest can’t hear track at gig (path missing) | Explicit **playability badge** (local / LAN / prep-only) |
| Rights / ToS on remote personal media | Prefer LAN; document host Pass if remote music needed |
| Host goes offline mid-set | Cache index offline; never depend on live HTTP for RT buffer |
| Network on audio callback | All server I/O on **worker** only (`P-02`) |
| Oversharing whole server | Section-level share (Music only) — mirror Plex ACL idea |

---

## 7. Bottom line

**Relevant:** Plex-style **known servers + library invites + section ACL** so DJs can **share music crates** and plan sets together (browse, hybrid EXO, co-pilot over union).

**Irrelevant (for this use case):** media-center chrome, video remote passes, catalog Discover, turning Migx into a general Plex client.

**Implementation north-star:**  
`Shared library` as a first-class **external crate source** in the library sidebar + EXO hybrid session — whether the wire is Plex today or Migx-native share tomorrow.
