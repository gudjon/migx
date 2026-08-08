#!/usr/bin/env bash
# Migx installer — per-user, no sudo, no system directories.
#
# Modelled on how Claude Code and Codex install: everything lands under the
# invoking user's home, so an install never needs root and never collides with
# another user on the same Mac. `gudjon` installing does not touch anyone else.
#
#   ./install.sh              install (or upgrade) for the current user
#   ./install.sh --uninstall  remove the launcher and state dir
#   ./install.sh --dry-run    print what would happen, change nothing
#
# Deliberately a SYMLINK to the checkout rather than a copy: a copy silently
# goes stale the moment the repo moves forward, and "which migx am I running"
# becomes a real question mid-set. One binary, one source.
set -euo pipefail

BIN_DIR="${MIGX_BIN_DIR:-$HOME/.local/bin}"
STATE_DIR="${MIGX_STATE_DIR:-$HOME/Library/Application Support/Migx}"
CONFIG="${MIGX_CONFIG:-$HOME/.config/migx/config.json}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$REPO/tools/migx-cli/migx"

DRY=0; UNINSTALL=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

say() { printf '  %s\n' "$*"; }
run() { if [ "$DRY" = 1 ]; then say "would: $*"; else "$@"; fi; }

if [ "$UNINSTALL" = 1 ]; then
  echo "Uninstalling Migx for $USER"
  run rm -f "$BIN_DIR/migx" "$BIN_DIR/migx-tui"
  say "left in place: $STATE_DIR and $CONFIG (your library index and settings)"
  say "remove them by hand if you really mean it — they are not regenerable"
  exit 0
fi

echo "Installing Migx for $USER"

# Refuse rather than install something broken.
[ -x "$LAUNCHER" ] || { echo "error: launcher not found or not executable: $LAUNCHER" >&2; exit 1; }
command -v python3 >/dev/null || { echo "error: python3 is required and was not found" >&2; exit 1; }

run mkdir -p "$BIN_DIR" "$STATE_DIR" "$(dirname "$CONFIG")"
run ln -sf "$LAUNCHER" "$BIN_DIR/migx"
[ -x "$REPO/tools/migx-cli/migx-tui" ] && run ln -sf "$REPO/tools/migx-cli/migx-tui" "$BIN_DIR/migx-tui"
say "launcher -> $BIN_DIR/migx"
say "state    -> $STATE_DIR"

if [ ! -f "$CONFIG" ]; then
  say "no config yet — run: migx config.init --library /path/to/Music"
else
  say "config   -> $CONFIG (kept; install never overwrites your settings)"
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) say "PATH     -> ok, \`migx\` is available now" ;;
  *) echo
     echo "  $BIN_DIR is not on your PATH. Add this to ~/.zshrc:"
     echo "      export PATH=\"$BIN_DIR:\$PATH\""
     ;;
esac

echo
echo "  try:  migx config.show   ·   migx set.plan   ·   migx-tui"
