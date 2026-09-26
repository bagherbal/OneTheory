# Local inverse for the alternate rank-two duality map

This calculation concerns the frozen alternate I6 constituent `F`, not
the earlier selected I6 ray. On each of its six affine charts, write its
two-term presentation on the Schoen hypersurface as

```text
R^3 --A--> M^5 --> F --> 0.
```

The signed complementary `3×3` minors of `A` form the alternating `5×5`
matrix `J`. The exact identities `J A=0` and `Aᵀ J=0` make `J` a strict
map from the presentation complex to its determinant-twisted dual: the
degree-zero component is `J`; the other degree component is zero. The
previous six-chart pairing certificate proves these identities and its
hypersurface-corrected overlap covariance. The determinant line and
frame must still be carried explicitly in any global totalization.

For ordered middle rows `u<v`, put `Δ=J[u,v]`. On the principal open
`D(Δ)`, let `S` have only `S[u,v]=-1` and `S[v,u]=1`. Direct exact Laurent
arithmetic verifies

```text
J S J = Δ J.
```

Consequently `S/Δ` is an inverse of `J` on `im J`. The local-freeness
certificate gives rank `A=3` everywhere on the declared cover. Thus
`im J=ker(Aᵀ)` and `ker J=im A` after localizing at `Δ`. Hence `S/Δ`
induces an actual inverse `F*⊗det(F) → F` on that principal open, not
merely a numerical matrix inverse at a sample point. All ten minors are
nonzero on the hypersurface at the same exact coordinate witness with
base `(1,2,3)` and fiber derived from the two equation coefficients.
Thus all sixty principal opens are nonempty. Their union covers the
rank-three locus. Different choices induce the same quotient map on
their intersections, because both invert the same `J`.

The strict Hom representative also has terms on the three right
syzygy-dual generators, so applying `S/Δ` directly to its middle terms
would discard part of the cocycle. The same minor gives a local
contraction of the full dual two-term presentation. Let `I` be the three
rows complementary to `u,v`, `B=A[I,:]ᵀ`, `D=det B`, and insert
`adj(B)` into those rows of a `5×3` matrix `T`. Then

```text
Aᵀ T = D id₃,
P = D id₅ - T Aᵀ,
Aᵀ P = 0,
P² = D P,
J S P = Δ P.
```

Thus `T/D` contracts the right syzygy-dual part, while
`S P/(Δ D)` maps the surviving dual middle component into the
quotient `F`. All identities hold over exact Laurent polynomials before
division on each of the sixty principal opens. This is a local chain
retract, not a global Čech representative.

This proves the local rank-two duality needed to convert the strict
alternate up-Higgs Hom class toward the constituent tensor. It does
**not** apply `S/Δ` to the 324-term Hom cochain. That requires restriction
to the refined minor-open cover, exact determinant/frame bookkeeping,
Alexander–Whitney-compatible Čech multiplication, and Koszul homotopies
for the hypersurface overlap corrections. Nor does it lift a resulting
tensor class through `Λ²V` on the universal outer cone. Those remain the
next chain computations before any Yukawa entry can be claimed.
