"""Order a pile of tracks into a set that can actually be mixed.

`mixing.py` answers "do these two work, and which move?" for ONE pair. A set
is the next question up: given N tracks, what order keeps every transition
mixable? That is a sequencing problem, not a scoring one, and nothing in the
CLI answered it — so the ordering lived in throwaway scripts and died with the
shell that ran it.

Deliberately reuses `mixing.plan()` for every pair rather than re-scoring here.
A second opinion about whether two tracks work would drift from what
`track.show` and the Deck view tell the DJ about the same pair, which is the
failure `P-11` names.

**What it is not:** this plans an order. It does not play, queue, beatmatch or
touch an engine — there is no audio here. The output is a running order a human
(or the TUI) can act on.

## Why greedy, and what that costs

It walks the set greedily: from the current track, take the best-scoring next
track from what is left. Greedy is honest about its weakness — it spends the
easy transitions early and can strand awkward tracks at the end. That is
visible in the output rather than hidden, because every transition prints its
own pitch and reach.

The alternative (optimal ordering) is a Hamiltonian-path problem — exponential,
and wrong-headed for a DJ set anyway, since a set has an *arc*: you do not want
the globally smoothest order, you want one that opens quiet and builds.

## Scoring, and why the pitch fader is weighted so heavily

On top of the technique score, a candidate earns:

- `+30` harmonically compatible — the loudest single signal in a blend
- `+20` beatmatchable at all
- `+25` inside `±8%` — the default pitch range on most gear. A transition that
  needs `±16%` is one many DJs physically cannot perform, so "possible in
  theory" and "possible on the deck in front of you" are scored apart.
- `-15` when the match relies on double/half-time. It is a real technique, not
  a default, and choosing it silently produces sets that feel wrong for reasons
  the running order does not explain.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from . import feedback, layout, mixing

# Bonuses on top of the technique score. Tuned so "reachable on real gear"
# outranks "theoretically beatmatchable" — see the module docstring.
HARMONIC_BONUS = 30
BEATMATCH_BONUS = 20
IN_RANGE_BONUS = 25
TIME_TRICK_PENALTY = -15

# A DJ saying "this lands after a melodic breakdown" is a stronger signal than
# any tempo arithmetic — it is the one thing the numbers cannot know.
PAIRS_AFTER_BONUS = 70


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v).strip().lower() for v in value if str(v).strip()]
    return [str(value).strip().lower()]


def matches(track: dict[str, Any], filters: dict[str, Any]) -> bool:
    """Does this track's frontmatter satisfy every filter?

    AND across keys, OR within a key: `--mood late --floor peak` means both,
    while a track tagged [hypnotic, late] satisfies `--mood late`.

    A track with NO frontmatter fails any filter rather than passing by
    default. Silently including unannotated tracks would make a filtered set
    indistinguishable from an unfiltered one — the DJ would think the taste
    filter worked when it did nothing.
    """
    meta = track.get("meta") or {}
    for key, wanted in filters.items():
        have = _as_list(meta.get(key))
        if not have:
            return False
        if not set(_as_list(wanted)) & set(have):
            return False
    return True

# How many buckets of the energy curve count as the "opening" of a track.
OPENING_BUCKETS = 8


def opening_energy(track: dict[str, Any]) -> float:
    """Mean loudness of a track's first buckets — how hot it starts."""
    energy = track.get("energy") or []
    if not energy:
        return 0.0
    head = energy[:OPENING_BUCKETS]
    return sum(head) / len(head)


def transition_score(
    outgoing: dict[str, Any], incoming: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    """Score this pair, and return the plan that justifies the score.

    Floor judgments on the *incoming* track (weak / worked / transition rating)
    are folded here so Arrange, `set.plan`, and Deck never disagree about the
    same pair (`P-11`). Physics still dominate the magnitude.
    """
    plan = mixing.plan(outgoing, incoming)
    best = plan["techniques"][0]
    score = best["score"]

    if plan["harmonic"].get("compatible"):
        score += HARMONIC_BONUS

    # An explicit "plays well after this" outranks the arithmetic.
    after = _as_list((incoming.get("meta") or {}).get("pairs_after"))
    if after:
        out_meta = outgoing.get("meta") or {}
        out_names = set(_as_list(out_meta.get("mood"))) | set(
            _as_list(out_meta.get("floor"))
        )
        stem = (outgoing.get("name") or "").lower()
        if any(a in out_names or a in stem for a in after):
            score += PAIRS_AFTER_BONUS

    beatmatch = plan["beatmatch"]
    if beatmatch.get("possible"):
        score += BEATMATCH_BONUS
    if beatmatch.get("fits_range") == "±8%":
        score += IN_RANGE_BONUS
    if beatmatch.get("relation"):  # "double-time" / "half-time"
        score += TIME_TRICK_PENALTY

    score += feedback.candidate_bias(incoming)
    return score, plan


def drop_duplicate_recordings(
    tracks: Iterable[dict[str, Any]], library_root: Path
) -> list[dict[str, Any]]:
    """Keep one copy of each recording, using the library's own identity rule.

    Without this a set plays the same song twice under two credits — the
    Diplo/Soulwax case `layout.find_duplicates` exists to catch. Reuses that
    rule rather than comparing titles here, so the CLI has one answer to "are
    these the same recording".
    """
    duplicates = layout.find_duplicates(Path(library_root))
    superseded: set[str] = set()
    for paths in duplicates.values():
        # Deterministic winner so the same library plans the same set twice.
        superseded.update(sorted(paths)[1:])
    return [t for t in tracks if t.get("path") not in superseded]


def _pick_opener(mixable: list[dict[str, Any]]) -> dict[str, Any]:
    """Lead the set, letting the DJ's verdict outrank the energy heuristic.

    Opening energy is a guess about a record; `--verdict opener` is a DJ
    telling us. Ranked so a track flagged `peak` is pushed off the opening
    slot even when it happens to start quietly — which is exactly the case the
    energy rule gets wrong.
    """
    return max(
        mixable,
        key=lambda t: (
            feedback.placement_bias(t, 1) - opening_energy(t) * 10,
        ),
    )


def plan_set(
    tracks: list[dict[str, Any]],
    library_root: Path | None = None,
    opener: str | None = None,
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Order tracks into a running set, with the move into each one.

    `opener` is a path; without it the coldest-opening track leads, because a
    set that starts at peak energy has nowhere to go.
    """
    pool = list(tracks)
    filtered_out = 0
    if filters:
        before = len(pool)
        pool = [t for t in pool if matches(t, filters)]
        filtered_out = before - len(pool)
    if library_root is not None:
        pool = drop_duplicate_recordings(pool, library_root)

    # A retired track is out before anything is scored — the DJ said so, and
    # no amount of harmonic fit overrides "do not play this again".
    retired = [t for t in pool if feedback.is_retired(t)]
    pool = [t for t in pool if not feedback.is_retired(t)]

    mixable = [t for t in pool if t.get("bpm") and t.get("camelot")]
    unplannable = [t for t in pool if not (t.get("bpm") and t.get("camelot"))]

    if not mixable:
        return {
            "schema": "migx.set-plan/1",
            "tracks": [],
            "unplannable": [t.get("name") for t in unplannable],
            "note": "no track has both bpm and camelot — run `library.analyze`",
        }

    if opener is not None:
        lead = next(
            (t for t in mixable if t.get("path") == opener or t.get("name") == opener),
            None,
        )
        if lead is None:
            lead = _pick_opener(mixable)
    else:
        lead = _pick_opener(mixable)

    order = [lead]
    remaining = [t for t in mixable if t is not lead]
    rows: list[dict[str, Any]] = [
        {
            "position": 1,
            "name": lead.get("name"),
            "path": lead.get("path"),
            "bpm": lead.get("bpm"),
            "camelot": lead.get("camelot"),
            "duration_s": lead.get("duration_s"),
            "transition": None,
        }
    ]

    while remaining:
        scored = [(transition_score(order[-1], c), c) for c in remaining]
        (score, plan), chosen = max(scored, key=lambda pair: pair[0][0])
        beatmatch = plan["beatmatch"]
        rows.append(
            {
                "position": len(order) + 1,
                "name": chosen.get("name"),
                "path": chosen.get("path"),
                "bpm": chosen.get("bpm"),
                "camelot": chosen.get("camelot"),
                "duration_s": chosen.get("duration_s"),
                "transition": {
                    "score": score,
                    "technique": plan["techniques"][0]["name"],
                    "why": plan["techniques"][0]["why"],
                    "pitch_pct": beatmatch.get("pitch_pct"),
                    "fits_range": beatmatch.get("fits_range"),
                    "relation": beatmatch.get("relation"),
                    "harmonic": plan["harmonic"].get("note"),
                    "relation_key": plan["harmonic"].get("relation"),
                },
            }
        )
        order.append(chosen)
        remaining.remove(chosen)

    total_s = sum((t.get("duration_s") or 0) for t in order)
    reaches = [
        r["transition"]["fits_range"] for r in rows[1:] if r["transition"]
    ]
    return {
        "schema": "migx.set-plan/1",
        "tracks": rows,
        "duration_s": round(total_s, 1),
        "in_easy_range": sum(1 for r in reaches if r == "±8%"),
        "transitions": len(reaches),
        "unplannable": [t.get("name") for t in unplannable],
        # Reported, never silent: a track vanishing from a set with no
        # explanation is indistinguishable from a bug (P-34).
        "retired": [t.get("name") for t in retired],
        # Reported, never silent: a filter that quietly removed most of the
        # library must not look like a small library.
        "filtered_out": filtered_out,
    }
