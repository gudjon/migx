#!/usr/bin/env python3
"""lint-dossier-frontmatter — every planning dossier's AGENTS.md carries the
required dossier frontmatter, and its prefix is registered.

Checks, for each real dossier under kanban/planning/ (the `_template` and
`00-PORTFOLIO` dirs are not dossiers and are skipped):
  - AGENTS.md exists and has a frontmatter block;
  - the required keys are present: id, slug, type, prefix, title, phase,
    sealed, facilitator, created, lastUpdated;
  - type == "dossier";
  - prefix appears in kanban/planning/00-PORTFOLIO/prefix-registry.yaml.

Exit 0 on pass, non-zero with a clear message on failure.
Run:  python3 kanban/scripts/lint-dossier-frontmatter.py
"""
import pathlib
import sys

_here = pathlib.Path(__file__).resolve()
for _p in [_here, *_here.parents]:
    if (_p / "kanban" / "scripts" / "_kanban_lint.py").exists():
        sys.path.insert(0, str(_p / "kanban" / "scripts"))
        _REPO = _p
        break
from _kanban_lint import die, iter_dossier_dirs, ok, parse_yaml_lite, read_frontmatter

REQUIRED = [
    "id", "slug", "type", "prefix", "title", "phase",
    "sealed", "facilitator", "created", "lastUpdated",
]


def registered_prefixes(repo):
    reg = parse_yaml_lite(
        (repo / "kanban" / "planning" / "00-PORTFOLIO" / "prefix-registry.yaml").read_text()
    )
    return {d.get("prefix") for d in (reg.get("dossiers") or []) if d}


def main():
    repo = _REPO
    prefixes = registered_prefixes(repo)
    errors = []
    n = 0
    for dossier in iter_dossier_dirs(repo):
        n += 1
        agents = dossier / "AGENTS.md"
        rel = agents.relative_to(repo)
        if not agents.is_file():
            errors.append(f"{dossier.relative_to(repo)}: missing AGENTS.md")
            continue
        fm = read_frontmatter(agents)
        if not fm:
            errors.append(f"{rel}: no frontmatter block")
            continue
        missing = [k for k in REQUIRED if k not in fm or fm[k] in (None, "")]
        if missing:
            errors.append(f"{rel}: missing/empty keys: {', '.join(missing)}")
        if fm.get("type") != "dossier":
            errors.append(f"{rel}: type must be 'dossier', got {fm.get('type')!r}")
        pfx = fm.get("prefix")
        if pfx and pfx not in prefixes:
            errors.append(f"{rel}: prefix {pfx!r} not in prefix-registry.yaml")

    if errors:
        die(f"dossier frontmatter invalid ({len(errors)} problem(s))", errors)
    ok(f"dossier frontmatter valid across {n} dossier(s)")


if __name__ == "__main__":
    main()
