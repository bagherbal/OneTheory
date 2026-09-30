# First actual invariant subline sections

At the proved ample metric twist `H=(14,16,1)`, the frozen alternate
carrier's first Serre subline has cover degree `A=(13,17,0)`. This note
constructs its **1,115 quotient sections** in the actual equivariant
frame. They are a subline basis, not the 2,655 sections of `V1(H)` and
not the 5,345 sections of the rank-four bundle.

The two published Schoen equations are linear in the common base
coordinates `(mu,nu)`. Their determinant eliminates that base:

```text
R(x,u) = 2 F(x)F(u) - G(x)G(u),  bidegree (3,3).
```

The projection of the cover to `P2_x × P2_u` has this single
scheme-theoretic hypersurface equation. The Koszul exact sequences
identify the actual section space as the principal quotient

```text
H0(cover,A) = S_(13,17) / R S_(10,14).
```

This is why its dimension is `17,955 − 7,920 = 10,035`, not the
ambient `17,955`. The complete eliminated relation is read from the
frozen `F,G` cubics; no coefficients are fitted or guessed.

The first atlas has subline scalars `(ω²,1)`. The frozen alternate
carrier applies the determinant-repairing common flat character
`(ω,ω²)` to both constituents, so the **actual** subline frame is
`(1,ω²)` after tensoring `H` with its declared natural commuting
ambient-coordinate linearization. Another flat character choice for
`H` would shift the selected invariant sector and must be recorded
separately. The coordinate substitutions make `R` invariant under both
generators. In each ambient bidegree, `T` is diagonal and `P` has
three-element monomial orbits. Summing each orbit in the actual
`T`-fixed character sector with its
exact `P` coefficients gives 1,995 invariant ambient vectors at
degree `(13,17)` and 880 at `(10,14)`. Multiplication by `R` is
injective and equivariant, so the quotient invariant dimension is
`1,995 − 880 = 1,115`.

The executable certificate constructs every invariant ideal column
and uses exact sparse elimination to select 1,115 complementary
canonical orbit sums. The artifact lists their six-coordinate
monomial labels. Together with the recorded frame and the frozen deck
substitutions, each label specifies an explicit three-monomial global
section; the artifact also hashes the full exact ideal matrix. An
independent finite-field specialization checks that the selected
complement and ideal columns span the full ambient invariant space.

This construction is conditional on the selected heterotic Schoen
realization. It does not lift Hilbert–Burch quotient sections through
the non-split Serre extension, construct `V2` sections, assemble a
rank-four basis, or compute a metric or physical Yukawa.
