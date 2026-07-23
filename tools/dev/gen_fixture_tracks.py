#!/usr/bin/env python3
"""Generate two NextGen dev test tracks with KNOWN bpm + tonal root.

The NextGen deck-shell (identity/clock/transport, cap-track-identity/cap-deck-clock) needs real
loaded tracks to test against — the fixture-mode base (nextgen-ui-architecture invariant #4). Pure
sines have no beat, so the analyzer can't show a real BPM; these tracks carry a strong kick at an exact
BPM plus a sustained bass tone at a chosen key root, so the BPM badge and the colour-coded KEY badge
both light up correctly once analyzed.

Output (gitignored — regenerate with `just dev-fixtures`):
  res/dev-fixtures/Demo Deck A - 128 BPM Am.wav
  res/dev-fixtures/Demo Deck B - 125 BPM Gm.wav

stdlib only (wave, struct, math). Filename is the title (WAV carries no rich tags; Mixxx falls back to it).
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
SECONDS = 16
AMP = 0.62  # headroom below clipping


def _kick(t: float) -> float:
    """A short decaying ~55 Hz sine burst — the beat transient the analyzer locks to."""
    if t > 0.16:
        return 0.0
    env = math.exp(-t * 26.0)
    # pitch drops from ~120 Hz to ~50 Hz over the burst (classic kick chirp)
    freq = 50.0 + 70.0 * math.exp(-t * 40.0)
    return env * math.sin(2.0 * math.pi * freq * t)


def _samples(bpm: float, root_hz: float):
    beat = 60.0 / bpm
    total = int(SAMPLE_RATE * SECONDS)
    for n in range(total):
        t = n / SAMPLE_RATE
        # kick on every beat
        into_beat = t % beat
        s = 0.9 * _kick(into_beat)
        # off-beat tick for rhythmic clarity
        if abs((t % beat) - beat / 2.0) < (1.0 / SAMPLE_RATE) * 220:
            s += 0.12 * math.sin(2.0 * math.pi * 2000.0 * t) * math.exp(-((t % (beat / 2.0))) * 90.0)
        # sustained bass tone at the key root (gives key detection something to read)
        s += 0.28 * math.sin(2.0 * math.pi * root_hz * t)
        s += 0.14 * math.sin(2.0 * math.pi * root_hz * 1.5 * t)  # a fifth above
        yield max(-1.0, min(1.0, s * AMP))


def write_wav(path: Path, bpm: float, root_hz: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in _samples(bpm, root_hz):
            frames += struct.pack("<h", int(s * 32767.0))
        w.writeframes(bytes(frames))
    print(f"wrote {path}  ({bpm:g} BPM, root {root_hz:g} Hz, {SECONDS}s)")


def main() -> None:
    out = Path(__file__).resolve().parents[2] / "res" / "dev-fixtures"
    # A: 128 BPM, root A2 (110 Hz) → key A; B: 125 BPM, root G2 (98 Hz) → key G
    write_wav(out / "Demo Deck A - 128 BPM Am.wav", 128.0, 110.0)
    write_wav(out / "Demo Deck B - 125 BPM Gm.wav", 125.0, 98.0)


if __name__ == "__main__":
    main()
