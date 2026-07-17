# JOURNAL — PLT

## 2026-07-17 — scaffold + Waves 1–3 execute

- Registered prefix **PLT** in `prefix-registry.yaml`.  
- Scaffolded dossier from `_template`.  
- Wave 1: wrote pure Core Audio soak tool (PortAudio static failed link on JACK).  
  All buffer sweeps **PASS** (128/256/512 @48k, 256@44.1k). EVD-PLT-0001.  
  Engine gtests 16/16 PASS via `mixxx-test` direct (ctest tree has recursive include glitch).  
- Wave 2: collapsed `build.yml` to single macOS arm64 job; disabled flatpak publish;
  DORMANT.md on debian/flatpak/wix.  
- Wave 3: WAVEFORM-PARITY-MATRIX.md — HOLD delete; documented live deprecated includes.  
- Decision: **no Wave 5 rewrite** — CA baseline solid on built-in.

## Residuals (honest)

- No USB / AirPods hardware at soak time.  
- Dual-deck GUI soak still manual.  
- GitHub Actions not executed in this session (local gate only).  
- Local `ctest` include recursion — pre-existing; use `mixxx-test` binary.
