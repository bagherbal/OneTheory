# Original section features: discovery, not certification

## Question and scope

Can all 5,345 original sections be evaluated repeatedly without reconstructing
cochains or doing rational-ball arithmetic for each polynomial term? Success
would permit the first integration cloud to spend time on the integral rather
than repeating already certified lifting mathematics. It would not establish
an integral, HYM solution, matter metric, or physical Yukawa matrix.

## Exact representation being compiled

The trusted complete first-chart archive contains 90,865 polynomials and
3,621,141 nonzero exact terms in its original ordered coefficient channels.
The constant channel has nine raw generators; each of the two extension
channels has four. Compilation interns the actual eight-variable monomials,
then records CSR offsets, feature indices, and binary64 coefficient pairs.
The full archive and canonical decompressed stream hashes are pinned. The
original section identity remains independent of chart and numerical output.

Before conversion, the transformation is merely

    polynomial_i(x) = sum_j coefficient_ij * monomial_j(x).

It changes neither the exact polynomial nor its order. It shares monomial
features across all channels and sections. No new cochain, homotopy, bundle,
quotient, or geometric object is constructed. Existing determinant-certified
frame projections supply P0, P1, P2. The output channels are exactly the same
algebraic expressions as in the certification evaluator:

    C0 = P0 * raw_constant
    Cm = P0 * (raw_correction_m, 0, 0, 0, 0, 0) + Pm * raw_constant.

The resulting columns retain the full original ordered section basis and the
caller's explicit four-dimensional quotient basis. A frame in a different
chart is rejected; a new chart must be explicitly compiled, not silently
converted through an adapter.

## Numerical meaning and independent attacks

Binary64 embeds omega as -1/2 + i sqrt(3)/2. Rational coefficients, coordinate
centers, and projection centers are converted explicitly. Input radii are
**not propagated**, rounding is **not certified**, and centers are **not
asserted to lie on the variety**. These output values are discovery arithmetic,
not an alternative exact result. Nonfinite outputs fail explicitly.

Independent tests compare the compiled coefficients with existing bounded
polynomial evaluation and independently evaluate selected raw polynomials
over Q(omega) at the exact arithmetic centers. Certification remains available
and unchanged. The comparisons are probes, not a proof of an all-point error
bound. The source hash and full term/count checks protect complete execution
from replacement by probes; the probes test arithmetic fidelity independently.

The benchmark evaluates every column on all 15 existing fixed regression
domains twice. Each repetition must reproduce identical numerical bytes and
basis labels. Timings distinguish compilation from evaluation. This is an
observed repeated-workload measurement, not an asymptotic speed theorem or a
matched speedup against a different old run. The domains are not independent
integration samples and none is a selected physical moduli point.

## Next scientific use

Freeze this numerical representation after independent checks. The next step
is an actual independently generated, identity-preserving auxiliary cloud,
same-sample precision refinement, and numerical/statistical error control for
the factorized global kernel. A covariance computed on regression centers is
not a controlled integral. A trial section form is not a canonical matter
metric, and neither a stabilized vacuum nor HYM convergence follows here.
