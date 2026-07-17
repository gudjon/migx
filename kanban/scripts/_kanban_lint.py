#!/usr/bin/env python3
"""Shared helpers for the Migx kanban discipline linters (Phase 3).

Dependency-light: Python 3 stdlib only. Provides a tiny hand-rolled
frontmatter / YAML-lite parser so the linters never depend on PyYAML, plus a
few small utilities the linters share (repo-root discovery, colored pass/fail
reporting, dossier-dir detection).

This module is imported by the sibling `*.py` linters. Every linter bootstraps
`sys.path` to find this file by walking up to the repo root, so each script
stays runnable as `python3 <script>` from the repo root regardless of the
script's own directory depth.

The parser understands the shapes that actually occur in the kanban corpus:
scalars (bare / "quoted" / 'quoted'), booleans, null, inline `[a, b]` lists,
block `- item` lists, block `- key: val` lists-of-maps, and one-or-more levels
of nested mappings. Trailing `# comments` outside quotes are stripped. It is
NOT a general YAML implementation and deliberately rejects nothing it does not
understand — it just parses what it can.
"""
from __future__ import annotations

import pathlib
import re
import sys

try:
    import yaml as _yaml  # PyYAML — the correct parser when present (CI installs it)
except Exception:  # pragma: no cover - fallback to the hand-rolled parser below
    _yaml = None


# --------------------------------------------------------------------------
# repo-root discovery (so linters can locate each other / the tree)
# --------------------------------------------------------------------------
def find_repo_root(start: pathlib.Path | None = None) -> pathlib.Path:
    """Walk up from `start` (default: this file) until a dir contains `kanban/`."""
    here = (start or pathlib.Path(__file__)).resolve()
    for p in [here, *here.parents]:
        if (p / "kanban").is_dir() and (p / ".claude").is_dir():
            return p
    # Fallback: assume this file lives at <root>/kanban/scripts/_kanban_lint.py
    return pathlib.Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# YAML-lite frontmatter parser
# --------------------------------------------------------------------------
class _Entry:
    __slots__ = ("indent", "content")

    def __init__(self, indent: int, content: str):
        self.indent = indent
        self.content = content


def _strip_comment(line: str) -> str:
    """Remove a trailing `# comment` that is not inside a quoted string."""
    out = []
    quote = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        else:
            if ch in ('"', "'"):
                quote = ch
                out.append(ch)
            elif ch == "#":
                break
            else:
                out.append(ch)
    return "".join(out).rstrip()


def _scalar(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
        return v[1:-1]
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if v in ("", "null", "~"):
        return None
    return v


def _split_top_commas(s: str):
    parts, buf, quote, depth = [], [], None, 0
    for ch in s:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
            buf.append(ch)
        elif ch in "[":
            depth += 1
            buf.append(ch)
        elif ch in "]":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip() != ""]


def _inline_list(v: str):
    inner = v.strip()[1:-1].strip()
    if not inner:
        return []
    return [_scalar(x) for x in _split_top_commas(inner)]


def _value(v: str):
    v = v.strip()
    if v.startswith("["):
        return _inline_list(v)
    return _scalar(v)


def _looks_structured(content: str) -> bool:
    if content.startswith("- "):
        return True
    # a "key:" or "key: value" (but not a bare scalar containing a colon in a URL)
    m = re.match(r"^[^\s:][^:]*:(\s|$)", content)
    return bool(m)


def _open_quote_at_end(s: str):
    """Return the quote char if `s` ends still inside an unclosed quote, else None."""
    quote = None
    for ch in s:
        if quote:
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
    return quote


def _join_multiline(lines):
    """Fold physical lines that belong to one multi-line quoted scalar into one."""
    joined, buf = [], None
    for ln in lines:
        if buf is None:
            buf = ln
        else:
            buf = buf + " " + ln.strip()
        if _open_quote_at_end(buf) is None:
            joined.append(buf)
            buf = None
    if buf is not None:
        joined.append(buf)
    return joined


def _entries_from(lines):
    entries = []
    for raw in _join_multiline(lines):
        stripped = _strip_comment(raw)
        if stripped.strip() == "":
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        entries.append(_Entry(indent, stripped.strip()))
    return entries


def _parse_block(entries, i, indent):
    if i >= len(entries):
        return None, i
    if entries[i].content.startswith("-"):
        return _parse_list(entries, i, indent)
    return _parse_map(entries, i, indent)


def _parse_map(entries, i, indent):
    d = {}
    n = len(entries)
    while i < n:
        e = entries[i]
        if e.indent != indent or e.content.startswith("-"):
            break
        key, _, val = e.content.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            if i + 1 < n and entries[i + 1].indent > indent:
                child, i = _parse_block(entries, i + 1, entries[i + 1].indent)
                d[key] = child
            else:
                d[key] = None
                i += 1
        else:
            d[key] = _value(val)
            i += 1
    return d, i


def _parse_list(entries, i, indent):
    items = []
    n = len(entries)
    while i < n:
        e = entries[i]
        if e.indent != indent or not e.content.startswith("-"):
            break
        content = e.content[1:].strip()  # text after the dash
        child_indent = indent + 2
        virt = []
        if content:
            virt.append(_Entry(child_indent, content))
        i += 1
        while i < n and entries[i].indent > indent:
            virt.append(entries[i])
            i += 1
        if not virt:
            items.append(None)
        elif len(virt) == 1 and not _looks_structured(virt[0].content):
            items.append(_value(virt[0].content))
        else:
            val, _ = _parse_block(virt, 0, virt[0].indent)
            items.append(val)
    return items, i


def parse_yaml_lite(text: str) -> dict:
    """Parse a whole YAML document (e.g. prefix-registry.yaml).

    Uses PyYAML when available (correct); falls back to the hand-rolled parser.
    """
    if _yaml is not None:
        try:
            val = _yaml.safe_load(text)
            if isinstance(val, dict):
                return val
            return {"_root": val} if val is not None else {}
        except Exception:
            pass
    entries = _entries_from(text.splitlines())
    if not entries:
        return {}
    val, _ = _parse_block(entries, 0, entries[0].indent)
    return val if isinstance(val, dict) else {"_root": val}


def parse_frontmatter(text: str) -> dict:
    """Parse a leading `--- ... ---` frontmatter block into a dict. {} if none."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    block = []
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        block.append(ln)
    if _yaml is not None:
        try:
            val = _yaml.safe_load("\n".join(block))
            return val if isinstance(val, dict) else {}
        except Exception:
            pass
    entries = _entries_from(block)
    if not entries:
        return {}
    val, _ = _parse_block(entries, 0, entries[0].indent)
    return val if isinstance(val, dict) else {}


def read_frontmatter(path: pathlib.Path) -> dict:
    return parse_frontmatter(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# dossier helpers
# --------------------------------------------------------------------------
DOSSIER_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-.+-[A-Z]{3}--.+$")


def iter_dossier_dirs(repo: pathlib.Path):
    """Yield real dossier dirs under kanban/planning/ (excludes _template, 00-PORTFOLIO)."""
    planning = repo / "kanban" / "planning"
    if not planning.is_dir():
        return
    for child in sorted(planning.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("_") or child.name.startswith("00-"):
            continue
        if DOSSIER_DIR_RE.match(child.name):
            yield child


def dossier_prefix_from_dirname(name: str):
    m = re.match(r"^\d{4}-\d{2}-\d{2}-.+-([A-Z]{3})--.+$", name)
    return m.group(1) if m else None


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------
def die(msg: str, errors=None):
    print(f"FAIL: {msg}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    sys.exit(1)


def ok(msg: str):
    print(f"PASS: {msg}")
    sys.exit(0)
