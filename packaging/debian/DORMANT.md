# DORMANT — Debian/Ubuntu packaging

**Status:** dormant as of PLT Wave 2 (2026-07-17) / [ADR-006](../../kanban/architecture/decisions/ADR-006-platform-scope-apple-silicon.md).

Migx ships **macOS 26+ Apple Silicon only**. This tree is retained for historical reference and
upstream Mixxx parity; it is **not** a supported product path.

- CI: Debian/Ubuntu legs removed from `.github/workflows/build.yml`
- Active packaging: `packaging/macos/`
- Do not re-enable without an explicit product ADR reversing ADR-006
