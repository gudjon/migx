#!/usr/bin/env python3
"""verify-command-vocabulary — the CLI surface may only speak the domain's language.

`ADR-008` makes the command surface the product spine, serving the DJ UI and the
agentic peers equally. Two rules keep that from rotting, and this lint is the
closed loop (`P-01`) behind both:

1. **Every command id is `<noun>.<verb>`**, and the `<noun>` appears in some
   bounded context's ubiquitous-language table. Otherwise the CLI grows a second
   vocabulary beside the DDD one — two truths (MG-3), and `P-11` for agents.
2. **Every command declares one of the four kinds** — command / query / event /
   capability. A fifth kind is a decision, not a convenience.

The surface is read from the CLI itself (`system.capabilities`), not from a
hand-maintained list, so this cannot pass by describing commands that do not
exist — MG-3 "derive, don't restate".

Run:  python3 kanban/architecture/lint/verify-command-vocabulary.py
"""
import json
import pathlib
import re
import subprocess
import sys

_here = pathlib.Path(__file__).resolve()
for _p in _here.parents:
    if (_p / "kanban" / "scripts" / "_kanban_lint.py").exists():
        sys.path.insert(0, str(_p / "kanban" / "scripts"))
        REPO = _p
        break
from _kanban_lint import die, ok  # noqa: E402

CARDS = REPO / "kanban" / "architecture" / "ddd" / "bounded-contexts"
CLI = REPO / "tools" / "migx-cli" / "migx"

VALID_KINDS = {"command", "query", "event", "capability"}
COMMAND_ID = re.compile(r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")

# First column of a markdown table row, when it is `code`-quoted.
_TERM = re.compile(r"^\|\s*`([^`]+)`\s*\|")


def ubiquitous_terms() -> dict[str, list[str]]:
    """Every term declared in any context's ubiquitous-language table."""
    terms: dict[str, list[str]] = {}
    for card in sorted(CARDS.glob("*.md")):
        if card.name.startswith("_"):
            continue
        in_table = False
        for line in card.read_text(encoding="utf-8").splitlines():
            if line.startswith("## Ubiquitous language"):
                in_table = True
                continue
            if in_table and line.startswith("## "):
                in_table = False
                continue
            if not in_table:
                continue
            match = _TERM.match(line)
            if match:
                terms.setdefault(match.group(1).strip().lower(), []).append(
                    card.stem
                )
    return terms


def surface() -> list[dict]:
    """Read the live command manifest from the CLI."""
    proc = subprocess.run(
        [str(CLI), "system.capabilities", "--json"],
        capture_output=True, text=True, cwd=REPO,
    )
    if proc.returncode != 0:
        die("could not read the command surface",
            [f"{CLI} system.capabilities --json exited {proc.returncode}",
             proc.stderr.strip()[:400]])
    try:
        return json.loads(proc.stdout)["commands"]
    except (json.JSONDecodeError, KeyError) as exc:
        die("command manifest is not readable JSON", [str(exc)])
    return []


def main() -> int:
    if not CLI.exists():
        ok("no migx CLI present — nothing to check")
        return 0

    terms = ubiquitous_terms()
    commands = surface()
    errors, warnings = [], []

    for cap in commands:
        cid = cap.get("id", "")
        kind = cap.get("kind", "")

        if not COMMAND_ID.match(cid):
            errors.append(
                f"{cid!r}: not a valid command id — expected <noun>.<verb>, "
                "lowercase kebab"
            )
            continue

        if kind not in VALID_KINDS:
            errors.append(
                f"{cid}: kind {kind!r} is not one of "
                f"{', '.join(sorted(VALID_KINDS))} (ADR-008 §3)"
            )

        noun = cid.split(".", 1)[0]
        if noun not in terms:
            errors.append(
                f"{cid}: noun {noun!r} appears in no ubiquitous-language "
                "table. Add it to the owning context's card, or rename the "
                "command to a term the domain already uses (ADR-008 §4)."
            )

        if not cap.get("summary"):
            warnings.append(f"{cid}: no summary — agents read this to choose")
        if kind in {"command", "query"} and not (
            cap.get("emits") or cap.get("writes")
        ):
            warnings.append(
                f"{cid}: declares neither `emits` nor `writes`; an agent "
                "cannot tell what it produces"
            )

    if not commands:
        errors.append("the command surface is empty")

    for warn in warnings:
        print(f"WARN: {warn}", file=sys.stderr)
    if errors:
        die(f"command vocabulary ({len(errors)} problem(s))", errors)

    ok(
        f"command vocabulary: {len(commands)} command(s) checked against "
        f"{len(terms)} domain term(s), {len(warnings)} warning(s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
