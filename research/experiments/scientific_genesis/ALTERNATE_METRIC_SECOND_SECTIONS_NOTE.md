# Actual alternate V2 metric sections

At the certified generating twist `H=(14,16,1)`, the **actual alternate
second constituent** now has a complete 2,690-vector invariant section
basis: 1,135 subline sections and 1,555 genuinely lifted quotient sections.
This uses the frozen I6 character ray `(0,1)` and common determinant repair
`[1,2]`, not the reference second constituent. It remains conditional on
the selected heterotic UV realization. No outer-extension point, metric,
vacuum, mass, or mixing datum is selected.

## Actual ideal and frame

The twisted subline is `A=(15,15,0)`, the four F0 objects are `(15,12,2)`,
and the three F1 objects are `(15,11,2)`. The Hilbert--Burch ideal map is

```text
g = (u1^2*u2, u0*u2^2, u0*u1*u2, u0^2*u1).
```

Its cokernel identifies with the length-six ideal in degree `(15,15,2)`.
The source-derived repaired subline frame is `(1,1)`; the ideal-image frame
is `(omega,omega^2)`. The implementation checks `g F = character * pullback(g)`
against each actual homogeneous frame, including its fixed third F0 object.

Multiplication by an equation of pullback character `e` requires source
frame `q*e`, **not** `q/e`: acting on `s*p` in target frame `q` gives
`q*pullback(s)*e*p`. The actual equation P characters are `(omega^2,1)`.
Therefore the two source frames and syzygy frame are as follows; T
exponents are two throughout the ideal sequence.

| Term | Degree | P exponent | Invariant dimension |
| --- | --- | --- | --- |
| Ideal target | `(15,15,2)` | 1 | 5,892 |
| p1 source | `(12,15,1)` | 0 | 2,628 |
| p2 source | `(15,12,1)` | 1 | 2,568 |
| Koszul syzygy | `(12,12,0)` | 0 | 859 |

The initial inverse-character convention was rejected by exact equation-image
reconstruction before a basis artifact was written. All final relation
columns are independently reconstructed with the correct characters.

## Why the ideal Koszul sequence is exact

Write the native homogeneous coordinate ring as `Q(omega)[u0,u1,u2]`.
The actual monomial ideal has the primary decomposition

```text
I6 = (u1,u2^2) intersect (u2,u0^2) intersect (u0,u1^2).
```

Least-common-multiple intersections reproduce exactly the four minimal
generators above. Each component is primary to a coordinate-axis prime.
There is no embedded origin component. The resulting one-dimensional ring
is Cohen--Macaulay; adjoining x and P1 homogeneous variables preserves this
property. Equivalently, the source-verified length-one Hilbert--Burch
resolution has the expected depth.

Use the actual second Schoen equation first:
`p2=2 nu F(u)+mu G(u)`. On the i-th reduced axis it is
`u_i^3*(2 f_i nu+g_i mu)`. Every `f_i` is nonzero. Thus p2 avoids each
associated minimal prime and is a nonzerodivisor. Its quotient remains
Cohen--Macaulay and has no embedded associated primes. Its reduced minimal
components are the u-origin or an axis with `2 f_i nu+g_i mu=0`.

The first equation `p1=mu F(x)+nu G(x)` is nonzero on the origin component.
On an axis component it is `mu*(F(x)-g_i G(x)/(2 f_i))`, which is nonzero
because the actual F and G are linearly independent: F consists of pure
cubes with nonzero coefficients, while G also has a nonzero xyz coefficient.
Hence p1 is also a nonzerodivisor. These input conditions and the actual
primary decomposition are checked by code and independent tests.

The standard facts used here are that
[Cohen--Macaulay modules have no embedded associated primes](https://stacks.math.columbia.edu/tag/0BUS),
[proper dimension drops preserve Cohen--Macaulay quotients](https://stacks.math.columbia.edu/tag/02JN),
and [regular sequences are Koszul-regular](https://stacks.math.columbia.edu/tag/062F).
Regularity on both the ambient ring and its I6 quotient eliminates hidden
Tor in restricting the ideal to the Schoen complete intersection.

All relevant ideal twists have H0-only ambient cohomology: the native ideal
has resolution `O(-4)^3 -> O(-3)^4`, and even the smallest native degree
here is 12. All free-line terms in that resolution have nonnegative degree;
both other factors are nonnegative too. Taking exact finite-group invariants
therefore gives the displayed H0 Koszul presentation. The relation rank is
at most `2628+2568-859=4337`. An exact integral 4,337-square minor nonzero
under `omega -> 2` in F7 proves the matching lower bound, leaving 1,555
quotient basis vectors. This finite-field map is an algebraic certificate,
not a numerical approximation to physical coefficients.

## Subline stabilizers and actual nonsplit lifts

For the subline, eliminating P1 gives the actual invariant relation
`R=2 F(x)F(u)-G(x)G(u)`. The invariant polynomial target and relation
source have dimensions 2,056 and 921, leaving 1,135 sections. Each contains
one P-fixed monomial: uniform exponents five or four in both plane factors.
Such an admissible fixed orbit has coefficient one, not the factor three
of an unnormalized Reynolds sum. A nontrivial stabilizer character instead
excludes the orbit. Tests attack both cases. Multiplication by nonzero R
is injective; an independently verified 921-square minor fixes the quotient
complement, including every source relation's stabilizer normalization.

The actual F0 extension residuals are cubic polynomials in u, constant in
x, with the sole P1-overlap pole `1/(mu*nu)`. Twelve low-degree templates
cover four F0 generators times `mu^2`, `mu*nu`, and `nu^2`. Each is solved
and checked using the existing full Čech--Koszul differential. Multiplication
by global plane polynomials transports the lifts, since the primitive has
no outgoing structural arrow and the contraction acts only in P1. Actual
P orbit sums give all 1,555 invariant quotient lifts; strict T invariance
and full closure are verified for every section.

The H0 exact sequence proves that the 1,135 injected subline sections plus
these lifts form a complete, independent basis. Every archived coefficient
is in `Z[omega]`, and every P1 chart and permitted Laurent pole is explicit.
Compression only identifies the nine identical polynomial plane-vertex
restrictions. Full-cover expansion has 271,035 terms. Independent tests
replay both minors, every exact relation column, all 2,690 section
differentials and deck actions, and every prescribed quotient image. The
two pole directions and regular middle case also match the separate
full-cover homotopy engine. Dropping the actual correction fails closure.

Reproducer:

```bash
python -m research.experiments.scientific_genesis.alternate_metric_second_sections
```

Both constituent bases now exist. They are **not** a rank-four basis:
V2 sections must still be lifted through the parameter-dependent universal
outer extension. Ricci-flat/HYM convergence, physical normalization, common
vacuum stabilization, and Genesis-to-UV derivation remain unresolved.
