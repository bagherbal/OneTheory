# Actual-cover integration prerequisite

This closes the residue/auxiliary-measure prerequisite for the frozen alternate
carrier's metric path. It supplies neither samples nor a metric. No extension
coordinate, Kähler vacuum, or measured observable is chosen.

The published starting point is Braun, Brelidze, Douglas, and Ovrut,
[Calabi-Yau Metrics for Quotients and Complete Intersections](https://arxiv.org/abs/0712.3563v2).
Its Schoen construction provides a double residue and a projective
line/point/line integration scheme. We derive the conventions below separately
and substitute **our actual** F and G, not another paper's example cubics.

## Explicit chart and orientation

Specify a nonzero pivot and a distinct eliminated coordinate in each plane,
plus the P1 pivot. Normalize those pivots to one. The ambient order is
`(s,z,r,w,t)`; `z,w` are eliminated and the free order is `(s,r,t)`.
The actual equations remain

```text
f = mu F(x) + nu G(x)
g = 2 nu F(u) + mu G(u).
```

Let `sigma_x = sum_i (-1)^i x_i dx_0 ... omit dx_i ... dx_2`, and
similarly for u, while `sigma_p = mu dnu - nu dmu`. In the explicit
ambient order their product has sign

```text
epsilon = (-1)^(x_pivot + u_pivot + p_pivot
                + [x_free > x_solve] + [u_free > u_solve]).
```

The convention `df wedge dg wedge Omega = sigma_x wedge sigma_u wedge sigma_p`
then gives `Omega = h ds wedge dr wedge dt`, with
`h = -epsilon * scale / (f_z g_w)`. A vanishing denominator means this
projection chart is ramified, not that the cover is singular. It is rejected
without an automatic replacement. The nonzero form scale is caller supplied;
the algebraic probe scale one is not a physical normalization or vacuum input.
Positive volume is `(i/8) Omega wedge conjugate(Omega)`, hence its Lebesgue
density is exactly `|h|^2`.

Implicit differentiation gives `z_s=-f_s/f_z`, `z_t=-f_t/f_z`,
`w_r=-g_r/g_w`, and `w_t=-g_t/g_w`. These tangents annihilate both actual
equation gradients. Chart-transition tests differentiate homogeneous ratios
independently, checking the complex determinant and both real densities.
Across the two P1 charts, `t_mu=1/t_nu`, `f_mu=f_nu/t_nu`, and
`g_mu=g_nu/t_nu`; thus `J_mu=J_nu/t_nu^2`. The residue sign change agrees
with `dt_mu/dt_nu=-1/t_nu^2` identically, not just at an algebraic probe.

## Normalized auxiliary law

Choose `omega_FS=(i/2pi) partial bar-partial log(sum |Z|^2)`, with
hyperplane integral one. Independent SU-uniform plane lines and a P1 point
have intersection measure `A=omega_x wedge omega_u wedge omega_p` on the
cover. Each generic configuration yields nine points. This is not the
distribution obtained by sampling the free affine variables uniformly.

The mass follows from the actual complete-intersection class:

```text
integral_X Hx Hu Hp
  = coefficient_(Hx^2 Hu^2 Hp) Hx Hu Hp (3Hx+Hp)(3Hu+Hp)
  = 9.
```

The normalized point law is therefore `A/9`. For a plane coordinate q and
tangent v, put
`kappa(q,v) = ((1+|q|^2)|v|^2 - |q^dagger v|^2)/(1+|q|^2)^2`.
The auxiliary Lebesgue density in `(s,r,t)` is `M/pi^3`, where
`M=kappa((s,z),(1,z_s))*kappa((r,w),(1,w_r))/(1+|t|^2)^2`.
All other tangent components disappear when wedged with the P1 form.
An independent test instead pulls back all three complete Hermitian forms
and takes the coefficient of `a*b*c` in their matrix-pencil determinant;
it obtains M without using that factorization.

The cover importance weight is `9*pi^3*|h|^2/M`. For a descended invariant
integrand, its quotient integral divides by the independently declared free
covering degree. Here that degree is also nine, giving `pi^3*|h|^2/M`.
The two factors of nine have different derivations. Pi remains an explicit
symbolic factor, not an approximate scalar or hidden normalization.

## Descent and remaining gate

Direct polynomial substitution checks both actual equation units for P and T.
The homogeneous volume multiplier is the product of the three coordinate
determinants. Dividing by both equation units gives residue character one
for each generator. Their matrices are unitary, so the auxiliary form is
invariant too. Omitting an equation unit fails the regression test.

The two exact probe densities and weights are reproducible and content
addressed. The independent sign, tangent, mixed-wedge, chart, and mutation
tests support this prerequisite, not numerical integration accuracy.
Controlled projective roots, branch-complete sampling, sampling error,
Ricci-flat/HYM convergence, matter overlaps, the remaining Yukawa sectors,
and a common stabilized vacuum are still required. Genesis-to-UV remains
unresolved independently of this conditional heterotic calculation.
