# Projection-free weights for the unchanged positive law

Conditional on the explicit heterotic realization; no physical moduli are fixed.
The target is the same residue volume and the auxiliary law is still
`beta^3 / 72`, with `beta = FS_x + FS_u + FS_p`. FS is normalized by `i/(2 pi)`.
The residue construction follows the complete-intersection convention in
[Braun, Brelidze, Douglas, Ovrut](https://arxiv.org/html/0712.3563v2).
The determinant cancellation below is derived here, not attributed to that paper.

## General Hermitian identity

Let `G` be a positive Hermitian ambient 5-by-5 matrix and `J` a rank-two
2-by-5 equation Jacobian. Choose ANY three coordinate covectors `K` for which
`L = (J; K)` is invertible. The last three columns `T` of `L^-1` satisfy
`JT=0` and `KT=I`, so they are the tangent frame in those free coordinates.

Put `H = L^-dagger G L^-1`. Its lower-right block is `T^dagger G T`.
The upper-left block of `H^-1 = L G^-1 L^dagger` is `J G^-1 J^dagger`.
The Schur-complement determinant identity therefore gives

```
det(T^dagger G T) = det(G) det(J G^-1 J^dagger) / |det(L)|^2.
```

The residue coefficient is the declared ambient sign times the nonzero scale
divided by `det(L)`. The FS-cube density times `pi^3` is
`6 det(T^dagger G T)`. Thus BOTH appearances of the chosen chart determinant
cancel from the weight without `pi^3`:

```
W_cover = 72 |scale|^2 / [6 det(G) det(J G^-1 J^dagger)].
W_quotient = W_cover / covering_degree.
```

This is a ratio, not an individual residue or free-coordinate density. It
requires no particular fiber derivative to be nonzero and makes no tangent
basis selection. Projective pivots and coordinate order remain explicit inputs.

On a projective-chart overlap let `M` be the ambient coordinate Jacobian and
`S` the diagonal rescaling of the two defining equations. On `f=g=0`,
`J'=S J M^-1` and `G'=M^-dagger G M^-1`, hence
`D'=|det(S)/det(M)|^2 D`. A plane pivot change has coordinate determinant
equal, up to sign, to the inverse cube of its affine pivot; the corresponding
cubic equation has that same rescaling. A base pivot change has coordinate
determinant minus the inverse square of the pivot; both equations each rescale
by its inverse. Thus the ratio has modulus one on every such overlap, and
`D'=D`. This uses the actual Calabi--Yau multidegrees, not a hidden normalization.

## Actual sparse Jacobian and positive sum

Keep ambient order `(s,z,r,w,t)`, with actual equations `f(s,z,t)` and
`g(r,w,t)`. Their original coefficients, including the second-pencil factor
two, are unchanged. Let `Sx=1+|s|^2+|z|^2`, `Su=1+|r|^2+|w|^2`,
and `Sp=1+|t|^2`.

For a projective-plane FS block,
`G_q=(S I-q q^dagger)/S^2`, `G_q^-1=S(I+q q^dagger)`, and `det(G_q)=S^-3`.
The projective-line block has inverse `Sp^2` and determinant `Sp^-2`.
Consequently define the nonnegative exact conormal terms

```
Ax = Sx (|f_s|^2 + |f_z|^2 + |s f_s + z f_z|^2)
Au = Su (|g_r|^2 + |g_w|^2 + |r g_r + w g_w|^2)
Ap = Sp^2 |f_t|^2
Bp = Sp^2 |g_t|^2.
```

The two shared-base contributions have rank one. Their determinant contribution
cancels identically, giving the positive expression

```
det(J G^-1 J^dagger) = Ax Au + Ax Bp + Au Ap
D = (Ax Au + Ax Bp + Au Ap) / (Sx^3 Su^3 Sp^2)
W_cover = 12 |scale|^2 / D.
```

Independent full ambient inverses and determinants, not this simplified sum,
check the formula. The sparse Jacobian rank is two on the actual smooth cover,
as established by disjoint pencil critical supports. Thus the sum is positive
everywhere on the cover, including both kinds of critical fibers. At a
first-factor critical point `Ax=0`, the term `Au Ap` remains positive; at a
second-factor critical point `Au=0`, the term `Ax Bp` remains positive.
The result is a family-level identity, not an enumeration claim.

## Controlled enclosures and scope

The implementation evaluates original equation gradients on certified exact
cover points or complete-root enclosures. It uses outward rational intervals
for every squared modulus and positive product. Inversion is allowed only
when the resulting interval for `D` has strictly positive lower endpoint.
It never inverts an individual fiber gradient or silently raises precision.
A coarse interval that reaches zero remains unresolved, despite pointwise
smoothness of the actual variety. Disk centers are only arithmetic test
functionals, not cover points.

Regression output includes all 18 original regular domains and all 18 declared
axis-critical domains. The identity also applies to triangle-critical points,
but no triangle input certificate or complete global numerical input atlas is
claimed. A global quantitative bound, controlled independent uniform proposals,
integration error control, practical section throughput, Ricci-flat/HYM
convergence, physical Yukawas, and common stabilized vacuum remain open.
