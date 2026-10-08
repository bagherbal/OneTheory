# Genesis: director's plan

One continuous shot, from the unified moment to the cosmic horizons. It has
no cuts. Every state is turned into the next by a transformation the eye
can follow, and every shape on the centre stage comes from a formula in
[`physics.py`](physics.py) or [`cosmos.py`](cosmos.py).

## The screen

| Zone | What it shows |
| --- | --- |
| Top | Title of the moment and one plain-language sentence for viewers with no physics background. |
| Centre (big) | The thing itself, drawn from its formula: roots, curves, tori, fields, particles, the web, a galaxy. |
| Left (small) | The formulas and numbers, for viewers who want them. |
| Right, top | An inset box that opens when numbers are shaping the picture: masses, spectra, curves. |
| Right, bottom | Evidence badges: where each scene comes from and how sure we are. |
| Bottom | The cosmic clock, logarithmic, from t → 0 to 13.8 billion years. |

### Evidence colours

| Badge | Meaning |
| --- | --- |
| 🟩 **PROVEN** | A mathematical theorem. |
| 🟦 **MEASURED** | An experiment or observation. |
| 🟪 **ESTABLISHED** | Tested standard theory. |
| 🟣 **ONETHEORY** | Computed exactly in this repository. |
| 🟧 **SELECTED** | A chosen realization, conditional. |
| 🟨 **HYPOTHESIS** | Proposed but untested. |
| 🟥 **ONE POSSIBLE REALITY** | A gap filled with a plausible picture so the film stays continuous. |

## The acts and the joins between them

| # | Moment (clock) | Centre stage | How it joins the next act |
| --- | --- | --- | --- |
| 1 | The One: a quantum seed (t → 0) | A point of light that is really a Gaussian vacuum cloud, with its Wigner rings. Inset: the trace proof that `[x,p] = iħ` has no finite solution. | The ½-probability ring becomes the string. |
| 2 | One vibrating string (Planck time) | A closed string with left and right movers. Then the graviton: a pure quadrupole note, shown beside LIGO's ring of test masses. Then the 240 E8 roots stream out of the string and form the Petrie projection. | The E8 crystal shrinks into the inset; the string stays at the centre. |
| 3 | Ten dimensions, a hidden shape | A box with glued edges and winding strings (string gas). Windings annihilate, three directions grow and the rest stay curled. One curled circle is the oval of a Hesse cubic. Sweeping λ shows the singular fibre at λ = 1. The oval becomes a cycle on a torus, and two torus families over a sphere make Schoen's Calabi–Yau. A ℤ3×ℤ3 orbit of 9 points merges into one point. | Four SU(4) strands wrap the torus. |
| 4 | The shape chooses the forces (GUT era) | The geometry and the E8 crystal swap places. 12 SU(4) roots are absorbed, 40 Spin(10) roots survive, 60 become Higgs-like (6,10) and 128 become matter (4,16). Inset: the extended Dynkin diagram with node 6 cut. | The 16 matter roots with one SU(4) label light up. |
| 5 | Matter: three families | The 16 roots fly onto the (T₃, Y) charge chart of one family. Wilson lines colour it into Q, u^c, d^c, L, e^c and ν^c. It is copied into three families (27/9 = 3), and glow sizes show the measured masses. Inset: OneTheory's Yukawa texture. | The families shrink into the inset as space itself comes on stage. |
| 6 | Inflation (10⁻³⁶ → 10⁻³² s) | A physical zoom. Each octave of ripples is born as twinkling jitter at the horizon, freezes and is stretched, while a comoving grid flies apart. Then the view widens until it is exactly the primordial pattern P (n_s = 0.9649). | The same pixels are reused as the hot soup's background. |
| 7 | Reheating | The pattern heats up and a soup of every particle of act 5 appears, slightly denser where the ripples were higher. | The soup keeps running underneath the Higgs field. |
| 8 | The Higgs field settles (9 × 10⁻¹² s) | The Mexican hat V(φ,T) with λ = 0.129 changes shape as T falls through 159.5 GeV, and the ball rolls into the trough. Inset: W, Z, H and top masses growing. | The hat fades and the soup returns. Heavy particles decay. |
| 9 | Confinement (2 × 10⁻⁵ s) | Quark–antiquark pairs annihilate in flashes. Survivors lock in red-green-blue triplets. Inset: a rotating proton, 9 MeV of quarks inside 938 MeV. | The nucleons stay. |
| 10 | The first three minutes | Neutrinos fly free and n → p conversions freeze n/p near 1/7. Positrons annihilate. Two helium-4 nuclei form from 32 nucleons (Y = 0.25). Inset: abundances. | Electrons remain free. |
| 11 | First light (372,000 yr) | A glowing fog. Electrons settle onto nuclei, the fog clears and its pattern turns into the CMB map: the same ripples. Inset: the 2.7255 K blackbody. | The CMB map is reused as the start of the web. |
| 12 | The cosmic web (0.1–1 Gyr) | The CMB light fades and matter moves by Zel'dovich, x = q + D ψ(q), with δ = ∇² of the same ripples. Filaments and knots form and the first stars light up. Inset: D(t) with a clock-driven marker. | We dive into one knot. |
| 13 | A galaxy | Zoom into the knot. A gas cloud spins into a two-armed logarithmic spiral (p = 12°). The Sun appears at 8.2 kpc. Inset: flat and Keplerian rotation curves. | We zoom back out through the same knot. |
| 14 | The horizons (13.8 Gyr) | The galaxy becomes a point in the web, and the web becomes a smooth disk. The particle horizon (46.1 Gly) is ringed by the CMB shell, made from the same ripples. The Hubble sphere (14.5 Gly) and event horizon (16.7 Gly) are drawn. Inset: a(t) with acceleration from 7.7 Gyr. | Finale: the colour key and the open problems. |

## Where the gaps are filled (and labelled)

* **Seed → string.** OneTheory's Genesis → UV link is open. The film shows
  the vacuum ring becoming the string and labels it *one possible reality*.
* **Why three large dimensions.** It uses the string-gas idea
  (Brandenberger–Vafa 1989), labelled *hypothesis*. Only 2 of the 9
  directions are drawn.
* **Real slices.** The Hesse curves are real 2D slices of complex curves,
  labelled as such.
* **Inflation.** It is shown for 7.8 e-folds, not about 60, and labelled.
* **Reheating temperature and the matter–antimatter excess.** Both are
  unknown and labelled. Survivors are shown about 10⁸ times too often so
  they are visible.
* **Acoustic peaks and the CDM transfer.** These are shapes, not a Boltzmann
  code. The docstrings say so.
* **Dark matter and dark energy.** They are named as hypotheses. The hidden
  E8′ sector is offered only as one idea.

## Why there are no jumps

* Every updater reads a `ValueTracker`; no updater reads wall time. So a
  skipped section and a rendered section end in the same state.
* One live image carries acts 6–14. Its painters hand over only where they
  paint identical pixels, and
  [`tests/test_engine.py`](tests/test_engine.py)
  checks those seams:
  * inflation → widening;
  * widening → soup;
  * soup → CMB;
  * web zoom-in → zoom-out.
* Text in the HUD fades out before the new text fades in, so lines never
  overlap.
