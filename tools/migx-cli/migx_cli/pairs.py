"""What you actually played after what — mined from listening history.

The **personal** layer of a song package: not what the field does, not what the
room did tonight, but the transitions *you* keep reaching for. Evidence, never
assertion — which is why it lives apart from the `pairs_after` a DJ writes by
hand in `notes.md`. Precedence when they disagree is **floor > personal >
field**: a thing the room rejected outranks a habit, and a habit outranks a
chart.

## The one judgement that makes this honest: what counts as consecutive

Two plays being adjacent in a log does not make them a transition. You stopped
for an hour, you went to bed, you started a different night — treating those as
"B follows A" invents edges that never happened, and an invented edge is worse
than a missing one because nothing downstream can tell them apart.

So a pair is only recorded when the second play starts within `MAX_GAP_S` of
the first. A gap larger than that **breaks the chain** rather than joining it.

## Counting, not scoring

This emits counts and leaves ranking to the caller. A count is checkable
against the log; a score is an opinion, and burying an opinion inside a miner
means nobody downstream can tell which is which.
"""

from __future__ import annotations

from typing import Any, Iterable

# Beyond this, the next play is a new listening session rather than a mix.
# Ten minutes is longer than any single track and far shorter than a break.
MAX_GAP_S = 600

# An edge seen once is a coincidence; the caller decides where the bar sits,
# but this is the default a set planner should trust.
DEFAULT_MIN_COUNT = 2


def consecutive(plays: Iterable[dict[str, Any]], max_gap_s: int = MAX_GAP_S) -> list[dict[str, Any]]:
    """Ordered (from -> to) pairs from timestamped plays.

    `plays` need `key` (any stable identity — ISRC preferred) and `at` (epoch
    seconds). Sorted here rather than trusting the caller: an out-of-order log
    would otherwise silently produce backwards edges.
    """
    ordered = sorted(
        (p for p in plays if p.get("key") and p.get("at") is not None),
        key=lambda p: p["at"],
    )
    out: list[dict[str, Any]] = []
    for first, second in zip(ordered, ordered[1:]):
        gap = int(second["at"]) - int(first["at"])
        if gap > max_gap_s:
            continue          # a break, not a transition
        if first["key"] == second["key"]:
            continue          # a repeat is not a pair
        out.append({"from": first["key"], "to": second["key"], "gap_s": gap})
    return out


def tally(
    plays: Iterable[dict[str, Any]],
    max_gap_s: int = MAX_GAP_S,
    min_count: int = DEFAULT_MIN_COUNT,
) -> dict[str, list[dict[str, Any]]]:
    """`{from_key: [{"to":…, "count":…}, …]}`, strongest first.

    Edges below `min_count` are dropped: one occurrence is a coincidence, and
    a package full of one-off edges reads as knowledge while being noise.
    """
    counts: dict[str, dict[str, int]] = {}
    for edge in consecutive(plays, max_gap_s):
        counts.setdefault(edge["from"], {})
        counts[edge["from"]][edge["to"]] = counts[edge["from"]].get(edge["to"], 0) + 1

    out: dict[str, list[dict[str, Any]]] = {}
    for source, targets in counts.items():
        kept = [
            {"to": target, "count": n}
            for target, n in targets.items()
            if n >= min_count
        ]
        if not kept:
            continue
        kept.sort(key=lambda e: (-e["count"], e["to"]))
        out[source] = kept
    return out


def as_edges(tallied: dict[str, list[dict[str, Any]]], source: str) -> list[dict[str, Any]]:
    """Flatten to jsonl-shaped rows, each carrying WHERE it came from.

    Provenance is not decoration: a personal edge and a chart edge must never
    become indistinguishable once written, or precedence cannot be applied.
    """
    rows = []
    for from_key, targets in sorted(tallied.items()):
        for edge in targets:
            rows.append(
                {
                    "from": from_key,
                    "to": edge["to"],
                    "count": edge["count"],
                    "layer": "personal",
                    "source": source,
                }
            )
    return rows
