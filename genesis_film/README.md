# Genesis: a film of the whole of reality, from the One to the horizons

A single, continuous [Manim](https://www.manim.community/) animation. It
starts at the unified moment and follows, without one cut, how everything
emerges: a quantum seed, one vibrating string, a hidden six-dimensional
shape, the forces and three families of matter, inflation, the hot soup, the
Higgs field, protons, nuclei, the first light, the cosmic web, a galaxy and
the horizons of the visible universe.

**Watch:** [`output/genesis.mp4`](output/genesis.mp4). It runs 7 min 19 s at 1280×720 and 30 fps, with a soft ambient soundtrack.

**Plan:** [`DIRECTOR_PLAN.md`](DIRECTOR_PLAN.md) describes the acts, the joins
between them and every gap that had to be filled.

## Watching it

Anyone can follow the **centre**: it always shows the thing itself, drawn
from its real formula, and the **subtitle** says in one plain sentence what
is happening. If you know the physics, the **left panel** gives the formulas
and numbers, and the **inset** on the right opens when numbers are shaping
the picture. The **cosmic clock** at the bottom runs on a logarithmic scale
from t → 0 to 13.8 billion years.

The **badges** at the bottom right separate reality from doubt:

| Badge | Meaning |
| --- | --- |
| 🟩 PROVEN | A mathematical theorem. |
| 🟦 MEASURED | An experiment or observation. |
| 🟪 ESTABLISHED | Tested standard theory. |
| 🟣 ONETHEORY | Computed exactly in this repository. |
| 🟧 SELECTED | A chosen realization, true only if the choice is right. |
| 🟨 HYPOTHESIS | Proposed but not tested. |
| 🟥 ONE POSSIBLE REALITY | A plausible picture that fills a gap so the story stays continuous. |

## What is drawn from what

* **E8.** All 240 roots in their 30-fold Coxeter-plane projection and their
  exact split into SU(4) × Spin(10) (12 + 40 + 60 + 64 + 64).
* **Matter.** The 16 weights of one family are placed by their real
  isospin and hypercharge, which gives the correct charges for Q, u^c, d^c,
  L, e^c and ν^c.
* **Geometry.** The real Hesse pencil x³ + y³ + 1 = 3λxy, with its base
  points and the singular λ = 1 fibre. Tori and two torus families over a
  sphere stand for Schoen's Calabi–Yau.
* **Cosmos.**
  * one Gaussian field with the measured tilt n_s = 0.9649;
  * a Mexican hat with λ = m_H²/2v² = 0.129;
  * BBN numbers: n/p → 1/7 and Y = 0.25;
  * the 2.7255 K blackbody;
  * Zel'dovich motion with δ = ∇² of the same field;
  * a logarithmic spiral galaxy with a flat rotation curve;
  * flat ΛCDM ages and horizons (H₀ = 67.4, Ω_m = 0.315), giving 13.79 Gyr,
    46.1, 14.5 and 16.7 Gly.

The inflation ripples, the CMB, the cosmic web and the CMB shell at the
horizon are **one and the same field**, so you can follow the same pattern
from 10⁻³² s to today.

## Files

| File | Role |
| --- | --- |
| [`physics.py`](physics.py) | NumPy formula engine: E8, families, Hesse curves, strings, random fields, ΛCDM, the Higgs potential, galaxies. |
| [`cosmos.py`](cosmos.py) | NumPy painters for acts 6–14: inflation, the particle soup, CMB, web, galaxy and horizons, on one primordial field. |
| [`stage.py`](stage.py) | The layout: title, centre, formulas, inset, evidence badges, cosmic clock. |
| [`visuals.py`](visuals.py) | Manim builders: E8 diagram, glow points, tori, spheres, the Dynkin diagram, live images. |
| [`genesis.py`](genesis.py) | The `Genesis` scene, acts 1–5. |
| [`late_acts.py`](late_acts.py) | Acts 6–14 and the finale. |
| [`render.sh`](render.sh) | Renders act groups in parallel, joins them and adds the soundtrack. |
| [`soundtrack.py`](soundtrack.py) | Synthesizes the ambient score from the act timeline. Chords cross-fade, so the sound never jumps either. It sets the mood only and carries no data. |

Tests:
[`tests/test_genesis_film.py`](tests/test_genesis_film.py).
They check the formulas, and they check that the painters hand over on
identical pixels, so the film has no jumps.

## Rendering

You need Manim Community 0.19 or later (the Cairo renderer; LaTeX is not
needed), its system libraries (Cairo, Pango) and ffmpeg.

```bash
pip install manim
cd genesis_film
./render.sh                                   # 1280x720, 30 fps → output/genesis.mp4
GENESIS_ACTS=3-5 manim -ql genesis.py Genesis # quick look at acts 3..5 only
```
