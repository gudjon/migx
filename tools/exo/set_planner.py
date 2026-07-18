#!/usr/bin/env python3
"""Set-level co-pilot: reason about a whole set, not just the next track.

"An agent that understands a set" (the AI-DJing thesis) needs more than the
next-track suggestion in copilot_why_next.py. This composes that per-transition
scoring into two set-level capabilities:

  - audit:  score every consecutive transition in a planned order, surface the
            harmonic/tempo/energy arc, and flag the weakest links (the mixes that
            would clunk) so a DJ can fix a set before playing it.
  - plan:   propose a smooth order from a crate (greedy: from a start track,
            repeatedly take the best-scoring unplayed next track), reasoning from
            musical properties (Camelot + tempo + energy), not a declared order.

Offline Layer B: no RT engine, no ControlObjects, no network. Proposals only.

Usage:
  python3 tools/exo/set_planner.py --session SESSION.json --audit
  python3 tools/exo/set_planner.py --session SESSION.json --plan [--start SONG_ID]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from copilot_why_next import (  # noqa: E402
    bpm_of,
    edge_index,
    energy_tail,
    load_json,
    load_songs,
    score_candidate,
)


def _camelot(song):
    return (song.get("key") or {}).get("camelot")


def audit_order(order, songs, edges):
    """Score each consecutive transition in the given order."""
    transitions = []
    for a, b in zip(order, order[1:]):
        if a not in songs or b not in songs:
            continue
        sc, reasons, rel = score_candidate(a, b, songs, edges, order)
        transitions.append({"from": a, "to": b, "score": round(sc, 1),
                            "relation": rel, "reasons": reasons})
    return transitions


def plan_order(start, songs, edges):
    """Greedy: from start, repeatedly take the highest-scoring unplayed track.
    Scores with an empty order so the plan reasons from Camelot/tempo/energy,
    not a pre-declared sequence."""
    remaining = set(songs) - {start}
    order = [start]
    while remaining:
        nxt = max(remaining, key=lambda c: score_candidate(order[-1], c, songs, {}, [])[0])
        order.append(nxt)
        remaining.discard(nxt)
    return order


def arc_line(order, songs):
    parts = []
    for sid in order:
        s = songs[sid]
        parts.append(f"{_camelot(s) or '?'}/{bpm_of(s):.0f}")
    return "  →  ".join(parts)


def report(order, songs, edges, title):
    trans = audit_order(order, songs, edges)
    total = sum(t["score"] for t in trans)
    avg = total / len(trans) if trans else 0.0
    out = [f"## {title}", "", f"**Order:** {arc_line(order, songs)}", "",
           f"**Set coherence:** {total:.0f} total, {avg:.1f} avg/transition "
           f"across {len(trans)} transitions", "", "### Transitions"]
    for t in trans:
        # the one-line "headline" reason (harmonic + tempo), plus the score
        head = next((r for r in t["reasons"] if r.startswith("Camelot compatible")), None)
        tempo = next((r for r in t["reasons"] if r.startswith("tempo")), "")
        cue = head or next((r for r in t["reasons"] if r.startswith("Camelot")), "")
        out.append(f"- `{t['from']}` → `{t['to']}` — **{t['score']}**  ·  {cue}  ·  {tempo}")
    if trans:
        weakest = min(trans, key=lambda t: t["score"])
        out += ["", f"### Weakest link (fix this first)",
                f"- `{weakest['from']}` → `{weakest['to']}` (score {weakest['score']})"]
        for r in weakest["reasons"]:
            out.append(f"  - {r}")
    out += ["", "### House physics",
            "- Offline proposal only — human acks before any deck load; no RT/network."]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--session", required=True)
    ap.add_argument("--audit", action="store_true", help="score the session's declared order")
    ap.add_argument("--plan", action="store_true", help="propose a smooth order")
    ap.add_argument("--start", help="start song id for --plan (default: first in order)")
    args = ap.parse_args()

    session_path = Path(args.session)
    session = load_json(session_path)
    songs = load_songs(session_path, session)
    edges = edge_index(session)
    order = session.get("order") or list(songs)

    if not args.audit and not args.plan:
        args.audit = True

    blocks = []
    if args.audit:
        blocks.append(report(order, songs, edges, "Set audit — planned order"))
    if args.plan:
        start = args.start or order[0]
        planned = plan_order(start, songs, edges)
        blocks.append(report(planned, songs, edges, f"Set plan — proposed order (from `{start}`)"))
    print("\n\n".join(blocks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
