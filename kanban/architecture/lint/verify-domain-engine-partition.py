#!/usr/bin/env python3
"""The engine must not reach into the library, and every card must declare a side.

Two checks, one wall (`ADR-010`, `ADR-011`):

1. Every bounded-context card carries `side: engine | domain | seam | adapter`.
   Without it an agent cannot tell which `src/` folders are the RT engine and
   which are inherited GUI or library code — the mistake that would drag Qt and
   SQLite onto the booth path.

2. `src/engine/**` must not include `library/`, `database/`, or ArcFlow.
   `track/` IS allowed: the snapshot/load crossing is legal and banning it would
   be wrong.

## Why this RATCHETS instead of hard-failing

A hard fail on day one against pre-existing violations gets the lint commented
out within a week, and then it guards nothing. So the baseline is pinned and
only an INCREASE fails. The count is printed every run, which makes it a
number someone can drive down rather than a boolean nobody looks at.

Lower the baseline when you fix violations. Never raise it to make a branch pass.
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
CARDS = REPO / "kanban" / "architecture" / "ddd" / "bounded-contexts"
ENGINE = REPO / "src" / "engine"

VALID_SIDES = {"engine", "domain", "seam", "adapter"}
# Banned includes. `track/` is deliberately absent — it is a legal crossing.
BANNED = ("library/", "database/", "arcflow")

# Pinned 2026-08-18. Lower as violations are fixed; never raise.
BASELINE_VIOLATIONS = 0


def main() -> int:
    missing_side, bad_side = [], []
    if CARDS.is_dir():
        for card in sorted(CARDS.glob("*.md")):
            if card.name.startswith("_"):
                continue
            text = card.read_text(encoding="utf-8")
            match = re.search(r"^side:\s*(\S+)", text, re.M)
            if not match:
                missing_side.append(card.stem)
            elif match.group(1) not in VALID_SIDES:
                bad_side.append(f"{card.stem}: {match.group(1)}")

    violations = []
    if ENGINE.is_dir():
        for src in sorted(ENGINE.rglob("*.cpp")) + sorted(ENGINE.rglob("*.h")):
            for line in src.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.lstrip().startswith("#include"):
                    continue
                low = line.lower()
                for banned in BANNED:
                    if banned in low:
                        rel = src.relative_to(REPO)
                        violations.append(f"{rel}: {line.strip()[:78]}")

    print(f"engine→library includes: {len(violations)} "
          f"(baseline {BASELINE_VIOLATIONS})")
    print(f"cards missing `side:`  : {len(missing_side)}")

    failed = False
    if len(violations) > BASELINE_VIOLATIONS:
        print(f"FAIL: {len(violations) - BASELINE_VIOLATIONS} NEW engine→library include(s)")
        for v in violations[:12]:
            print(f"  - {v}")
        failed = True
    if bad_side:
        print(f"FAIL: {len(bad_side)} card(s) with an unknown side")
        for b in bad_side:
            print(f"  - {b} (want one of {', '.join(sorted(VALID_SIDES))})")
        failed = True
    if missing_side:
        # Fatal since Wave 0 landed `side:` on all 17. A new card without it is
        # a card nobody has decided the side of — exactly the ambiguity ADR-011
        # exists to remove, because this field decides what Swift may link.
        print(f"FAIL: {len(missing_side)} card(s) missing `side:`")
        for m in missing_side:
            print(f"  - {m}")
        failed = True

    if failed:
        return 1
    print("PASS: partition wall holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
