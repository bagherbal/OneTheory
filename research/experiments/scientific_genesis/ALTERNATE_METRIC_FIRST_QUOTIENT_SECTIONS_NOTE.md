# Actual first Serre-quotient section basis

At the declared metric twist `H=(14,16,1)`, the frozen alternate
carrier's first Serre quotient now has **1,540 explicit invariant
sections over Q(omega)**. Their canonical eight-exponent labels specify
exact three-term polynomial orbit sums. No extension parameter is
selected. These sections must still be lifted through the genuine
non-split Serre extension before they join the existing 1,115 subline
sections as a V1 basis. The construction remains conditional on the
selected heterotic realization.

## Compress the actual Hilbert–Burch presentation

The actual first matrix has columns `(x2,-x1,0)` and `(x2,0,-x0)`.
The ordered row of ideal generators is `(x0*x1,x0*x2,x1*x2)`; its
product with that matrix is zero. It is the usual resolution of the
three coordinate points, not a new fitted presentation. Multiplication
by this row identifies the ambient cokernel with
`I=(x0*x1,x0*x2,x1*x2)` in degree `(13,17,2)`.

The source-checked equivariance identity is `g P_F0 = omega^2 P(g)`
and likewise `g T_F0 = omega^2 T(g)`. Thus the ideal image has scalar
frame `(omega^2,omega^2)`, using the actual common determinant repair
and the declared natural ambient metric-twist linearization. The
individual F0 line frames are not substituted for this ideal frame.

The monomial basis of I contains precisely the x monomials with at
least two nonzero exponents. Canonical P orbit sums in the T-fixed
sector give 5,814 ambient invariant ideal sections. This replaces
the larger F0/F1 block presentation without changing its cokernel.

## Why restriction is the actual ideal Koszul quotient

Let S be the eight-variable polynomial ring over Q(omega). The
coordinate-axis ring `S/I` is Cohen–Macaulay: its three-variable part
is reduced of dimension one, with the exact coordinate-point
Hilbert–Burch resolution, and the other variables are polynomial
extensions. On its i-th axis the first Schoen equation is
`x_i^3 (f_i mu + g_i nu)`, with `f_i != 0` read from the frozen F.
It misses each minimal axis prime and is a nonzerodivisor.

The quotient by that equation is again Cohen–Macaulay and has no
embedded associated primes. Its minimal components are the affine
x-origin and the axes with `f_i mu+g_i nu=0`. On the origin the
second equation remains the nonzero polynomial `2 nu F(u)+mu G(u)`.
On the i-th axis component it becomes
`(nu/f_i)(2 f_i F(u)-g_i G(u))`, again nonzero because F(u),G(u)
are linearly independent. The actual F has only nonzero pure cubes;
the actual G has a nonzero mixed `u0*u1*u2` term. **G also has pure
cubes and must not be replaced by u0*u1*u2.** Hence the second
equation avoids every associated prime. The two equations are a
regular sequence on S/I as well as on S. The Cohen–Macaulay facts
used here are [Stacks, Cohen–Macaulay modules](https://stacks.math.columbia.edu/tag/00N2)
and [Cohen–Macaulay rings](https://stacks.math.columbia.edu/tag/00N7).

Regular sequences have exact Koszul complexes, so the short exact
sequence `0 -> I -> S -> S/I -> 0` gives exactness of the two-equation
Koszul complex on I. It also identifies the restricted Hilbert–Burch
cokernel with the actual pulled-back ideal sheaf, without a hidden
Tor term. The generic implication is [Stacks, regular implies
Koszul-regular](https://stacks.math.columbia.edu/tag/062F); the component
checks above apply it to these specific frozen equations.

Every ideal line in this calculation has x degree at least 10,
nonnegative u/P1 degrees, and no higher ambient cohomology: coordinate
point evaluation on P2 is surjective already at positive x degree.
Consequently global sections of the ideal Koszul complex are exact.
Taking finite-group invariants is exact in characteristic zero. The
source equation units shift the P-frame exponent from 2 to 1 for the
first equation and leave it at 2 for the second; T stays at 2.
The dimensions are therefore

```text
K2: 840 -> K1: 2394 + 2720 -> K0: 5814 -> quotient: 1540 -> 0.
```

In particular the exact relation image has rank
`2394+2720-840=4274`. This upper bound is derived from exactness,
not guessed from modular rank or inserted as a physical input.

## Exact complementary vectors, without a large rational RREF

The code constructs every equation image with integral coefficient
pairs `(a,b)` denoting `a+b omega`, verifies reconstruction in the
target invariant basis, and archives all 5,114 exact relation columns.
Forward elimination under the explicitly declared ring homomorphism
`Z[omega] -> F7`, `omega -> 2`, selects a nonzero 4,274-square minor.
Its determinant is nonzero in Z[omega] and hence Q(omega): a zero
algebraic integer could not have a nonzero image in F7. This is an
exact algebraic certificate, not approximate rank or a physical
finite-field model.

The remaining 1,540 canonical orbit vectors are a quotient basis.
Indeed the independent relation columns together with those coordinate
unit vectors have determinant equal, up to sign, to the certified
minor. They span the full 5,814-dimensional target space. The artifact
records the pivot rows, independent column indices, every complement
label, both archive hashes, frames, and prerequisites. Basis selection
is deterministic and explicit.

Independent tests replay every equation image directly from the frozen
cubics modulo seven, then transpose the selected minor and verify it
by row elimination. They do not call the research relation or column
elimination algorithms. This supplies a second computational path
for the actual coefficient matrix and its nonzero minor, alongside
the structural derivation of its maximal rank.

## Remaining physical dependencies

Neither ideal orbit sums nor Hilbert–Burch preimages solve the Serre
lifting equation. Its missing primitives must be derived from the
actual extension cochains. The V2 and rank-four bases, Ricci-flat/HYM
convergence, matter metrics, common stabilized vacuum, normalized
Yukawas, and low-energy predictions remain unavailable. No measured
observable has entered this construction.
