"""Musical key notation — normalise whatever a tagger wrote into Camelot.

DJs mix by the Camelot wheel, but every tool writes the key differently:

    Beatport / iTunes   "Fm", "F#m", "Gbm"
    Traktor             "8A", "Fm"
    Mixed In Key        "8A" (already Camelot)
    rekordbox           "Fm" or "8A" depending on preference
    Open Key            "10m" / "10d"
    classical-ish       "F minor", "Bb Major"

This module converts all of them to Camelot (`8A`, `12B`) so `{camelot}` in a
filename means one thing. **This is not key *detection*** — that is
`AnalyzerKey` in `src/analyzer/` (arch-analyzer), and a second implementation
here would be the parallel-implementation antipattern (`P-11`). We only read
what a tagger already decided.
"""

from __future__ import annotations

import re

# Camelot wheel: minor keys are the A ring, major keys the B ring.
_MINOR = {
    "G#": "1A",
    "Ab": "1A",
    "D#": "2A",
    "Eb": "2A",
    "A#": "3A",
    "Bb": "3A",
    "F": "4A",
    "C": "5A",
    "G": "6A",
    "D": "7A",
    "A": "8A",
    "E": "9A",
    "B": "10A",
    "F#": "11A",
    "Gb": "11A",
    "C#": "12A",
    "Db": "12A",
}
_MAJOR = {
    "B": "1B",
    "F#": "2B",
    "Gb": "2B",
    "C#": "3B",
    "Db": "3B",
    "G#": "4B",
    "Ab": "4B",
    "D#": "5B",
    "Eb": "5B",
    "A#": "6B",
    "Bb": "6B",
    "F": "7B",
    "C": "8B",
    "G": "9B",
    "D": "10B",
    "A": "11B",
    "E": "12B",
}

# Enharmonic spellings taggers actually emit for the same pitch class.
_ALIASES = {
    "DB": "C#",
    "EB": "D#",
    "GB": "F#",
    "AB": "G#",
    "BB": "A#",
    "E#": "F",
    "B#": "C",
    "FB": "E",
    "CB": "B",
}

_CAMELOT_RE = re.compile(r"^([1-9]|1[0-2])\s*([AB])$", re.IGNORECASE)
_OPENKEY_RE = re.compile(r"^([1-9]|1[0-2])\s*([dm])$", re.IGNORECASE)
# Capture the mode loosely and interpret it below: matching it in the pattern
# makes case handling brittle ("Major" vs "maj" vs the bare "m"/"M").
_KEY_RE = re.compile(r"^([A-G])\s*([#b♯♭]?)\s*([A-Za-z.]*)\s*$")


def _norm_root(root: str, accidental: str) -> str:
    accidental = accidental.replace("♯", "#").replace("♭", "b")
    token = f"{root.upper()}{accidental}"
    return _ALIASES.get(token.upper(), token)


def to_camelot(value: str | None) -> str | None:
    """Return Camelot notation, or None when the input says nothing useful."""
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None

    # Already Camelot.
    match = _CAMELOT_RE.match(text)
    if match:
        return f"{int(match.group(1))}{match.group(2).upper()}"

    # Open Key: 1m..12m (minor) / 1d..12d (major). Open Key n == Camelot n+7.
    match = _OPENKEY_RE.match(text)
    if match:
        number = (int(match.group(1)) + 7 - 1) % 12 + 1
        ring = "A" if match.group(2).lower() == "m" else "B"
        return f"{number}{ring}"

    # Spelled-out or short musical key.
    match = _KEY_RE.match(text)
    if not match:
        return None
    root, accidental, mode = match.groups()
    pitch = _norm_root(root, accidental or "")

    mode = (mode or "").strip().rstrip(".")
    folded = mode.lower()
    if folded.startswith("min"):
        is_minor = True
    elif folded.startswith("maj"):
        is_minor = False
    elif mode == "m":
        # The one genuinely ambiguous token. Lowercase "m" means minor
        # everywhere in DJ tooling ("Am"); uppercase "M" means major.
        is_minor = True
    elif mode in ("", "M"):
        is_minor = False
    else:
        return None  # trailing junk — better no key than a wrong one

    table = _MINOR if is_minor else _MAJOR
    return table.get(pitch)


def parse_bpm(value: str | float | int | None) -> float | None:
    """A tag BPM, sanity-checked. Returns None rather than a nonsense tempo."""
    if value is None:
        return None
    try:
        bpm = float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None
    if not 20.0 <= bpm <= 300.0:
        return None
    return round(bpm, 2)
