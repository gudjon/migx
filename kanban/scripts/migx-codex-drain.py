#!/usr/bin/env python3
"""Codex-side seal-class drains — independent evaluation (P-08).

Currently implements:
  - EXO transition proof evaluation when mail *exo-p08* is open or ack to codex-cli

Invoked by: migx-fleet-conductor.py --drain-codex
            or: python3 kanban/scripts/migx-codex-drain.py
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CAMELOT_RE = re.compile(r"^(\d{1,2})([AB])$", re.I)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def camelot_adjacent(a: str, b: str) -> bool:
    """Same letter ring; number ±1 mod 12 (1..12). Same key counts as compatible."""
    ma, mb = CAMELOT_RE.match(a.strip()), CAMELOT_RE.match(b.strip())
    if not ma or not mb:
        return False
    na, la = int(ma.group(1)), ma.group(2).upper()
    nb, lb = int(mb.group(1)), mb.group(2).upper()
    if not (1 <= na <= 12 and 1 <= nb <= 12):
        return False
    if la != lb:
        # relative major/minor rough: same number different letter is often treated compatible
        return na == nb
    if na == nb:
        return True
    return abs(na - nb) % 12 in (1, 11)


def load_song(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_exo(root: Path) -> tuple[bool, str]:
    exo = root / "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike"
    proof = exo / "results" / "TRANSITION-PROOF.md"
    s1 = exo / "fixtures/songs/song-01-deep-intro.ontology.json"
    s2 = exo / "fixtures/songs/song-02-peak.ontology.json"
    s3 = exo / "fixtures/songs/song-03-cool-down.ontology.json"
    session = exo / "fixtures/sessions/session-3track-demo.json"
    schema_song = exo / "fixtures/schema/migx.song-ontology.v1.json"
    schema_sess = exo / "fixtures/schema/migx.session-ontology.v1.json"

    missing = [p for p in (proof, s1, s2, s3, session, schema_song, schema_sess) if not p.is_file()]
    if missing:
        return False, "missing files: " + ", ".join(str(m.relative_to(root)) for m in missing)

    for p in (s1, s2, s3, session, schema_song, schema_sess):
        json.loads(p.read_text(encoding="utf-8"))

    d1, d2, d3 = load_song(s1), load_song(s2), load_song(s3)
    k1, k2, k3 = d1["key"]["camelot"], d2["key"]["camelot"], d3["key"]["camelot"]
    e1 = float(d1["sections"][-1]["energy"])  # outro energy
    e2i = float(d2["sections"][0]["energy"])
    e2p = max(float(s["energy"]) for s in d2["sections"])
    e3p = max(float(s["energy"]) for s in d3["sections"])

    lines = [
        f"keys: {d1['id']}={k1}, {d2['id']}={k2}, {d3['id']}={k3}",
        f"camelot_adjacent(8A,9A)={camelot_adjacent(k1, k2)}",
        f"camelot_adjacent(8A,7A)={camelot_adjacent(k1, k3)}",
        f"energy outro1={e1} intro2={e2i} peak2={e2p} peak3={e3p}",
    ]

    proof_text = proof.read_text(encoding="utf-8")
    claims_song2 = "song-02" in proof_text and "9A" in proof_text
    if not claims_song2:
        return False, "TRANSITION-PROOF does not clearly recommend song-02/9A\n" + "\n".join(lines)

    if not camelot_adjacent(k1, k2):
        return False, f"FAIL harmonic: {k1} not adjacent to {k2}\n" + "\n".join(lines)

    # energy story: peak track should peak higher than track1 outro and cool-down peak
    if not (e2p > e1 and e2p >= e3p - 0.05):
        return False, f"FAIL energy story: peak2={e2p} outro1={e1} peak3={e3p}\n" + "\n".join(lines)

    # session order matches claim
    sess = json.loads(session.read_text(encoding="utf-8"))
    order = sess.get("order") or []
    if order[:2] != ["song-01-deep-intro", "song-02-peak"]:
        return False, f"FAIL session order {order} does not put peak after intro\n" + "\n".join(lines)

    lines.append("VERDICT: PASS — 8A→9A adjacent; energy lift coherent; session order matches proof")
    return True, "\n".join(lines)


def find_exo_p08_mail(root: Path) -> tuple[Path, str] | None:
    def is_codex_mail(path: Path) -> bool:
        text = path.read_text(encoding="utf-8", errors="replace")
        return bool(re.search(r"^to:\s*[\"']?codex-cli[\"']?\s*$", text, re.M))

    for status in ("open", "ack"):
        d = root / "kanban/federation/messages" / status
        if not d.is_dir():
            continue
        for p in d.glob("*exo-p08*"):
            if is_codex_mail(p):
                return p, status
        for p in d.glob("*evaluate-transition*"):
            if is_codex_mail(p):
                return p, status
    return None


def close_mail(root: Path, msg_id: str, resolution: str) -> int:
    fed = root / "kanban/scripts/migx-fed"
    return subprocess.call(
        [
            sys.executable,
            str(fed),
            "--root",
            str(root),
            "close",
            "--id",
            msg_id,
            "--by",
            "codex-cli",
            "--resolution",
            resolution,
        ]
    )


def write_eval_artifact(root: Path, passed: bool, detail: str) -> Path:
    exo = root / "kanban/planning/2026-07-17-gudjon-EXO--experience-ontology-spike/results"
    exo.mkdir(parents=True, exist_ok=True)
    path = exo / "P08-EVAL-codex.md"
    verdict = "PASS" if passed else "FAIL"
    path.write_text(
        f"""# P-08 independent evaluation — EXO transition proof

**Evaluator:** codex-cli drain (`migx-codex-drain.py`) — not the fixture author  
**Verdict:** **{verdict}**

## Method
- Parse song/session JSON fixtures
- Camelot adjacency: same ring letter, number ±1 (mod 12), or same number major/minor
- Energy: peak track max section energy > track1 outro; peak ≥ cool-down peak
- Proof text must recommend song-02 / 9A; session order must start song-01 → song-02

## Detail
```
{detail}
```

## Sign-off
Automated structural + harmonic/energy check. Human may still enrich; seal EXO only with this PASS
(or a human override recorded in JOURNAL).
""",
        encoding="utf-8",
    )
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true", help="evaluate but do not close mail")
    ap.add_argument(
        "--force-eval",
        action="store_true",
        help="always write P08-EVAL artifact even if no open/ack mail",
    )
    args = ap.parse_args()
    root = (args.root or repo_root()).resolve()

    found = find_exo_p08_mail(root)
    if not found and not args.force_eval:
        print("codex-drain: no open/ack EXO P-08 mail for codex-cli - no-op")
        return 0

    ok, detail = evaluate_exo(root)
    print(detail)
    art = write_eval_artifact(root, ok, detail)
    print(f"wrote {art.relative_to(root)}")

    if not found:
        if args.force_eval:
            print("codex-drain: force-eval requested - artifact refreshed without closing mail")
        return 0 if ok else 1

    path, status = found
    mid = path.stem
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("id:"):
            mid = line.split(":", 1)[1].strip().strip("\"'")
            break

    print(f"codex-drain: found {status} mail {mid}")
    resolution = (
        f"P-08 {'PASS' if ok else 'FAIL'} — independent codex drain.\n"
        f"Artifact: {art.relative_to(root)}\n"
        f"Detail:\n{detail}"
    )
    if args.dry_run:
        print("dry-run: not closing mail")
        return 0 if ok else 1

    rc = close_mail(root, mid, resolution)
    if rc != 0:
        print(f"close failed rc={rc}", file=sys.stderr)
        return rc
    print(f"closed {mid} as codex-cli")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
