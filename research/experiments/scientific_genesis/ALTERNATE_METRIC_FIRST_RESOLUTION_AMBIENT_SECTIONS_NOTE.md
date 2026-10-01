# Actual first-resolution ambient invariant sections

The frozen alternate carrier uses the determinant-repairing common flat
character `(omega,omega^2)`. With the proved metric twist `H=(14,16,1)`
in its declared natural ambient linearization, the first Hilbert–Burch
blocks are `F0=O(11,17,2)^3` and `F1=O(10,17,2)^2`. The executable
stream specifies **13,338 F0** and **7,524 F1** invariant ambient vectors
over `Q(omega)`. These are inputs to restriction, not a quotient or
constituent section basis. No metric or physical Yukawa is claimed.

## Actual block action and structural basis proof

The polynomial coordinate substitutions and block frames are read from
the frozen first constituent, then multiplied by the common character.
For both blocks, `P^3=T^3=1`; the block commutator cancels the coordinate
commutator. In particular, the three F0 lines cannot be descended
individually. Their actual block representation is essential.

In F0, `T` is diagonal with block eigenvalues `(1,omega,omega^2)`.
Exactly one block coordinate is T-fixed for each ambient monomial.
`P` permutes block coordinates cyclically, so every T-fixed label lies
in a free three-element orbit. The sum `s+Ps+P^2s` is invariant and has
coefficient one at its canonical label. Different orbits have disjoint
support. Thus these sums are an independent spanning basis, with
`78*171*3/3=13338` members. This argument does not depend on a large
matrix-rank computation.

In F1, `T=omega^2 I`; `P` mixes the two block coordinates. Its coordinate
monomial orbits still have length three: a P-fixed x monomial would
have three equal exponents, impossible at x degree 10. The T-fixed
coordinate sector has `66*171*3/3=11286` monomials (rotation of the
x exponents balances the three T weights). For each coordinate orbit,
the two sums obtained from its canonical monomial and the two block
unit vectors are independent: projection onto that canonical monomial
recovers those unit vectors. Invariance determines the coefficients
on the other two orbit monomials. Consequently these vectors span the
invariants, with `2*11286/3=7524` members.

The artifact hashes the complete ordered streams and stores the frames
and first examples. The original exact generator verified P/T invariance
of every section. An independent verifier replays every term using
integer pairs `(a,b)` for `a+b omega`, with multiplication reduced by
`omega^2+omega+1=0`; it reproduces both hashes without the research
sparse-action implementation. Both embeddings into F7 check that ring
arithmetic independently. Source checks fix the coordinate substitutions
and exact frame coefficients, rather than trusting residues alone.

## The remaining quotient and lift

The next section space must impose both actual Schoen equations and
the Hilbert–Burch arrows. Exactness of invariants in characteristic zero
allows these relations to be imposed in the invariant block spaces.
The ambient Koszul dimensions give restricted F0 dimension
`13338-5130-6240+1800=3768` and restricted F1 dimension
`7524-2736-3520+960=2228`. These are dimension consequences of the
acyclic line/Koszul sequences already certified at this twist, not
selected complementary vectors. Their Hilbert–Burch quotient has
dimension `3768-2228=1540`.

Constructing its actual complementary vectors, lifting them through the
non-split Serre extension, and combining them with the existing 1,115
subline sections remain necessary. V2, rank-four sections, controlled
Ricci-flat/HYM convergence, the common vacuum, and physical
normalization remain open. Every statement here is conditional on the
selected heterotic Schoen realization and uses no observational input.
