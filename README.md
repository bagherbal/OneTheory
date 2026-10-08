# OneTheory

OneTheory is a code-first scientific engine for building a computational model of reality from mathematically defined objects, verified physical laws, executable state transitions, and terminal observables. The paper and the current standalone verifier are migration sources; this repository is not organized by paper chapters.

Reality is assembled from lower verified components. Missing physics remains missing: an unresolved prerequisite must remain explicit and must never be replaced by a guessed coefficient, synthetic matrix, fallback value, or speculative bridge. In particular, no native-origin interpretation is allowed to masquerade as a connection to the heterotic carrier. Failed routes remain research results or killed hypotheses, not production domains.

## The answer so far, in one page

OneTheory asks how everything observed could arise from one primitive and be
computed without fitting. The table shows how far the chain is derived **today**.
Each status is backed by code, tests and content-addressed artifacts.

| Layer | What OneTheory has | Status |
| --- | --- | --- |
| **Genesis (the "1")** | A proved constraint: no finite characteristic-zero algebra carries `AB - BA = λ I` with `λ ≠ 0`, so canonical quantum phase space cannot be a finite exact object. Finite CAR (fermionic) systems and positive characteristic evade it. | Constraint **PROVED**. Derivation of quantum postulates, causality, gravity and constants **BLOCKED**. |
| **Quantum gravity (UV)** | Ten-dimensional E8×E8 heterotic string, recorded as convention-frozen law objects (metric, dilaton, B/H, gauge fields, torsionful curvature, Green–Schwarz/Bianchi data). Gravity is quantized here as the massless spin-two closed-string state. Four-dimensional Einstein gravity is its low-energy limit. | **SELECTED** as the conditional realization, not derived from Genesis. |
| **Space** | Schoen Calabi–Yau threefold with a free ℤ3×ℤ3 quotient: exact cover, quotient, Cox presentation, intersection ring and deck action. | Exact; published geometry input. |
| **Gauge forces and matter** | A rank-four SU(4) bundle family over `P¹` (`alternate-i6-ray-0-1-P1`). It is locally free, descends to the quotient, has trivial determinant and is slope-stable. Wilson lines give exactly three families with right-handed neutrinos, one Higgs pair, no anti-families and no massless colour triplets. | **COMPUTED** from chain-level data. Three families and one Higgs pair are selection constraints, not predictions. |
| **Yukawa couplings** | All four 3×3 holomorphic matrices (up, down, charged lepton, Dirac neutrino) are exact over `Q(ω)[a0,a1]`. All share one structure, explained below. Each has rank at least two, and all four have rank three on a common open set. | Holomorphic **COMPUTED**. Physical (normalized) Yukawas **OPEN**. |
| **Metrics** | 5,345-section invariant basis, global generation, an exact integration measure, certified roots and a 2,048-point sample cloud. The H1 anomaly is diagnosed as an in-sample leverage effect: mean leverage 87%, effective training size 1,258 below the 1,337 threshold, curvature blow-up 212× on training points only, and better than H0 out of sample. | **OPEN**. A registered prediction for the 8,192-point training run decides the diagnosis. |
| **Hidden sector, instantons, vacuum** | Necessary hidden HYM chamber `4 j1 + 7 j2 − 12 j3 > 0`; exceptional-section zero modes. | **OPEN**: no hidden bundle, Pfaffian normalization or stabilized vacuum. |
| **Observables** | Reserved for blind terminal comparison. | No prediction yet; zero fitted inputs. |

OneTheory therefore does **not** yet derive reality from one primitive. It is
an exact, falsifiable chain from a selected quantum-gravitational theory down
to complete holomorphic Yukawa matrices. Its open links are named, and nothing
in it is fitted.

## How reality emerges in this framework

```text
1  ──(open: Genesis → UV)──▶  quantum gravity: 10D E8×E8 heterotic string
                                │ compactify on the Schoen CY / (ℤ3×ℤ3)
                                ▼
                         4D spacetime + gravity (Einstein limit)
                                │ SU(4) ⊂ E8 visible bundle, stable
                                ▼
                    SO(10) ──(ℤ3×ℤ3 Wilson lines)──▶ Standard Model gauge group
                                │ H¹(V), H¹(∧²V)
                                ▼
                    3 families + 1 Higgs pair (exact cohomology)
                                │ cubic products of cohomology classes
                                ▼
          holomorphic Yukawas (exact) ──(open: metrics, vacuum)──▶ masses, mixing, CP
```

The Genesis moment is the top arrow. The project has turned it into a precise
open problem rather than a narrative. It must produce quantum phase,
Lorentzian causality, gravitational coupling and the heterotic UV without
importing them. The proved finite-algebra no-go says where such a derivation
cannot start.

### Watch it: the Genesis film

[`genesis_film/`](genesis_film/README.md) is a single continuous Manim
animation of this whole chain, joined to established cosmology: from the
quantum seed, through the string, E8, Schoen's Calabi–Yau and three
families, to inflation, nuclei, the first light, the cosmic web, a galaxy and
the horizons. The centre always shows the actual shape computed from its
formula. A side panel shows the equations. Colour-coded badges mark every
scene as proven, measured, established, OneTheory-computed, selected,
hypothesis, or one possible reality. Video:
[`genesis_film/output/genesis.mp4`](genesis_film/output/genesis.mp4).

## The best current explanation of the Yukawa couplings

`research/experiments/hierarchy_valuation` proves that all four exact
holomorphic matrices are controlled by **one hidden symmetry**.

1. **One anomalous U(1).** The visible bundle is a nonsplit extension
   `0 → V1 → V → V2 → 0`. One family comes from `V1` (E) and two from `V2` (F).
   In every sector the powers of the extension parameter are
   `[[–,0,0],[0,1,1],[0,1,1]]`. That is exactly the charge pattern E = −1,
   F = 0, extension class = +1. The vanishing E–E coupling is forced by the
   symmetry, not imposed.
2. **Where the symmetry lives.** The slope of `V1` is
   `6 (j1 − j2)(j1 + j2 + 6 j3)`, so the stability wall is the plane `j1 = j2`
   in the Kähler cone. Both constituents are proven stable on the **whole** wall.
   The extension is stable just beside it (`j2 > j1`) and unstable across it.
   At the wall the U(1) becomes a 4D gauge symmetry, and the extension modulus
   is its Froggatt–Nielsen flavon, with VEV² set by the distance to the wall.
   The visible wall region meets the necessary hidden-sector chamber for
   `j3/j1 < 11/12`.
3. **The texture this forces.** Over the flavon's power series, every sector
   has invariant-factor orders `(0,0,1)`: two families unsuppressed and one
   suppressed by one power of the flavon.

4. **Why it cannot be repaired by more walls.** Both Serre sublines of the
   bundle carry no family cohomology, so the three families occupy only two
   pieces of the bundle's complete filtration: one family in one piece, two in
   the other. No combination of wall symmetries can then give three mass
   levels. An exact screen of every three-family SU(4) line-bundle model on
   the same quotient (all 1,649 descending line classes with degrees up to 8)
   gives the same split, `1 + 2` or `3`,
   never `1 + 1 + 1`. Each such model either has the "cross" texture (two
   heavy, one massless) or no leading Yukawa at all.

Consequence: this carrier explains the **structure** of its Yukawa couplings
exactly, but its bundle modulus makes two families heavy and one light. The
observed spectrum has one heavy family. This agrees with the independent finding of
[Braun, He and Ovrut (2006)](https://arxiv.org/abs/hep-th/0601204) that the
minimal heterotic standard model on the same geometry makes one family
naturally light. OneTheory now explains why: one anomalous U(1) and a
two-piece family structure. On this geometry the abelian route to a realistic
hierarchy is closed in every case examined. The observed one-heavy pattern
must come from non-split bundle data away from walls, from Kähler-metric
hierarchies, or from worldsheet instantons. The least-suppressed
instantons, on the 81 exceptional curves of area exactly `j3`, carry zero flux
of the wall U(1). They can only
correct couplings that are already allowed, so they cannot change this
texture. This is now a sharp, testable design criterion (gate G3 in
[`hierarchy_valuation/PLAN.md`](research/experiments/hierarchy_valuation/PLAN.md)).

## The proposed universal hierarchy number, audited

The predecessor projects ([ASHA](https://github.com/bagherbal/asha-engine),
[MinTOE](https://github.com/bagherbal/MinTOE)) and the migration draft propose

```text
ε⁴ = (9/5) · (14/431) · 1/(8π),   ε = 0.219619476873…
```

as one number linking quantum state, exceptional geometry, gravity and flavor.
OneTheory records it as a **bridge target** and tests it without letting it
enter any calculation:

* `431 = 6·8·9 − 1` removes a "scalar identity" from `Λ²X₄ ⊗ V₈ ⊗ End(F₃)`.
  An exact invariant count shows `Λ²X₄ ⊗ V₈` has **no** Lorentz-invariant line,
  so no such identity exists. Under flavor alone the traceless part is 384.
* `1/(8π)` is gravity's coupling at the reduced Planck energy, true by
  definition of that energy: a units convention, not a measurement.
* The readings of `14` (Majorana support `2·7` versus `dim G2`) and `9/5`
  (colour/hypercharge versus a nine-operator tight frame) changed across
  projects while the numbers stayed fixed.
* With order-one coefficients, exponent patterns fit equally well for any
  `ε ≈ 0.20–0.25`. The sharp reading `|V_us| = ε` is off by about 8σ.

The full MinTOE calculation is now kept in a tested
[evidence ledger](research/experiments/mintoe_ledger/README.md) as a
**registered hypothesis**, not retired. About 20 observables lie within ~1σ.
The 7th-digit matches carry no evidence: m_τ tracks a superseded average, v
uses a rounded Planck mass, and the integer S-corrections form a positional
number system. Several things do survive:

* the cores `ln(MbarP/v) ≈ 12π − √3/2` and
  `ln(v/(√2 m_τ)) ≈ 4π/3 + 3/10 + 7/72`, each a nominal ~2% post-hoc
  coincidence;
* the Koide–Brannen relation (Q = 2/3 and phase 2/9, within m_τ errors);
* a hash-registered prediction set (δ_CP = 270°, m1 = 0, Σm_ν = 58.8 meV,
  m_ββ = 2.24 meV, Δm², m_H, ...).

Upcoming experiments will test that set. A derivation of the cores is the
open theory target.

## What completes the theory

These are ordered by how cheaply they discriminate. Full detail is in
[`PLAN.md`](research/experiments/hierarchy_valuation/PLAN.md) and the
[research map](research/experiments/scientific_genesis/RESEARCH_MAP.md).

1. **Flavor origin (G2/G3).** The abelian route is closed on this geometry in
   every case examined, and the least-suppressed instantons are U(1)-neutral.
   What remains is matter-metric scaling along Kähler degenerations, the bundle
   far from its walls, or a different carrier or geometry.
2. **Metrics.** Controlled Ricci-flat/HYM convergence with useful error bounds.
   [`metric_sampling`](research/experiments/metric_sampling/README.md) shows
   the H1 anomaly is in-sample leverage, not geometry, and registers a
   falsifiable prediction for the pending 16,384-point population.
3. **Hidden sector and vacuum.** A hidden bundle in the necessary chamber,
   anomaly cancellation, and a stabilized common vacuum fixing all moduli.
4. **Blind comparison.** Hash-registered predictions of masses, mixing and CP,
   compared with data only afterward.
5. **Genesis → UV.** A typed primitive that produces quantum phase, causality,
   gravity and the heterotic structure.

## Repository architecture

Production code lives under `src/onetheory` and may be consumed by `research`; production never imports research. Exact mathematics is kept separate from controlled numerical work, and measured observables are terminal comparison and falsification data rather than geometry or vacuum selectors. `reality.py` is the sole composition root and may report an incomplete model when required dependencies are unresolved.

Simulation consumes the same physical laws and immutable state objects as scientific computation. The established four-dimensional kernel exposes parameterized spacetime, fields, gauge, matter, quantum, and Einstein laws, while the engine provides controlled textbook benchmark trajectories for external animation consumers without introducing a second physics implementation or rendering dependency.

The production reference branch is the published one-Higgs heterotic Schoen carrier. Its executable slice carries the exact observable split-wall ledger, local/open-locus admissibility certificates, scoped degree-three and order-five exclusions, and a finite holomorphic flavor frontier on which the lawful tree-level up matrix is exactly zero. The ten-dimensional heterotic law records, symbolic K/W/f/D slots, and the fail-closed prerequisite graph never treat a topological identity as a solved connection, metric, or coefficient. All Yukawa, metric, and vacuum results above belong to the separate, conditional research carrier and are not promoted into production.

## Dependency direction

```text
core → math → physics → models
              ↘
                engine
models + engine → reality
production → verification
production → research
```

The final two arrows mean “inspected or consumed by,” not reverse imports: verification inspects production from outside, and research may consume production while production must not import research.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
pytest
```

The original DOCX paper and standalone Python program remain unchanged at the repository root as migration sources.
