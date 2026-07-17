#!/usr/bin/env python3
"""PreToolUse (Edit|Write|MultiEdit) — warn when editing a real-time audio path.

Signal-only, read-only, degrade-safe: swallows every error and always exits 0, because it runs on the
shared settings every concurrent session loads. A hook bug must degrade to "no warning," never a
blocked harness. It emits hookSpecificOutput.additionalContext reminding the agent of the RT-safety
house rule (P-02 / rt-audio-safety rule) when the edited file lives on an audio-thread path.

Self-test: `python3 warn-rt-audio-edit.py --self-test`
"""
import json
import sys

# Directories whose code can run on (or feed) the real-time audio callback thread.
RT_PREFIXES = ("src/engine/", "src/effects/", "src/vinylcontrol/", "src/soundio/")

MESSAGE = (
    "RT-AUDIO PATH: this file may run on the real-time audio thread. House physics (MG-6, P-02/AP-02): "
    "no allocation, no lock, no blocking, no GUI-QObject touch on any process()-reachable path; cross-thread "
    "data crosses lock-free (util/fifo.h / atomic double-buffer / ControlObject). A 'faster on average' "
    "change that violates this is a regression, not an optimization. Perf claims need a p99/underrun "
    "benchmark contract (P-03/P-18). See .claude/rules/rt-audio-safety.md and src/engine/AGENTS.md."
)


def file_path_from(payload):
    ti = payload.get("tool_input", {}) or {}
    # Edit/Write use file_path; MultiEdit too. Normalize to a repo-relative-ish string.
    return ti.get("file_path") or ti.get("path") or ""


def is_rt_path(path):
    if not path:
        return False
    p = path.replace("\\", "/")
    # Match regardless of absolute prefix by checking for the marker anywhere.
    return any(marker in p for marker in RT_PREFIXES)


def emit(context):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": context,
        }
    }))


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # no input / bad json → silent, exit 0
    try:
        if is_rt_path(file_path_from(payload)):
            emit(MESSAGE)
    except Exception:
        return


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        assert is_rt_path("/Users/x/migx/src/engine/enginebuffer.cpp")
        assert is_rt_path("src/effects/backends/foo.cpp")
        assert not is_rt_path("src/library/dao/trackdao.cpp")
        assert not is_rt_path("")
        print("ok")
        sys.exit(0)
    main()
    sys.exit(0)
