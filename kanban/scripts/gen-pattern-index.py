#!/usr/bin/env python3
"""gen-pattern-index — regenerate the pattern index table in patterns/AGENTS.md.

The index table in `kanban/patterns/AGENTS.md` (columns: ID | Title | Domain)
is *derived* from the `P-*.md` / `AP-*.md` card frontmatter — never hand-edited
(AP-04). This script rewrites only the block between the
`<!-- pattern-index:start -->` / `<!-- pattern-index:end -->` markers, in
numeric order with P cards before AP cards.

Modes:
  (default)   rewrite the table in place from the card files.
  --check     exit non-zero if the on-disk table is stale (CI gate); write nothing.

Exit 0 on pass; non-zero (with a diff hint) on a stale --check or a bad card.
Run:  python3 kanban/scripts/gen-pattern-index.py [--check]
"""
import pathlib
import re
import sys

_here = pathlib.Path(__file__).resolve()
for _p in [_here, *_here.parents]:
    if (_p / "kanban" / "scripts" / "_kanban_lint.py").exists():
        sys.path.insert(0, str(_p / "kanban" / "scripts"))
        _REPO = _p
        break
from _kanban_lint import die, ok, read_frontmatter

START = "<!-- pattern-index:start -->"
END = "<!-- pattern-index:end -->"
CARD_RE = re.compile(r"^(P|AP)-(\d+)-")


def sort_key(fm):
    """Numeric order; P (rank 0) before AP (rank 1)."""
    kind = str(fm["id"]).split("-")[0]
    rank = 0 if kind == "P" else 1
    return (rank, int(fm["_num"]))


def build_table(repo, errors):
    pat_dir = repo / "kanban" / "patterns"
    rows = []
    for f in sorted(pat_dir.glob("*.md")):
        m = CARD_RE.match(f.name)
        if not m:
            continue
        fm = read_frontmatter(f)
        pid, title, domain = fm.get("id"), fm.get("title"), fm.get("domain")
        if not pid or not title or not domain:
            errors.append(f"patterns/{f.name}: frontmatter missing id/title/domain")
            continue
        fm["_num"] = m.group(2)
        rows.append(fm)
    rows.sort(key=sort_key)
    lines = ["| ID | Title | Domain |", "|---|---|---|"]
    for fm in rows:
        lines.append(f"| {fm['id']} | {fm['title']} | {fm['domain']} |")
    return "\n".join(lines)


def rewrite_between_markers(text, table):
    if START not in text or END not in text:
        return None
    pre, rest = text.split(START, 1)
    _, post = rest.split(END, 1)
    return f"{pre}{START}\n{table}\n{END}{post}"


def main():
    repo = _REPO
    check = "--check" in sys.argv[1:]
    agents = repo / "kanban" / "patterns" / "AGENTS.md"
    errors = []

    table = build_table(repo, errors)
    if errors:
        die(f"pattern cards malformed ({len(errors)} problem(s))", errors)

    text = agents.read_text(encoding="utf-8")
    new_text = rewrite_between_markers(text, table)
    if new_text is None:
        die(f"patterns/AGENTS.md missing {START} / {END} markers")

    n = table.count("\n") - 1  # rows minus the two header lines
    if check:
        if new_text != text:
            die(
                "pattern index is stale — run `python3 kanban/scripts/gen-pattern-index.py`",
                ["the table between the pattern-index markers does not match the card files"],
            )
        ok(f"pattern index up to date ({n} card(s))")
    else:
        if new_text != text:
            agents.write_text(new_text, encoding="utf-8")
            ok(f"pattern index regenerated ({n} card(s))")
        ok(f"pattern index already current ({n} card(s))")


if __name__ == "__main__":
    main()
