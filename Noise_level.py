"""
=============================================================
  Noise Level Meter  —  Noise_level.py
  Author : Your Name
  GitHub : https://github.com/yourusername/noise-level-meter
=============================================================

Measures the surrounding noise level in real-time using your
microphone. Calculates dBFS values, shows a live terminal bar,
classifies the environment, and prints a summary at the end.

Requirements:
    pip install sounddevice numpy

Usage:
    python Noise_level.py

Python: 3.7+
"""

import sounddevice as sd
import numpy as np
import time
import math
import sys


# ─── Configuration ────────────────────────────────────────────────────────────

SAMPLE_RATE = 44100   # samples per second
BLOCK_SIZE  = 2048    # audio samples per block (~46 ms per block)
METER_WIDTH = 40      # number of characters in the terminal bar

# dBFS thresholds  (all values are negative — closer to 0 = louder)
QUIET_THRESHOLD  = -35   # quieter than this → Quiet
NORMAL_THRESHOLD = -20   # between QUIET and this → Normal
                          # above this → Noisy


# ─── Core functions ───────────────────────────────────────────────────────────

def dbfs(block: np.ndarray) -> float:
    """
    Convert a block of audio samples to dBFS (decibels relative to full scale).

    Steps:
      1. If stereo, average the two channels into mono.
      2. Compute RMS  =  sqrt( mean( samples² ) )
      3. Convert to dB:  20 * log10(rms)

    Returns -120.0 for near-silent blocks (avoids log(0) crash).
    """
    if block.ndim > 1:
        block = np.mean(block, axis=1)   # stereo → mono

    rms = np.sqrt(np.mean(block ** 2))

    if rms <= 1e-12:
        return -120.0                    # effectively silence

    return 20.0 * math.log10(rms)


def classify(db: float) -> str:
    """
    Classify a dBFS value into an environment label.

    Thresholds:
      ≤ -35 dB  →  Quiet
      ≤ -20 dB  →  Normal
      above     →  Noisy
    """
    if db <= QUIET_THRESHOLD:
        return "Quiet"
    elif db <= NORMAL_THRESHOLD:
        return "Normal"
    else:
        return "Noisy"


def suggestion(label: str) -> str:
    """Return a human-readable tip based on the environment label."""
    tips = {
        "Quiet":  "Good for study, reading, or deep focus.",
        "Normal": "Good for conversation or light work.",
        "Noisy":  "Too noisy! Not ideal for study or concentration.",
    }
    return tips.get(label, "")


def render_meter(db: float) -> str:
    """
    Build a terminal progress bar for the given dBFS value.

    The scale maps -60 dB (silent) → 0 filled bars
                    0 dB (max)     → METER_WIDTH filled bars

    Example output:  [################------------------------]  -24.3 dB
    """
    clamped  = max(-60.0, min(0.0, db))
    fill_pct = (clamped + 60.0) / 60.0          # 0.0 – 1.0
    filled   = int(fill_pct * METER_WIDTH)

    bar = "#" * filled + "-" * (METER_WIDTH - filled)
    return f"[{bar}] {db:6.1f} dB"


# ─── Colour helpers (ANSI — skipped on Windows cmd) ──────────────────────────

def _ansi(code: str, text: str) -> str:
    """Wrap text in an ANSI colour code (no-op if stdout is not a TTY)."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def coloured_label(label: str) -> str:
    """Return the label string with an ANSI colour matching its severity."""
    colours = {"Quiet": "32", "Normal": "33", "Noisy": "31"}   # green / yellow / red
    return _ansi(colours.get(label, "0"), f"{label:>6}")


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Noise Level Meter")
    print("  Values in dBFS  |  -60 = silent,  0 = maximum")
    print("=" * 60)

    # Ask how long to measure
    try:
        duration = int(input("\nSeconds to measure: "))
        if duration <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a positive whole number.")
        sys.exit(1)

    print(f"\nMeasuring noise for {duration} second(s) — press Ctrl+C to stop early.\n")

    levels = []
    start  = time.time()

    try:
        with sd.InputStream(
            samplerate = SAMPLE_RATE,
            blocksize  = BLOCK_SIZE,
            channels   = 1,
            dtype      = "float32"
        ) as stream:

            while time.time() - start < duration:
                block, _overflowed = stream.read(BLOCK_SIZE)
                level = dbfs(block)
                levels.append(level)

                label   = classify(level)
                bar_str = render_meter(level)
                col_lbl = coloured_label(label)

                # \r overwrites the current line → live-update effect
                print(f"\r{bar_str} | {col_lbl}", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n[Stopped early by user]")
    except sd.PortAudioError as e:
        print(f"\n\nMicrophone error: {e}")
        print("Make sure a microphone is connected and not used by another app.")
        sys.exit(1)

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n")
    print("=" * 60)

    if not levels:
        print("No audio data was captured.")
        sys.exit(0)

    avg   = float(np.mean(levels))
    peak  = float(np.max(levels))
    quiet = float(np.min(levels))
    label = classify(avg)

    print(f"  Readings collected : {len(levels)}")
    print(f"  Average level      : {avg:.1f} dB  →  {label}")
    print(f"  Quietest moment    : {quiet:.1f} dB")
    print(f"  Loudest moment     : {peak:.1f} dB")
    print(f"  Suggestion         : {suggestion(label)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
