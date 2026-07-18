---
id: output-verification-formats-naming
type: knowledge
title: "Output verification — formats & naming at each stage"
status: active
owner: gudjon
created: "2026-07-18"
lastUpdated: "2026-07-18"
task: kanban/tasks/research-output-verification-formats-naming.md
related:
  - headless-sim-ground-truth-agentic-cli
  - closed-loops-and-tdd-feedback-gaps
  - world-model-experience-ontology
  - P-07
  - P-09
  - P-11
  - AP-10
---

# Output verification — formats & naming at each stage

**Question:** What does each stage emit, under what **name/format**, and how do **downstream consumers** verify they can handle it?

**Rule:** One writer per artifact family (`P-07`). Agents must not invent parallel names (`P-11`). Wrong shape = **RED** for TDD/CI.

---

## 1. Pipeline map (stages → consumers)

```text
[Analyzer / tags] → Track DB / FSL
[EXO tools]       → ontology + session JSON → copilot → QML fixture
[Engine tests]    → gtest / bench stdout → EVD markdown
[Sim (proposed)]  → out.wav + metrics.json → CI / agent
[Federation]      → messages/*.md → peers
[pre-commit/CI]   → logs / checks → humans
```

---

## 2. Stage inventory

### 2.1 EXO song ontology

| | |
|---|---|
| **Path pattern** | `…/fixtures/songs/<song-id>.ontology.json` or `Song.migx/ontology.json` (FSL later) |
| **Format** | JSON; `"schema": "migx.song-ontology/1"` |
| **Schema home** | `…/fixtures/schema/migx.song-ontology.v1.json` |
| **Writer** | Human / `spotify_uri_import.py` / future analyzer export |
| **Readers** | `check_fixtures.py`, `copilot_why_next.py`, agents |
| **Verify** | `just exo-fixtures-check` / `python3 tools/exo/check_fixtures.py` |
| **Naming** | `song-id` stable kebab; imported: `song-sp-<id>.ontology.json` |

**Gap:** Production FSL path not unified with fixture path yet — document dual homes until FSL hardens.

### 2.2 EXO session ontology

| | |
|---|---|
| **Path pattern** | `…/fixtures/sessions/session-<slug>.json` |
| **Format** | JSON; `"schema": "migx.session-ontology/1"` |
| **Required** | `id`, `tracks[]`, `order[]`; optional `edges`, `policy`, `kind` |
| **Writer** | Human / import tools |
| **Readers** | copilot, agents, dogfood |
| **Verify** | same fixture check + edge enum validation |
| **Edge enum** | `harmonically-compatible` \| `next-energy` \| `planned-transition` \| `sequence-only` |

**Gap:** P-08 noted misuse of `harmonically-compatible` for non-adjacent cool-downs — need stricter edge semantics or separate `narrative-transition`.

### 2.3 Co-pilot outputs

| Artifact | Path (SSoT) | Mirror / consumer |
|---|---|---|
| Why-next markdown | `…/results/COPILOT-WHY-NEXT.md` | Human |
| Why-next JSON | `…/results/COPILOT-WHY-NEXT.json` | **Must** copy → `res/qml/CoPilot/fixture_why_next.json` via `just exo-copilot-why` |
| Intent inbox | `…/fixtures/dogfood/intent-inbox.v1.json` | Future CO reconciler |
| Session mirror | `…/fixtures/dogfood/session-mirror.v1.json` | Dogfood |

**Verify:** JSON parse + required keys (`proposal`, scores); QML fixture **byte-equal or schema-equal** to results JSON after mirror recipe.

**Naming:** keep `COPILOT-WHY-NEXT.*` uppercase; version intent schema in filename `*.v1.json`.

### 2.4 EVD evidence (dossiers)

| | |
|---|---|
| **Path** | `kanban/planning/<dossier>/results/EVD-<ID>.md` or `EVD-<ID>-<slug>.md` |
| **Format** | Markdown + YAML frontmatter (`id`, `type: evidence`, `status`, …) |
| **Writer** | Wave owner (agent/human) |
| **Readers** | Seal, later waves, P-08 eval |
| **Naming** | Prefer `EVD-0001`, `EVD-DSP-01-…`, `EVD-PLT-0001-…` — **prefix by domain** |
| **Verify** | Frontmatter has `id`; body has runnable reproduce command; pin commit SHA |

**Gap:** No automated linter for EVD shape yet; add to kanban-discipline or `tools/exo`-style checker.

### 2.5 Federation messages

| | |
|---|---|
| **Path** | `kanban/federation/messages/{open,ack,closed}/<from>-<to>-<date>-<nnn>-<slug>.md` |
| **Format** | Markdown + frontmatter (`from`, `to`, `type`, `status`, `acceptance`, …) |
| **Template** | `MSG-TEMPLATE.md` |
| **Writer** | `migx-fed send` / ack / close |
| **Readers** | peers, harness |
| **Verify** | `migx-fed doctor` / message schema check |

**Do not** hand-edit status without moving directories (breaks poll).

### 2.6 Benchmark / gtest outputs

| | |
|---|---|
| **Runner** | `build/mixxx-test --benchmark --benchmark_filter=…` or gtest |
| **Capture** | stdout + optional Google Benchmark JSON (`--benchmark_out=`) |
| **Promote to** | EVD markdown tables (human-curated) |
| **Naming** | Bench names `BM_<Area><What>` (existing: `BM_WaveformScrubFrame`, `BM_EngineFilterBiquadPeaking`) |
| **Verify** | CI or agent greps `BM_` existence; EVD cites filter string |

### 2.7 Sound format test corpus

| | |
|---|---|
| **Path** | `src/test/soundFileFormats/` |
| **Naming** | descriptive + rate/bit (e.g. `1kHzR440HzLReference_32i96kStereo.wav.bz2`) |
| **Writer** | `generateFiles.sh` |
| **Readers** | Manual matrix / SoundSource tests |
| **Verify** | Load tests; not golden-mix |

### 2.8 Sim outputs (proposed — lock before implement)

From headless-sim note:

| Artifact | Proposed path | Format |
|---|---|---|
| Scenario | `res/sim/scenarios/<Sxx-slug>.json` | `schema: migx.sim-scenario/1` |
| Corpus WAV | `res/sim/corpus/<slug>-48k.wav` | PCM WAV 48k stereo float/int16 — pick one, document |
| Run out | `build/sim-out/<scenario-id>/master.wav` | gitignored |
| Metrics | `build/sim-out/<scenario-id>/metrics.json` | `schema: migx.sim-metrics/1` |
| Golden hash | `res/sim/goldens/<scenario-id>.sha256` | text hash + meta |

**Verify:** `just sim-verify` / gtest compares metrics + optional PCM hash.

### 2.9 QML / resources

| | |
|---|---|
| **Co-pilot fixture** | `res/qml/CoPilot/fixture_why_next.json` |
| **Rule** | Generated only via just recipe from results SSoT — do not hand-edit both |
| **Verify** | qmllint + optional json-schema |

### 2.10 Library / DB

| | |
|---|---|
| **Schema** | `res/schema.xml` versioned migrations (`P-27`) |
| **Writer** | DAO only |
| **Verify** | migration tests; never raw SQL from agents |

---

## 3. Cross-cutting naming rules

| Kind | Convention |
|---|---|
| Schema strings | `migx.<domain>/<major>` e.g. `migx.song-ontology/1` |
| Schema files | `migx.<domain>.v<major>.json` |
| Stable ids | kebab-case, globally unique within type (`song-01-deep-intro`) |
| Dates in paths | ISO `YYYY-MM-DD` |
| Evidence | `EVD-` + domain optional + number |
| Benches | `BM_` + PascalCase area |
| Agent must not | `*_v2`, `*New`, `final_final` next to canonical (`P-11`) |

### Versioning

- **Breaking** schema change → bump major, keep old fixtures until migrated.  
- **Additive** fields → same major if readers ignore unknown keys (`additionalProperties` policy per schema).  
- Supersede docs with redirect stubs (see old plex knowledge path).

---

## 4. Downstream compatibility matrix

| Producer → Consumer | Contract | Breakage mode |
|---|---|---|
| EXO song → copilot | schema + key/energy fields | silent bad ranking |
| COPILOT JSON → QML | mirror path + keys | blank co-pilot chrome |
| Intent inbox → future CO | `intent-inbox.v1` shape | no engine effect |
| EVD → next wave | pin numbers + command | false win / false regress |
| Fed message → peer | frontmatter + dir | undelivered mail |
| Sim metrics → CI | schema + thresholds | flaky or blind CI |
| Analyzer → FSL | track.toml + ontology split | dual SSoT drift |

---

## 5. Verification tooling (recommended)

| Tool | Role |
|---|---|
| `tools/exo/check_fixtures.py` | **Exists** — extend for stricter edges |
| `migx-fed doctor` | **Exists** — message schema |
| **Proposed** `tools/verify_outputs.py` or `just verify-outputs` | Run all validators; exit ≠0 on fail |
| **Proposed** JSON Schema check for COPILOT + intent + sim | One library (Python jsonschema) |
| pre-commit / CI | Call verify-outputs on changed globs |

**RED for agents:** `just verify-outputs` fails → cannot claim wave done.

---

## 6. Gaps (priority)

| Priority | Gap | Fix |
|---|---|---|
| P0 | Session edge semantics loose | Tighten enum + docs; fixture test for illegal pairs |
| P0 | QML fixture can drift from results | CI check equal or schema; only generate via just |
| P1 | No EVD frontmatter linter | Small checker in kanban-discipline |
| P1 | Sim paths not frozen yet | Freeze in this note before W1 sim code |
| P2 | Dual EXO homes (fixtures vs FSL) | ADR or FSL charter when production export lands |
| P2 | Benchmark JSON not archived | Optional `--benchmark_out` in EVD recipe |

---

## 7. Relation to headless sim

Sim **must not** invent paths ad hoc. Before `SimScenario` code:

1. Add `migx.sim-scenario/1` + `migx.sim-metrics/1` schema files under agreed tree.  
2. Register golden naming in this note (already proposed §2.8).  
3. Wire `verify-outputs` to reject scenarios missing schema/id.

---

## 8. Recommendation

1. **Adopt** the stage table as SSoT for artifact contracts.  
2. **Extend** `check_fixtures.py` + add `just verify-outputs` aggregating EXO + fed doctor + (later) sim.  
3. **Freeze sim naming** before implementation.  
4. **Do not** big-bang rename all EVD files — new EVDs follow domain-prefixed names only.  
5. Every new agent pipeline stage **adds a row here first** (output verification before code).

---

## 9. Bottom line

Downstream safety is a **closed loop**: producer writes a **versioned, named** artifact; a **validator** is the sensor; CI/peer is the independent evaluator. Formats already exist for EXO, federation, and EVD — the work is **unifying rules, tightening gaps, and requiring verification before “done.”** Sim and agentic CLI inherit those rules; they do not bypass them.
