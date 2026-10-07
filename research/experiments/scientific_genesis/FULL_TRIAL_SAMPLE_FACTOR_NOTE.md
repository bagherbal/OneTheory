# Complete weighted-sample-factor diagnostic

## Question and immutable population

The full original unit-H0 Gram trial failed its frozen Cholesky gate.
Its complete-coordinate eigendirection is unresolved at floating-point scale,
while direct quadratic accumulation across all original kernels is positive.
The next question is whether the **unformed** complete weighted sample factor
has resolved numerical span, or whether that original factor itself is poorly
conditioned. This diagnostic uses the same 1,536 training and 512 held-out
inputs, all 5,345 sections, selected unstabilized point and original unit H0.
It supplies no inverse form and cannot retrospectively admit the old trial.

## Exact algebra and numerical realization

For each original four-by-N saved row matrix Q, let G=Q Q-dagger and G=L L-dagger.
Stack every `sqrt(w/n) L^-1 Q` in the original ordinal order to form M. In exact
arithmetic `A=M-dagger M`. With the earlier explicit solver diagonal
`D=sqrt(diag A)`, factor the **complete** rectangular matrix `M D^-1 = U R`.
All N original columns remain in order. No pivoting, eigenvalue cutoff,
pseudoinverse, reduced model or modified initializer occurs. U is a numerical
Householder representation, not a physically selected matter basis. R is a
full N-by-N triangular factor, not an admitted inverse metric.

The numerical implementation uses the documented raw-reflector form of
[SciPy QR](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.qr.html)
and [LAPACK QR factorization](https://www.netlib.org/lapack/explore-html/d0/da1/group__geqrf.html).
Applying the reflectors' conjugate transpose to **every** original scaled
column checks the complete reconstruction against R and the zero lower block.
Columns are processed in bounded memory blocks, not omitted or selected.
The original weighted factor and full R are retained as non-pickle NumPy
arrays, with source/parent hashes and explicit original-coordinate references.

The triangular one-norm reciprocal condition estimate and reconstruction
residual are binary64 discovery diagnostics. Neither establishes exact sample
rank, input/rounding error bounds or usable statistical integral accuracy.
Nonzero numerical pivots alone are not a rank proof. Ill conditioning of M
is not to be silently repaired; it identifies a need for original-input
precision or mathematically justified full-coordinate solver work. Favorable
diagnostics still require a separately declared and verified inverse step.
The original failure, policy, operator and every sample remain unchanged.

## Reproduction

```bash
source .venv/bin/activate
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python -u -m \
  research.experiments.scientific_genesis.full_trial_sample_factor \
  5a7953df972ee465e28c0bec9db09173b3fa81e20409503f171d7da280c37bfc \
  bc7f9c9819829269b9978823e4d3c99119bce97ef548a26014d6a333a8b89001 \
  64
```

This execution verifies the original whole cloud first and obtains no new
entropy or geometric samples. Existing result installation refuses replacement.
Large arrays remain local generated outputs; versioned captured input receipts
and frozen sources allow their reproduction in a separate checkout.
