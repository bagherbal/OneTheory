# Base-eliminating charts for the actual cover

Scope: conditional on the unchanged explicit heterotic realization. This
calculation is an integration prerequisite, not a physical metric or a choice
of extension parameters, physical Kähler class, or vacuum.

## Actual equations and certified inputs

Use the original equations `mu F(x)+nu G(x)=0` and
`2 nu F(u)+mu G(u)=0`, with the original diagonal-plus-product cubics. An exact
projective plane point outside the pencil base locus determines the shared
base: `[-G(x):F(x)]` from the first factor or `[-2F(u):G(u)]` from the second.
The partner point is a root of the actual other pencil restricted to a declared
line. A complete three-root certificate supplies its disks and any infinity
branch. Normalized disks enclose actual roots; their centers are not asserted
to satisfy the cover equations. An exact source point cannot be replaced by a
disk center. The new point-line configuration records this distinction.

## Coordinates, signs, and tangent frames

Keep the original ambient order `(s,z,r,w,t)` and the declared projective pivots.
Write the two affine equations as `f(s,z,t)` and `g(r,w,t)`. The original
ambient residue sign remains the product of projective-chart signs and the
explicit plane-coordinate permutations.

On the first-factor critical chart, retain free coordinates `(s,z,r)`. Require
`f_t` and `g_w` to be certified units. Then

```
t_s = -f_s/f_t, t_z = -f_z/f_t
w_s = -g_t t_s/g_w, w_z = -g_t t_z/g_w, w_r = -g_r/g_w
det(df,dg,ds,dz,dr) = -f_t g_w
```

On the second-factor critical chart, retain free coordinates `(r,w,s)`.
Require `g_t` and `f_z` to be certified units. Then

```
t_r = -g_r/g_t, t_w = -g_w/g_t
z_r = -f_t t_r/f_z, z_w = -f_t t_w/f_z, z_s = -f_s/f_z
det(df,dg,dr,dw,ds) = f_z g_t
```

The determinants refer to covector rows in the SAME ambient order. Thus the
residue is the original ambient sign times the declared nonzero scale divided
by the displayed determinant. Multiplying either tangent frame by either
equation gradient gives zero. Full five-dimensional exact determinants provide
an independent check of both signs. On overlaps with regular charts, changing
free coordinates transforms both residue density and auxiliary density by the
same squared Jacobian norm; their weight ratio is unchanged.

## Reused positive density

In either frame pull back the same normalized ambient forms
`FS_x + FS_u + FS_p`. The density times `pi^3` is six times the determinant of
the sum of the three pulled-back Hermitian Gram matrices. This is the previously
derived auxiliary law, not a second geometry implementation. Its cover mass
is 72. The weight without `pi^3` is `72 |h|^2 / density`; quotient conversion
requires the explicit degree, here nine. Circular bounds certify every inverse
and a strictly positive real density interval. A failed unit or positivity
test is an unresolved chart, never a fallback value.

## Reproduced critical fibers and limits

For each factor use the three coordinate-axis points. Their shared base values
are exact in `Q(omega)`. At these points the source plane gradient is exactly
zero, whereas its base derivative is nonzero. Disjoint critical supports of
the two original pencils ensure the partner surface is regular. The declared
partner line `(1,0,0),(0,1,1)` supplies all three certified partner roots, giving
18 actual cover domains. Source pivots, ascending remaining source coordinates,
partner pivot zero, partner solve coordinate two, and base pivot zero are all
recorded. No root or chart is silently dropped.

These are deterministic regression domains, not uniform samples. Generic
base-eliminating formulas also apply to other certified inputs whose named
Jacobians are units. The artifact does NOT certify all triangle-node inputs,
a complete global atlas, a quantitative global weight bound, controlled uniform
proposals, integration errors, practical section throughput, or Ricci-flat/HYM
convergence. Those remain prerequisites to physical normalization.
