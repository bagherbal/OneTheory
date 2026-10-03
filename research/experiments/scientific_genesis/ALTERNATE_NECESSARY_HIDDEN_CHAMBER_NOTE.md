# Necessary hidden HYM chamber, not a hidden bundle

## Inputs and scope

The frozen alternate non-split P1 cone has parameter-independent rational
quotient Chern coordinates `c2(V)=(8/3,5/3,4)`. The selected Schoen tangent
class is `(4,4,0)`. Coordinates are dual to the declared divisor order
`(tau1,tau2,phi)`, with quotient integration equal to cover integration / 9.
Thus, **conditional on no extra Bianchi sources**, the required hidden class
is `(4/3,7/3,-4)`. This is a rational target, not a constructed hidden bundle
or an integral/torsion anomaly certificate.

The necessary wall is already published in
[Braun, He and Ovrut, hep-th/0602073v1](https://arxiv.org/abs/hep-th/0602073),
equations 39--44. It is applied here to the alternate carrier because its
rational Chern data agree. No identity of the bundles is asserted. The source
archive digest is pinned by the existing immutable published manifest.

## Independent analytic derivation

Assume a compact Kahler threefold, a determinant-trivial unitary hidden
bundle, and a trace-free HYM connection with anti-Hermitian curvature F.
Fix the fundamental trace convention
`c2 = Tr(F wedge F)/(8*pi^2)` when `Tr F=0`.
The HYM equations make F primitive of type (1,1), so
`*F = -J wedge F`. Therefore

```text
positive Yang--Mills energy
  = - integral Tr(F wedge *F)
  = 8*pi^2 integral c2(hidden) wedge J >= 0.
```

Equality forces F=0 and hence vanishing real c2. Our rational target is
nonzero, so the pairing must be strictly positive. A positive embedding
index changes the normalization but not this sign. No E8 embedding or
connection is supplied by this argument. With `J=(x1,x2,y)`, the quotient
pairing is `(4*x1+7*x2-12*y)/3`; the cover pairing is nine times this.
The full positive Kahler cone must therefore be intersected with
`4*x1+7*x2-12*y>0` in this branch. Saturation is excluded as well.

## Family-level consequences

The existing sufficient visible-stability box has center `(6,9,3)` and
coordinate radius `1/32`. Its center is only a feasibility witness, not a
selected physical polarization. The hidden quotient pairing at the center
is 17. On the whole box it is bounded below by
`17-(4/3+7/3+4)/32 = 1609/96 > 0`. The already-certified nine slope upper
bounds remain strictly negative. Thus the necessary common region contains
an open three-dimensional box for every nonzero outer extension parameter.

To attack the idea that visible stability alone suffices, declare the
symbolic slice `J=s*(3,4,t)`, with `s>0`. This is an analytic test family,
not a vacuum choice or a scan. Substitution into all nine cover slope
polynomials gives `s^2*(A+B*t)`. Their exact common negative interval is
`13/12 < t < 29/6`; the lower face comes from row 8 and the upper from row 2.
The hidden quotient pairing is `s*(40/3-4*t)`. Consequently:

```text
visible sufficient stability:       13/12 < t < 29/6
necessary hidden-compatible slice:  13/12 < t < 10/3
excluded visible-stable slice:      10/3 <= t < 29/6
```

Every excluded member violates the necessary hidden HYM condition for the
fixed target, regardless of the hidden polynomial maps. This is a scoped
chamber exclusion, not a no-go for other brane/flux/non-Kahler branches.

## Verification and unresolved prerequisites

The thin producer uses existing exact class arithmetic, sparse polynomials,
and stability bounds. It pins both authoritative parent digests. Regression
tests independently integrate the published cover expression
`11*tau1^2+8*tau2^2-4*tau1*tau2`, use Fraction arithmetic for the box and
each affine bound, check all box corners, and reject rehashed changes to
parents or scientific scope. No numerical geometry or cochain search runs.

Positive pairing is necessary, never sufficient. Hidden maps, local freeness,
descent, integral/torsion anomaly cancellation, actual common slope stability,
hidden spectrum, metrics, superpotential and stabilization remain missing.
No Kahler class, extension point, vacuum or physical observable is selected.
