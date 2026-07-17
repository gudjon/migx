#!/usr/bin/env python3
"""lint-federation-messages — federation mail frontmatter valid + relates_to resolves.

Complements `migx-fed doctor` (which only checks the folder layout). For every
handoff under kanban/federation/messages/{open,ack,closed}/*.md this checks the
per-message contract (kanban/federation/FEDERATION.md):

  - required frontmatter present: id, from, to, type, status, created, severity,
    subject, acceptance;
  - from/to are registered peers (peers.yaml); type/severity/status use the CLI
    vocabulary (imported from `migx-fed`, the single home for those enums);
  - status matches the folder it lives in (state = location invariant);
  - id equals the filename stem (the <from>-<to>-date-NNN-slug naming convention);
  - every relates_to entry resolves — a repo path, a dossier prefix, a task slug,
    a P-/AP-/ADR-/PS- id, an initiative id, or a sibling message id.

Exit 0 on pass, non-zero with a clear message on failure.
Run:  python3 kanban/scripts/lint-federation-messages.py
"""
import importlib.util
import pathlib
import re
import sys
from importlib.machinery import SourceFileLoader

_here = pathlib.Path(__file__).resolve()
for _p in [_here, *_here.parents]:
    if (_p / "kanban" / "scripts" / "_kanban_lint.py").exists():
        sys.path.insert(0, str(_p / "kanban" / "scripts"))
        _REPO = _p
        break
from _kanban_lint import die, ok, parse_frontmatter, parse_yaml_lite

REQUIRED = ("id", "from", "to", "type", "status", "created", "severity", "subject", "acceptance")


def load_cli_vocab(repo):
    """Import the migx-fed CLI as a module to reuse its enums (MG-3: one home)."""
    path = repo / "kanban" / "scripts" / "migx-fed"
    spec = importlib.util.spec_from_file_location("migx_fed", path, loader=SourceFileLoader("migx_fed", str(path)))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.VALID_TYPES, mod.VALID_SEVERITY, mod.STATUS_DIRS


def known_ids(repo):
    """Every typed id / prefix a relates_to entry may resolve to (non-path)."""
    ids = set()
    reg = repo / "kanban" / "planning" / "00-PORTFOLIO" / "prefix-registry.yaml"
    if reg.exists():
        for d in parse_yaml_lite(reg.read_text(encoding="utf-8")).get("dossiers") or []:
            if isinstance(d, dict) and d.get("prefix"):
                ids.add(str(d["prefix"]))
    for f in (repo / "kanban" / "tasks").glob("*.md"):
        ids.add(f.stem)
    for f in (repo / "kanban" / "patterns").glob("*.md"):
        m = re.match(r"^((?:P|AP)-\d+)-", f.name)
        if m:
            ids.add(m.group(1))
    for f in (repo / "kanban" / "initiatives").glob("*.md"):
        ids.add(f.stem)
    for f in (repo / "kanban" / "architecture" / "decisions").glob("ADR-*.md"):
        m = re.match(r"^(ADR-\d+)", f.name)
        if m:
            ids.add(m.group(1))
    for f in (repo / "kanban").rglob("PS-*.md"):
        ids.add(f.stem)
    for st in ("open", "ack", "closed"):
        for f in (repo / "kanban" / "federation" / "messages" / st).glob("*.md"):
            ids.add(f.stem)
    return ids


def resolves(ref, repo, ids):
    ref = str(ref).strip()
    if not ref:
        return True
    if "/" in ref or ref.endswith(".md"):
        return (repo / ref).exists()
    return ref in ids


def main():
    repo = _REPO
    valid_types, valid_sev, status_dirs = load_cli_vocab(repo)
    peers = set((parse_yaml_lite((repo / "kanban" / "federation" / "peers.yaml").read_text("utf-8")).get("peers") or {}).keys())
    ids = known_ids(repo)
    errors, n = [], 0

    for st in status_dirs:
        d = repo / "kanban" / "federation" / "messages" / st
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name.startswith("_"):
                continue
            n += 1
            rel = f.relative_to(repo)
            fm = parse_frontmatter(f.read_text(encoding="utf-8"))
            for k in REQUIRED:
                if not fm.get(k):
                    errors.append(f"{rel}: missing required field `{k}`")
            if fm.get("id") and fm["id"] != f.stem:
                errors.append(f"{rel}: id `{fm['id']}` != filename stem `{f.stem}`")
            if peers and fm.get("from") and fm["from"] not in peers:
                errors.append(f"{rel}: from `{fm['from']}` not a registered peer")
            if peers and fm.get("to") and fm["to"] not in peers:
                errors.append(f"{rel}: to `{fm['to']}` not a registered peer")
            if fm.get("type") and fm["type"] not in valid_types:
                errors.append(f"{rel}: type `{fm['type']}` not in {valid_types}")
            if fm.get("severity") and fm["severity"] not in valid_sev:
                errors.append(f"{rel}: severity `{fm['severity']}` not in {valid_sev}")
            if fm.get("status") and fm["status"] != st:
                errors.append(f"{rel}: status `{fm['status']}` != folder `{st}` (state=location)")
            for ref in fm.get("relates_to") or []:
                if not resolves(ref, repo, ids):
                    errors.append(f"{rel}: relates_to `{ref}` does not resolve")

    if errors:
        die(f"federation messages invalid ({len(errors)} problem(s))", errors)
    ok(f"federation messages valid: {n} message(s) checked")


if __name__ == "__main__":
    main()
