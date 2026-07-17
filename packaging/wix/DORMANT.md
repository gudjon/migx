# DORMANT — Windows WiX packaging

**Status:** dormant as of PLT Wave 2 (2026-07-17) / [ADR-006](../../kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md).

Windows is not a Migx product target. Tree retained; CI Windows matrix legs removed.
CMake still has `if(WIN32)` WIX paths for accidental host builds — not exercised in CI.
