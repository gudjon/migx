#!/usr/bin/env python3
"""verify-sealed-dossier-has-closure — a sealed dossier has a real, authored
loop-closure retrospective (never green-over-boilerplate, AP-01).

For every dossier whose AGENTS.md declares `sealed: true`:
  - 91-LOOP-CLOSURE/00-LOOP-CLOSURE.md must exist;
  - its closure frontmatter must also declare `sealed: true`;
  - its `## Retrospective` section must be AUTHORED, not the scaffold:
    boilerplate is detected when the retro still carries the template's
    `<angle-bracket>` placeholders, is byte-identical to the _template retro,
    or contains too little authored prose.

Exit 0 on pass, non-zero with a clear message on failure. With no sealed
dossiers this passes trivially.
Run:  python3 kanban/scripts/verify-sealed-dossier-has-closure.py
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
from _kanban_lint import die, iter_dossier_dirs, ok, parse_frontmatter, read_frontmatter

PLACEHOLDER_RE = re.compile(r"<[^>\n]{3,}>")
MIN_AUTHORED_CHARS = 200  # authored prose in the retro, minus scaffold headings


def retro_section(text: str) -> str:
    """Return the text of the `## Retrospective` section, or ''."""
    m = re.search(r"^##[^\n]*Retrospective[^\n]*$", text, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s", text[start:], re.MULTILINE)
    return text[start : start + nxt.start()] if nxt else text[start:]


def template_retro(repo) -> str:
    tmpl = repo / "kanban" / "planning" / "_template" / "91-LOOP-CLOSURE" / "00-LOOP-CLOSURE.md"
    return retro_section(tmpl.read_text(encoding="utf-8")) if tmpl.is_file() else ""


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def authored_len(section: str) -> int:
    """Chars of prose after dropping the 5 scaffolded lens headings and markup."""
    body = re.sub(r"^\s*\d+\.\s*\*\*[^*]+\*\*", "", section, flags=re.MULTILINE)
    body = re.sub(r"[#*`|>_-]", "", body)
    return len(norm(body))


def main():
    repo = _REPO
    tmpl_retro = norm(template_retro(repo))
    errors = []
    n_sealed = 0

    for dossier in iter_dossier_dirs(repo):
        agents = dossier / "AGENTS.md"
        if not agents.is_file():
            continue
        if read_frontmatter(agents).get("sealed") is not True:
            continue
        n_sealed += 1
        rel = dossier.relative_to(repo)
        closure = dossier / "91-LOOP-CLOSURE" / "00-LOOP-CLOSURE.md"
        if not closure.is_file():
            errors.append(f"{rel}: sealed:true but no 91-LOOP-CLOSURE/00-LOOP-CLOSURE.md")
            continue
        ctext = closure.read_text(encoding="utf-8")
        if parse_frontmatter(ctext).get("sealed") is not True:
            errors.append(f"{rel}: closure exists but its frontmatter is not sealed:true")
        section = retro_section(ctext)
        if not section.strip():
            errors.append(f"{rel}: closure has no `## Retrospective` section")
            continue
        if PLACEHOLDER_RE.search(section):
            errors.append(f"{rel}: Retrospective still contains <template placeholders>")
        elif tmpl_retro and norm(section) == tmpl_retro:
            errors.append(f"{rel}: Retrospective is byte-identical to the _template scaffold")
        elif authored_len(section) < MIN_AUTHORED_CHARS:
            errors.append(
                f"{rel}: Retrospective has too little authored prose "
                f"({authored_len(section)} < {MIN_AUTHORED_CHARS} chars) — looks like boilerplate"
            )

    if errors:
        die(f"sealed dossiers not honestly closed ({len(errors)} problem(s))", errors)
    ok(f"sealed dossiers honestly closed: {n_sealed} sealed dossier(s) checked")


if __name__ == "__main__":
    main()
