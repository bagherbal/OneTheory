# Full-basis finite-cloud inverse steps

## Imported law and explicit scalar convention

The generalized bundle T-operator uses the original section matrix S, stored
here as four fiber rows and N section columns:

`A(H) = integral w * S† (S H S†)^(-1) S`.

[Anderson, Braun and Ovrut](https://arxiv.org/html/1103.3041), equations (3.19),
(3.22) and Table 1, specify the inverse T-operator update. Their displayed
normalization is `N/Vol`. This code declares an additional **computational
projective scalar gauge** instead of silently inserting a physical volume or
canonical matter normalization. For rank r and finite reference weights,

`H_next = (r * mean(w) / N) * A_n(H)^(-1)`.

This is r times the displayed unscaled inverse update when the same empirical
volume is used. Multiplication of a fiber metric by a spatially constant positive
scalar does not change its connection. The rank factor is also derived by
`tr(H * S† (S H S†)^(-1) S) = r`, giving the projectively balanced trace N.
The mean reference weight is recorded exactly as a rational average of the
saved dyadic numbers. It is not the true physical volume. Common pi-cubed and
quotient factors cancel between numerator and denominator; no SI scale emerges.

The point remains selected and unstabilized. Convergence at one twist would not
establish HYM convergence, harmonic representatives, physical flavor or a vacuum.

## Full kernels and computational scaling

Saved numerical rows Q need not be exactly orthonormal. The unit-input sum
therefore evaluates `Q† (Q Q†)^(-1) Q`, not an assumed exact `Q†Q`. Four-by-four
Cholesky factors provide the row whitening. This is an invertible fiber change
that preserves the section-space kernel, not physical normalization. Each
sample's entire N-column row matrix is retained. Complete original sample
identities occur exactly once; missing inputs prevent an operator result.

The pilot diagonal values span about `3.2e16`, warning against blindly inverting
the original numerical coordinates. Put `D=sqrt(diag A)` and `B=D^-1 A D^-1`.
If `B=L L†` passes the declared numerical admission gates, the output is

`H_next = c D^-1 L^-† L^-1 D^-1`, with `c=r*mean(w)/N`.

Every original coordinate survives this invertible solver congruence. D is
recorded explicitly. The initial form is still the original identity; no
empirical diagonal form is substituted as H0. The output factor acts in the
original named basis. Bytes-backed factor arrays are immutable, including
against NumPy setflags attempts.

For later numerical evaluation, `Z=L^-1 D^-1 Q†` gives
`Q H_next Q† = c Z†Z`. Thus the full inverse form can be applied without
materializing a second large inverse matrix. This is exact algebra for the
stored factors, not a reduced section approximation.

## Admission and scientific limits

The necessary sample-rank condition is checked before inversion. An unresolved
coordinate norm, failed full Cholesky factor, reciprocal-condition estimate
below the declared threshold, or failed full inverse residual produces an
explicit obstruction. No ridge, pseudoinverse, truncated eigenvectors or
replacement samples are used. A checked Hermitian roundoff projection is
explicitly recorded rather than silently asserted exact.

NumPy/SciPy supply binary64 **discovery arithmetic** for the real full-size
calculation; versions and tolerances are recorded. Condition estimates and
residuals are numerical diagnostics, not rounding or input-error certificates.
Generic exact-oracle matrices in tests are not physical sections. Actual carrier
calculations must consume the complete source-bound training cloud and retain
the separately predeclared validation population. No statistical theorem for a
fixed independent H may automatically be reused for adaptive training iterates.

The 512-point validation operator also has rank at most 2,048, so a full-matrix
identity residual has a finite-sample rank floor in N=5,345 dimensions. It cannot
be mistaken for a high-precision HYM residual. Separate sampling/refinement
analysis and actual curvature diagnostics remain necessary before promotion.

## Reproducible full-cloud execution

An immutable inverse request fixes batch size and Hermitian, reciprocal-condition
and residual thresholds before the complete cloud is available. It binds the
original public input request, selected point, source hashes, all 1,536 training
and 512 held-out ordinals, unit H0, and the explicit projective scale. Readers
obtain no new entropy and perform no geometric replay. The actual operator is
unavailable while any original training **or validation** checkpoint is missing
or unresolved. Held-out samples never select H1.

After complete input validation, the calculation consumes every original training
point once, saves the full N-by-N operator in deterministic little-endian non-pickle
NumPy format, then runs the declared inverse admission checks. An unresolved
inverse retains that operator and its obstruction but exports no inverse form.
A successful numerical inverse additionally saves the full solver diagonal and
Cholesky factor; the output reader requires the original basis, source hashes,
dimensions, artifact checksums, exact reference scalar and scientific limits.
Installation is atomic and refuses replacement of a different existing array.
The complete validation population is preserved for a later independent diagnostic;
this first-step output does not claim that validation or convergence has run.
