# Structural spectrum of the alternate stable component

This note concerns the ray `(0,1)` only. Let `E` and `F` be the two
rank-two equivariant constituents, and let `V` be any non-split member of
their certified outer `P¹(Q(omega))` family. The common flat character
twist is `theta=(1,2)`. The stability statement is source-scoped to the
certified sufficient Kähler chamber `K^s`; this note does not enlarge it.

The determinant lines have cover degrees `(-2,2,0)` and `(2,-2,0)`.
Exact line transfers give zero cohomology in every degree for each line.
For any rank-two equivariant bundle `F`, exterior contraction is natural:

```text
F* = F tensor det(F)^-1
Hom(F tensor det(E), E)
    = E tensor F tensor (det(E) tensor det(F))^-1.
```

The determinant-twisted Hom transfer has `H0=0`, `H1=4`, and forward
deck characters `(0,0), (1,2), (2,0), (2,2)`. The atlas-derived action
checks every independent boundary and satisfies the `Z3 x Z3` relations.
An independent exact character calculation applies the Fourier projector
`(1/9) sum_{a,b} omega^(-ua-vb) Tr(P^a T^b)` to the saved action matrices;
it recovers the same four multiplicities without using their eigenspaces.
The product determinant has character `delta=(2,1)`. Tensor characters
before the common repair are the Hom characters plus `delta`. Since a
rank-four determinant shifts by `4 theta`, `delta+4 theta=0` modulo three.
The exterior-square tensor shifts by `2 theta`, giving repaired forward
characters `(0,1), (0,2), (1,2), (2,1)`. The established source-section
convention inverts forward characters; this set is invariant under that
inversion.

There is an equivariant filtration of `wedge^2 V` with successive pieces
`det(E)`, `E tensor F`, and `det(F)`. The two determinant pieces are
acyclic, so the associated long exact sequences give a canonical
equivariant isomorphism of `H1(wedge^2 V)` with `H1(E tensor F)`, for
**every** outer extension parameter. No chosen extension point or explicit
chain-level tensor map is needed for this cohomology representation.
The repaired determinant is trivial; self-duality of `wedge^2 V` and
Calabi–Yau Serre duality then give cover dimensions `(0,4,4,0)`.

For matter, exact mixed transfer gives `H*(E)=(0,9,0,0)` and
`H*(F)=(0,18,0,0)`. The outer long exact sequence therefore gives
`H*(V)=(0,27,0,0)` for every parameter. The published free deck action
has zero nonidentity holomorphic Lefschetz traces, so `H1(V)` is three
regular representations. Its common flat twist only permutes characters.
Calabi–Yau Serre duality gives `H1(V*)=0`. Under the fixed published
Spin(10) Wilson weights, the `16` sector therefore has three families
including three right-handed neutrinos and no anti-families. In the `10`
sector, the inverse-weight test retains one up-type and one down-type
doublet character, but neither color-triplet character. These are
**selected structural-spectrum constraints**, not predictions from
foundational Genesis.

The theorem does not generate strict cone-level matter/Higgs cocycles,
`H*(End V)`, Yukawa products, a compatible hidden sector, or a stabilized
vacuum. In particular, the cohomological isomorphism is not a substitute
for the chain representatives needed to compute a Yukawa matrix. Its
evidence is the content-addressed structural-spectrum artifact; the
published free quotient and Wilson embedding remain selected inputs.
