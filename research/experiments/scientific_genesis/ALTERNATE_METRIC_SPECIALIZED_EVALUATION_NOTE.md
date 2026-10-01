# Regular-factor specialization of the universal section evaluator

The frozen carrier and its 5,345-vector universal section basis are unchanged.
This experiment evaluates that **same** basis; it does not construct another
bundle, select extension coordinates, or simplify the physical laws.

## The computational deficiency

The original local evaluator obtains valid values by constructing full-cover
cochains and independently checking the universal corrections. Its four
spanning probes required large intermediate cochains. Repeating this expansion
for every column at every metric sample is unnecessary: the raw homotopy
depends on negative Laurent support, not positive exponent magnitudes.

The actual outer coefficients are polynomial in every `u` coordinate. Every
actual target object arrow is polynomial in both plane factors, and the
Koszul equations are polynomial. Every actual target component has nonnegative
second-plane ambient degree. The code checks all these premises rather than
asserting that arbitrary Čech complexes permit specialization.

## Naturality over the regular polynomial coefficient ring

Consider the part of the actual target complex whose `u` Laurent support is
empty. The raw Čech differential and homotopy have constant integer matrices
on the `u` cover cells in this sector, independently of the `u` exponents.
Their signs still depend on the same structural parity. Consequently they
are linear over `Q(omega)[u0,u1,u2]` on this sector. The object and equation
arrows preserve it because their `u` exponents are nonnegative.

For a supplied exact homogeneous coordinate tuple `u`, coefficient evaluation
is a ring homomorphism. It therefore commutes with the raw homotopy and with
the full perturbation **after the latter's polynomial coefficients have also
been evaluated**. In particular it commutes with the entire certified finite
series `sum(j=0..4)(-h Delta)^j h` in this regular sector. The finite filtration
bound is unchanged. This statement does not apply to a Laurent pole, a
changing negative-support sector, or an arbitrary substitute coefficient.

The implementation encodes an evaluated coefficient at ambient `u` degree
`d` by the dummy monomial `u0^d`. This preserves the original component,
Koszul grade, cover cells, and structural signs when using the existing
homotopy. **It is internal degree bookkeeping, not a physical cochain or a
choice of a bundle frame.** When perturbing an encoded source of degree `d`,
the original operator first produces exponents `(d,0,0)+m`. Only the actual
arrow monomial `m` is evaluated; the resulting degree is again encoded by
its new dummy monomial. Grouping by source component makes `d` unambiguous.

Tests compare this path with direct evaluation *after* the original full
perturbation on actual outer/source operator units. They also compare both
orders of raw homotopy and specialization. The existing independent
negative-support operator certificate supplies the premise that the raw
integer matrices genuinely depend only on support and parity. The ring-linear
derivation above covers all positive magnitudes, not just tested examples.

## Three separate deck channels

The universal correction is the explicitly normalized
`-(1+P+P^2) h'(E_i s)/3`. Specialization is performed in three separate
channels, at `u`, `P(u)`, and `P^2(u)`, using the **actual** monomial
coordinate substitutions and their Eisenstein phases. This evaluates the
polynomial part of each pulled-back coefficient correctly.

Cells, `x/p` monomials, homogeneous object frames, and Koszul equation units
are still pulled back by the original full deck action. Before doing so, the
artificial dummy monomial's deck scalar is removed: its numerical coefficient
already contains the real `u` pullback. Its dummy numerator is then ignored
in the final local evaluation. The declared original chart line-frame
denominators are retained exactly.

Without this correction the dummy `u0^d` would introduce a second, spurious
deck phase. A mutation attack deliberately omits the correction and fails
comparison with an independently archived full-cochain probe. Exact
projective rescaling of all three homogeneous coordinate groups also leaves
the resulting properly framed column unchanged.

A separate exact point uses `x=(1,1,1)`, `u=(1,-1,0)`, `p=(1,0)` on chart
`(0,0,0)`. The actual V2 subline section numbered 2,670 has a nonzero value
there. Its constant and both outer-correction coefficients agree with the
original full-cochain evaluator. All three deck channels have no zero `x`
coordinate, so this comparison does not rely on first-plane pruning. It also
tests regular `u` specialization at a zero coordinate and the other P1 chart;
it is still an algebraic check, not geometric sampling or a vacuum selection.

## Zero-coordinate pruning is a functional identity

For one deck channel, let `x_i` map to a zero coordinate of the supplied
physical evaluation point. A cochain monomial with positive exponent of
`x_i` cannot contribute to the final point value. The raw homotopy preserves
that exponent; every actual perturbation coefficient has nonnegative plane
exponents. Thus positivity cannot be lost along any path in the finite
series. The original chart pivots used in the final denominator are nonzero.

These terms may be dropped before the series and after each perturbation.
This is an equality of the final **linear point functional**. A pruned
intermediate residual need not be closed, and its primitive is never exported
as a physical section. Closure of the actual unpruned universal basis comes
from its independent full lifting certificate.

## Source-column reuse and full matrix scope

On a plane-global V2 section, the ordered outer cup product chooses the P1
suffix vertex of the actual arrow. Its signs are those independently certified
by the complete source-module identity. After regular `u` specialization,
terms with the same source object, `x` monomial, `p` monomial, and P1 chart
are combined exactly. The evaluated finite operator on each such unit is
cached per deck channel and parameter. The original archived section is
then a declared linear combination of these units. No new section-basis
choice or coefficient fit is made.

Both parameter corrections feed the original quotient frame. The upper-right
quotient correction is included as well as the genuine nonsplit section
correction. Injected V1 columns and lower V2 coordinates are evaluated from
their original saved section records. Constants and both linear parameter
coefficients are retained; no parameter value is selected.

The artifact writer evaluates every index in `range(5345)` in the original
order and records a content-addressed, deterministically compressed stream
of three exact 4 by 1 columns per index. All coefficients of the four prior
full-cochain probes must agree before the artifact can be written. Their
constant determinant `1/81` provides an independently established rank-four
minor for the complete point matrix at every extension parameter.

The point is the prior exact algebraic probe, not a chosen vacuum. A full
point matrix is **not** controlled numerical sampling on the Calabi–Yau,
an integration measure, a converged Ricci-flat/HYM approximation, a matter
metric, or a physical Yukawa prediction. Those gates remain open. In
particular, the cost of operator compilation is not a convergence result;
reuse across geometric samples and controlled numerical error still need
to be established before performing metric integrals.

Reproduce the complete exact matrix with:

```bash
python -m research.experiments.scientific_genesis.alternate_metric_specialized_evaluation
```
