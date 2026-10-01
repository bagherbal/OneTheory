# Actual auxiliary-weight moments

Scope: the frozen cubics, the smooth compact cover, and the declared
probability law `A/9`, where `A = FS_x wedge FS_u wedge FS_p`. The weight
is the nonzero residue volume divided by that probability density. This
result concerns the ideal continuous law, not a law of rounded rational
inputs. It supplies no samples, numerical variance bound, confidence
interval, chosen bundle modulus, vacuum, metric, or physical prediction.

## Critical-value algebra, not root enumeration

Keep `t = mu/nu`. Write each actual plane equation as

```text
P = A(t)x^3 + B(t)y^3 + C(t)z^3 + D(t)xyz.
R = ABC; H = D^3 + 27R.
```

The gradient equations show that a singular point with all coordinates
nonzero requires `D^3 = -27ABC`: multiply the three gradient equations
and cancel the nonzero squared coordinate product. If a coordinate
vanishes and all pure coefficients are nonzero, the other gradient
equations preclude a projective singular point. Thus the critical-value
support is `R H`. At a simple root of R, exactly one pure coefficient
vanishes. D and the other coefficients are nonzero. The sole singular
point is its coordinate axis; its affine quadratic term is `D yz`,
with nonzero Hessian determinant `-D^2`.

At a root of H with R nonzero, diagonal scaling over C changes P to
`X^3+Y^3+Z^3-3XYZ`. The identity

```text
(X+Y+Z)(X+omega Y+omega^2 Z)(X+omega^2 Y+omega Z)
  = X^3+Y^3+Z^3-3XYZ
```

gives three distinct nonconcurrent lines and three ordinary nodes, not
a cusp or concurrent triple point. The identity and node Hessians are
independently tested. This classical factorization is discussed by
[Artebani and Dolgachev](https://arxiv.org/abs/math/0611590).
It does not mean that our two varying-coefficient pencils are replaced
by that reference's example pencil. The reduced support has degree six;
the full plane discriminant `R H^3` has degree twelve, up to a nonzero
constant. Triangular singular fibers must not be treated as multiple
critical *values* for the local density argument.

Reading our actual Cox coefficients gives the monic reduced supports

```text
first:  t^6 + (30+60omega)t^3 - 243
second: t^6 - (80/81+160omega/81)t^3 - 64/243.
```

Both are square-free. Their gcd is one. Within each pencil, R and H
are coprime and D is nonzero on their zero sets. Homogeneous evaluation
at `[mu:nu]=[1:0]` gives nonzero R and H, so infinity contributes no
critical fiber. Each surface has three one-node fibers and three
three-node fibers: twelve critical points. These assertions are exact
Q(omega) polynomial calculations, not approximate root searches.

## Smooth surfaces and the fiber product

At an axis node, `P_t` is the nonzero derivative of the vanishing affine
pure coefficient. At an all-nonzero-coordinate node, the gradient
equations give `A x^3 = B y^3 = C z^3 = -D xyz/3`. Consequently

```text
H' = 3D^2 (D' - (D/3)(A'/A+B'/B+C'/C))
P_t = xyz H'/(3D^2).
```

Square-freeness implies `H' != 0`. Hence the equation surface in
`P2 x P1` is smooth at every plane-fiber node; away from nodes a plane
derivative is nonzero. This also excludes singular base points: a base
point singular on the equation surface would require all plane
derivatives and `P_t` to vanish together. The affine plane coordinates
are local coordinates on the surface at a node, and its projection to
P1 has a nondegenerate quadratic critical point.

The disjoint critical-value sets ensure that at least one factor
projection is a submersion everywhere on the fiber product. It is
therefore smooth. The critical locus of the common projection consists
of each of those isolated nodes times the partner's smooth compact
cubic curve. These finitely many smooth curves are disjoint and have
complex codimension two in X. The complete-intersection degrees
`(3,0,1)` and `(0,3,1)` cancel the ambient canonical degrees. The
residue is a smooth nowhere-zero top form on the smooth cover.

## Local density comparison and all nonnegative moments

Near one critical curve choose affine plane coordinates `(z,w)` on
the nodal surface and a smooth fiber coordinate y on its partner.
The common base is `t=T(z,w)`. Nondegeneracy of the Hessian implies

```text
c (|z|^2+|w|^2) <= |dT|^2 <= C (|z|^2+|w|^2)
```

on a sufficiently small neighborhood: `dT = H_0(z,w) + O(r^2)`,
with `H_0` an invertible complex linear map. No exact change to a
quadratic normal form is needed.

The first plane FS metric is positive definite in `(z,w)`. The second
plane FS metric is positive along the partner fiber y. Its remaining
terms involve dt and disappear after wedging with the P1 form.
The P1 form pulls back to a positive smooth multiple of
`i dT wedge conjugate(dT)`. Thus, relative to smooth six-dimensional
coordinate volume, A is comparable above and below to `r^2`, where
`r^2=|z|^2+|w|^2`. The residue density is comparable to a positive
constant. The importance weight W is therefore comparable to `r^-2`.
These estimates are two-sided, not merely an upper bound.

For a nonnegative real moment order q, the transverse radial integral
has four real dimensions and is comparable to

```text
E_(A/9)[W^q] near the critical curve
  ~ integral_0^epsilon r^(-2q) r^2 r^3 dr
  = integral_0^epsilon r^(5-2q) dr.
```

It converges exactly when `q < 3`; q=3 diverges logarithmically.
Finitely many charts cover the compact critical curves. Away from
them the auxiliary density is positive, so compactness supplies a
bounded weight. The cover weight consequently has finite second
moment and infinite third moment. Dividing the weight by the free
quotient degree nine changes no moment threshold for invariant
integrands. No third-family interpretation accompanies this exponent.

## What this permits and what it does not

A bounded continuous tested integrand has finite second moment after
importance weighting. Its third moment need not be finite; the
constant integrand already supplies a counterexample. Standard error
theorems requiring finite third absolute centered moments cannot be
assumed for W: subtracting its finite mean does not remove this tail.

Finite variance alone is not a computable variance upper bound. This
proof does not implement independent draws from A/9, quantify clipping
bias, bound the error of any finite point cloud, cover singularly
growing integrands, or establish Ricci-flat/HYM convergence. Controlled
sampling and quantitative integration errors remain required before
physical normalization. Genesis-to-UV and the common vacuum remain
unresolved independently.
