#!/usr/bin/env python3
"""Generate or check res/qml/Theme/Theme.qml against res/design/DESIGN.md tokens.

Wave-1 DUI spike: DESIGN.md is SSoT for a subset of Theme color/typography properties.
Image paths and complex computed colors remain hand-maintained in Theme.qml until a later wave.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DESIGN = REPO / "res" / "design" / "DESIGN.md"
THEME = REPO / "res" / "qml" / "Theme" / "Theme.qml"

# DESIGN token path → Theme.qml property name
COLOR_MAP = {
    "background": "backgroundColor",
    "text": "textColor",
    "white": "white",
    "accent": "accent",
    "accentColor": "accentColor",
    "blue": "blue",
    "green": "green",
    "red": "red",
    "yellow": "yellow",
    "warning": "warningColor",
    "darkGray": "darkGray",
    "darkGray2": "darkGray2",
    "darkGray3": "darkGray3",
    "darkGray4": "darkGray4",
    "midGray": "midGray",
    "midGray2": "midGray2",
    "midGray3": "midGray3",
    "lightGray": "lightGray",
    "lightGray2": "lightGray2",
    "lightGray3": "lightGray3",
    "embeddedBackground": "embeddedBackgroundColor",
    "sunkenBackground": "sunkenBackgroundColor",
    "knobBackground": "knobBackgroundColor",
    "libraryPanelSplitterBackground": "libraryPanelSplitterBackground",
    "libraryPanelSplitterHandle": "libraryPanelSplitterHandle",
    "libraryPanelSplitterHandleActive": "libraryPanelSplitterHandleActive",
    "deckInfoBarBackground": "deckInfoBarBackgroundColor",
    "deckEmptyCoverArt": "deckEmptyCoverArt",
}

TYPO_MAP = {
    "fontFamily": "fontFamily",
    "buttonFontPixelSize": "buttonFontPixelSize",
    "textFontPixelSize": "textFontPixelSize",
}


def parse_design_md(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit(f"{path}: missing YAML front matter")
    end = text.find("\n---", 3)
    if end < 0:
        raise SystemExit(f"{path}: unclosed front matter")
    block = text[3:end]
    # minimal YAML subset: section keys and "  key: value"
    data: dict = {"colors": {}, "typography": {}}
    section = None
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if re.match(r"^[a-zA-Z_][\w]*:\s*$", line):
            section = line.split(":", 1)[0].strip()
            if section not in data and section not in ("name", "version"):
                data[section] = {}
            continue
        m = re.match(r'^  ([a-zA-Z_][\w]*)\s*:\s*"([^"]*)"\s*$', line)
        if not m:
            m = re.match(r"^  ([a-zA-Z_][\w]*)\s*:\s*'([^']*)'\s*$", line)
        if not m:
            m = re.match(r"^  ([a-zA-Z_][\w]*)\s*:\s*(\S+)\s*$", line)
        if m and section in ("colors", "typography"):
            data[section][m.group(1)] = m.group(2).strip()
            continue
        m2 = re.match(r'^([a-zA-Z_][\w]*)\s*:\s*"([^"]*)"\s*$', line)
        if not m2:
            m2 = re.match(r"^([a-zA-Z_][\w]*)\s*:\s*'([^']*)'\s*$", line)
        if not m2:
            m2 = re.match(r"^([a-zA-Z_][\w]*)\s*:\s*(\S+)\s*$", line)
        if m2 and m2.group(1) not in ("colors", "typography") and not line.startswith(" "):
            data[m2.group(1)] = m2.group(2).strip()
            section = None
    return data


def theme_property_values(theme_text: str) -> dict[str, str]:
    """Extract `property color|int|string name: value` simple assignments."""
    out: dict[str, str] = {}
    for m in re.finditer(
        r"property\s+(?:color|int|string)\s+(\w+)\s*:\s*([^\n]+)",
        theme_text,
    ):
        name, val = m.group(1), m.group(2).strip().rstrip(";")
        # only quote/hex/number literals for check
        if val.startswith('"') or val.startswith("'") or val.startswith("#") or re.match(r"^\d+$", val):
            out[name] = val.strip("\"'")
    return out


def check(design: dict, theme_text: str) -> list[str]:
    """Compare DESIGN tokens to Theme *literal* assignments only.

    Theme may alias (e.g. textColor: white); those are not literal and are skipped.
    """
    props = theme_property_values(theme_text)
    errors: list[str] = []
    for dkey, tkey in COLOR_MAP.items():
        want = design.get("colors", {}).get(dkey)
        if not want:
            errors.append(f"DESIGN missing colors.{dkey}")
            continue
        got = props.get(tkey)
        if got is None:
            # aliased or non-literal in Theme — OK for wave 1
            continue
        if got.lstrip("#").lower() != want.lstrip("#").lower():
            errors.append(f"{tkey}: Theme={got!r} DESIGN={want!r}")
    for dkey, tkey in TYPO_MAP.items():
        want = design.get("typography", {}).get(dkey)
        if not want:
            continue
        got = props.get(tkey)
        if got is None:
            continue
        if str(got) != str(want):
            errors.append(f"{tkey}: Theme={got!r} DESIGN={want!r}")
    if not design.get("colors"):
        errors.append("DESIGN colors section empty/unparsed")
    return errors


def apply_to_theme(design: dict, theme_text: str) -> str:
    """Replace simple literal property values that map from DESIGN."""
    text = theme_text
    for dkey, tkey in COLOR_MAP.items():
        want = design.get("colors", {}).get(dkey)
        if not want:
            continue
        lit = want if want.startswith("#") or want.startswith("'") else want
        if not (lit.startswith("#") or lit.startswith('"') or lit.startswith("'")):
            lit = f'"{lit}"' if tkey in ("fontFamily",) else lit
        if tkey.endswith("Color") or tkey in COLOR_MAP.values():
            if not lit.startswith("#") and not lit.startswith('"'):
                # hex colors
                if re.match(r"^[0-9a-fA-F]{6,8}$", lit):
                    lit = f"#{lit}"
            if lit.startswith("#"):
                # Theme uses double-quoted or single-quoted or bare # in some places
                pattern = rf"(property color {tkey}\s*:\s*)(\"[^\"]*\"|'[^']*'|#[0-9A-Fa-f]+)"
                text2, n = re.subn(pattern, rf'\g<1>"{lit}"' if False else rf"\g<1>{lit}", text, count=1)
                # normalize to double quotes for hex
                text2, n = re.subn(
                    rf"(property color {tkey}\s*:\s*)(\"[^\"]*\"|'[^']*'|#[0-9A-Fa-f]+)",
                    rf'\1"{lit}"',
                    text,
                    count=1,
                )
                if n:
                    text = text2
    for dkey, tkey in TYPO_MAP.items():
        want = design.get("typography", {}).get(dkey)
        if want is None:
            continue
        if tkey == "fontFamily":
            text, n = re.subn(
                rf'(property string {tkey}\s*:\s*)("[^"]*"|\'[^\']*\')',
                rf'\1"{want}"',
                text,
                count=1,
            )
        else:
            text, n = re.subn(
                rf"(property int {tkey}\s*:\s*)\d+",
                rf"\g<1>{want}",
                text,
                count=1,
            )
    # banner comment once
    banner = (
        "// Generated-from-DESIGN tokens: run "
        "`python3 tools/design/gen_theme_from_design.py` "
        f"(source {DESIGN.relative_to(REPO)}). "
        "Do not hand-edit token hex values covered by DESIGN.md.\n"
    )
    if "Generated-from-DESIGN" not in text:
        if text.startswith("pragma Singleton"):
            lines = text.splitlines(True)
            # insert after pragma + imports block start
            insert_at = 0
            for i, line in enumerate(lines[:10]):
                if line.startswith("pragma") or line.startswith("import"):
                    insert_at = i + 1
            lines.insert(insert_at, banner)
            text = "".join(lines)
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 1 if Theme drifts from DESIGN.md")
    ap.add_argument("--write", action="store_true", help="apply DESIGN tokens into Theme.qml")
    args = ap.parse_args()
    if not args.check and not args.write:
        args.write = True  # default: generate/apply

    if not DESIGN.is_file():
        print(f"missing {DESIGN}", file=sys.stderr)
        return 2
    if not THEME.is_file():
        print(f"missing {THEME}", file=sys.stderr)
        return 2

    design = parse_design_md(DESIGN)
    theme_text = THEME.read_text(encoding="utf-8")

    if args.check:
        errs = check(design, theme_text)
        if errs:
            print("DESIGN.md ↔ Theme.qml drift:")
            for e in errs:
                print(f"  - {e}")
            return 1
        print("OK: Theme.qml matches DESIGN.md tokens")
        return 0

    new_text = apply_to_theme(design, theme_text)
    THEME.write_text(new_text, encoding="utf-8")
    print(f"wrote {THEME.relative_to(REPO)}")
    # re-check
    errs = check(design, new_text)
    if errs:
        print("warning: residual drift after write:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: tokens applied and check clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
