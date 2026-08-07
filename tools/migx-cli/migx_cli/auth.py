"""Spotify OAuth 2.0 PKCE for a native CLI — no client secret, stdlib only.

PKCE (RFC 7636) is the correct flow for a distributed desktop/CLI app:
a shipped client *secret* is not a secret, so we never have one. The
client id is public by
design and comes from `MIGX_SPOTIFY_CLIENT_ID` (or `--client-id`).

Tokens live in the macOS Keychain via `/usr/bin/security`, never in a dotfile.

Register the app at https://developer.spotify.com/dashboard with redirect URI:
    http://127.0.0.1:8888/callback
"""

from __future__ import annotations

import base64
import hashlib
import http.server
import json
import os
import secrets
import subprocess
import threading
import urllib.parse
import urllib.request
import webbrowser
from typing import Any

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
REDIRECT_HOST = "127.0.0.1"
REDIRECT_PORT = 8888
REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"

KEYCHAIN_SERVICE = "migx-spotify"

# Read-only scopes. We never request playlist-modify-* or streaming: this tool
# reads your library, it does not write to your Spotify account or touch audio.
SCOPES = (
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
)


class AuthError(RuntimeError):
    pass


# ---------------------------------------------------------------- PKCE pair


def _pkce_pair() -> tuple[str, str]:
    """(verifier, challenge) — S256 per RFC 7636 §4.1-4.2."""
    verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(64)).decode().rstrip("=")
    )
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return verifier, challenge


# ------------------------------------------------------------ keychain I/O


def _keychain_write(account: str, value: str) -> None:
    subprocess.run(
        [
            "/usr/bin/security",
            "add-generic-password",
            "-U",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            account,
            "-w",
            value,
        ],
        check=True,
        capture_output=True,
    )


def _keychain_read(account: str) -> str | None:
    proc = subprocess.run(
        [
            "/usr/bin/security",
            "find-generic-password",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            account,
            "-w",
        ],
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def _keychain_delete(account: str) -> bool:
    proc = subprocess.run(
        [
            "/usr/bin/security",
            "delete-generic-password",
            "-s",
            KEYCHAIN_SERVICE,
            "-a",
            account,
        ],
        capture_output=True,
    )
    return proc.returncode == 0


# --------------------------------------------------------- loopback capture


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    result: dict[str, str] = {}

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        for key in ("code", "state", "error"):
            if key in params:
                _CallbackHandler.result[key] = params[key][0]
        body = (
            b"<html><body style='font:16px -apple-system;padding:3rem'>"
            b"<h2>Migx &mdash; Spotify linked</h2>"
            b"<p>You can close this tab and return to the terminal.</p>"
            b"</body></html>"
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: Any) -> None:
        pass  # keep the terminal clean


def _await_callback(expected_state: str, timeout_s: int) -> str:
    _CallbackHandler.result = {}
    server = http.server.HTTPServer(
        (REDIRECT_HOST, REDIRECT_PORT), _CallbackHandler
    )
    server.timeout = timeout_s
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    thread.join(timeout_s)
    server.server_close()

    res = _CallbackHandler.result
    if not res:
        raise AuthError(
            f"no callback received within {timeout_s}s — login aborted"
        )
    if "error" in res:
        raise AuthError(f"Spotify denied authorization: {res['error']}")
    if res.get("state") != expected_state:
        raise AuthError("state mismatch — possible CSRF, login aborted")
    if "code" not in res:
        raise AuthError("callback carried no authorization code")
    return res["code"]


# ------------------------------------------------------------ token exchange


def _post_token(payload: dict[str, str]) -> dict[str, Any]:
    data = urllib.parse.urlencode(payload).encode("ascii")
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise AuthError(
            f"token endpoint returned {exc.code}: {detail}"
        ) from exc


def client_id(explicit: str | None = None) -> str:
    cid = explicit or os.environ.get("MIGX_SPOTIFY_CLIENT_ID", "").strip()
    if not cid:
        raise AuthError(
            "no Spotify client id — set MIGX_SPOTIFY_CLIENT_ID or"
            " pass --client-id.\n"
            "Create an app at"
            " https://developer.spotify.com/dashboard and add the "
            f"redirect URI exactly: {REDIRECT_URI}"
        )
    return cid


def login(
    cid: str, timeout_s: int = 180, open_browser: bool = True
) -> dict[str, Any]:
    """Run the interactive PKCE flow; persist the refresh token.

    Returns the token info dict.
    """
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(24)

    params = {
        "client_id": cid,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": " ".join(SCOPES),
        "code_challenge_method": "S256",
        "code_challenge": challenge,
    }
    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print(f"Opening browser to authorize Migx (scopes: {', '.join(SCOPES)})")
    print(f"If it does not open, paste this URL:\n  {url}\n")
    if open_browser:
        webbrowser.open(url)

    code = _await_callback(state, timeout_s)
    tok = _post_token(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": cid,
            "code_verifier": verifier,
        }
    )
    if "refresh_token" not in tok:
        raise AuthError("Spotify returned no refresh token")

    _keychain_write("refresh_token", tok["refresh_token"])
    _keychain_write("client_id", cid)
    return tok


def access_token(cid: str | None = None) -> str:
    """Exchange the stored refresh token for a fresh access token."""
    refresh = _keychain_read("refresh_token")
    if not refresh:
        raise AuthError("not logged in — run `migx spotify.login` first")
    cid = cid or _keychain_read("client_id") or client_id()

    tok = _post_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": cid,
        }
    )
    # Spotify rotates refresh tokens; persist the new one when present.
    if tok.get("refresh_token"):
        _keychain_write("refresh_token", tok["refresh_token"])
    if "access_token" not in tok:
        raise AuthError(
            "refresh did not return an access token — try logging in again"
        )
    return tok["access_token"]


def logout() -> bool:
    removed = _keychain_delete("refresh_token")
    _keychain_delete("client_id")
    return removed


def status() -> dict[str, Any]:
    return {
        "logged_in": _keychain_read("refresh_token") is not None,
        "client_id_stored": _keychain_read("client_id") is not None,
        "scopes": list(SCOPES),
        "redirect_uri": REDIRECT_URI,
        "token_store": f"macOS Keychain (service={KEYCHAIN_SERVICE})",
    }
