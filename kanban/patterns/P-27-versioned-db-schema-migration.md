---
id: P-27
type: pattern
title: "SQLite schema changes go through forward-only versioned migrations"
status: active
severity: MUST
domain: library
related: [P-28, P-07, AP-15]
created: "2026-07-17"
lastUpdated: "2026-07-17"
---

# P-27 — SQLite schema changes go through forward-only versioned migrations

## Statement
A change to the library database schema is expressed as a new versioned revision in `res/schema.xml`,
not as an ad-hoc `ALTER`/`CREATE` scattered in DAO code. Migrations are forward-only and additive; a
backwards-compatible one stays safely re-appliable, and one that isn't sets `min_compatible`.

## Why
`res/schema.xml` is the single source of truth for the DB shape (MG-3, `P-07`): Mixxx reads the
user's stored revision and applies each newer `<revision version="N">` in order to upgrade the library
in place. A DAO that mutates the schema on its own forks that truth — some databases get the change,
some don't, and the version number no longer describes the actual shape. The file's own header is
explicit: backwards-compatible migrations must be re-appliable without overwriting or deleting user
data, or else declare `min_compatible`. Losing a user's library metadata is unrecoverable, so the
discipline is non-negotiable.

## How to apply
- Add a new `<revision version="N+1">` with a `<description>` and idempotent `<sql>` (e.g.
  `CREATE TABLE IF NOT EXISTS`, add-column guarded so re-apply is safe); never edit an existing
  revision's SQL.
- Keep it backwards compatible (re-appliable, non-destructive) where possible; if not, set
  `min_compatible` to the new version.
- Access the new columns/tables through the DAO layer (`P-28`), not raw SQL in callers.
- Never `ALTER`/`CREATE` the library schema outside this migration path.

## Example — wrong
```cpp
// In some DAO method, at runtime:
query.exec("ALTER TABLE library ADD COLUMN my_new_field INTEGER");  // off-SSoT, unversioned, un-re-appliable
```

## Example — right
```xml
<!-- res/schema.xml -->
<revision version="41">
  <description>Add my_new_field to library.</description>
  <sql>ALTER TABLE library ADD COLUMN my_new_field INTEGER DEFAULT 0;</sql>
</revision>
```

## Detection
Review: `ALTER TABLE`/`CREATE TABLE` on the library DB outside `res/schema.xml`; an edit to an existing
revision's SQL; a schema change with no version bump.

## Cross-references
`res/schema.xml` is the schema SSoT per `P-07`; access goes through `P-28`. Hardcoding schema shape off
its home is an instance of `AP-15`.
