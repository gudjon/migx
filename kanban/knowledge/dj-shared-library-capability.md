---
id: dj-shared-library-capability
type: knowledge
title: "DJ shared libraries — Migx-native capability (Plex as prior art only)"
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
  - initiative-ai-djing-product
prior_art:
  - "Plex-style known servers + section ACL + invite (pattern only — no product dependency)"
  - "Subsonic/OpenSubsonic client ecosystem (optional wire format later)"
  - "Migx BaseExternalLibraryFeature, EXO hybrid crates, sequence-only policy"
note: >
  Capability design for DJs sharing crates with each other. Not a Plex integration project.
  No Plex account, SDK, or server required in the architecture.
---

# DJ shared libraries — Migx capability

**Assumption:** **No Plex dependency.** We do not ship “connect to Plex” as a product requirement.  
Plex (and friends) are **prior art** for a product behavior we want under our own control:

> A DJ **hosts** a music library. Other DJs **connect** as guests, **browse** that crate, **plan** a set
> (EXO/session), and **play** only when the audio is actually available under house physics.

That is a **Migx capability** — Layer B agent seams + library — not a third-party media-server client.

---

## 1. Capability statement

| | |
|---|---|
| **Name** | Shared libraries (DJ-to-DJ) |
| **Who** | Host DJ + one or more guest DJs |
| **What** | Host exposes a **music crate** (tracks + optional playlists/cues). Guests see it as a **known library source** in Migx. |
| **Why** | Residency partners, back-to-backs, “play off my collection tonight,” shared prep without USB sticks only. |
| **Not** | General home theater, random cloud streaming, dual-deck over bad WAN by default. |

### Capability surface (product verbs)

1. **Host** — publish a share (library / crate / folder set).  
2. **Invite** — grant a guest identity access (token, link, account, or LAN trust).  
3. **Discover** — guest lists **known shares** they may use.  
4. **Browse / search** — guest indexes metadata offline-capable when possible.  
5. **Pull into session** — hybrid EXO session: my tracks + shared tracks.  
6. **Play with policy** — local/LAN path preferred; otherwise prep-only / sequence-only.  
7. **Revoke** — host drops guest; guest UI updates.

---

## 2. Scenarios (use-case only)

| ID | Scenario | Host | Guest need | Success |
|---|---|---|---|---|
| **S1** | Same venue, same LAN | Laptop/NAS on gig network | Browse + load into decks | Shared tracks play RT-safe |
| **S2** | Prep together before gig | Home server | Browse + build session order | EXO session mixes both crates |
| **S3** | Residency crate | One owner, many DJs | Read-only shared collection | Stable share id; ACL music-only |
| **S4** | Hand off a set | Exports session/crate | Import session graph | Order + cues + identity, not full server |

**Co-pilot (Layer C):** rank “what next?” over **union of my library ∪ shared libraries** using EXO edges (harmonic, energy, policy).

---

## 3. Prior art (inspiration only — not architecture)

| Prior art | Lesson we keep | What we do **not** take |
|---|---|---|
| **Plex known servers + shares** | “Libraries I’m allowed to see” list; section-level invite | Plex account, PMS protocol, plex.tv as SSoT |
| **Plex Music-only share** | Don’t share whole media life — share the crate | Movies/TV product |
| **LAN-first clients** | Gig reliability = local path/LAN | Remote multi-deck as default |
| **OpenSubsonic ecosystem** | Optional **wire** later if we want open clients | Mandatory Subsonic branding |
| **USB / Engine / rekordbox export** | Offline handoff still matters | Replacing shares with USB only |

**Architecture rule:** prior art informs UX and ACL vocabulary. **Implementation is Migx-native** (our server or our share protocol, our identity, our EXO).

---

## 4. Target architecture (no third-party server required)

```text
┌─────────────────────────────────────────────────────────────┐
│  LAYER C  Co-pilot ranks over my crate ∪ shared crates      │
└────────────────────────────▲────────────────────────────────┘
                             │ EXO session graph
┌────────────────────────────┴────────────────────────────────┐
│  LAYER B  Shared-library capability                         │
│  · Share registry (known shares for this user)              │
│  · Invite / ACL (music crate scope)                         │
│  · Index sync (worker) → library feature / EXO source ids   │
│  · Playability policy (local | lan | prep-only)             │
└────────────────────────────▲────────────────────────────────┘
                             │ ControlObject only for intents
┌────────────────────────────┴────────────────────────────────┐
│  LAYER A  Instrument                                        │
│  Load track only via existing SoundSource path when policy  │
│  says playable — no network on RT thread (P-02)             │
└─────────────────────────────────────────────────────────────┘

Host runtime (same box or small “crate host” on NAS/Mac):
  Share service  →  advertises share id + ACL + track index
                 →  optionally serves file bytes on LAN
Guest Migx:
  Share client   →  known shares list → browse → session pull
```

### Identity & EXO

| Concept | Representation |
|---|---|
| Share | Stable `share_id` (UUID) + display name + host label |
| Track in share | `source: shared` + `external_ids.share_track_id` (+ path if known) |
| Session | Hybrid `order[]` + edges; policy flags for non-playable rows |
| Playability | `local` · `lan` · `prep_only` (never silent fail at gig) |

Same lesson as Spotify hybrid: **identity/prep is free; multi-deck needs real audio reachability.**

### Where code would live (when built)

| Piece | Likely home |
|---|---|
| Sidebar “Shared libraries” | `LibraryFeature` / external feature pattern (`BaseExternalLibraryFeature`) |
| Share host service | New small component or optional daemon — **not** engine |
| Index / ACL | Worker + settings; optional FSL/sidecar export of share manifest |
| Session union | EXO session schema (`source` / policy already hybrid-ready) |

---

## 5. Playability policy (the product truth for DJs)

| Badge | Meaning | Decks |
|---|---|---|
| **Local** | File on this Mac / mounted volume | Full multi-deck |
| **LAN** | Host reachable on local network; latency OK | Allowed when soak says so |
| **Prep only** | Metadata/order only; audio not RT-reachable | Sequence / plan, not dual-deck |

UI must show badge **before** load. Co-pilot must not propose a dual-deck move into prep-only rows without saying so.

---

## 6. Capability vs non-goals

### In scope
- Host/guest shared **music crates**  
- Known-share list + invite/revoke  
- Browse, search, pull into EXO session  
- Play when local/LAN policy allows  
- Co-pilot over shared ∪ personal crates  

### Out of scope (this capability)
- Any **required** Plex/Jellyfin/Navidrome install  
- Video, Live TV, general media center  
- Default dual-deck over cellular/WAN  
- Network I/O on the audio callback  

### Optional later (adapters, not core)
- **Import adapter:** “I already have a Plex/Subsonic server — pull index into a Migx share once.”  
  That is **migration convenience**, not a runtime dependency.

---

## 7. Doable delivery waves

| Wave | Deliverable | Gate |
|---|---|---|
| **W0** | This capability note + UX verbs | Done |
| **W1** | Fixture-only: 2 DJs, 1 shared crate, EXO hybrid session demo (no network) | `exo-fixtures-check` green |
| **W2** | LAN share spike: host process + guest browse on same machine/network | Manual dogfood; worker-only I/O |
| **W3** | Playability badges + load policy | Cannot load prep-only as multi-deck without confirm |
| **W4** | Invite token + revoke | Two accounts/devices |
| **W5** | Co-pilot ranks across union | Offline why-next over hybrid session |

Each wave: no RT regression; pre-commit on touched files.

---

## 8. Relation to other Migx bets

| Bet | Relationship |
|---|---|
| **EXO** | Shared tracks are nodes in the session graph; edges still harmonic/energy/policy |
| **FSL / Song.migx** | Share manifest can point at sidecars or export a crate pack |
| **Spotify hybrid** | Orthogonal commercial identity; shared lib is **self-hosted peer share** |
| **Federation (agents)** | Agents coordinate product work; **not** the DJ share plane |
| **Apple Silicon RT** | Shared play only when underrun-safe (LAN/local); never sacrifice P-02 |

---

## 9. Bottom line

We are building **shared libraries as a first-class Migx capability for DJs** — host, invite, known shares, browse, session union, playability policy, co-pilot over the union.

**Plex is a reference for how “known servers + invites” feel**, not a dependency, not a roadmap milestone, and not part of the runtime architecture unless we later add an optional import adapter.
