# Problem — platform tax vs Apple-Silicon product floor

Migx forked Mixxx with a multi-OS CI/packaging surface and a PortAudio-abstracted SoundIO stack.
ADR-006 now declares **macOS 26+ Apple Silicon only**. Until CI, packaging, and measurement catch
up, the repo still *acts* multi-platform while the product promise is single-platform.

Three immediate risks:

1. **Unknown underrun baseline on the only supported OS** after the Tahoe 26 jump (latency/safety
   offset drift; community coreaudiod flake reports).  
2. **CI burns cycles** on Ubuntu/Windows/Intel/Android legs that cannot ship.  
3. **Temptation to delete** `waveform/**/deprecated/` before parity — already failed once (agy bulk
   delete broke live base-class includes).

This dossier closes those three with measurement → prune → parity gate, feature-preserving for Mac DJs.
