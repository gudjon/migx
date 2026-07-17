#!/usr/bin/env python3
"""verify-skill-grounding — every SKILL.md carries the Class-A grounding contract, and every pat-*
skill cites real pattern cards without restating them (P-05).

Checks each .claude/skills/*/SKILL.md:
  - non-empty `defers_to`, `audit_gate`, `verifiable_output_shape`;
  - for pat-* skills: `metadata.cites_patterns` lists IDs that each map to an existing
    kanban/patterns/<ID>-*.md card; the body is thin (<= ~30 non-blank lines after frontmatter) and
    links to a pattern card (cite-not-restate heuristic).

Run:  python3 .claude/architecture/lint/verify-skill-grounding.py
"""
import pathlib
import re
import sys

_here = pathlib.Path(__file__).resolve()
for _p in _here.parents:
    if (_p / "kanban" / "scripts" / "_kanban_lint.py").exists():
        sys.path.insert(0, str(_p / "kanban" / "scripts"))
        REPO = _p
        break
from _kanban_lint import die, ok, parse_frontmatter  # noqa: E402

SKILLS = REPO / ".claude" / "skills"
PATTERNS = REPO / "kanban" / "patterns"
BODY_MAX = 30


def _card_exists(pid):
    return any(PATTERNS.glob(f"{pid}-*.md"))


def _body_after_frontmatter(text):
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((k for k in range(1, len(lines)) if lines[k].strip() == "---"), 0)
        lines = lines[end + 1 :]
    return [ln for ln in lines if ln.strip()]


def main():
    errors, n = [], 0
    for skill in sorted(SKILLS.glob("*/SKILL.md")):
        n += 1
        rel = skill.relative_to(REPO)
        text = skill.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        name = fm.get("name") or skill.parent.name
        for key in ("defers_to", "audit_gate", "verifiable_output_shape"):
            if not fm.get(key):
                errors.append(f"{rel}: missing/empty grounding field `{key}`")
        if name.startswith("pat-"):
            meta = fm.get("metadata") or {}
            cites = meta.get("cites_patterns") or []
            if not cites:
                errors.append(f"{rel}: pat-* skill has no metadata.cites_patterns")
            for pid in cites:
                if not _card_exists(str(pid)):
                    errors.append(f"{rel}: cites_patterns {pid!r} has no pattern card")
            body = _body_after_frontmatter(text)
            if len(body) > BODY_MAX:
                errors.append(f"{rel}: pat-* body has {len(body)} lines (>{BODY_MAX}) — restating, not citing (P-05)")
            if not re.search(r"\]\([^)]*kanban/patterns/[^)]+\)|\.\./\.\./\.\./kanban/patterns/", text):
                errors.append(f"{rel}: pat-* body links to no pattern card (cite-not-restate)")
    if errors:
        die(f"skill grounding violations ({len(errors)} problem(s))", errors)
    ok(f"skill grounding clean: {n} skill(s) checked")


if __name__ == "__main__":
    main()
