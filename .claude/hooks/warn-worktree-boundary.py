#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit) — warn on a cross-worktree-boundary edit.

Signal-only, read-only, degrade-safe: swallows every error and always exits 0. Warns when the session
is working inside a `.claude/worktrees/<name>/` worktree but the edit targets a path OUTSIDE that
worktree (e.g. the main checkout) — the cross-boundary edit that corrupts worktree isolation. See
.claude/rules/worktree-hygiene.md.

Self-test: `python3 warn-worktree-boundary.py --self-test`
"""
import json
import sys

MARKER = "/.claude/worktrees/"


def worktree_root(cwd):
    """If cwd is inside a .claude/worktrees/<name>/, return that worktree root, else None."""
    if not cwd or MARKER not in cwd:
        return None
    idx = cwd.find(MARKER)
    tail = cwd[idx + len(MARKER):]
    name = tail.split("/", 1)[0]
    if not name:
        return None
    return cwd[:idx] + MARKER + name


def is_cross_boundary(cwd, file_path):
    root = worktree_root(cwd)
    if root is None or not file_path:
        return False
    # An absolute edit path that does not live under the current worktree root = cross-boundary.
    if file_path.startswith("/"):
        return not file_path.startswith(root + "/")
    return False  # relative paths resolve inside the worktree — not a boundary crossing


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    try:
        cwd = payload.get("cwd", "") or ""
        ti = payload.get("tool_input", {}) or {}
        fp = ti.get("file_path") or ti.get("path") or ""
        if is_cross_boundary(cwd, fp):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        "WORKTREE BOUNDARY: cwd is inside a .claude/worktrees/ worktree but this edit "
                        f"targets a path outside it ({fp}). Edit within your worktree, or switch context "
                        "first. See .claude/rules/worktree-hygiene.md."
                    ),
                }
            }))
    except Exception:
        return


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        wt = "/home/u/migx/.claude/worktrees/agent-x"
        assert is_cross_boundary(wt + "/src", "/home/u/migx/src/engine/e.cpp")
        assert not is_cross_boundary(wt + "/src", wt + "/src/engine/e.cpp")
        assert not is_cross_boundary("/home/u/migx", "/home/u/migx/src/x.cpp")
        print("ok")
        sys.exit(0)
    main()
    sys.exit(0)
