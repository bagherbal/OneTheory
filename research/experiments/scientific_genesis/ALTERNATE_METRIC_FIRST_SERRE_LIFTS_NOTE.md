# Actual first-constituent metric sections

This is conditional on the frozen heterotic/Schoen realization and its
determinant-repaired alternate carrier. No vacuum, metric, or observed input
is selected. At the declared generating twist `H=(14,16,1)`, the first
constituent now has a complete **2,655-vector invariant section basis**.
The second constituent is now constructed in the separate
`ALTERNATE_METRIC_SECOND_SECTIONS_NOTE.md`. Universal rank-four lifts
remain open; this artifact certifies only V1.

## Why nine templates replace 1,540 homotopy solves

Ten spread quotient-lift probes had the same one-step homotopy pattern.
The resulting structural-compression question was whether their large
polynomial factors could transport a finite set of actual lifts.

In the actual first Serre complex, the subline has degree `(13,17,0)`;
the three Hilbert--Burch target objects have degree `(11,17,2)`. Their
ideal map is `(x0*x1, x0*x2, x1*x2)`. All F0-to-subline extension terms
have nonnegative plane exponents, zero second-plane degree, and the sole
Laurent denominator `mu*nu`. Their coefficients are identical on all
nine plane vertex charts. These statements are checked against every
actual source arrow; no split extension replaces them.

Temporarily subtract `(11,17,0)` from every object degree. Each F0
generator then has three polynomial P1 sections: `mu^2`, `mu*nu`, and
`nu^2`. For all nine generator/monomial combinations, the existing full
Čech--Koszul differential produces a degree-one subline residual solely
on the P1 overlap. Its existing tensor-cover contraction supplies a
primitive in one step. The **full** differential of that primitive equals
the residual, so subtraction produces an actual closed lift.

Multiplication by a global plane polynomial is a cochain map: restrictions,
the Hilbert--Burch arrows, and actual extension arrows are polynomial-linear.
It preserves regularity because neither the polynomial factor nor the
template has a plane pole. On these templates the Čech homotopy acts only
in P1, so the plane factor commutes with it. There is no higher perturbation:
the primitive lies in the subline's k0 term, with no outgoing extension,
Hilbert--Burch, or Koszul arrow. This proves the transport rule for arbitrary
plane factors in the declared degrees, not only sampled monomials.

For each certified quotient label, choose the first declared ideal generator
dividing it, transport its appropriate template, then sum its three P images.
The homogeneous frame is the actual common flat-character repair `[1,2]`.
Every resulting section is checked for T invariance, P invariance, and
closure; covariance of a deck average is not silently assumed.

## Complete basis and exact encoding

The 1,115 previously certified subline sections inject into `H0(V1(H))`.
The 1,540 constructed lifts map to the **entire previously certified quotient
basis** under the actual Hilbert--Burch ideal map. Exactness of the H0
sequence proves the union is independent and spanning. This does not require
a large artificial rank calculation or an arbitrary extension parameter.

The archive stores all 2,655 cochains exactly over `Z[omega]`. A term
`[object, eight_exponents, P1_vertex, [a,b]]` means coefficient `a+b*omega`
repeated on all nine P2-by-P2 vertex charts, with the P1 vertex explicit.
There are 226,530 terms after full-cover expansion. Laurent poles, their
allowed charts, object degrees, and the nonsplit correction remain explicit.
No equation, correction, or normalization is hidden by compression.

Independent tests use a separate integer-polynomial calculation to replay
all sections' P1 differential plus actual extension residual. Both plane
Čech directions cancel because the polynomials repeat on every vertex;
k0 has no Koszul differential, and these representatives contain no F1
terms. Tests independently replay both deck actions and every quotient image.
The two pole directions and the regular middle case also agree exactly
with the separate full-cover homotopy calculation. Removing the correction
fails closure. Archive and uncompressed-stream hashes are checked.

Reproducer:

```bash
python -m research.experiments.scientific_genesis.alternate_metric_first_serre_lifts
```

The JSON artifact binds the three prerequisite artifacts and the full archive.
The actual alternate V2 basis is separately certified. The next prerequisite
is parameter-dependent rank-four lifts. No Ricci-flat/HYM convergence, matter
normalization, physical Yukawa matrix, or Genesis-to-UV derivation follows
from this section-basis result alone.
