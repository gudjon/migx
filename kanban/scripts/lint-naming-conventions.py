#!/usr/bin/env python3
"""lint-naming-conventions — typed-ID files use anchor filenames, never prose.

Checks (GLOSSARY.md ID rules):
  - pattern cards in kanban/patterns/ match `P-<n>-<kebab>.md` /
    `AP-<n>-<kebab>.md` (a missing number = a banned prose-name ID);
  - Problem Statements match `PS-<PFX>-<n>.md` where <PFX> is 3 uppercase
    letters;
  - task cards in kanban/tasks/ are kebab-case `<slug>.md`.

Exit 0 on pass, non-zero with a clear message on failure.
Run:  python3 kanban/scripts/lint-naming-conventions.py
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
from _kanban_lint import die, ok

KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
PATTERN_RE = re.compile(rf"^(?:P|AP)-\d+-{KEBAB}\.md$")
PS_RE = re.compile(r"^PS-[A-Z]{3}-\d+\.md$")
TASK_RE = re.compile(rf"^{KEBAB}\.md$")

# files in a typed dir that are docs, not typed-ID cards
DOC_ALLOW = {"AGENTS.md", "README.md", "PATTERN-CATALOGUE-PLAN.md"}


def main():
    repo = _REPO
    errors = []

    # 1) pattern / antipattern cards
    pat_dir = repo / "kanban" / "patterns"
    for f in sorted(pat_dir.glob("*.md")):
        if f.name in DOC_ALLOW:
            continue
        if f.name.startswith(("P-", "AP-")):
            if not PATTERN_RE.match(f.name):
                errors.append(
                    f"patterns/{f.name}: not `P-<n>-<kebab>.md` / `AP-<n>-<kebab>.md`"
                )
        else:
            errors.append(
                f"patterns/{f.name}: not a recognised card (no P-/AP- anchor, "
                "and not an allowed doc)"
            )

    # 2) Problem Statements anywhere under kanban/ (00-FOUNDATION dirs)
    for f in sorted((repo / "kanban").rglob("PS-*.md")):
        if not PS_RE.match(f.name):
            errors.append(
                f"{f.relative_to(repo)}: PS filename must be `PS-<PFX>-<n>.md` "
                "(PFX = 3 uppercase letters)"
            )

    # 3) task cards are kebab-case
    task_dir = repo / "kanban" / "tasks"
    if task_dir.is_dir():
        for f in sorted(task_dir.glob("*.md")):
            if f.name in DOC_ALLOW:
                continue
            if not TASK_RE.match(f.name):
                errors.append(f"tasks/{f.name}: task filename must be kebab-case `<slug>.md`")

    if errors:
        die(f"naming conventions violated ({len(errors)} problem(s))", errors)
    ok("naming conventions clean (patterns, problem statements, tasks)")


if __name__ == "__main__":
    main()
