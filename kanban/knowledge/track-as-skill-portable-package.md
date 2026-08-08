---
id: track-as-skill-portable-package
type: knowledge
title: "Track-as-skill — portable per-song knowledge packages (non-DJ inspirations)"
status: draft
owner: gudjon
authored_by: grok-signal
created: "2026-08-08"
lastUpdated: "2026-08-08"
defers_to:
  - kanban/knowledge/filesystem-driven-architecture.md
  - kanban/knowledge/world-model-experience-ontology.md
  - kanban/knowledge/session-coaching-multimodal-agent.md
  - kanban/knowledge/agent-filesystem-hooks-integration.md
related:
  - tools/migx-cli/migx_cli/sidecar.py
  - tools/migx-cli/migx_cli/feedback.py
  - kanban/architecture/decisions/ADR-008-cli-core-two-equal-clients.md
note: >
  Research: treat each recording like a Claude Code skill — progressive disclosure,
  portable folder (or sidecar package) of open-ended data points for agents and
  humans. Inspired by skill packages, not only DJ software.
---

# Track-as-skill — portable per-song knowledge packages

## The idea in one line

A song is not an `.mp3` with a few ID3 tags. It is a **portable expertise package** —
like a Claude Code / Codex **skill folder** — that travels with the audio and grows
for years: themes, emotions, “good after X”, bootleg policy, SFX associations,
scenario-specific cues, transition recipes.

Agents and humans both open the same package; progressive disclosure keeps context
cheap.

## Why this resonates with field signal (not only DJs)

| Domain metaphor | Portable unit | Progressive disclosure |
| --- | --- | --- |
| **Claude Code / Codex skills** | Folder + `SKILL.md` + `scripts/` + `references/` + `assets/` | Name+description always loaded; body only on match |
| **Agent plugins** (zip / `plugin.json`) | Installable bundle of skills + assets | Marketplace-shaped, versioned |
| **K8s / microservices sidecar** | App binary + sidecar that carries ops knowledge | Core stays small; augment without rewrite |
| **RAW photo + XMP** | Image binary + sidecar metadata that survives renames | Editors read sidecar; file stays portable |
| **Game asset pack** | Sprite + hitboxes + animation metadata + SFX refs | Engine loads what level needs |
| **Research paper folder** | PDF + notes + bib + related graphs | You don’t re-read the whole corpus for one cite |
| **Design project dump** | Per-project folder + agent-named exports | Searchable patterns across jobs |
| **Docker image layers** | Base (audio) + layers of config/knowledge | Copy once; layers stack |

Field consensus on skills (2025–2026): **skills are packages, not prompts**. Owner,
version, restore, on-demand load. The same critique applies to tracks: stuffing
everything into one giant library DB row or one mega-prompt is context bloat;
**routing + packages** scale.

Vercel’s filesystem thesis applies directly: the agent already knows how to `ls`,
`grep`, and `cat` a song package the way it navigates a repo.

## What Migx already has (do not reinvent)

Today’s hybrid is correct directionally:

- **Audio file** = the immutable recording (one inode in `Collection/`).
- **Sidecar** (`track.json` beside audio) = human/agent-facing SSoT for cues,
  feedback, analysis fragments (`filesystem-driven-architecture`).
- **DB** = rebuildable index for search/sort (not the authoring surface).
- **Feedback vocabulary** = structured judgments that change `set.plan`.
- **Session state** = night-local, not lifetime track truth.

The gap is **shape and progressive disclosure**: one flat sidecar will become a
kitchen sink. Skills solved that with **layers**. Tracks should too.

## Proposal: song package layouts (two compatible shapes)

### Shape A — “sidecar stays a file” (minimal, ship-friendly)

Keep one audio file; grow a **directory of knowledge next to it**:

```text
Collection/A/Artist/128 8A - Title.mp3          # the recording (never duplicated)
Collection/A/Artist/128 8A - Title.migx/        # the skill package
  MANIFEST.md           # name + description + triggers (skill frontmatter)
  identity.json         # isrc, path hash, duration, source, license flags
  analysis/             # machine: bpm, camelot, energy, structure, stems refs
  perform/              # cues by scenario: open.json, mix-out-peak.json, radio-edit.json
  taste/                # human/agent judgments: fit, placement, themes, emotions
  graph/                # edges: good_after[], good_before[], pairs/, avoid[]
  sfx/                  # associations: gap drops, risers, samples to arm
  transitions/          # recipes: echo-out into 8A, long blend notes
  notes/                # free prose, session quotes, “bootleg only”
  assets/               # cover, waveform preview, optional stems (links ok)
  history.jsonl         # append-only floor verdicts (optional mirror of feedback)
```

**Invariant:** one recording, one package. Crate links point at the **audio**; the
package is discovered by same basename / path convention. Never copy audio into the
package (Collection rule).

### Shape B — “folder is the song” (true container)

```text
Collection/A/Artist/128 8A - Title/
  audio.mp3             # or .wav / .aiff
  MANIFEST.md
  …same subdirs as above…
```

Closer to a skill folder / Ableton Project-ish unit. Harder for dumb tools that
expect a flat mp3. Prefer **Shape A** unless owner wants folder-first UX.

## MANIFEST.md as the skill router (the important part)

Skills work because **description is a routing signal**, not a summary. Same for
songs:

```markdown
---
name: amelie-lens-feel-it
title: "Feel It"
artists: ["Amelie Lens"]
isrc: …
bpm: 128
camelot: 8A
description: >
  Peak-room techno tool. Use when the floor is already warm and you need a
  straight 8A push. Avoid as opener. Bootleg-adjacent energy; not for pure
  melodic crowds. Pairs well after long melodic breakdowns.
triggers:
  - peak
  - techno
  - after-melodic
  - 8A-push
policy: floor-ok          # or: bootleg-special | practice-only | retire
---

# Feel It — package notes

Human prose the agent only loads when this track is in focus…
```

Agent workflow (progressive disclosure):

1. **Index pass:** only `name` + `description` + bpm/key (~50–100 tokens/track).  
2. **Candidate match:** `set.plan` / Arrange uses identity + analysis + taste flags.  
3. **In focus:** load `perform/`, `transitions/`, `graph/` for *this* song.  
4. **Never** load 500 full packages into a coach prompt.

That is exactly the SKILL.md lesson applied to a music library.

## What data points belong where (your examples)

| Your idea | Package home | Typed vs prose | Who writes |
| --- | --- | --- | --- |
| Themes / emotions | `taste/themes.json` or tags in sidecar | closed vocab + free note | human + agent from speech |
| Good *pre* song for another | `graph/good_before[]` or edge on *other* track’s `good_after` | **pair edges**, not only tags | human, Last.fm-ish, session log |
| Good *after* a type of song | `graph/after_types[]` e.g. `melodic-breakdown` | closed types | human + agent |
| Brand new / unknown | `identity.freshness` / `taste.confidence` | enum | ingest default |
| Bootleg / special crowd only | `MANIFEST.policy` + `taste.audience` | enum + note | human (high trust) |
| Good after *specific* song | `graph/pairs/{isrc-or-id}.json` | pair memory | floor feedback + transition rating |
| SFX associations | `sfx/associations.json` | path refs into SFX library | human + coach |
| Transition ideas | `transitions/*.md` + structured `technique` | recipe + enum | human + mixing plan harvest |
| Scenario cue points | `perform/open.json`, `perform/mix-out-peak.json`, … | cues with `scenario` key | human + agent (`track.cue`) |
| Floor “worked / weak / retire” | `taste/feedback.jsonl` (or existing sidecar feedback) | closed vocab | session coach |

**Critical split (already in feedback.py):**

- **Lifetime vs session** — “this night the crowd is melodic” is *not* a permanent
  track fact (`session.room` / night log).
- **Physics vs taste** — bpm/key/energy are analysis; “bootleg only” is policy.
- **Node vs edge** — “good after song B” is a **graph edge**, not a property you
  can fully store only on one node without the pair id.

## Non-DJ inspirations to steal intentionally

1. **Progressive disclosure (skills)** — index tiny; load deep only when in focus.  
2. **Package contract** — install path, owner, version, restore (skill packaging
   discourse): a track package should be copyable to another machine and still
   make sense.  
3. **Sidecar pattern** — audio is the “app container”; knowledge is the sidecar
   that augments without rewriting the waveform.  
4. **XMP / sidecar culture (photo)** — rename-safe association; tools that only
   know the binary still play audio.  
5. **Asset packs (games)** — binary + hitboxes + VFX refs; same as audio + cues +
   SFX associations.  
6. **Research corpus folders** — notes and graphs *beside* the artifact; agents
   grep the corpus.  
7. **Append-only history** — skills and agents prefer restore; floor feedback
   should append, not overwrite (already true for `feedback` entries).  
8. **Security of portable skills** — unsigned skill packs are dangerous; same for
   auto-imported track packages with scripts/. **No executable scripts inside a
   track package by default** — data only. Scripts live in Migx/skills, not in
   every song.

## What *not* to do

| Trap | Why |
| --- | --- |
| One giant JSON with 200 free-text fields | Unqueryable; agents invent structure |
| Embed all knowledge in ID3 | Tiny, tool-hostile, no graph |
| Require folder-as-song for every file day one | Breaks simple players / hardlinks |
| Put night room state on the track forever | Corrupts lifetime priors |
| Executable hooks inside song packages | Supply-chain risk (skill malware pattern) |
| Duplicate audio into package | Breaks Collection “one recording” law |
| Force LLM to invent pair edges without evidence | Hallucinated graph is worse than empty |

## How agents use it (closed loop)

```text
Trigger   → track is selected / playing (session.now)
Capture   → voice: "bootleg only, great after melodic openers"
Intelligence → agent maps to policy + graph/after_types + note
Adjustment → writes taste/ + graph/ in the package (CLI)
Re-check  → next set.plan / Arrange reads typed fields + bias
```

Commands stay the spine:

```bash
migx track.show "Feel It" --json          # identity + latest taste
migx track.feedback now --fit worked --placement peak
migx track.note now --tag bootleg --note "special room only"
# future:
migx track.graph now --good-after isrc:… 
migx track.package validate path.mp3
```

Filesystem remains greppable:

```bash
rg -l "bootleg" Collection/**/*.migx/MANIFEST.md
jq '.themes' …/taste/themes.json
```

## Migration path (respect current tree)

1. **Keep** flat sidecar writes for cues/feedback (shipped).  
2. **Add** optional `.migx/` package dir; migrate fields gradually; `track.show`
   merges package + sidecar.  
3. **Index** only MANIFEST frontmatter into rebuildable DB / ArcFlow for search.  
4. **Pair edges** start as transition feedback on incoming track; graduate to
   explicit `graph/pairs/` when second identity is known.  
5. **Never** block playback if package is missing — audio alone still plays.

## Fit with session coaching + hooks

- **Lifetime package** = skill for the song.  
- **Session `now.json` / history** = which skill is active tonight.  
- **Hooks `TrackPlaying`** = “this package just became focus; agent may load deep
  layers.”  
- **Coach skill** = maps speech into package writes, not free chat logs.

## Open product questions (owner)

1. Shape A (sidecar dir) vs Shape B (folder is song) for Collection UX?  
2. Closed vocabulary for themes/emotions (EXO) vs free tags first?  
3. How aggressive to auto-fill graph edges from Last.fm / play history vs only
   human floor truth?  
4. Share packages across machines (git? rsync Collection?) without leaking
   bootleg notes?  

## Bottom line

Yes: treat each song like a **skill package** — portable, progressive, agent-native —
not like a dumb file with sticky notes in a central DB. Migx is already halfway
there (sidecar SSoT). The inspiration from outside DJ software is the **skill
routing model**: tiny descriptions for the whole library, deep knowledge only when
a track is *in play* or *in plan*.
