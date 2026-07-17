# Execution — phase plan (PLT)

## Waves

| # | Wave | Deliverable | Verifiability gate | Status |
|---|---|---|---|---|
| 1 | SoundIO soak | EVD-PLT-0001 + soak tool | zero hard_err/late on buffer sweeps; 16/16 engine gtests | **met** |
| 2 | CI/packaging prune | mac-only build matrix; DORMANT packaging | workflows parse; local arm64 binary still present; no Mac feature loss | **met** (local) |
| 3 | Waveform parity | WAVEFORM-PARITY-MATRIX.md | matrix complete; 0 deletes | **met** (HOLD) |

## Gate definitions

### Wave 1
```bash
./tools/soundio/coreaudio_pa_soak --seconds 20 --buffer 256 --rate 48000
# RESULT gate_stable_callback=PASS
build/mixxx-test --gtest_filter='EngineBufferTest.*:…'  # 16 PASSED
```

### Wave 2
- `.github/workflows/build.yml` matrix = single `macOS arm64` job  
- `release.yml` flatpak publish `if: false`  
- `packaging/{debian,flatpak,wix}/DORMANT.md` present  
- `PIPEWIRE=OFF` explicit in CI cmake_args  

### Wave 3
- `results/WAVEFORM-PARITY-MATRIX.md` lists features + live deps  
- `git status` shows no deletions under `src/waveform/**/deprecated/`  

## House-physics guardrails
- No RT path edits  
- No bulk GL delete  
- Bisectable commits  

## Rollback
- Wave 2: restore prior `build.yml` matrix from git  
- Wave 1: tool-only; no product binary change  
- Wave 3: docs-only  

## Next after this dossier (not in scope)
- Manual USB/AirPods dual-deck soak enrichment  
- UIX dossier for real GL retirement after parity dogfood  
- Wave 4 Accelerate / Wave 5 native CA only if product need
