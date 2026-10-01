# Complete projective intersection roots

The exact integration measure is not enough to generate usable geometric
points. This prerequisite certifies roots of the actual cubic pencils
restricted to a caller-supplied line/point/line configuration. Its witnesses
are regression configurations, **not samples from the auxiliary law** and
not points chosen in extension, Kähler, or vacuum moduli.

## Reuse and demonstrated deficiency

Production exact field norms, sparse polynomial substitution, derivatives,
monic normalization, GCD, and rank checks are reused. Existing vacuum Newton
steps use machine complex values and supply no complete polynomial root
inclusion proof. MPSolve is not installed. No general numerical algebra
package or production physics algorithm is introduced for these cubics.

The projective sampling construction is the one described by
[Braun et al.](https://arxiv.org/abs/0712.3563v2). Verified root inclusions,
rather than residual-only convergence, are standard in reliable numerical
analysis; see [Rump and Oishi](https://www.tuhh.de/ti3/paper/rump/RuOi09a.pdf).
Our elementary finite-polynomial certificate is derived explicitly below;
it is not an implementation of their general nonlinear-function algorithm.

## Exact one-root certificate

For an exact Q(omega) polynomial and an exact center c, write

```text
f(c+w) = sum(k=0..n) T_k w^k,
T_k = f^(k)(c)/k!.
```

Norms are rational: `|a+b omega|^2=a^2-a*b+b^2`. To bound their square
roots without floating arithmetic, let that rational be N/D and choose
S=2^bits. With `m=isqrt(N*D*S^2)`, the bounds are
`m/(D*S)` and `(m+1)/(D*S)`, coinciding when the radicand is a square.
Their validity follows directly by squaring the two rational bounds.

On `|w|=r`, the certificate requires

```text
lower(|T_1|)*r > upper(|T_0|) + sum(k=2..n) upper(|T_k|)*r^k.
```

The right side bounds `|f(c+w)-T_1*w|`. Rouché's theorem compares f with
the linear polynomial `T_1*w`, so the disk contains exactly one root,
counting multiplicity. This also proves simplicity. A radius-zero record
instead requires the exact identities `f(c)=0` and `f'(c)!=0`.

All certificate quantities are exact. Tests reconstruct every Taylor
coefficient by the binomial theorem rather than the implementation's
derivatives, square each rational bound independently, and recheck the
strict inequality. Invalid Taylor data, bounds, radii, and duplicates fail.

## Proposals are not evidence

Simultaneous Durand--Kerner updates provide candidate centers only. Updates
are rounded to the explicitly declared omega coefficient mesh, ties to
even, preventing unbounded rational-denominator growth. Root radius,
coefficient precision, modulus-bound precision, and iteration cap are all
caller supplied. A small residual is never sufficient for acceptance.

Symmetric real proposal sets can remain real for a quadratic with nonreal
roots. Conjugation-symmetric triples can also trap a real cubic with three
distinct real roots. The fixed computational seed convention uses unequal
omega-ray radii `(1,2omega,3omega^2)`, shifted by the root mean and scaled
by a Cauchy bound. This is not a choice of physical coordinates or moduli.
There is no automatic reseeding, precision change, or fallback. Failure
within the work cap raises failed convergence, not a geometric no-go.

Acceptance requires one-root disks to be pairwise strictly disjoint and
their number to equal the polynomial's exact degree. The fundamental
theorem of algebra then proves completeness. Declared finer precision
gives independently certified smaller disks; tests establish their unique
containment in the earlier disks, not merely agreement of decimal values.

## Infinity and the actual cover

Each explicit line has basis vectors v0,v1 and parameterization
`x=s*v0+t*v1`. Exact rank rejects dependent vectors. The actual first
restriction is `mu F(x)+nu G(x)` and the second is
`2nu F(u)+mu G(u)`, both homogeneous binary cubics. The shared P1 point
is a geometric integration coordinate, not an extension or vacuum input.

In a declared parameter chart, a finite polynomial of degree m leaves
`3-m` roots at the excluded projective point. A simple infinity root is
retained as an explicit marker; it is never discarded or replaced by an
automatic chart choice. Exact GCD detects repeated finite roots; infinity
multiplicity greater than one rejects the nontransverse configuration.
The all-zero restriction, including a line contained in a fiber, also
fails explicitly. These inputs cannot silently bias a future sampler.

The Cartesian product of both complete three-root lists retains all nine
intersection roots. Saved witnesses include an actual leading-zero branch
with a simple infinity root. Independent direct substitution checks the
restricted cubic coefficients against the frozen F and G.

## Remaining physical boundary

A disk denotes an exact algebraic root of its defining polynomial, with a
certified error bound on its **center**. Centers are not exact cover points
and are never admitted through the exact `CoverPoint` constructor. Parameter
error is not automatically projective-coordinate or integral error: those
require explicit chart conditioning and propagated bounds.

This closes a root-certification prerequisite only for declared exact
Q(omega) configurations that pass the certificates. It does not implement
the SU-uniform proposal distribution, quantify its finite-precision bias,
bound section/density evaluations, certify integration accuracy, or produce
a Ricci-flat/HYM metric. Those gates, physical normalization, the common
vacuum, remaining Yukawa sectors, and Genesis-to-UV remain unresolved.
