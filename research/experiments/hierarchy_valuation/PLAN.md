# Hierarchy valuation program

Question under test: does one dimensionless number,

```text
epsilon^4 = (9/5) S*,   S* = (14/431) (1/(8 pi)),   epsilon = 0.219619476873...
```

arise from a primitive quantum/gravitational state **and** act as the
geometric valuation parameter of the physical Yukawa matrices,

```text
Y_f^phys = D_qL(epsilon) U_f D_qR(epsilon)   (up to derived unit cores and metrics)?
```

This plan is written so that each step either moves the claim toward a theorem
or kills a version of it cheaply. No step uses a measured mass or mixing angle
upstream. Observations enter only in the terminal comparison of gate G6.

## 1. Audit: what the equation currently contains

Source: migration draft, section 3.11, and `hierarchy_bridge_parameters` in
`Experimental_Draft_OneTheory.py`. The draft labels the whole section
`[B]`: a bridge target, not a result.

| Ingredient | Status in the repository | Content it can carry |
| --- | --- | --- |
| `rho = I/431` | No 431-dimensional space, group action or primitive action is defined anywhere | For **any** irreducible unitary Weyl--Heisenberg action the unique invariant state is `I/d` (Schur). Symmetry explains `1/d`, never `d = 431`. |
| `14/431` | `431` appears once in the draft with no derivation. In MinTOE/ASHA, `431 = 6*8*9 - 1 = dim(Lambda^2 X4 (x) V8 (x) End F3) - 1` and `14 = 2*7` (rank-two Majorana support times `dim C7`), not `dim G2` | `seed_audit.py`: `Lambda^2 X4 (x) V8` has **zero** Lorentz-invariant lines, so there is no canonical "scalar identity" to remove. Under flavor alone the traceless part is 384. The "minus one" has no invariant meaning. |
| `1/(8 pi)` | Defined as `alpha_G` at the reduced Planck energy | `G Ebar_P^2/(hbar c^5) = 1/(8 pi)` holds **by definition** of `Ebar_P`. It is a units convention, not a measured gravitational strength. |
| `9/5` | Draft MISSING_INPUT: "the nine operators U_g ... are not serialized". ASHA instead reads it as `3 * 3/5` (colour times inverse hypercharge normalization) | Any unit-norm tight frame of 9 vectors in `C^5` has frame constant `9/5`. Content only in "why 5". Two incompatible readings of the same factor across projects. |
| fourth root | Definition | Unexplained (see section 4). |
| second prefactor | `eta_Q^4 = (4/3) S*`, `eta_Q = 0.2037` | A second, independently chosen rational prefactor already exists for left-handed quarks. |
| exponent filters | `D_Q = diag(eta^3, eta^2, 1)`, `D_U = diag(eps^5, eps^2, 1)`, `D_D = diag(eps^2, eps, 1)` | Declared, not derived. `ord(Y_u) = (8,4,0)` holds only if `eta ≈ eps` (they differ by about 8%). |

Conclusion: every factor has a generic explanation that does not single out the
numbers used, and the meanings attached to 14 and 9/5 changed between ASHA,
MinTOE and OneTheory while the numbers stayed fixed (a signature of post-hoc
interpretation). The real conjecture is the **choice** `(d, D, g, n) = (5, 431, 14, 4)`
together with the identification `epsilon = valuation parameter`.

## 2. Evidential power of valuation-level agreement (terminal comparison only)

This assesses how much a match could prove. It is not an input to any
calculation.

* With dense O(1) unit cores, the draft exponents fit approximate running
  masses and CKM magnitudes about equally well for any `epsilon` between
  about 0.20 and 0.25. The implied cores span a factor of about 5 to 7 for every choice
  (at `epsilon = 0.2196`: 0.35 to 1.96; at 0.225: 0.32 to 1.74; at 0.25: 0.24 to 1.22).
* Keeping everything else fixed, every integer `D` from about 257 to 627 gives
  `epsilon` in `[0.20, 0.25]`. Valuations cannot tell 431 from 300 or 600.
* The fourth root gives 0.2196 and the fifth root gives 0.2974. Both lie in the
  tolerated range.
* The sharp reading `|V_us| = epsilon` is excluded at about 8 sigma
  (0.2250 ± 0.0007 against 0.2196). Any sharp test therefore needs derived
  unit cores.

**Consequence for the plan:** agreement of exponents can never be the evidence.
Only derived unit cores and several independent, precise estimators can confirm
the number.

## 3. New exact result: the frozen carrier's bundle modulus is a flavon with the wrong charges

`wall_valuation.py` (tests: `tests/integration/test_hierarchy_valuation_wall.py`).

1. All four completed holomorphic matrices (up, neutrino, down, charged lepton)
   have extension-degree pattern `[[-,0,0],[0,1,1],[0,1,1]]`. This is one
   anomalous-U(1) charge assignment: E family charge -1, F families 0, flavon
   (extension class) +1. The vanishing E-E entry is **forced**, because its
   predicted degree is -1. An independent first-row cofactor expansion
   reproduces all four certified determinants exactly.
2. The cover slope of `V1` is exactly `6 (j1 - j2)(j1 + j2 + 6 j3)`. Production
   geometry agrees with an independent Chow-ring calculation. The stability wall
   is the plane `j1 = j2` inside the Kähler cone. The stable side is `j2 > j1`,
   which contains both certified polarizations.
3. Near the wall the extension modulus is the anomalous-U(1) flavon of
   [Anderson--Gray--Ovrut](https://arxiv.org/abs/1001.2317).
   Its D-flat value obeys `|a|^2 ∝ xi_FI ∝ -mu(V1)`, which vanishes linearly in `j2 - j1`.
4. Over `C[[eps]]` with `a = eps * a_hat`, the invariant-factor orders are
   `(0,0,1)` in every sector: four constant 2x2 minors, and the determinant is
   exactly linear.

**Theorem (scoped, three premises listed in the report).** On the frozen
alternate carrier, the only bundle modulus produces two unsuppressed families
and one family suppressed by a single power, in all four sectors. It cannot
produce `(8,4,0)`, `(5,3,0)`, `(1,2,3)` or any deeper parametric hierarchy.

Premise status (gate G1). **Stability is now certified exactly**
(`wall_stability.py`): both constituents are stable on the whole wall
`J = (1,1,s)`, `s > 0`. Only the four lines with already certified Hom vanishing
ever reach nonnegative degree there, and only for `s <= 1/6`. The extension is
stable on the adjacent side `j2 > j1` and destabilized by `V1` across it. The
D-flat identification and the finite limit of split-bundle matter metrics are
standard results (Anderson--Gray--Lukas--Ovrut; Donaldson--Uhlenbeck--Yau
continuity toward the polystable graded object `V1 + V2`). They are cited, not
machine-certified.

**Physical reading.** On the stable side, the canonical texture is
`Y ~ [[0, r, r'], [c, eps, eps], [c', eps, eps]]`. Its two heavy masses are
`|r|` and `|c|`, the norms of the constant E-row and E-column, and the light
mass is `O(eps)`. The carrier therefore makes **two families heavy and one
light** in every sector. The observed quark and lepton spectra have one heavy
family. Matching them would need `|c|/|r| ~ 10^-2` from O(1) metric data, a
numerical accident rather than a mechanism.

Implication: if this carrier yields a parametric hierarchy at all, it must come
from Kähler- or complex-structure degenerations of the **metrics**, or from
worldsheet instantons. It cannot come from the holomorphic bundle data.

## 3b. The two-piece obstruction is structural on this geometry

`family_pieces.py` and `line_sum_screen.py` (tests:
`tests/integration/test_hierarchy_valuation_family_pieces.py`).

1. **Complete filtration of the frozen carrier.** Both Serre sublines have
   cover cohomology `(0,0,9,0)`. This comes from the actual two-equation
   Koszul complex, with a single supporting column, so no differential can act.
   Every family therefore injects into a quotient piece. In
   `0 < L1 < V1 < V1+L2 < V` the families occupy only two of the four graded
   pieces: one in `V1/L1` and two in `V/(V1+L2)`.
2. **No wall charge can separate the two.** Left- and right-handed fields both
   come from `H1(V)`, so they carry the same charge vector `(a,b,b)`. An
   exhaustive tropical computation over 1,377 charge/offset cases, with
   holomorphically forbidden entries, never gives three distinct orders.
   Three pieces with charges `(4,2,0)` give exactly `(0,4,8)`, the draft's up
   pattern, so the target needs three family-carrying pieces.
3. **Line-bundle SU(4) sums on the same quotient.** Line cohomology is
   computed from the exact Koszul E2 page with the actual Schoen equations,
   refusing any line where `d2` could act. The project's known
   higher-transgression line `(4,8,0)` is correctly refused. Any summand of a
   three-family sum without anti-families must have `chi` in
   `{0,-9,-18,-27}`, and `chi` needs no differential. This exact prefilter
   reproduces the unfiltered box-four result and makes larger boxes cheap.
   Of 1,649 descending lines with `|a|,|b|,|c| <= 8`, the only refused lines
   are `(k,-k,0)`, all with `chi = 0`. Every one of the 14 c1-trivial sums with
   27 cover families and no anti-families distributes families as `27` or
   `9 + 18`, never `9 + 9 + 9`. The set is unchanged from box six to box eight,
   and the result holds when every refused line is admitted optimistically
   as an acyclic summand.
4. **Leading textures.** Slot automorphisms `λ_a` with product one rescale a
   coupling `16_a 16_b 10_cd` by `λ_a λ_b λ_c λ_d`. A leading coupling
   therefore needs four distinct slots, and families couple only across
   slots. Of the 14 sums, four have the **cross texture** (two unsuppressed
   families, one massless) and ten have **no leading Yukawa** at all. None
   gives one heavy family.

5. **Partial splits.** Up to degree eight there are exactly four descending
   one-family lines: `(-1,1,1)`, `(-1,4,0)`, `(1,-1,1)` and `(4,-1,0)`. Neither
   frozen constituent plus two lines (`W + L1 + L2`, structure group
   `S(U(2) x U(1) x U(1))`) can place one family in each of three slots.

**Literature cross-check.** For the minimal heterotic standard model on the
same SU(4)/Schoen ℤ3×ℤ3 geometry,
[Braun--He--Ovrut](https://arxiv.org/abs/hep-th/0601204) found by different
methods (Leray selection rules) that one of the three families is naturally
light. That is the same two-heavy/one-light pattern. The results above give
it a structural cause (one anomalous U(1) plus a two-piece filtration) and
show it recurring across every construction screened here.

**Consequence.** On the Schoen ℤ3×ℤ3 quotient, every abelian wall/split
mechanism examined fails in one of two ways. It gives two heavy families and
one light, or it gives no leading coupling. The observed one-heavy hierarchy
must therefore come from non-split bundle data away from walls, from
Kähler-metric hierarchies, or from worldsheet instantons. The prime instanton
candidates are the exceptional sections below. This is scoped to the
line lattice box `|a|,|b|,|c| <= 8` of the quotient's Picard group (rank 3)
and to the frozen carrier. It is not a theorem about
every SU(4) bundle.

## 4. "Why four?" as a discriminating question, not a choice

Each candidate below is a hypothesis with a computable test on whichever
carrier survives gates G2 and G3.

| Candidate | Mechanism | Test |
| --- | --- | --- |
| `eps^2 ∝ xi_FI` | D-flatness gives `\|flavon\|^2 ∝ xi`, so `eps^4 ∝ xi^2` | The exponent relating flavon VEV to the slope polynomial in a derived wall regime |
| rank-four determinant | `S(U(1)^4)` split of an SU(4) bundle, product of four flavon factors | Charge lattice of a full-flag split carrier |
| quartic Kähler data | Slopes are quadratic in `J`, the volume is cubic | Scaling of matter metrics along degenerations (G2) |
| instanton action | `eps^4 = exp(-S_inst)`. Concrete candidates are the 81 exceptional sections `sigma x sigma'` (9 on the quotient). Their ambient class is `x^2 u^2`, so their area is exactly `J.C = j3`. `V` restricts trivially to them, so the spin-twisted zero modes vanish (`ALTERNATE_SECTION_CURVE_RESTRICTIONS_NOTE.md`) and their Pfaffians are not forced to zero. On the hidden-compatible wall region `j3 < (11/12) j1` they are the least suppressed instantons. Through the Green--Schwarz shift they can carry anomalous-U(1) charge and generate U(1)-forbidden entries. `eps^4 = e^{-S}` would mean `S ≈ 6.06`. | Pfaffian normalization and U(1) charge of these instantons, then their contribution to each texture entry. They cannot lift the two unsuppressed E-F masses, so they test only the light entries |

Kill rule: if the derived relation in the surviving channel is not a fourth
power, this form of the equation dies, whatever its numerical agreement.

## 5. Gates (cheapest discriminating step first)

| Gate | Work | Inputs already certified | Pass | Kill |
| --- | --- | --- | --- | --- |
| **G0** done | Audit, evidential power, wall valuation theorem | All four holomorphic matrices, Schoen geometry | Exact | — |
| **G1** stability done | Certify the three premises: constituent stability at `j1=j2`, `V` stability on `j2>j1` near the wall (reuse `retained_slope_stability` line-Hom machinery), D-term normalization | Constituent presentations, Hom engines | Theorem promoted | A premise fails: restate the scope |
| **G2** weeks | Asymptotic matter-metric valuations along declared Kähler rays `J(s)` inside the stable cone, using localization at large flux ([Blesneag et al. 2018](https://arxiv.org/abs/1801.09645)); that method is abelian, so its extension to these non-abelian constituents is itself part of the gate | Constituent line data, section bases | Family-dependent exponents | Uniform exponents: the carrier has no parametric hierarchy, so retire it as a flavor-hierarchy carrier (not as an SU(4) carrier) |
| **G3** started: line-sum box screen negative (section 3b) | Carrier design theorem. Families from one graded piece share a U(1) charge, so three distinct valuations need the three families to come from **three distinct graded pieces** (a filtration with at least three steps, for example `L1 + L2 + W` or a full four-line flag). The frozen carrier has two (one family in `V1`, two in `V2`), which is exactly why it gives `(0,0,1)`. Fix the U(1)^k charge patterns needed for the target valuations, with the Wilson-line split of each 16. Search the computable-carrier category for SU(4) bundles near multi-wall split loci with these charges | Computable-carrier engines, Tier A/B/C contracts | A stable carrier with the required charge lattice and spectrum | No such carrier in a declared finite category: scoped no-go |
| **G4** | Express `eps` as a derived function of moduli in the surviving channel; derive the power `n` | G2/G3 output | `n = 4` derived | `n ≠ 4`: kill the equation in this form |
| **G5** | Shared hidden sector and vacuum: stabilized moduli value | Existing blocker (priority 8.5) | Moduli fixed without fitting | Unstabilized: the value test stays open |
| **G6** | Blind test. Hash-register every `eps` estimator and unit-core derivation **before** metric/vacuum execution. Then compare at least three independent estimators with each other and with 0.21962 | Physical Yukawas from metrics plus G5 | Mutual agreement at about 1% with no tuning | Disagreement beyond the derived error bars |
| **G7** | Origin: typed primitive action producing the 431-dimensional carrier, the G2 channel, and a convention-free gravitational quantity (for example `M_c^2/Mbar_Pl^2` from the heterotic matching) replacing `1/(8 pi)` | None yet | Theorem | No typed construction: the equation stays a bridge target |

## 6. Validation of this plan

* **Discriminating:** every gate has an outcome that changes the next action.
  G0 already removed one whole channel.
* **No leakage:** neither the value 0.2196 nor any observation enters G1 to G5.
  Comparison happens only in G6, after registration.
* **Cheapest first:** G1 and G2 are exact or asymptotic and need no Ricci-flat
  sampling. The current top project priority, metric convergence for this
  carrier, still matters for normalized Yukawas. G0 shows it cannot by itself
  create a parametric hierarchy from the bundle modulus. Run G1 and G2 before
  committing to a large sampling campaign aimed at flavor.
* **Pre-mortem:** (a) the premises of section 3 fail. G1 detects this, and the
  statement is restated rather than silently kept. (b) Hierarchies come only
  from O(1) numerical accidents. G2 detects this as uniform exponents.
  (c) A surviving channel fits valuations but not values. G6 detects this, and
  section 2 already says valuations are not evidence.
* **What would be extraordinary evidence:** derived unit cores, at least three
  independent estimators agreeing at the percent level with 0.21962 and no
  tuning, and a registered blind prediction of something not yet measured
  (for example a neutrino-sector quantity), followed by the origin theorem G7.

## 7. Relevant external results (`github.com/openai/math`, 722 manuscripts)

None addresses heterotic flavor, the number 431, or this equation. Peripheral
results that bear on specific gates:

* 055, numerical Bridgeland stability at large volume on threefolds with trivial
  canonical class. This is the framework for wall-crossing as `J` moves, relevant to G1 and G2.
* 050, ample bundles without Griffiths-positive metrics. Positivity of a metric
  cannot be assumed. The continuum bound `tau <= 9/2` uses section-induced
  metrics, which are positive by construction, so it is unaffected.
* 038, Fujita freeness. For a CY threefold, `4L` is globally generated for ample
  `L` (dimension three was already known). This may help choose smaller twists
  with fewer sections in the metric program.
* 266, exactly three MUBs in dimension six. Weyl--Heisenberg context for G7.
  431 is prime, so the full set of 432 MUBs exists. This does not explain 431.
* 270, the unique BFSS threshold bound state. Rigorous quantum-gravity support
  for the UV duality web, not for this equation.
* 280 and 282, unitary VOAs to conformal nets, and scale to conformal symmetry
  in 4D QFT. Foundational context for the Genesis-to-QFT contract.
