#!/usr/bin/env python3
"""Regression test for the set-level planner (plan_order / audit_order).

Pins the set-level invariants: the plan is a valid permutation, audits produce
n-1 transitions, and the planner clusters beatmixable tracks ahead of an
un-mixable outlier (the DnB-in-a-house-set case). Run: python3 tools/exo/test_set_planner.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from set_planner import audit_order, plan_order  # noqa: E402


def song(sid, camelot, bpm):
    return {"id": sid, "source": "local", "key": {"camelot": camelot}, "bpm": bpm}


def main() -> int:
    # Three mixable house tracks + one un-mixable DnB outlier.
    songs = {
        "a": song("a", "8A", 126),
        "b": song("b", "9A", 128),
        "c": song("c", "7A", 124),
        "dnb": song("dnb", "9A", 174),  # harmonically fine, tempo-incompatible
    }
    failed = 0

    plan = plan_order("a", songs, {})
    if sorted(plan) != sorted(songs):
        print(f"[FAIL] plan is not a valid permutation: {plan}")
        failed += 1
    else:
        print(f"[ok] plan is a valid permutation: {plan}")

    trans = audit_order(plan, songs, {})
    if len(trans) != len(songs) - 1:
        print(f"[FAIL] expected {len(songs)-1} transitions, got {len(trans)}")
        failed += 1
    else:
        print(f"[ok] {len(trans)} transitions for {len(songs)} tracks")

    # The un-mixable DnB must NOT be placed between two mixable house tracks:
    # it should sit at an end (index 0 or last) so the clash is isolated.
    idx = plan.index("dnb")
    if idx in (0, len(plan) - 1):
        print(f"[ok] un-mixable DnB isolated at an end (index {idx})")
    else:
        print(f"[FAIL] un-mixable DnB buried mid-set at index {idx}: {plan}")
        failed += 1

    # A smooth plan should beat the deliberately-bad order that buries the DnB.
    bad = ["a", "dnb", "b", "c"]
    plan_total = sum(t["score"] for t in audit_order(plan, songs, {}))
    bad_total = sum(t["score"] for t in audit_order(bad, songs, {}))
    if plan_total >= bad_total:
        print(f"[ok] plan coherence {plan_total:.0f} >= buried-DnB order {bad_total:.0f}")
    else:
        print(f"[FAIL] plan {plan_total:.0f} worse than buried order {bad_total:.0f}")
        failed += 1

    print("PASS" if not failed else f"FAILED ({failed})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
