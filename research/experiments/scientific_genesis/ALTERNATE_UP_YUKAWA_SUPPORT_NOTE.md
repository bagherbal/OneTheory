# Universal up-Yukawa support on the frozen alternate component

This is a structural statement about the exact non-split universal family
`0 → E → V(a) → F → 0`, where `E` and `F` have rank two and
`a=(a0,a1)`. It does not calculate a coupling. The common flat twist is
suppressed in the exterior-degree notation; it changes characters but not
these support or parameter-degree arguments. No projective point is chosen.

The exact constituent transfers give `H²(E)=0`. A class in `H¹(E)` thus
has a constant representative in `V`, while every needed `H¹(F)` class
has an exact lift of the form `f + a0 e0 + a1 e1`. The eight explicit
matter-correction identities certify those lifts in the frozen component.

Put `K=ker(Λ²V → det F)`. The filtration is
`det E ⊂ K ⊂ Λ²V`, with `K/det E = E⊗F`. Both determinant endpoints are
acyclic, so `H¹(Λ²V) ≅ H¹(E⊗F)` canonically. A fixed middle class `h`
can be lifted to `K` as `h + a0 k0 + a1 k1`: the only new differential
lands in `det E` and is linear in the universal outer arrow; acyclicity
provides a primitive for each coefficient. This is an existence and
support argument, **not** a constructed full Čech Higgs cocycle.

In the determinant pairing, only terms with exactly two `E` factors and
two `F` factors survive. Hence:

| Matter types | Possible extension degree | Reason |
| --- | --- | --- |
| `E,E` | none | The Higgs has no `det F` component. |
| `E,F` or `F,E` | zero only | One constant `E⊗F` Higgs term survives. |
| `F,F` | one only | One matter correction or the `det E` Higgs correction survives. |

For each of the two physical up-type Wilson sectors, the certified basis
has one `E` class and two `F` classes. In this filtration-adapted basis,
the universal holomorphic matrix therefore has the *form*

```text
Y(a) = [ 0       B      ]
       [ C  a0 D0+a1 D1]
```

where `B` is `1×2`, `C` is `2×1`, and `D0,D1` are `2×2` matrices of
**uncomputed** exact couplings. These letters denote unknown results,
not generic or fitted physical coefficients. Every potentially nonzero
determinant monomial uses one `B`, one `C`, and one linear `D` entry.
Therefore `det Y(a)=a0 λ0+a1 λ1`, with `λ0,λ1` still uncomputed. If
both vanish, no member has rank three at this order. Otherwise exactly
one point of the projective `P¹(Q(omega))` family has zero determinant.
The rank at that point, and every matrix entry, remain unknown.

This theorem changes the next rank test: once the same-cone Higgs chain
class and contraction exist, two exact determinant coefficients decide
whether generic rank three is possible. A full matrix is still required
to complete the scientific objective. Character support alone cannot
establish that any allowed entry is nonzero.
