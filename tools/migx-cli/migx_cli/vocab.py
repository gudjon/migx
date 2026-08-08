"""Vocabulary packs — a closed word list per domain, on the filesystem.

Frontmatter today accepts any string, so `peak`, `peaktime` and `peak-time` can
all coexist. Three spellings of one idea is three truths: a filter for one
misses the others, and neither the DJ nor an agent can tell whether a term is
absent or merely spelled differently. That is vocabulary drift, and it is the
opposite of the single-source-of-truth the rest of this system holds.

A pack is one Markdown file, same shape as everything else here:

    <library>/Vocabulary/techno.md

    ---
    mood: [hypnotic, driving, dark, euphoric]
    floor: [warmup, mid, peak, closer]
    ---

    Peak in techno means the room is already committed — not the loudest
    record, the one that assumes momentum.

Frontmatter is the closed list a tool checks; the body is what "peak" *means*
in this domain, which is exactly the thing a genre argument is actually about.
Disco's peak is not techno's peak, so packs are **per-domain and additive** —
loading techno and disco together allows both vocabularies rather than forcing
one.

## Warn, never refuse

Unlike `notes.RESERVED`, which raises because writing `bpm:` into prose would
create a second authority for a fact `track.json` owns, an unknown mood is a
*curation* problem, not a correctness one. A DJ who invents a word mid-set must
not be blocked — they should be told, and the pack updated when they choose.
Blocking here would train people to stop annotating, which costs more than the
drift it prevents.

Packs live on the library volume, so they travel with the music and a
disconnected drive takes its vocabulary with it — which is correct: the terms
describe those tracks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import notes

VOCAB_DIR = "Vocabulary"

# Fields a pack may constrain. Anything else in frontmatter is free text by
# design — packs narrow the axes you filter on, not everything you can say.
CLOSED_FIELDS = ("mood", "floor", "tested", "policy")


def vocab_dir(library_root: Path | str) -> Path:
    return Path(library_root) / VOCAB_DIR


def load(library_root: Path | str) -> dict[str, Any]:
    """Merge every pack on the volume. Additive union, never last-wins.

    Two packs disagreeing about `floor` is not a conflict to resolve — techno
    and disco genuinely have different vocabularies, and a DJ playing both
    needs both. Overwriting would silently delete one domain's language.
    """
    directory = vocab_dir(library_root)
    terms: dict[str, set[str]] = {}
    packs: list[str] = []
    if not directory.is_dir():
        return {"packs": [], "terms": {}, "loaded": False}

    for path in sorted(directory.glob("*.md")):
        parsed = notes.parse(path.read_text(encoding="utf-8"))
        packs.append(path.stem)
        for field, value in parsed["meta"].items():
            if field not in CLOSED_FIELDS:
                continue
            words = value if isinstance(value, (list, tuple)) else [value]
            terms.setdefault(field, set()).update(
                str(w).strip().lower() for w in words if str(w).strip()
            )
    return {
        "packs": packs,
        "terms": {k: sorted(v) for k, v in terms.items()},
        "loaded": bool(packs),
    }


def check(meta: dict[str, Any], vocabulary: dict[str, Any]) -> list[dict[str, Any]]:
    """Terms not in any loaded pack, with the closest known alternatives.

    Returns [] when no pack is loaded: with no vocabulary defined, nothing can
    be off-vocabulary, and inventing a complaint would be worse than silence.
    """
    known = vocabulary.get("terms") or {}
    if not known:
        return []
    out = []
    for field, value in (meta or {}).items():
        allowed = known.get(field)
        if not allowed:
            continue
        words = value if isinstance(value, (list, tuple)) else [value]
        for word in words:
            term = str(word).strip().lower()
            if not term or term in allowed:
                continue
            near = [a for a in allowed if term in a or a in term]
            if not near:
                near = [a for a in allowed if a[:3] == term[:3]]
            out.append(
                {
                    "field": field,
                    "term": term,
                    "known": allowed,
                    "did_you_mean": near[:3],
                }
            )
    return out
