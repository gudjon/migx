"""Bounded ArcFlow queries over Migx's disposable library graph.

Migx owns the query templates and output schemas.  Callers choose a bounded
product question, never arbitrary GQL; ArcFlow remains a read-only derived
index on this path and is never reachable from the audio callback.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_DATA_DIR = Path.home() / ".migx" / "graph"
DEFAULT_ARCFLOW = Path.home() / ".arcflow" / "bin" / "arcflow"
MAX_LIMIT = 100


class GraphError(RuntimeError):
    """ArcFlow is unavailable or returned an invalid query result."""


def arcflow_bin(explicit: str | None = None) -> Path:
    """Resolve the runtime without silently falling back to another engine."""
    return Path(
        explicit or os.environ.get("MIGX_ARCFLOW_BIN") or DEFAULT_ARCFLOW
    ).expanduser()


def _query(entity: str, limit: int) -> tuple[str, str]:
    if not 1 <= limit <= MAX_LIMIT:
        raise GraphError(f"limit must be between 1 and {MAX_LIMIT}")
    if entity == "track":
        return (
            "track-distinct-playlists/1",
            "MATCH (t:Track)-[:ON]->(p:Playlist) "
            "WITH t.key AS key, t.title AS track, "
            "count(DISTINCT p.id) AS playlists "
            "RETURN key, track, playlists "
            "ORDER BY playlists DESC, track, key "
            f"LIMIT {limit}",
        )
    if entity == "artist":
        return (
            "artist-distinct-playlists/1",
            "MATCH (t:Track)-[:BY]->(a:Artist), "
            "(t)-[:ON]->(p:Playlist) "
            "WITH a.name AS artist, count(DISTINCT p.id) AS playlists "
            "RETURN artist, playlists "
            "ORDER BY playlists DESC, artist "
            f"LIMIT {limit}",
        )
    raise GraphError("entity must be 'track' or 'artist'")


def _cell(column: str, value: Any) -> Any:
    """Restore known metric types without coercing numeric-looking names."""
    if column != "playlists":
        return value
    if not isinstance(value, str):
        return value
    try:
        return int(value)
    except ValueError:
        raise GraphError(f"ArcFlow returned a non-integer {column}: {value!r}")


def execute(
    query: str,
    *,
    data_dir: str | Path = DEFAULT_DATA_DIR,
    binary: str | Path | None = None,
    timeout: float = 30,
) -> dict[str, Any]:
    """Execute one already-bounded query through ArcFlow's JSON surface."""
    runtime = arcflow_bin(str(binary) if binary is not None else None)
    store = Path(data_dir).expanduser()
    if not runtime.is_file():
        raise GraphError(f"ArcFlow runtime not found: {runtime}")
    if not store.is_dir():
        raise GraphError(
            f"ArcFlow graph not found: {store} (run mirrors-to-graph first)"
        )

    try:
        proc = subprocess.run(
            [
                str(runtime),
                "query",
                query,
                "--data-dir",
                str(store),
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise GraphError(
            f"ArcFlow query timed out after {timeout:g}s"
        ) from exc
    except OSError as exc:
        raise GraphError(f"could not start ArcFlow: {exc}") from exc

    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "no detail"
        raise GraphError(f"ArcFlow query failed: {detail[:400]}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise GraphError("ArcFlow query did not return JSON") from exc

    columns = payload.get("columns")
    rows = payload.get("rows")
    if not isinstance(columns, list) or not isinstance(rows, list):
        raise GraphError("ArcFlow JSON is missing columns or rows")
    if not all(isinstance(row, dict) for row in rows):
        raise GraphError("ArcFlow JSON rows are not objects")
    payload["rows"] = [
        {column: _cell(column, row.get(column)) for column in columns}
        for row in rows
    ]
    return payload


def rank(
    entity: str,
    *,
    limit: int = 12,
    data_dir: str | Path = DEFAULT_DATA_DIR,
    binary: str | Path | None = None,
) -> dict[str, Any]:
    """Rank tracks or artists by distinct playlist membership."""
    query_id, query = _query(entity, limit)
    result = execute(query, data_dir=data_dir, binary=binary)
    return {
        "schema": "migx.graph-ranking/1",
        "entity": entity,
        "metric": "distinct-playlists",
        "query_id": query_id,
        "snapshot": result.get("__snapshot"),
        "data_dir": str(Path(data_dir).expanduser()),
        "rows": result["rows"],
        "count": len(result["rows"]),
    }
