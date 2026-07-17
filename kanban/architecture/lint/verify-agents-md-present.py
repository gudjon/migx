#!/usr/bin/env python3
"""verify-agents-md-present — every DDD card's `agents_md:` charter file exists.

A card points at a per-domain charter (src/<domain>/AGENTS.md); this fails if the pointer dangles.

Run:  python3 kanban/architecture/lint/verify-agents-md-present.py
"""
import pathlib
import sys

_here = pathlib.Path(__file__).resolve()
for _p in _here.parents:
    if (_p / "kanban" / "scripts" / "_kanban_lint.py").exists():
        sys.path.insert(0, str(_p / "kanban" / "scripts"))
        REPO = _p
        break
from _kanban_lint import die, ok, read_frontmatter  # noqa: E402

CARDS = REPO / "kanban" / "architecture" / "ddd" / "bounded-contexts"


def main():
    errors, n = [], 0
    for card in sorted(CARDS.glob("*.md")):
        if card.name.startswith("_"):
            continue
        n += 1
        fm = read_frontmatter(card)
        am = fm.get("agents_md")
        if not am:
            errors.append(f"{card.name}: no agents_md: pointer")
            continue
        if not (REPO / str(am)).exists():
            errors.append(f"{card.name}: agents_md points at a missing file: {am}")
    if errors:
        die(f"DDD agents_md pointers dangling ({len(errors)} problem(s))", errors)
    ok(f"DDD agents_md charters present: {n} card(s) checked")


if __name__ == "__main__":
    main()
