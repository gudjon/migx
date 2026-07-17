#!/usr/bin/env python3
"""verify-prefix-registry — the prefix registry is internally coherent and
covers every prefix in use.

Checks:
  - every registered dossier prefix is UPPERCASE, exactly 3 letters, unique;
  - every 3-letter prefix used in a kanban/planning/ dossier dir name is
    registered (register-before-use, MG-3);
  - every registered initiative id has the shape `initiative-<slug>` (no
    legacy `INIT-` anchor — the filename slug IS the id, per GLOSSARY).

Exit 0 on pass, non-zero with a clear message on failure.
Run:  python3 kanban/scripts/verify-prefix-registry.py
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
from _kanban_lint import (
    die,
    dossier_prefix_from_dirname,
    iter_dossier_dirs,
    ok,
    parse_yaml_lite,
)

THREE_UPPER = re.compile(r"^[A-Z]{3}$")


def main():
    repo = _REPO
    reg_path = repo / "kanban" / "planning" / "00-PORTFOLIO" / "prefix-registry.yaml"
    reg = parse_yaml_lite(reg_path.read_text())
    errors = []

    dossiers = reg.get("dossiers") or []
    registered = []
    for d in dossiers:
        pfx = (d or {}).get("prefix")
        if pfx is None:
            errors.append(f"registry: a dossier entry has no 'prefix' key: {d}")
            continue
        if not THREE_UPPER.match(str(pfx)):
            errors.append(f"registry: prefix {pfx!r} is not UPPERCASE 3-letter")
        registered.append(str(pfx))

    seen = set()
    for pfx in registered:
        if pfx in seen:
            errors.append(f"registry: prefix {pfx!r} registered more than once")
        seen.add(pfx)

    # every prefix used in planning dir names must be registered
    for dossier in iter_dossier_dirs(repo):
        used = dossier_prefix_from_dirname(dossier.name)
        if used and used not in seen:
            errors.append(
                f"planning/{dossier.name}: prefix {used!r} used but not registered"
            )

    # initiative ids: initiative-<slug>, no INIT- anchor
    for i in reg.get("initiatives") or []:
        iid = (i or {}).get("id")
        if iid is None:
            errors.append(f"registry: an initiative entry has no 'id' key: {i}")
            continue
        if str(iid).startswith("INIT-"):
            errors.append(f"registry: initiative id {iid!r} uses a banned INIT- anchor")
        elif not re.match(r"^initiative-[a-z0-9]+(-[a-z0-9]+)*$", str(iid)):
            errors.append(
                f"registry: initiative id {iid!r} must be 'initiative-<kebab-slug>'"
            )

    if errors:
        die(f"prefix registry incoherent ({len(errors)} problem(s))", errors)
    ok(
        f"prefix registry coherent: {len(registered)} dossier prefix(es), "
        f"{len(reg.get('initiatives') or [])} initiative(s)"
    )


if __name__ == "__main__":
    main()
