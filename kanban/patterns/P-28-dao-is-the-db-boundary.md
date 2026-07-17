---
id: P-28
type: pattern
title: "All library DB access goes through the typed DAO layer"
status: active
severity: SHOULD
domain: library
related: [P-27, P-07]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-28 — All library DB access goes through the typed DAO layer

## Statement
Access to the library database goes through the typed Data Access Object layer in `src/library/dao/`
(`TrackDAO`, `PlaylistDAO`, `CueDAO`, `AnalysisDao`, …). Callers work with typed objects and DAO
methods; raw `QSqlQuery`/SQL strings do not leak into mixer, controllers, GUI, or engine code.

## Why
`src/library/dao/` is the one boundary between the app and SQLite: it centralizes the SQL, the schema
knowledge, transaction handling, and the mapping to typed objects. Scattering raw SQL across callers
forks that knowledge (MG-3, `P-07`) — every caller now encodes column names and query shape, so a
schema migration (`P-27`) has to chase SQL through the whole codebase instead of updating one layer,
and each ad-hoc query is a fresh chance to get escaping, threading, or a column name wrong.

## How to apply
- Add or extend a DAO method for a new query; return typed objects, not raw rows.
- Keep SQL strings and `QSqlQuery` inside `src/library/dao/`; callers depend on the DAO interface only.
- The DAO owns transactions and knows the current schema (`P-27`); callers don't hand-write column
  lists.
- If a caller "needs" raw SQL, that's a missing DAO method — add it, don't inline the query.

## Example — wrong
```cpp
// In a controller/mixer/GUI file:
QSqlQuery q(db);
q.exec("SELECT title FROM library WHERE id=" + QString::number(id));  // raw SQL outside the DAO boundary
```

## Example — right
```cpp
// Through the boundary:
TrackPointer pTrack = m_pTrackDAO->getTrackById(id);   // typed, schema-aware, transaction-safe
QString title = pTrack->getTitle();
```

## Detection
Review: `QSqlQuery`/raw SQL strings against the library DB outside `src/library/dao/`; column names
hardcoded in non-DAO callers.

## Cross-references
Pairs with `P-27` (the DAO owns schema knowledge); it's `P-07` (single authority) applied to DB access.
