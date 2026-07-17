---
id: runbook-gemini-cli-macos-fix
type: runbook
title: "Fix Gemini CLI / Antigravity login stuck on macOS"
status: active
owner: gudjon
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# Fix Gemini CLI / Antigravity login (macOS)

## Why “I login but it’s not logging in”

On this machine we reproduced **two separate failures** that feel like “login does nothing”:

### A) Gemini CLI + Google OAuth (Code Assist for individuals) is **rejected by Google**

```text
IneligibleTierError: This client is no longer supported for Gemini Code Assist
for individuals. Migrate to Antigravity: https://antigravity.google
```

After **2026-06-18**, free / Google AI Pro / Ultra **consumer** traffic is **not** served on Gemini CLI
via OAuth. The CLI can still show “Authenticated…” (local token exists) while every prompt fails with:

- `Content generator not initialized`
- `An unknown error occurred`
- 0 tokens / 0 tool calls

So OAuth “login” can **complete in the browser** and still **not work**. That is expected under the
deprecation — not a broken Mac setting.

### B) Antigravity OAuth often completes in browser but app/CLI never “takes” the session

Common on macOS (also reported widely on forums):

1. Click Sign in → browser opens  
2. You finish Google login  
3. Redirect `antigravity://oauth-success` fires  
4. UI stays on Sign in / CLI still unauthenticated  

**Why on this Mac:** the URL scheme `antigravity:` is registered to **Antigravity.app**
(`com.google.antigravity`), not necessarily the Homebrew CLI. Browser handoff goes to the **desktop
app**. If the app is stuck / wrong account / out of date, the CLI never receives a usable session.

Also common: account “not eligible”, login loop after updates, keychain write failures.

---

## What works (do this)

### Path 1 — **API key** for Gemini CLI (most reliable today)

Bypasses Code Assist OAuth entirely. Still supported for **API keys**.

```bash
# 1) Create a key (browser)
open https://aistudio.google.com/apikey

# 2) Save it (never commit this file)
printf '%s' 'PASTE_YOUR_KEY_HERE' > ~/.gemini/api_key
chmod 600 ~/.gemini/api_key

# 3) New terminal (loads ~/.zshrc which exports GEMINI_API_KEY from that file)
source ~/.zshrc
# confirm presence only:
[[ -n $GEMINI_API_KEY ]] && echo "GEMINI_API_KEY=set" || echo "unset"

# 4) Test
/opt/homebrew/bin/gemini -p "Reply with exactly: OK"
```

Settings on this machine are already set to:

```json
{ "security": { "auth": { "selectedType": "gemini-api-key" } } }
```

Stale OAuth was moved to `~/.gemini/oauth_creds.json.bak-disabled` so the CLI stops pretending
OAuth-personal works.

Helper: `~/bin/gemini-with-key.sh` (same key file).

### Path 2 — Antigravity CLI (`agy`) after a clean desktop login

```bash
# Prefer brew CLI explicitly
/opt/homebrew/bin/agy --version   # expect 1.1.3

# 1) Fully quit Antigravity.app (Cmd+Q)
# 2) Open the app and sign in there first (it owns antigravity://)
open -a Antigravity

# 3) If stuck on Sign in after browser returns:
#    - System Settings → Privacy & Security → allow Antigravity if blocked
#    - Default browser: allow pop-ups / disable strict tracker blocking for accounts.google.com
#    - Turn OFF VPN briefly
#    - Try personal @gmail.com if gudjon@oz.com Workspace is blocked for consumer Antigravity

# 4) Then try CLI
/opt/homebrew/bin/agy -p "Reply with exactly: OK"
```

If brew `agy` and app `agy` fight over PATH:

```bash
alias agy='/opt/homebrew/bin/agy'   # already in ~/.zshrc
hash -r
```

### Path 3 — Clean slate OAuth (only for Antigravity app, not for dead Gemini consumer OAuth)

```bash
# Quit Antigravity first
# Optional nuclear for app login loop (you will re-login):
# mv ~/Library/Application\ Support/Antigravity ~/Library/Application\ Support/Antigravity.bak-$(date +%Y%m%d)
open -a Antigravity
```

Do **not** expect Gemini CLI OAuth-personal to revive after re-login — Google disabled that tier on this client.

---

## What we already fixed on this machine

| Fix | Status |
|---|---|
| Removed npm `gemini` 0.33.2 shadowing brew 0.46.0 | done |
| Installed Homebrew `antigravity-cli` → `/opt/homebrew/bin/agy` | done |
| Confirmed OAuth-personal → `IneligibleTierError` | done |
| Disabled stale `oauth_creds.json`; settings → `gemini-api-key` | done |
| `~/.zshrc` loads `GEMINI_API_KEY` from `~/.gemini/api_key` | done |
| Opened AI Studio API key page | done |

**Solved (owner):** `agy` 1.1.3 logged in as `gudjon@oz.com` (subscription Sign-in path).  
Gemini CLI option 1 remains dead for Ultra/individuals — do not go back to `gemini` for OAuth.

**Optional check:** UI showed “Antigravity Starter Quota” — if you expect **Google One AI Ultra** limits, confirm the same account in Google One and Antigravity account settings.

---

## Quick decide

| Goal | Use |
|---|---|
| **Subscription + Sign in with Google** (Ultra/Pro) | **`agy` (Antigravity CLI)** ← correct path |
| Pay-per-token, no subscription | API key + legacy `gemini` |
| Gemini CLI **1. Sign in with Google** | **Not available** for individuals after 2026-06-18 |
| Migx multi-agent | Claude Code (implement) + Codex (verify) + Grok (signal). Antigravity **paused** (no tokens) |

---

## Verify

```bash
# API key path
[[ -n $GEMINI_API_KEY ]] && /opt/homebrew/bin/gemini -p "OK"

# Antigravity path  
/opt/homebrew/bin/agy --version
/opt/homebrew/bin/agy -p "OK"
```

If API key path still fails: key revoked, Generative Language API restricted, or billing/project issue in Google Cloud — create a **new** AI Studio key and retry.

If Antigravity browser returns but app never advances: protocol-handler / account eligibility issue — use Path 1 for terminal work; report to Google with account + macOS version if you need the app.
