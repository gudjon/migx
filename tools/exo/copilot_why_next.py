#!/usr/bin/env python3
"""Offline Layer B co-pilot: propose next track with explainable reasons.

Reads session ontology (or dogfood session-mirror) + song ontologies.
Does NOT touch the RT engine, ControlObjects, or network.

Policy (Octave / Spotify contract):
  - local → local: multi-deck OK if multi_deck_allowed
  - any → spotify or spotify → any: sequence-only (no dual Spotify stream)
  - harmonic edges preferred when present; energy always cited

Examples:
  python3 tools/exo/copilot_why_next.py \\
    --session kanban/.../fixtures/sessions/session-hybrid-prep-demo.json

  python3 tools/exo/copilot_why_next.py \\
    --mirror kanban/.../fixtures/dogfood/session-mirror.v1.json \\
    --write-intent kanban/.../fixtures/dogfood/intent-inbox.v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAMELOT_RE = re.compile(r"^(\d{1,2})([AB])$", re.I)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_ref(base: Path, ref: str) -> Path:
    return (base / ref).resolve()


def camelot_neighbors(code: str) -> set[str]:
    m = CAMELOT_RE.match(code.strip())
    if not m:
        return set()
    n = int(m.group(1))
    mode = m.group(2).upper()
    # ring 1..12
    prev_n = 12 if n == 1 else n - 1
    next_n = 1 if n == 12 else n + 1
    flip = "B" if mode == "A" else "A"
    return {f"{n}{mode}", f"{prev_n}{mode}", f"{next_n}{mode}", f"{n}{flip}"}


def energy_tail(song: dict[str, Any]) -> float:
    samples = (song.get("energy_curve") or {}).get("samples") or []
    if not samples:
        return 0.5
    return float(samples[-1])


def energy_head(song: dict[str, Any]) -> float:
    samples = (song.get("energy_curve") or {}).get("samples") or []
    if not samples:
        return 0.5
    return float(samples[0])


def load_songs(session_path: Path, session: dict[str, Any]) -> dict[str, dict[str, Any]]:
    base = session_path.parent
    out: dict[str, dict[str, Any]] = {}
    for t in session.get("tracks") or []:
        sid = t["song_id"]
        ref = t.get("ontology_ref")
        if not ref:
            continue
        p = resolve_ref(base, ref)
        if not p.is_file():
            raise FileNotFoundError(f"missing ontology for {sid}: {p}")
        out[sid] = load_json(p)
    return out


def session_from_mirror(mirror_path: Path) -> tuple[Path, dict[str, Any], str]:
    """Return (session_path, session, current_song_id)."""
    mirror = load_json(mirror_path)
    ref = mirror.get("ontology_session_ref")
    if not ref:
        raise SystemExit("mirror missing ontology_session_ref")
    session_path = resolve_ref(mirror_path.parent, ref)
    session = load_json(session_path)
    # current = playing deck if any, else Channel1
    current = None
    for d in mirror.get("decks") or []:
        if d.get("play") and d.get("loaded_song_id"):
            current = d["loaded_song_id"]
            break
    if not current:
        decks = mirror.get("decks") or []
        current = (decks[0] or {}).get("loaded_song_id") if decks else None
    if not current:
        order = session.get("order") or []
        current = order[0] if order else None
    if not current:
        raise SystemExit("cannot determine current song from mirror")
    return session_path, session, current


def edge_index(session: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    idx: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for e in session.get("edges") or []:
        key = (e["from"], e["to"])
        idx.setdefault(key, []).append(e)
    return idx


def score_candidate(
    current_id: str,
    cand_id: str,
    songs: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str], list[dict[str, Any]]],
    order: list[str],
) -> tuple[float, list[str], str]:
    """Return (score, reasons, relation_hint)."""
    cur = songs[current_id]
    cand = songs[cand_id]
    reasons: list[str] = []
    score = 0.0

    cur_src = cur.get("source") or "local"
    cand_src = cand.get("source") or "local"
    cur_md = (cur.get("playback") or {}).get("multi_deck_allowed", cur_src == "local")
    cand_md = (cand.get("playback") or {}).get("multi_deck_allowed", cand_src == "local")

    relation = "planned-transition"
    if cur_src == "spotify" or cand_src == "spotify":
        relation = "sequence-only"
        reasons.append(
            f"source policy: {cur_src}→{cand_src} is sequence-only "
            f"(no dual Spotify multi-deck; multi_deck cur={cur_md} cand={cand_md})"
        )
        score += 5.0
    else:
        reasons.append(f"source policy: {cur_src}→{cand_src}; multi-deck allowed if both local")
        score += 8.0

    # explicit edges
    for e in edges.get((current_id, cand_id), []):
        rel = e.get("relation", "")
        note = e.get("notes", "")
        if rel == "harmonically-compatible":
            score += 30.0
            reasons.append(f"session edge harmonically-compatible: {note or rel}")
            relation = rel
        elif rel == "next-energy":
            score += 15.0
            reasons.append(f"session edge next-energy: {note or rel}")
        elif rel == "sequence-only":
            score += 10.0
            reasons.append(f"session edge sequence-only: {note or rel}")
            relation = "sequence-only"
        else:
            score += 5.0
            reasons.append(f"session edge {rel}: {note}")

    # Camelot math
    cur_key = (cur.get("key") or {}).get("camelot") or ""
    cand_key = (cand.get("key") or {}).get("camelot") or ""
    if cur_key and cand_key:
        neigh = camelot_neighbors(cur_key)
        if cand_key.upper() in {x.upper() for x in neigh}:
            score += 25.0
            reasons.append(f"Camelot compatible: {cur_key} → {cand_key} (self/±1/mode flip)")
            if relation == "planned-transition":
                relation = "harmonically-compatible"
        else:
            reasons.append(f"Camelot not adjacent: {cur_key} → {cand_key} (energy/sequence may still hold)")

    # Energy direction
    et, eh = energy_tail(cur), energy_head(cand)
    delta = eh - et
    if abs(delta) < 0.08:
        score += 8.0
        reasons.append(f"energy steady: tail {et:.2f} → head {eh:.2f}")
    elif delta > 0:
        score += 12.0
        reasons.append(f"energy lift: tail {et:.2f} → head {eh:.2f} (Δ+{delta:.2f})")
    else:
        score += 6.0
        reasons.append(f"energy cool: tail {et:.2f} → head {eh:.2f} (Δ{delta:.2f})")

    # Prefer next in planned order
    if current_id in order:
        i = order.index(current_id)
        if i + 1 < len(order) and order[i + 1] == cand_id:
            score += 20.0
            reasons.append("matches planned order (next in session.order)")
        elif cand_id in order[i + 1 :]:
            score += 4.0
            reasons.append("appears later in planned order")

    return score, reasons, relation


def propose(
    current_id: str,
    session: dict[str, Any],
    songs: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    order = session.get("order") or list(songs.keys())
    edges = edge_index(session)
    candidates = [s for s in order if s != current_id and s in songs]
    if not candidates:
        candidates = [s for s in songs if s != current_id]

    ranked: list[dict[str, Any]] = []
    for cid in candidates:
        sc, reasons, rel = score_candidate(current_id, cid, songs, edges, order)
        ranked.append(
            {
                "song_id": cid,
                "score": round(sc, 2),
                "relation": rel,
                "source": songs[cid].get("source") or "unknown",
                "camelot": (songs[cid].get("key") or {}).get("camelot"),
                "playback": songs[cid].get("playback") or {},
                "reasons": reasons,
            }
        )
    ranked.sort(key=lambda r: r["score"], reverse=True)
    best = ranked[0] if ranked else None

    return {
        "schema": "migx.copilot-why-next/1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "current_song_id": current_id,
        "current_source": songs[current_id].get("source"),
        "current_camelot": (songs[current_id].get("key") or {}).get("camelot"),
        "proposal": best,
        "ranked": ranked,
        "policy": {
            "spotify_multi_deck": False,
            "human_ack_required": True,
            "rt_safe": "no engine writes; intent only",
            "ux": "Predict → Ask → Explain",
        },
    }


def to_intent(proposal: dict[str, Any]) -> dict[str, Any]:
    p = proposal.get("proposal") or {}
    return {
        "schema": "migx.intent-inbox/1",
        "note": (
            "Offline dogfood intents — production path must marshal via ControlObject "
            "single-writer (P-06), never RT thread."
        ),
        "intents": [
            {
                "id": "intent-copilot-why-next",
                "type": "suggest_next_track",
                "status": "proposed",
                "from_song_id": proposal["current_song_id"],
                "to_song_id": p.get("song_id"),
                "relation": p.get("relation"),
                "score": p.get("score"),
                "reason": "; ".join(p.get("reasons") or []),
                "requires_human_ack": True,
                "co_writes": [
                    {
                        "group": "[Channel2]",
                        "key": "LoadTrack",
                        "value_note": f"load {p.get('song_id')} — illustrative only",
                    }
                ],
            }
        ],
    }


def render_md(result: dict[str, Any]) -> str:
    p = result.get("proposal")
    lines = [
        "# Co-pilot — why next (offline Layer B)",
        "",
        f"**Generated:** {result['generated_utc']}",
        f"**Current:** `{result['current_song_id']}` "
        f"({result.get('current_source')}, {result.get('current_camelot')})",
        f"**UX:** {result['policy']['ux']}",
        "",
    ]
    if not p:
        lines.append("_No proposal._")
        return "\n".join(lines) + "\n"

    lines += [
        f"## Proposal: `{p['song_id']}` (score {p['score']})",
        "",
        f"- relation: **{p['relation']}**",
        f"- source: `{p['source']}` · Camelot `{p.get('camelot')}`",
        f"- multi_deck_allowed: {(p.get('playback') or {}).get('multi_deck_allowed')}",
        "",
        "### Why",
        "",
    ]
    for r in p.get("reasons") or []:
        lines.append(f"- {r}")
    lines += ["", "### Ranked alternatives", ""]
    for row in result.get("ranked") or []:
        mark = "→" if row["song_id"] == p["song_id"] else " "
        lines.append(
            f"- {mark} `{row['song_id']}` score={row['score']} "
            f"({row['source']}, {row.get('camelot')}, {row['relation']})"
        )
    lines += [
        "",
        "### House physics",
        "",
        "- Intent status **proposed** — human must ack before any CO write.",
        "- No RT / network / dual Spotify multi-deck from this tool.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--session", type=Path, help="session ontology JSON")
    ap.add_argument("--mirror", type=Path, help="session-mirror.v1.json (implies session ref)")
    ap.add_argument("--current", type=str, help="override current song_id")
    ap.add_argument("--json-out", type=Path, help="write full proposal JSON")
    ap.add_argument("--md-out", type=Path, help="write markdown explanation")
    ap.add_argument(
        "--write-intent",
        type=Path,
        help="write migx.intent-inbox/1 JSON (proposed only)",
    )
    args = ap.parse_args()

    if args.mirror:
        session_path, session, current = session_from_mirror(args.mirror)
    elif args.session:
        session_path = args.session
        session = load_json(session_path)
        order = session.get("order") or []
        current = args.current or (order[0] if order else None)
        if not current:
            print("need --current or non-empty order", file=sys.stderr)
            return 2
    else:
        print("provide --session or --mirror", file=sys.stderr)
        return 2

    if args.current:
        current = args.current

    songs = load_songs(session_path, session)
    if current not in songs:
        print(f"current song {current!r} not in session ontologies", file=sys.stderr)
        return 2

    result = propose(current, session, songs)
    md = render_md(result)
    print(md)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.json_out}", file=sys.stderr)
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(md, encoding="utf-8")
        print(f"wrote {args.md_out}", file=sys.stderr)
    if args.write_intent:
        intent = to_intent(result)
        args.write_intent.parent.mkdir(parents=True, exist_ok=True)
        args.write_intent.write_text(json.dumps(intent, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.write_intent}", file=sys.stderr)

    return 0 if result.get("proposal") else 1


if __name__ == "__main__":
    raise SystemExit(main())
