# Direct mixed-family Yoneda evaluation on the frozen carrier

Let `0 → E → V → F → 0` be the frozen alternate rank-two/rank-two
extension. The two determinant lines `L_E=det E` and `L_F=det F` obey
`L_E⊗L_F=O` on the cover. Their cohomology vanishes in every degree
in the certified determinant filtration. Thus the two exact sequences

```text
0 → L_E → K → E⊗F → 0
0 → K → Λ²V → L_F → 0
```

give a canonical isomorphism `H¹(Λ²V) ≅ H¹(E⊗F)`. This does not
construct a full Čech representative in `Λ²V`; it identifies its
cohomology class without choosing an extension parameter.

For rank-two `F`, wedge contraction and `L_E⊗L_F=O` identify
`E⊗F ≅ Hom(F⊗L_E,E)`. Let `h` be the saved strict 324-term Hom class,
`b` an exact `H¹(F)` class, and `a` an exact `H¹(E)` class. The mixed
Yukawa pairing can therefore be computed as

```text
H¹(E) × H¹(F) × H¹(Hom(F⊗L_E,E))
  → H¹(E) × H²(Hom(L_E,E))
  → H³(O)

(a,b,h) ↦ tr_detE(a ∪ (h ∘ b)).
```

This is the ordinary Yoneda/evaluation product followed by the
alternating determinant pairing. A full Hom-to-tensor chain inverse
is **not needed for this mixed-family coefficient route**. The
exterior-cone representative is still required by the broader
explicit-Higgs objective and by the parameter-linear `F-F` block.

The common-cover composition in `mixed_outer_yoneda.py` uses the
object/Koszul/Čech totalization signs. It is applied to the actual
strict classes, after the `L_E=(-2,2,0)` twist is checked against the
determinant artifact. The four resulting cochains have total degree
two and 207 terms each. Each is an exact full Čech--Koszul cycle; its
transferred reduced image lies outside the exact degree-one boundary
span. Hence all four define nonzero classes in
`H²(Hom(L_E,E)) = H²(E*)`. No random coefficients, scalar Yukawa
entry, or extension point entered this calculation.

In the exact fixed reduced basis, the two images within each tested
`F` character are proportional, not merely cohomologous. Taking the
saved seed `0` image as the reference, seed `5` has scalar
`(2-omega)/7` in character `(0,0)` and `(-3-2 omega)/7` in character
`(1,0)`. Because the subsequent determinant trace is linear, these
are also the ratios of the corresponding constant mixed-family
holomorphic entries in these *particular unnormalized matter bases*.
They are not basis-independent observables, mass ratios, or fitted
texture parameters. The absolute entries remain uncomputed.

Serre duality on the Calabi--Yau threefold gives a perfect pairing of
this `H²(E*)` with `H¹(E)`. The strict Hom character is `(2,0)`;
the two tested `F` sectors are `(0,0)` and `(1,0)`. Since `L_E` has
trivial deck character, the evaluated classes lie in characters
`(2,0)` and `(0,0)`, respectively. Their dual `E` characters are
`(1,0)` and `(0,0)`, each one-dimensional in the exact first-
constituent transfer. Consequently each tested `F` class has a
nonzero mixed-family pairing with the corresponding first-
constituent class. This is a **nonvanishing result**, not an exact
holomorphic matrix entry: the alternating contraction, scalar
residue, and common determinant/flat normalization still need to be
computed to know the coefficients and their ratios.

The next calculation should contract these four degree-two classes
with the two strict `E` classes and project the resulting degree-three
scalar cocycles to the ordered residue generator. This is a shorter
route to the constant mixed blocks than completing all minor-open
localization data first. The parameter-linear `F-F` block remains a
separate same-cone calculation.
