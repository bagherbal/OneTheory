"""Ambient soundtrack for the Genesis film, synthesized from the act timeline.

Owns:
    A slowly evolving stereo pad whose harmony follows the acts: one pure tone
    for the One, open fifths for the string, a suspended chord for the hidden
    dimensions, a triad for three families, a rising glide for inflation, a
    falling drone as the Higgs field settles, a glide down as the first light
    redshifts, and open fifths at the horizons. Chords cross-fade over seconds,
    so the sound never jumps either.

Depends on:
    NumPy and the Python standard library (wave, json).

Must not:
    Carry meaning the picture does not: it is mood only, not data.

Phase 0:
    Presentation layer only.

Usage:
    python soundtrack.py timeline.json out.wav
    where timeline.json is a list of [act_number, start_seconds, end_seconds].
"""

from __future__ import annotations

import json
import math
import sys
import wave

import numpy as np

RATE = 44100
BASE = 220.0          # A3: low enough to be calm, high enough for small speakers


def semitones(base: float, steps) -> list[float]:
    return [base * 2 ** (s / 12) for s in steps]


# act → (chord in semitones above BASE, brightness 0..1, special effect)
ACT_SOUND = {
    1: ((0, 12), 0.2, None),
    2: ((0, 7, 12, 19), 0.35, "pluck"),
    3: ((0, 5, 7, 12, 17), 0.35, None),
    4: ((-4, 0, 3, 7, 11), 0.45, None),
    5: ((3, 7, 10, 15), 0.5, None),
    6: ((0, 7, 12), 0.5, "rise"),
    7: ((5, 9, 12, 17), 0.65, "noise"),
    8: ((0, 7, 12, 16), 0.5, "fall"),
    9: ((2, 5, 9, 14), 0.5, None),
    10: ((10, 14, 17, 22), 0.6, None),
    11: ((0, 7, 12, 19, 24), 0.55, "redshift"),
    12: ((0, 3, 7, 10, 14), 0.4, "pulse"),
    13: ((7, 11, 14, 19), 0.5, "pan"),
    14: ((0, 7, 14, 19, 24), 0.45, "resolve"),
}


def voice(freq: float, t: np.ndarray, brightness: float, detune: float) -> np.ndarray:
    """A soft pad voice: a few harmonics with gentle chorus."""

    out = np.zeros_like(t)
    for h, weight in ((1, 1.0), (2, 0.35 * brightness), (3, 0.18 * brightness),
                      (4, 0.08 * brightness)):
        f = freq * h * (1 + detune)
        out += weight * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.11 * t * h))
    return out


def act_layer(act: int, t: np.ndarray, local: np.ndarray, length: float,
              rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    chord, brightness, effect = ACT_SOUND[act]
    left = np.zeros_like(t)
    right = np.zeros_like(t)
    progress = np.clip(local / max(length, 1e-6), 0, 1)
    glide = np.ones_like(t)
    if effect == "rise":
        glide = 2 ** (progress * 1.0)
    elif effect == "fall":
        glide = 2 ** (-0.5 * np.clip((progress - 0.25) / 0.5, 0, 1))
    elif effect == "redshift":
        glide = 2 ** (-0.6 * np.clip((progress - 0.5) / 0.5, 0, 1))
    for k, f in enumerate(semitones(BASE, chord)):
        freq = f * glide
        phase_t = np.cumsum(freq) / RATE / f        # integrate a gliding pitch
        pan = 0.5 + 0.35 * math.sin(k * 1.7)
        if effect == "pan":
            pan = 0.5 + 0.4 * np.sin(2 * np.pi * 0.05 * t + k)
        sig = voice(f, phase_t, brightness, 0.0015 * (k - 2)) / len(chord)
        if effect == "pulse":
            sig *= 0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * t + k)
        left += sig * (1 - pan)
        right += sig * pan
    if effect == "pluck":
        for start in np.arange(1.0, length, 2.5):
            since = local - start
            env = np.exp(-np.clip(since, 0, None) * 2.2) * np.clip(since / 0.01, 0, 1)
            tone = np.sin(2 * np.pi * 2 * BASE * t) * env * 0.12
            left += tone
            right += tone
    if effect == "noise":
        noise = rng.normal(size=len(t))
        kernel = np.exp(-np.arange(400) / 80.0)
        smooth = np.convolve(noise, kernel / kernel.sum(), mode="same") * 0.8
        left += smooth
        right += np.roll(smooth, 300)
    if effect == "resolve":
        fade = np.clip((length - local) / 10.0, 0, 1)
        left *= fade
        right *= fade
    return left, right


def render(timeline: list[tuple[int, float, float]], total: float, seed: int = 4) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(total * RATE)
    t = np.arange(n) / RATE
    mix = np.zeros((n, 2))
    cross = 3.0
    for act, start, end in timeline:
        lo = max(0, int((start - cross) * RATE))
        hi = min(n, int((end + cross) * RATE))
        tt = t[lo:hi]
        local = tt - start
        left, right = act_layer(act, tt, local, end - start, rng)
        env = np.clip((tt - (start - cross)) / cross, 0, 1) * np.clip(((end + cross) - tt)
                                                                         / cross, 0, 1)
        env = env * env * (3 - 2 * env)
        mix[lo:hi, 0] += left * env
        mix[lo:hi, 1] += right * env
    # Gentle room: a few decaying echoes.
    for delay, gain in ((0.031, 0.35), (0.047, 0.3), (0.089, 0.22), (0.137, 0.16)):
        d = int(delay * RATE)
        mix[d:, 0] += gain * mix[:-d, 1]
        mix[d:, 1] += gain * mix[:-d, 0]
    intro = np.clip(t / 4.0, 0, 1)[:, None]
    mix *= intro
    peak = np.max(np.abs(mix))
    return mix / peak * 0.32 if peak > 0 else mix


def write_wav(path: str, audio: np.ndarray) -> None:
    data = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(data.tobytes())


if __name__ == "__main__":
    spec = json.loads(open(sys.argv[1], encoding="utf-8").read())
    timeline = [(int(a), float(s), float(e)) for a, s, e in spec]
    total = max(e for _, _, e in timeline) + 1.0
    write_wav(sys.argv[2], render(timeline, total))
