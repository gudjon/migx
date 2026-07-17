#!/usr/bin/env python3
"""gen-index — regenerate the bounded-context roster table in kanban/architecture/README.md.

The canonical 16-context roster (id + intended src paths + thread_domain + rt_safety) lives here.
`status` is DERIVED: a context whose card file exists under ddd/bounded-contexts/ is `authored`
(and its owns/thread_domain/rt_safety are read from the card frontmatter — the authoritative source),
otherwise `planned` (using the intended defaults below).

Modes:
  (default)  rewrite the table between the <!-- ddd-roster:start/end --> markers in README.md
  --check    exit non-zero if the on-disk table is stale

Run:  python3 kanban/architecture/ddd/gen-index.py [--check]
"""
import pathlib
import sys

_here = pathlib.Path(__file__).resolve()
for _p in _here.parents:
    if (_p / "kanban" / "scripts" / "_kanban_lint.py").exists():
        sys.path.insert(0, str(_p / "kanban" / "scripts"))
        REPO = _p
        break
from _kanban_lint import read_frontmatter  # noqa: E402

START = "<!-- ddd-roster:start -->"
END = "<!-- ddd-roster:end -->"

# Canonical roster: (id, intended src paths, thread_domain, rt_safety). Grouped RT-first.
ROSTER = [
    ("arch-engine-realtime", "src/engine/", "rt-audio", "hard"),
    ("arch-effects-chain", "src/engine/effects/, src/effects/", "rt-audio + gui", "hard"),
    ("arch-mixer-decks", "src/mixer/", "rt-audio + gui", "hard"),
    ("arch-vinylcontrol", "src/vinylcontrol/", "rt-audio", "hard"),
    ("arch-audio-io", "src/soundio/", "rt-audio origin", "hard"),
    ("arch-sources-decode", "src/sources/, src/encoder/", "worker", "none"),
    ("arch-control-messaging", "src/control/", "any", "soft"),
    ("arch-controllers-mapping", "src/controllers/", "worker + gui", "none"),
    ("arch-library-db", "src/library/, src/database/", "gui + worker", "none"),
    ("arch-track-model", "src/track/", "any (read)", "soft"),
    ("arch-analyzer", "src/analyzer/", "worker", "none"),
    ("arch-musicbrainz", "src/musicbrainz/, src/network/", "worker", "none"),
    ("arch-waveform-render", "src/waveform/", "gpu-render", "soft"),
    ("arch-rendergraph", "src/rendergraph/, src/shaders/", "gpu-render", "none"),
    ("arch-skin-widgets", "src/skin/, src/widget/", "gui", "none"),
    ("arch-qml-ui", "src/qml/, res/qml/", "gui", "none"),
]

CARDS = REPO / "kanban" / "architecture" / "ddd" / "bounded-contexts"
README = REPO / "kanban" / "architecture" / "README.md"


def _owns_str(fm):
    owns = fm.get("owns") or []
    if isinstance(owns, list):
        # keep it compact: join the paths, strip trailing comments already handled by yaml
        return ", ".join(str(x).strip() for x in owns)
    return str(owns)


def build_table():
    rows = ["| id | src paths | thread_domain | rt_safety | status |", "|---|---|---|---|---|"]
    for cid, src, thread, rt in ROSTER:
        card = CARDS / f"{cid}.md"
        if card.exists():
            fm = read_frontmatter(card)
            src_v = _owns_str(fm) or src
            thread_v = fm.get("thread_domain") or thread
            rt_v = fm.get("rt_safety") or rt
            status = "authored"
        else:
            src_v, thread_v, rt_v, status = src, thread, rt, "planned"
        rows.append(f"| {cid} | {src_v} | {thread_v} | {rt_v} | {status} |")
    return "\n".join(rows)


def splice(text, table):
    i, j = text.find(START), text.find(END)
    if i == -1 or j == -1 or j < i:
        raise SystemExit(f"FAIL: markers {START}/{END} not found in {README}")
    return text[: i + len(START)] + "\n" + table + "\n" + text[j:]


def main():
    check = "--check" in sys.argv[1:]
    text = README.read_text(encoding="utf-8")
    new = splice(text, build_table())
    if check:
        if new != text:
            print("FAIL: ddd roster in README.md is stale — run gen-index.py", file=sys.stderr)
            sys.exit(1)
        print(f"PASS: ddd roster up to date ({len(ROSTER)} context(s))")
        sys.exit(0)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print(f"wrote ddd roster ({len(ROSTER)} context(s)) to {README.relative_to(REPO)}")
    else:
        print("ddd roster already up to date")


if __name__ == "__main__":
    main()
