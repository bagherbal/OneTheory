# A quantitative global bound for the unchanged positive auxiliary law

Conditional on the explicit heterotic realization. This is a conservative
integration certificate, not a physical metric or a choice of physical moduli.
The original equations, residue normalization, and law `beta^3/72` are unchanged.
Pi cubed remains symbolic in every weight bound.

## Unit homogeneous norms and the intrinsic denominator

Use unit homogeneous representatives for the two projective planes and base.
This is the standard auxiliary FS norm convention, not a physical polarization
selection. Put `f=mu F(x)+nu G(x)` and `g=2nu F(u)+mu G(u)`.
On the actual cover, Euler's identities `x dot grad_x f=3f=0` and
`p dot grad_p f=f=0` identify the full homogeneous derivative norms with their
horizontal projective norms; the same holds for g.

Write `eps_x=||grad_x f||`, `eta_x=||grad_p f||`, with analogous second-factor
norms. The projection-free denominator is

```
D = eps_x^2 eps_u^2 + eps_x^2 eta_u^2 + eps_u^2 eta_x^2.
```

For arbitrary unnormalized representatives with squared norms `Nx,Nu,Np`,
the plane norms squared divide by `Nx^2 Np` or `Nu^2 Np`; base norms squared
divide by `Nx^3` or `Nu^3`. Substitution gives exactly the previous affine
denominator, not another target volume.

## Exact total-surface certificates

For each actual surface the five homogeneous derivatives have bidegrees
`(2,1)` three times and `(3,0)` twice. A declared coefficient system uses
multiplier bidegrees `(2,1)` and `(1,2)`, respectively. It has 45 target
monomials and 54 source columns and exact rank 45 for each original surface.
Full polynomial multiplication verifies six identities

```
x_i^4 p_j^2 = sum(k=0..4) C_ijk(x,p) partial_k f,
```

and the corresponding g identities. The rank is NOT used alone as evidence;
the full multipliers are saved and checked. Monomials are lexicographically
ordered, and nonpivot certificate coefficients are explicitly set to zero.
These are certificate choices, not physical basis or parameter choices.

Let `L_ijk` be the sum of `|a|+|b|` for the exact coefficients `a+b omega`
of each multiplier. On unit groups every monomial has modulus at most one.
For the largest plane coordinate and largest base coordinate,
`|x_i|^4 |p_j|^2 >= 1/18`. Cauchy--Schwarz therefore gives

```
eps^2 + eta^2 >= tau = 1/[324 max(i,j) sum(k) L_ijk^2].
```

The two exact bounds are `tau_x=1/296` and `tau_u=6561/397600`.

## Exact fiber-gradient and base-separation certificates

For the actual diagonal-plus-product cubic let its homogeneous coefficients
be `A,B,C,D0`, and set `H=D0^3+27ABC`. Its three plane derivatives are q_i.
Elementary expansion gives, with cyclic `(i,j,k)`,

```
3 A_i H x_i^4 = (H x_i^2 - 9 A_j A_k D0 x_j x_k) q_i
                 + 3 A_k D0^2 x_k^2 q_j - D0^3 x_i x_k q_k.
```

Multiply by `A_j A_k/(3 lead(ABC H))` to obtain the exact saved identities
`R(mu,nu) x_i^4 = sum(k) B_ik q_k`, where R is the unchanged monic reduced
degree-six critical support. With coefficient modulus-sum bounds,

```
|R| <= C eps,   C=9 max(i) sum(k) bound(B_ik).
```

The two coprime homogeneous R polynomials give a 12-by-12 exact coefficient
system for degree-eleven base monomials. Full multiplication verifies
`mu^11=U_mu R_x+V_mu R_u` and `nu^11=U_nu R_x+V_nu R_u`.
If M bounds each of these four degree-five coefficients on the unit base,
the largest base coordinate gives

```
|R_x|+|R_u| >= s=1/(64 M),
max(eps_x,eps_u) >= e=s/[2 max(C_x,C_u)].
```

Here `2^-6` is a conservative rational lower bound for `2^(-11/2)`;
no floating-point value is used. Both base charts, including infinity, are
covered by these homogeneous identities.

## Global consequence and limits

If `eps_x >= e`, then `D >= eps_x^2 (eps_u^2+eta_u^2) >= e^2 tau_u`.
Otherwise `eps_u >= e` and `D >= e^2 tau_x`. Thus

```
D >= delta=e^2 min(tau_x,tau_u) > 0,
W_cover / pi^3 <= B=12 |scale|^2/delta,
W_quotient / pi^3 <= B/covering_degree.
```

For the ideal probability law, a variable in `[0,B]` has variance at most
`B^2/4`: subtract B/2, square, and use that variance minimizes the mean square
over constant centers. The certificate bounds are conservative; no practical
sample count is certified. Correct independent proposals, controlled numeric
input certificates, matrix integrand bounds, section throughput, integration
errors, Ricci-flat/HYM convergence, physical normalization, and a stabilized
common vacuum remain open. No point grid, observation, fitted coefficient,
or empirical extremum enters the proof.
