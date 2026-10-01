# Local fibers of the actual universal metric-section basis

The frozen alternate I6 ray `(0,1)`, determinant repair `[1,2]`, twist
`H=(14,16,1)`, and symbolic extension coordinates `a0,a1` are unchanged.
The result is conditional on the selected heterotic realization. It is
local algebraic evaluation, not a numerical Hermitian metric or a vacuum.

## Restriction of the actual complex

Choose a cover point satisfying both **actual** equations, a singleton
chart `(x_i != 0, u_j != 0, p_k != 0)`, and the declared line frames
`x_i^dx u_j^du p_k^dp`. No projective coordinates are silently rescaled.
An exact Laurent monomial is evaluated only when its poles are among
these explicitly inverted coordinates.

Project to Čech degree zero and Koszul summand `k0`. Čech incidence
raises cover degree, so cannot produce a surviving local generator.
Koszul differentials into `k0` multiply the two equations; these vanish
at the validated point. Mixed Koszul and overlap terms cannot contribute
to the surviving degree-zero generators. The remaining local differential
is precisely the singleton-chart object differential, including the
Serre degree-minus-one-to-subline corrections. Omitting those corrections
would define a different bundle.

There are four V1 and five V2 degree-zero generators, with two and three
degree-minus-one relation generators respectively. Applying the actual
constituent differential and both actual outer products to the declared
relation line frames gives

```text
B(a) = [ B1   a0 E0 + a1 E1 ]
       [  0        B2       ].
```

Here `B1` is 4 by 2, `B2` is 5 by 3, and each `Ei` is 4 by 3.
The outer blocks are not discarded. Tests independently specialize the
raw Hilbert–Burch polynomials, singleton Serre terms, and saved outer
terms, without invoking the differential or cup implementations.

## An explicitly based rank-four quotient

The caller declares two pivot rows of `B1` and three of `B2`, requiring
nonzero minors. The remaining generator rows, in their named original
order, are the four fiber-basis labels. Listing admissible minors does
not select an extension coordinate or conceal a basis convention.

Let `Si` select pivot rows, `Ni` select nonpivot rows, and
`Ui = Si Bi`. Define

```text
Pi = Ni - (Ni Bi) Ui^(-1) Si
Q(a) = [ P1  -P1(a0 E0+a1 E1) U2^(-1) S2 ]
       [  0                  P2          ].
```

Direct block multiplication gives `Q(a) B(a)=0` as a polynomial identity.
The selected 5 by 5 relation minor is block upper triangular, with
constant nonzero determinant `det(U1) det(U2)` for **every** `a0,a1`.
The inclusion `R` of the four nonpivot generators satisfies `Q(a)R=I4`.
Thus `B(a)` has rank five, `Q(a)` has rank four, and
`ker Q(a) = im B(a)`. This identifies the actual local cokernel, not
merely a four-dimensional space with a matching rank count. All boundary
representatives are killed for every parameter, including the split
origin as an algebraic identity; the lawful physical family still excludes
that origin.

For another explicitly chosen frame on the **same** chart and point,
`T = Q_new R_old` gives its transition matrix. Since
`I-R_old Q_old` takes values in `im B`,
`Q_new = T Q_old`. This proves inverse and cocycle identities; independent
sparse-polynomial products verify them. These are fiber-frame transitions,
not an asserted atlas across different Čech charts. Different chart or
line normalizations are rejected by this transition API.

## Evaluating genuine sections

The independently certified universal constructor supplies a section

```text
v(a) = (v1 + a0 b0 + a1 b1, v2).
```

All four cochains are restricted to the explicit singleton chart and line
frames before applying `Q(a)`. Its parameter corrections have support only
in the upper-right block; section corrections have support only in V1.
Consequently the quadratic coefficient products vanish exactly. The output
is an exact four-vector with constant, `a0`, and `a1` coefficients.
No extension point is chosen to produce this vector.

The saved probe uses `x=(1,-1,0)`, `u=(1,1,1)`, `p=(0,1)` and chart
`(0,0,1)`: the actual cubics obey `G(x)=0` and `F(u)=0`. This is a
geometric evaluation probe, not a stabilized vacuum or a moduli selector.
The implementation also checks the complementary `mu != 0` probe and
projective rescaling invariance. No observational data are read.

Two independent actual V1 columns and two independent actual V2 columns
are found in the declared section-stream order, with their selected indices
recorded as `0,1273,2670,3973`. The two V2 columns use their genuine
universal nonsplit lifts.
Their 4 by 4 fiber matrix is block upper triangular: injected V1 columns
have zero V2 components, while the V2 block is constant. Its exact nonzero
determinant `1/81` therefore proves spanning for all extension parameters at
the probe. An independent polynomial determinant check verifies this
identity without specializing parameters.

## Scope and remaining metric gate

An on-demand exact evaluator now accepts every actual basis index in
`range(5345)` at an admissible exact cover point and an explicit fiber
frame. The artifact materializes only four actual spanning columns, not a
complete 4 by 5345 matrix, an efficient metric sampling pipeline, or a
numerical convergence certificate. Its matrices and actual column indices
are content addressed together with the frozen input artifact digests.

Étale descent does not multiply a local fiber value by `1/9`; deck
averaging is already part of the certified global section construction.
The declared local line frames are not a Hermitian or canonical physical
normalization. Ricci-flat/HYM approximation still needs controlled section
evaluation and sampling, explicit conditional moduli, a declared measure,
positivity checks, and convergence evidence. Physical Yukawas, the other
flavor sectors, shared stabilization, and Genesis-to-UV remain unresolved.

Reproduce the algebraic probe with:

```bash
python -m research.experiments.scientific_genesis.alternate_metric_fiber_evaluation
```
