#!/usr/bin/env python3
"""verify-owns-paths-exist — every DDD card `owns:`/`exclude:` path exists.

Also WARNS (does not fail) when a top-level src/ folder is claimed by 0 or >1 *authored* contexts —
a coverage/overlap smell to groom, not a hard error while the roster is still filling in.

Run:  python3 kanban/architecture/lint/verify-owns-paths-exist.py
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


def _paths(fm, key):
    v = fm.get(key) or []
    return [str(x).strip() for x in v] if isinstance(v, list) else [str(v).strip()]


def main():
    errors, warnings = [], []
    claims = {}  # top-level src folder -> [context ids]
    n = 0
    for card in sorted(CARDS.glob("*.md")):
        if card.name.startswith("_"):
            continue
        n += 1
        fm = read_frontmatter(card)
        cid = fm.get("id") or card.stem
        for key in ("owns", "exclude"):
            for p in _paths(fm, key):
                if not p:
                    continue
                if not (REPO / p).exists():
                    errors.append(f"{card.name}: {key} path does not exist: {p}")
        for p in _paths(fm, "owns"):
            parts = p.strip("/").split("/")
            if len(parts) >= 2 and parts[0] == "src":
                claims.setdefault(f"src/{parts[1]}", []).append(cid)

    # coverage / overlap (warn-only)
    for folder, owners in sorted(claims.items()):
        distinct = sorted(set(owners))
        if len(distinct) > 1:
            warnings.append(f"{folder} claimed by >1 context: {', '.join(distinct)}")

    if warnings:
        for w in warnings:
            print(f"WARN: {w}", file=sys.stderr)
    if errors:
        die(f"DDD owns/exclude paths missing ({len(errors)} problem(s))", errors)
    ok(f"DDD owns/exclude paths exist: {n} card(s) checked, {len(warnings)} warning(s)")


if __name__ == "__main__":
    main()
