# Full original section covariance, not a physical metric

## Edge and inputs

This experiment connects the completed original 5,345-column bounded matrix
to an executable trial bundle-metric prerequisite. It consumes that archive,
not newly invented sections or a small substitute basis. Its fixed domain
remains the predecessor finite-chart regression domain, not an independent
draw or a selected extension/vacuum point. The original twist is (14,16,1),
with the common flat character (1,2). All four local fiber labels and both
formal extension parameters are retained.

For an explicitly supplied positive Hermitian section-coefficient covariance
H, the local expression is `G = S H S^dagger`, where
`S = C + a0 A0 + a1 A1`. This is the covariance defining a trial metric on
the TWISTED bundle. It is not a harmonic matter overlap. H is computational
input, not a derived physical coefficient or a fitted texture. The executed
regression explicitly supplies unit H in the named original section basis;
there is no automatic unit-metric default or canonicality claim.

## General positive input and streaming identity

The supplied form is `H = L D L^dagger`, with L unit lower triangular and D
strictly positive rational diagonal. Every off-diagonal entry of L is explicit
in Q(omega). This is not a restriction to diagonal metrics: arbitrary positive
Hermitian matrices over Q(omega) have such an exact LDL factorization. Conversely
this input is positive because `z^dagger H z` is a positive weighted sum of
absolute squares and L is invertible. No 5,345-square determinant is necessary.

Let `T = S L`. Its jth column is `S_j + sum(i>j) S_i L_ij`. The stream retains
that column until its last declared lower-triangular contribution arrives,
then adds `D_j T_mj T_nj^dagger` to each coefficient block. Thus every original
column is consumed exactly once; dense L is supported as well as sparse L.
Only explicitly exact zero scalar/zero-radius coefficients may be omitted.
Uncertain zero centers are retained. Memory may grow for dense forms; no
practical dense-H or multi-point cost guarantee is made.

Writing `eta=(1,a0,a1)`, the complete expression is

```
G(a,bar a) = sum(m,n=0..2) eta_m conjugate(eta_n) G_mn
G_mn      = sum(j=0..5344) D_j T_mj T_nj^dagger.
```

All nine 4-by-4 blocks are returned. Conjugate parameters are NOT identified
with holomorphic parameters. `G_nm=G_mn^dagger` follows from the real positive
diagonal; adjoint pairs are stored using that exact identity. Real diagonal
squares use the existing norm intervals. Positive-radius centers are explicitly
rounded to the declared dyadic precision with their displacement included in
the radius; exact singletons remain exact. No field element is converted to a
float, and no uncertain term is removed as a small coefficient.

## Weight and basis conventions

The same original certified point and unchanged positive auxiliary measure
provide W, with pi cubed kept symbolic, residue scale explicitly one and cover
degree explicitly nine. Multiplying every covariance block by the full weight
interval gives a COMPLETE weighted trial-covariance integrand on this declared
domain. It is neither an integral nor the HYM iteration kernel involving G^-1.
No midpoint is substituted for a weight or section enclosure.

For a declared section change `S'=S R`, invariance requires
`H'=R^-1 H (R^-1)^dagger`. For a local fiber change `S'=M S`, one has
`G'=M G M^dagger`. H, ordered section identities and the fiber basis therefore
travel together. The inverse of G would define a local trial metric only after
admission and line-twist normalization; those operations are not provided here.
Untwisting requires an explicitly supplied line metric. Global generation
and positive H give mathematical positive definiteness, not an interval inverse,
a balanced fixed point, a Ricci-flat/HYM residual, or harmonic representatives.

## Independent verification and remaining work

A separate Fraction-pair implementation reconstructs the full unit-H contraction
from all original archive columns, independently of OneTheory's scalar products,
streaming transformations and rounded accumulation. Independent exact products
of actual selected archive columns also test non-diagonal LDL input and complex
parameter routing. The original archive's cochain and operator certificates
remain the evidence for sections; this is not a new all-column cochain replay.
Every parent/archive hash is checked before and after consumption. Rehashed
basis, coefficient, weight, omission and scope changes must fail closed.

The output closes full covariance assembly on ONE existing domain. Independent
input clouds, complete new-domain section throughput, inverse/HYM kernels,
global integrand bounds, controlled integration, metric and twist convergence,
harmonic matter/Higgs metrics, a common stabilized vacuum, physical Yukawas and
Genesis-to-UV remain unresolved. No measured observable enters this experiment.

## A uniform denominator without selecting extension parameters

The full original archive also has an EXACT structural zero pattern:
injected columns are `(X_j,0)`, while lifted columns are `(a0 Z0_j+a1 Z1_j,Y_j)`.
The constant upper coordinates of lifted columns and every lower deformation
coordinate vanish with radius zero, not just with zero center. The reader
checks this pattern for every original column. For the executed unit-H input,
write A=XX^dagger, D=YY^dagger and Z=a0 Z0+a1 Z1. Then

```
G = [ A+ZZ^dagger  ZY^dagger ]
    [ YZ^dagger       D     ].
```

Both named 2-by-2 diagonal blocks have strict positive first diagonal and
determinant interval bounds on the WHOLE original certified domain. Sylvester's
criterion therefore proves A,D positive there. The Schur complement is
`A + Z (I-Y^dagger D^-1 Y) Z^dagger`. The matrix in parentheses is an orthogonal
projection: P=Y^dagger D^-1 Y is self-adjoint and P^2=P because D=YY^dagger.
Consequently the Schur complement is at least A in the positive order. For
positive A, its determinant is `det(A) det(I+A^-1/2 B A^-1/2) >= det(A)` for
any positive B. Thus, for EVERY complex a0,a1,

```
det G >= det A det D >= delta_A delta_D > 0.
```

The output records the exact rational lower bound, with original block labels
and minor enclosures. Independent Fraction-pair expansion verifies both minor
bounds. This is a family-level quantitative denominator result on the same
local domain, not a test at a chosen extension point. It does not bound the
inverse norm uniformly over unbounded affine parameters, extend to arbitrary
section forms without additional estimates, supply an inverse kernel, or prove
global integrand/integration/physical-metric convergence.
