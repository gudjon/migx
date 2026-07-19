---
id: signal-2026-07-19-launch-failure-analysis-for-claude
type: signal-brief
from: grok-signal
date: "2026-07-19"
relevance: actionable
topics: [build, launch, dogfood, macos, keyboard, jack, claude-code]
mapped_to:
  - kanban/runbooks/build-setup-macos-m4.md
  - 2026-07-19-get-running-macos-build-claude
method: "Terminal capture of ./build/mixxx; mixxx.log; code read of critical QMessageBox paths"
confidence: high
---

# Launch failure analysis — help Claude fix dogfood path

**User report:** App launched → **error dialog** → exited.  
**Grok reproduction (2026-07-19):** With isolated settings + resource path, **GUI started and stayed up** (PortAudio opened MacBook Air Speakers, skins painted, library scanner ran). Binary still **stale** (built Jul 17, `git 022149dd46-modified`).

Log artifact (clean run):  
`/tmp/migx-settings-test/mixxx.log` (also copy instructions below)

---

## What the log actually says (not the dialog text)

| Signal | Severity | Notes |
|---|---|---|
| `dlopen(libjack.0.dylib)` not found | **Noise** | PortAudio probes JACK; no JACK installed. Then: `libjack not found, so do not try…` — **non-fatal**. Do not install JACK just to silence this. |
| `ConfigObject: Could not read … mixxx.cfg` | Expected first-run | Creates defaults. |
| Locale **`en_IS`** (Iceland) | Env | Looks for `res/keyboard/is_IS.kbd.cfg` — **missing** (no Icelandic map in tree). |
| Fallback `en_US.kbd.cfg` path bug | **Real bug** | After locale miss, code tries `res/en_US.kbd.cfg` instead of `res/keyboard/en_US.kbd.cfg` → “starting without shortcuts”. Non-fatal. |
| Failed qt translations for `en_IS` | Noise | |
| Missing font “Open Sans Semibold” alias | Perf warning | Skin still loads. |
| PortAudio **opened** speakers | Success (our run) | |
| HID “controller is not open” spam | Noise | Internal keyboard/trackpad HID scan. |

**Critical dialogs in code that exit (if user saw these, match wording):**

1. **“Cannot access settings folder”** — `coreservices.cpp` ~453 — bad/unwritable `--settings-path` (sandbox).  
2. **“Cannot open database”** — `coreservices.cpp` ~870 — SQLite/Qt SQL / path unwritable.  
3. **“Error in skin file” / skin cannot be loaded** — `mixxxmainwindow.cpp` ~1381.

User did not paste dialog title; Claude should re-run and capture **exact** string from dialog or log.

---

## Repro / capture recipe (Claude — do this first)

```bash
cd /Users/gudjon/code/migx
git pull --ff-only
# Prefer rebuild — binary is stale vs FSL work:
just build   # or cmake --build build -j$(sysctl -n hw.ncpu)

mkdir -p /tmp/migx-dogfood
./build/mixxx --developer \
  --settings-path /tmp/migx-dogfood \
  --resource-path "$(pwd)/res" \
  2> /tmp/migx-dogfood.stderr | tee /tmp/migx-dogfood.stdout

# After exit or dialog OK:
grep -iE 'critical|error|fatal|Cannot |Failed|assert' /tmp/migx-dogfood/mixxx.log /tmp/migx-dogfood.stderr | head -50
```

**Default (no flags) settings dir on this Mac:**  
`~/Library/Application Support/Mixxx/`  
(or container path under `~/Library/Containers/org.mixxx.mixxx/...` if sandboxed install)

If dialog only appears on **default** path, compare clean `/tmp` settings vs Application Support (corrupt DB / permissions).

---

## Mitigations ranked for Claude

### P0 — Operational (no code)

1. **Always pass `--resource-path $(pwd)/res`** when running from `build/` tree (dev).  
2. **Use fresh `--settings-path /tmp/migx-dogfood`** for first dogfood; avoids bad Application Support state.  
3. **Rebuild** so binary matches HEAD (`a03a250`+). Stale binary confuses debugging.  
4. **Ignore JACK dlopen** unless user needs JACK (optional `brew install jack` only then).  
5. Capture **dialog title + body** + attach `mixxx.log` in federation status mail.

### P0 — Code fix (small, high value)

**Keyboard fallback path bug** — `src/controllers/keyboard/keyboardeventfilter.cpp` ~458:

```cpp
// BUG: drops "keyboard/" subdirectory
keyboardFile = mappingFilePath(resourcePath, QStringLiteral("en_US"));
// FIX: keep keyboard/ prefix
keyboardFile = mappingFilePath(
    QDir(resourcePath).filePath(QStringLiteral("keyboard")),
    QStringLiteral("en_US"));
```

Also consider shipping or aliasing **`is_IS.kbd.cfg`** → copy of `en_US` for Icelandic locale machines (this box is `en_IS`).

### P1 — If dialog is “Cannot open database”

- Confirm Qt SQLite: buildenv has `sqldrivers/libqsqlite` (static present).  
- Ensure settings path is writable; delete corrupt `mixxxdb.sqlite` under settings path (after backup).  
- Do not point `--settings-path` at a read-only or non-existent parent without create.

### P1 — If dialog is skin error

- Verify `--resource-path` points at repo `res/` with `res/skins/LateNight` (or configured skin).  
- Reset skin key in cfg / use defaults.

### P2 — Noise cleanup (optional)

- Reduce HID open spam / JACK probe log level for AS CoreAudio-only default.  
- Document in runbook: JACK not required on Migx AS path (Core Audio / PortAudio).

---

## X field note

Little DJ-specific “Mixxx launch dialog” discourse on X; general macOS native-app practice still applies: **capture log path, isolate settings, fix resource paths for unpackaged builds**. JACK missing is a classic PortAudio multi-backend noise, not a product defect on laptop Core Audio.

---

## Acceptance for Claude follow-up

1. Rebuild at current HEAD; `file build/mixxx` → arm64.  
2. Repro with `/tmp` settings + `res` resource path; attach log if dialog returns.  
3. Land keyboard fallback path fix + optional `is_IS` alias.  
4. Status mail to grok-signal: dialog exact text (or “no dialog, stays up”) + SHA.

Grok will not edit `src/**` in this wave; claim keyboard path if implementing.
