# Complete trial kernel and structural global bounds

## Declared edge

This experiment tests `alternate_section_covariance -> alternate_metric_trial_kernel
-> visible_metrics`, with direct prerequisites `alternate_metric_quotient_generation`,
`alternate_metric_lift_operator_certificate` and `alternate_metric_global_weight_bound`.
The last arrow still requires controlled integration, metric refinement, harmonic
representatives and a common stabilized vacuum. The current task closes the
unscaled trial integrand, not that physical arrow. No old section calculation or
automorphism sweep is restarted.

The section matrix S has all 5,345 original invariant columns, fiber rank four,
twist (14,16,1), common flat character (1,2), and both formal complex parameters.
Its complete original archived coefficient bounds and named bases are reused.
The section covariance is explicitly unit H as a computational initializer,
never a derived physical choice. The algorithm requires caller-supplied complex
parameter enclosures; there is no default extension point or vacuum.

## Kernel and conventions

Write G=S H S^dagger and K=S^dagger G^-1 S. This is the unscaled integrand
of the generalized bundle T-operator, with our sections stored as fiber rows
and section columns. The [published formulation](https://arxiv.org/pdf/1103.3041)
gives the section contraction in equations (3.18)-(3.19). Its global integral
normalization is NOT inserted here: no missing physical volume is inferred.
Weights retain the existing auxiliary law beta^3/72, explicit residue scale
one, degree-nine quotient conversion and symbolic pi cubed. The output is not
a T-operator iteration, a fixed point or a Hermitian Yang--Mills solution.

An invertible fiber change S'=M S gives G'=M G M^dagger and K'=K. A change
of local line trivialization also cancels, since it is a scalar fiber change.
Thus the trial kernel does not require line-metric untwisting; the final fiber
metric still does. The original invariant sections descend, so their kernel
has this intrinsic meaning on the quotient. For a section change S'=S R,
the covariance must change to H'=R^-1 H (R^-1)^dagger and K'=R^dagger K R.
Unit H is not preserved under an arbitrary nonunitary section change.

## Inversion on whole declared domains

The original all-parameter Schur certificate supplies det G >= delta > 0
throughout its certified geometric domain. We evaluate the full Hermitian
coefficient expression on explicitly supplied complex parameter disks. Every
coefficient and disk error is retained. The exact polynomial determinant
engine supplies the four-by-four determinant; its three-by-three minors
supply the adjugate. This extends the existing bounded pivot determinant's
demonstrated size-three limit rather than creating another sign algorithm.

The true determinant is real. Projecting its circular enclosure onto the real
axis and intersecting with the independently proved lower half-line yields
a positive denominator interval. An empty intersection or precision unable to
retain positivity is a failure, never a midpoint inverse or fallback constant.
The raw inverse determinant is much smaller than the declared absolute dyadic
mesh. Direct inversion therefore gives needlessly large errors even when
individual inverse entries are resolvable. We instead declare the exact
arithmetic rescaling `(adj G/M)/(det G/M)`, with M the certified determinant
upper endpoint. The normalized denominator interval must still retain positive
lower endpoint at the unchanged precision; otherwise admission fails. This
rescaling is recorded, not hidden as a physical normalization or precision
increase. Adjugate divided by that entire interval encloses the inverse. Hermitian
identities retain conjugate pairs and real diagonal entries explicitly.

The complete kernel is factorized, not replaced by a subset: it retains all
original columns and applies K v = S^dagger [G^-1 (S v)] to a caller's exact,
basis-declared section-coordinate vector. This avoids materializing a
5,345-square matrix. Every original index is consumed and every output index
is produced. Computational test vectors are not matter states or physical
results. The executed parameter disks enclose regions, not chosen points;
the family formula remains valid for arbitrary admitted explicit disks.

## Structural global bound

For any globally generating S and positive H, put
P=H^(1/2) S^dagger (S H S^dagger)^-1 S H^(1/2). Direct multiplication gives
P^dagger=P, P^2=P and tr(P)=4. Consequently 0 <= P <= I, K H K=K,
tr(H K)=4 and 0 <= K <= H^-1. No numerical matrix square root is required
for this proof. For the declared unit H, K itself is an orthogonal projection,
||K||_op=1 and ||K||_F^2=4. The existing quotient generation theorem and
certified universal lifts cover the complete alternate P1 family, not merely
the archived local domain. These are the hypotheses for the global bound.

For distinct i,j, positivity of the two-by-two compressions of K and I-K gives
|K_ij|^2 <= min(K_ii K_jj,(1-K_ii)(1-K_jj)) <= 1/4. The last inequality
uses K_ii+K_jj <= 1 or its complementary case. Diagonal entries lie in [0,1].
Thus with the existing global W/pi^3 <= B, the unscaled weighted kernel has
operator norm at most B, squared Frobenius norm at most 4 B^2, diagonal
entries in [0,B] and off-diagonal modulus at most B/2. The degree-nine
quotient bounds divide B by nine; squared bounds divide by 81. Pi powers
are recorded symbolically, never replaced by floats.

For a FIXED unit input, fixed extension parameters independent of the cloud,
and n independent draws from the declared ideal law,
the sample-mean squared Frobenius error is at most 4 B^2/n: independence
kills cross terms, while subtracting the true mean cannot increase the second
moment. Markov's inequality gives failure probability at most
4 B^2/(n epsilon^2) for Frobenius error epsilon. This conditional estimate
is not a realized cloud, a practical sample count or an integration result.
This probability statement holds for each fixed parameter value, not
simultaneously over a continuum of parameters. An adaptively selected input
requires a separate independence/error argument.

## Verification and physical boundary

Independent Fraction-pair Gaussian elimination on the complete original
archived arithmetic witnesses checks the inverse and all matrix-free output
coordinates, rather than copying the adjugate formula. Exact symbolic
projection identities supply the all-family argument; arithmetic attacks
include complex parameters and nonunitary fiber changes. Source/archive and
proof hashes must be checked before and after execution, including with
caches populated. Rehashed inputs, omitted columns, basis aliases, weights,
denominators and scientific scope changes must fail closed.

Only the original certified geometric domain is numerically executed. No new
complete-domain section calculation, independent cloud, controlled integral,
balanced iteration, Ricci-flat/HYM convergence, untwisted fiber metric,
harmonic matter/Higgs metric, normalized Yukawa, stabilized vacuum or
Genesis-to-UV derivation is asserted. No observation is an input.
