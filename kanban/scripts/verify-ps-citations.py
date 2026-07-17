#!/usr/bin/env python3
"""verify-ps-citations — Problem Statement citations resolve.

For every PS-*.md under kanban/:
  - any `path:line` citation (in `verified_against_code` or the body) points at
    a file that exists in the repo (best-effort: the path must exist; the line
    number is not range-checked). Angle-bracket `<placeholders>` are ignored so
    the _template PS passes.
  - every id in `resolves:` / `risks:` refers to a pattern card that exists in
    kanban/patterns/ (P-<n> / AP-<n>).

Exit 0 on pass, non-zero with a clear message on failure.
Run:  python3 kanban/scripts/verify-ps-citations.py
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
from _kanban_lint import die, ok, parse_frontmatter

SRC_EXT = "cpp|cc|cxx|c|h|hpp|hh|py|js|ts|qml|proto|cmake|txt|md|json|yaml|yml|sh|mm"
# path:line — path has a source-ish extension; not preceded by '<' (placeholder)
CITE_RE = re.compile(rf"(?<![<\w])([A-Za-z0-9_./\-]+\.(?:{SRC_EXT})):(\d+)")


def known_pattern_ids(repo):
    ids = set()
    for f in (repo / "kanban" / "patterns").glob("*.md"):
        m = re.match(r"^((?:P|AP)-\d+)-", f.name)
        if m:
            ids.add(m.group(1))
    return ids


def main():
    repo = _REPO
    pattern_ids = known_pattern_ids(repo)
    errors = []
    n_ps = 0
    n_cites = 0

    for ps in sorted((repo / "kanban").rglob("PS-*.md")):
        n_ps += 1
        rel = ps.relative_to(repo)
        text = ps.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)

        # resolves / risks edges must reference existing pattern cards
        for field in ("resolves", "risks"):
            for pid in fm.get(field) or []:
                if pid and pid not in pattern_ids:
                    errors.append(f"{rel}: {field}: {pid!r} has no pattern card")

        # path:line citations must exist on disk
        for m in CITE_RE.finditer(text):
            path = m.group(1)
            # skip obvious non-repo paths (URLs, bare words) and the id-like PS refs
            if path.startswith(("http", "//")):
                continue
            n_cites += 1
            if not (repo / path).exists():
                errors.append(f"{rel}: cited path does not exist: {path}:{m.group(2)}")

    if errors:
        die(f"PS citations broken ({len(errors)} problem(s))", errors)
    ok(f"PS citations resolve: {n_ps} PS file(s), {n_cites} path:line citation(s) checked")


if __name__ == "__main__":
    main()
