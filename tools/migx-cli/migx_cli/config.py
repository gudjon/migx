"""Configuration — one JSON file, one precedence order, no hidden state.

    ~/.config/migx/config.json          (override with $MIGX_CONFIG)

Precedence, highest first:

    1. an explicit CLI flag
    2. an environment variable  (MIGX_SPOTIFY_CLIENT_ID, MIGX_LIBRARY_ROOT)
    3. this config file
    4. the built-in default

That order is the whole contract: a flag always wins, so a config file can
never silently change what an explicit command does. `config.show` prints the
resolved values *and* where each came from, because "why did it write there?"
should never need a debugger.

Secrets are deliberately absent. The Spotify client id is public by design
(PKCE uses no secret), and the refresh token lives in the macOS Keychain. This
file is safe to read, diff, and commit to a dotfiles repo.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

SCHEMA = "migx.config/1"

DEFAULT_PATH = Path.home() / ".config" / "migx" / "config.json"

# Every knob, with the value used when nothing else is set.
DEFAULTS: dict[str, Any] = {
    "schema": SCHEMA,
    "library": {
        "root": str(Path.home() / "Music" / "Migx"),
        "template": "dj",
        "default_ext": "mp3",
        # Extra places to look for tracks you already own, beyond Collection/.
        "extra_roots": [],
        # hardlink | symlink. Hardlinks look like real files to DJ software;
        # symlinks are 49 bytes and some tools read that instead.
        "crate_link_mode": "hardlink",
    },
    "quality": {
        # Tiers eligible for the library index. Add "mp3-vbr-high" to accept
        # high VBR; anything below the bar always needs an explicit override.
        "allow_tiers": ["lossless", "mp3-320-cbr"],
    },
    "spotify": {
        "client_id": "",
        # Official API pacing only — never lower this to "go faster" in a loop.
        "min_interval_s": 0.3,
        # Default True: skip track pages when snapshot_id is unchanged.
        "if_changed": True,
        "mirror_root": str(Path.home() / "Music" / "Migx" / "_mirrors"),
    },
}

ENV_OVERRIDES = {
    "spotify.client_id": "MIGX_SPOTIFY_CLIENT_ID",
    "library.root": "MIGX_LIBRARY_ROOT",
}


def path() -> Path:
    """The config file location, honouring $MIGX_CONFIG."""
    override = os.environ.get("MIGX_CONFIG", "").strip()
    return Path(override).expanduser() if override else DEFAULT_PATH


def _deep_merge(base: dict[str, Any], over: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in (over or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _dig(data: dict[str, Any], dotted: str) -> Any:
    node: Any = data
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _put(data: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    node = data
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def load(config_path: Path | None = None) -> dict[str, Any]:
    """Defaults <- file <- environment. Never raises on a missing file."""
    target = Path(config_path) if config_path else path()
    merged = copy.deepcopy(DEFAULTS)

    if target.is_file():
        try:
            merged = _deep_merge(
                merged, json.loads(target.read_text(encoding="utf-8"))
            )
        except json.JSONDecodeError as exc:
            raise ValueError(f"{target}: invalid JSON — {exc}") from exc

    for dotted, env_name in ENV_OVERRIDES.items():
        env_value = os.environ.get(env_name, "").strip()
        if env_value:
            _put(merged, dotted, env_value)

    return merged


def sources(config_path: Path | None = None) -> dict[str, str]:
    """Where each overridable value actually came from."""
    target = Path(config_path) if config_path else path()
    on_disk = {}
    if target.is_file():
        try:
            on_disk = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            on_disk = {}

    out: dict[str, str] = {}
    for dotted, env_name in ENV_OVERRIDES.items():
        if os.environ.get(env_name, "").strip():
            out[dotted] = f"env:{env_name}"
        elif _dig(on_disk, dotted) is not None:
            out[dotted] = f"file:{target}"
        else:
            out[dotted] = "default"
    return out


def get(config: dict[str, Any], dotted: str, fallback: Any = None) -> Any:
    value = _dig(config, dotted)
    return fallback if value is None else value


def resolve(explicit: Any, config: dict[str, Any], dotted: str) -> Any:
    """A CLI flag always beats config. This is the precedence rule, in code."""
    return explicit if explicit not in (None, [], "") else get(config, dotted)


def save(config: dict[str, Any], config_path: Path | None = None) -> Path:
    target = Path(config_path) if config_path else path()
    target.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
    target.write_text(body, encoding="utf-8")
    return target


def scaffold(
    library_root: Path | str | None = None, client_id: str = ""
) -> dict[str, Any]:
    """A complete config with every key present — nothing implicit."""
    config = copy.deepcopy(DEFAULTS)
    if library_root:
        root = str(Path(library_root).expanduser())
        config["library"]["root"] = root
        config["spotify"]["mirror_root"] = str(Path(root) / "_mirrors")
    if client_id:
        config["spotify"]["client_id"] = client_id
    return config
