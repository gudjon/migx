#!/usr/bin/env python3
"""Regression test for the co-pilot's tempo/beatmatch scoring (tempo_compat).

Beatmatch compatibility is the #1 real mixing constraint the harmonic + energy
scores alone miss (DC-PDCL-5.1 real friction). This pins the behaviour so a
future change cannot silently drop tempo awareness or let a harmonically-perfect
but un-beatmixable candidate outrank a mixable one.

Run: python3 tools/exo/test_copilot_tempo.py   (exit 0 = pass)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from copilot_why_next import tempo_compat  # noqa: E402


def main() -> int:
    checks = [
        # (cur, cand, predicate, description)
        (128, 128, lambda s: s >= 20.0, "identical tempo is beatmixable"),
        (128, 130, lambda s: s >= 20.0, "±1.6% is beatmixable"),
        (128, 64, lambda s: s >= 20.0, "half-time is beatmixable"),
        (87, 174, lambda s: s >= 20.0, "double-time is beatmixable"),
        (128, 140, lambda s: 3.0 <= s <= 15.0, "~9% is a pitch stretch"),
        (128, 174, lambda s: s < 0, "house→DnB clash is penalized"),
        (0, 128, lambda s: s == 0.0, "unknown bpm is not scored"),
    ]
    failed = 0
    for cur, cand, pred, desc in checks:
        score, reason = tempo_compat(cur, cand)
        ok = pred(score)
        print(f"[{'ok' if ok else 'FAIL'}] {cur}->{cand} score={score:+.1f}  {desc}")
        if not ok:
            failed += 1
    # The load-bearing property: a tempo clash must outrank-penalize a match.
    if tempo_compat(128, 128)[0] <= tempo_compat(128, 174)[0]:
        print("[FAIL] a beatmixable pair must score above a tempo clash")
        failed += 1
    print("PASS" if not failed else f"FAILED ({failed})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
