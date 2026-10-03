# Projective intersections with uncertain input coefficients

## Declared edge and reuse

The controlled projective input-cell node cannot feed the existing exact-only
root engine by substituting its centers: that would discard the proposal error.
This experiment closes the root-inclusion edge **on admitted coefficient cells**.
It reuses the actual cubic pencils, original exact root proposals and Taylor
certificates, and established circular arithmetic. It does not implement another
root solver, RNG, integration law, physical carrier, or numerical metric.

## Uniform one-root theorem

In a declared projective chart write

```
P(z)=sum(j=0..3) a_j z^j,
|a_j-a_j^0| <= e_j.
```

For an exact center c and positive radius r, the existing center-polynomial
certificate bounds its Taylor coefficients T_k. Put

```
M >= |c|+r,
E=sum(j=0..3) e_j M^j.
L=lower(|T_1|)*r,
R=upper(|T_0|)+sum(k>=2) upper(|T_k|)*r^k.
```

If **L > R+E**, every coefficient choice in the cell has exactly one simple
root in that disk. Indeed on its boundary |P-T_1(z-c)| <= R+E < L;
[Rouche's theorem](https://complexanalysis.org/web/sec_argument-rouche.html)
compares it to the same linear polynomial. The proof uses a bound for the
whole disk, not a small residual at its center. Correlations between input
coefficients may be dropped to enlarge the certified family safely.

## Infinity, overlap and completeness

Binary coefficients are ordered as s^3, s^2 t, s t^2, t^3. Chart zero sets
s=1 and uses z=t/s; chart one sets t=1 and uses w=s/t. The center polynomial
may have a simple infinity root. It is covered by a **positive-radius** chart-one
disk, not a fixed infinity marker: a nonzero perturbed t^3 coefficient moves it.
The other declared starting chart is handled symmetrically. No automatic chart
or precision fallback is permitted.

Same-chart disks are disjoint by the exact center-distance inequality. For
opposite charts a common point would have z*w=1. Their product lies in the disk
with center c*d and radius |c|*r_d+|d|*r_c+r_c*r_d. Certifying that this disk
excludes one proves projective disjointness, including centers zero at opposite
chart origins. Three such disks, each with one root, exhaust every nonzero
homogeneous cubic in the coefficient cell, counting multiplicity on CP1.
Possible degree loss in either affine chart does not lose a projective root.

## Actual input construction

A caller declares the hyperplane pivot and ordered two free coordinate axes.
Its covector component must exclude zero. The parameter basis is
x_i=s, x_j=t, x_p=-(h_i*s+h_j*t)/h_p. Circular arithmetic encloses all its
coefficients; the exact center defines only a proposal line. Original cubic
monomials are restricted by finite coefficient convolution, with all errors
retained. The actual first pencil is mu F(x)+nu G(x); the second remains
2nu F(u)+mu G(u). An uncertain base must exclude the zero homogeneous vector.

This supports the nine-root line/base/line component and both three-root
point/line components. In the latter, source points determine the base by
[-G(x):F(x)] or [-2F(u):G(u)] using the unchanged cubic equations. All roots
are retained, and homogeneous coordinate disks propagate both line and root
uncertainty. They are coupled enclosures for actual cover points, **not**
exact field points and not inputs to the exact CoverPoint constructor.

## Failure and remaining work

An uncertified pivot, possible source base point, repeated center root, failed
uniform margin, or overlapping disks returns no accepted configuration. It is
not a geometric no-go. A sampler must refine the original input bit streams,
with declared root policies, rather than replace troublesome configurations.
The declared probes are deterministic regression cells, not independent draws.

Global numerical input coverage, a law-preserving stream/refinement workflow,
uniform selection of one root per independent configuration, density/frame and
section bounds for these new uncertain domains, finite-cloud integration errors,
practical section throughput, Ricci-flat/HYM convergence and a common vacuum
remain required. No physical parameters or observational inputs are selected.
