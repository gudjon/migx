#!/usr/bin/env python3
"""Every key the TUI handles must appear in KEYMAP.md.

`tui.help_view()` parses `res/design/KEYMAP.md` at runtime so bindings have one
home. That enforces one direction only: help cannot invent a binding that does
not exist. The reverse was unguarded — `run()` could handle a key nobody sees,
and it did: `m`, `:` and `?` shipped handled-but-undocumented, so the TUI had
features discoverable only by reading source.

An incomplete help screen is the quiet version of the defect this repo keeps
finding: a surface reporting what it knows while not knowing enough. Nothing
fails, nothing looks wrong, and the feature simply does not exist for anyone who
did not write it.

Checks `ord("x")` call sites in tui.py against the TUI table in KEYMAP.md.
Deliberately one-directional: a documented key with no handler is a separate
(and less harmful) problem, and flagging it here would make this lint fail on
the GUI twins that legitimately live in the same table.
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
TUI = REPO / "tools" / "migx-cli" / "migx_cli" / "tui.py"
KEYMAP = REPO / "res" / "design" / "KEYMAP.md"

# Keys that are navigation primitives documented as ranges, not literals.
# `j`/`k` live in "↑ / ↓ or j / k"; `g`/`G` in "PgUp / PgDn, g / G".
COVERED_BY_RANGE = {"j", "k", "g", "G"}
# Control characters that cannot appear as a literal table cell. The source
# spells them escaped, so the regex yields the two-character forms.
NOT_LITERAL = {"\\n", "\\t", " ", "\n", "\t"}


def main() -> int:
    if not TUI.is_file() or not KEYMAP.is_file():
        print("SKIP: tui.py or KEYMAP.md missing — nothing checked", file=sys.stderr)
        return 0

    handled = set(re.findall(r'ord\("(.+?)"\)', TUI.read_text(encoding="utf-8")))
    handled = {k for k in handled if k not in NOT_LITERAL and k not in COVERED_BY_RANGE}

    documented: set[str] = set()
    in_tui = False
    for line in KEYMAP.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_tui = "TUI" in line
            continue
        if not in_tui or not line.startswith("|"):
            continue
        for cell in re.findall(r"`([^`]+)`", line):
            for part in re.split(r"[/,]", cell):
                documented.add(part.strip())

    missing = sorted(k for k in handled if k not in documented)
    if missing:
        print(f"FAIL: {len(missing)} TUI key(s) handled but not in KEYMAP.md")
        for key in missing:
            print(f"  - `{key}` is handled in tui.py and invisible in `?` help")
        print("  Add a row to the TUI table; help_view() reads it at runtime.")
        return 1
    print(f"PASS: all {len(handled)} handled TUI key(s) documented in KEYMAP.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
