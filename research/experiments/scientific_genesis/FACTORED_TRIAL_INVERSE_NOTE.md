# Separately declared direct-factor inverse trial

The complete original weighted sample factor has QR reconstruction residual
about `3.814e-16` and triangular reciprocal-condition estimate about `9.958e-12`.
The failed binary64 normal-Gram Cholesky trial remains failed, with its original
request and thresholds unchanged. This experiment declares a **distinct**
factor-based numerical resolution policy before attempting its inverse. It
does not reinterpret the old condition threshold as already satisfied.

For the original full matrix `M D^-1=U R`, exact algebra gives
`A=D R-dagger R D`. Every original training sample, all 5,345 columns, unit H0
and the held-out population remain unchanged. The published inverse-T law
and explicit projective scalar gauge recorded in
`BALANCED_TRIAL_ITERATION_NOTE.md` therefore give
`H1=c D^-1 R^-1 R^-dagger D^-1`, with `c=4 mean(w)/5345`.

The real QR diagonals are made positive with explicit row signs. These signs
are stored and are unitary solver operations, not physical basis choices:
`R'-dagger R'=R-dagger R`. Put `L=R'-dagger`; the result is exactly the existing
original-basis inverse-form representation `c D^-1 L^-dagger L^-1 D^-1`.
No ridge, pseudoinverse, dropped section or new initializer is introduced.

The separately captured request requires a triangular reciprocal-condition
estimate at least `1e-12` and a complete `R' R'^-1-I` infinity-norm numerical
residual at most `1e-6`. Every inverse column is checked in blocks of 128;
absolute row residuals accumulate over the **whole** matrix before the gate.
These are diagnostics of triangular solves, not of the old squared Gram
inverse, and not certified forward/input errors. Failure exports no form.

Success supplies only a binary64 computational full-basis H1 factor at the
selected unstabilized point. The original finite input radii, root precision,
sample uncertainty and potential amplification remain unresolved. The next
metric integral must use this actual declared form and unchanged retained
sample inputs, not a substitute diagonal H. No HYM solution, matter metric,
canonical Yukawa, physical vacuum or useful statistical bound is supplied.

The request binds this source/note, the original failed trial, complete QR
packet, all original sources, and the explicit policy. Execution revalidates
the original entire cloud. Numerical arrays are retained locally as immutable
non-pickle outputs, with checksums. Small metadata and original captured inputs
are versioned; a fresh clone must reproduce the large arrays from those inputs.
