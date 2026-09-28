# Signed alternate first-order scalar

This experiment uses the frozen alternate carrier, its two declared outer
coefficients, and the determinant-sensitive null combinations already fixed
by the mixed up-sector block. It does not choose an extension point or use
observational data.

## Two-slot action, not a guessed primitive sign

The global signed-minor row is a degree-zero chain map `q_E:E→B₁`, with
`B₁=(-1,1,1)`. It kills the first A object and both first syzygies exactly.
The saved Higgs covector is `h:F→B₁⁻¹` of total degree one; equivalently,
it evaluates `B₁⊗F→O`. The mixed Higgs functional therefore applies the
global quotient before h. No non-global coefficient is commuted through h.

Write `p_i` for the internal degree of the i-th F object. The actual
degree-one quotient extension `q(eν):F→B₁` acts on an ordered exterior pair
as follows, with B₁ written first in the target:

```text
i∧j → q(eν)_i ⊗ j - (-1)^(p_i p_j) q(eν)_j ⊗ i.
```

The second-slot sign includes moving the extension coefficient past the
first internal vector. On an odd diagonal the two terms add. This is a
map into `B₁⊗F`, not a replacement of the exterior resolution by a literal
determinant line.

Now compose h after this map using the existing signed Hom composition.
For the first slot, h_j has external degree `1+p_j`; the Hom composition
contributes `(-1)^(p_i+p_i p_j)` relative to the ordinary coefficient cup.
For the second slot, the combined coefficient is `-(-1)^p_j`.
These are exactly the negatives of the two coefficients of the ordered
covector product `h∧q(eν)`. This derivation uses neither cover
commutativity nor a guessed minus sign.

The implementation constructs both full slot maps and composes them.
The resulting 191,628- and 169,983-term cochains equal `-h∧q(eν)` exactly
and are full cycles. Consequently the already checked primitive kν enters
with **positive** sign: `D kν + actionν = 0`. Independent small fixtures
exercise even/odd slots, ordinary odd diagonals, and Čech/Koszul crossings.

## Actual matter inputs

The required F representatives have only internal-degree-zero support,
including their A and F0 objects. Their four ordered wedges have respectively
2,169, 2,322, 2,349, and 2,211 terms. The null-to-null wedge has 2,997 terms.
Each is nonzero and closed under the complete exterior differential.
This is checked on actual cochains, not inferred from dimensions.

For each parameter, the null matter corrections satisfy
`D xL=-eν bL` and `D xR=-eν bR`. The solve and exact character average are
the same linear operations used for the saved matter lifts. Applied to the
null combination, they equal the corresponding linear combination of
those lifts; no new physical matter basis is selected.

## Ordered three-term screen

The candidate is evaluated in the literal order

```text
h ∪ (q_E(xL) ⊗ bR - bL ⊗ q_E(xR)) + kν ∪ (bL∧bR).
```

The first parenthesis includes both matter legs. Its coefficients are
retargeted explicitly to `B₁⊗F`; this common line twist changes neither
their Hom grading nor their monomials. Odd F inputs are rejected because
this particular tensor helper is scoped to the actual even matter support.

The full scalar differential is evaluated before any trace. A nonclosed
candidate carries no residue, including in the immutable screen record.
Successful local signs, primitive identities, and matter-wedge closure
alone do not prove that this ordered tensor construction is the derived
exterior pairing of the physical cone. The complete derived tensor
comparison, quotient trace convention, full matrix, canonical metrics,
and common vacuum are not claimed by this screen.

## Primitive-free closure test

Let δν be the two-slot quotient extension map above and let
`w=bL∧bR`. The same defect can be calculated without either the matter
homotopies or kν:

```text
Tν = (q(eν) bL) ⊗ bR + bL ⊗ (q(eν) bR) - δν(w)
D scalarν = h ∪ Tν.
```

Indeed `D q_E(x)=-q(eν)b`, h is closed, `D kν=h∧q(eν)`, and w is closed.
The possible constituent-action crossings in the intermediate tensor land
in the F A object, which h annihilates. The two-slot composition is the
already checked negative exterior product. These identities leave exactly
the displayed ordered tensor Leibniz difference. The implementation compares
this primitive-free expression with the **full** scalar differential; it
does not replace that differential by a projected cohomology zero.

This test identifies a possible missing comparison homotopy before another
large primitive solve. Strict commutativity of the ordered cover product
is not inserted as an axiom, including when the matter wedge itself is closed.

## Natural quotient cone

The signed action also has a concrete geometric target, without pretending
that the entire naive exterior of a twisted Čech complex is already certified.
Push out the actual sequence `0→E→V→F→0` along the **global** map `E→B₁`.
The resulting sequence `0→B₁→R→F→0` defines a rank-three bundle R. This
argument does not assume that E maps surjectively to B₁: its image is the
published ideal times B₁, and the pushout is an extension nonetheless.

Locally splitting the extension gives the exact exterior sequence
`0→B₁⊗F→Λ²R→det(F)→0`. Now use the actual Serre quotient
`F/A_F=I₆ B₂` and push out its left term:

```text
0 → B₁⊗F      → Λ²R → det(F) → 0
       ↓           ↓      ║
0 → K          → Q   → det(F) → 0
    K=B₁⊗I₆B₂
```

Q is a coherent quotient, not an additional physical vector bundle.
Its natural map from `Λ²V` is obtained by exterior functoriality followed
by this pushout. At the zero scheme of A_F, the sheaf injection remains
injective; a fibrewise subbundle assertion would be incorrect.

K has the seven-object, six-arrow Hilbert--Burch resolution obtained by
removing the A object from the actual F resolution and tensoring by B₁.
All constituent extension terms disappear under this legitimate quotient.
The saved Higgs factors through K and remains the same full 324-term cycle.
The two connecting arrows are the projected two-slot actions, with their
indices and line degrees checked against `Hom(Λ²F,K)`.

The implementation requires each connecting arrow to be a nonzero **full**
cycle. This supplies the coefficientwise square-zero condition for the
triangular universal quotient cone, not merely a dimension count. Its Higgs
action is recomposed on these actual quotient objects and checked against
the pinned full exterior product. A failed arrow or failed comparison
prevents this construction from being returned.

The matter comparison must also be checked **before** the Higgs annihilator.
The experiment retains the raw tensor difference and its projection to K;
`h∪T=0` is not by itself evidence that `T=0`. The scalar screen therefore
continues to distinguish a closed ordered expression from a fully identified
physical pairing.

Both actual quotient connecting arrows pass the full differential check:
their term counts are 103,986 and 87,354 for `(a0,a1)`. Their recomposed
Higgs actions reproduce the negative pinned exterior products exactly.
The unprojected tensor differences have respectively 31,668 and 30,234
terms, **all** in the actual A target. Thus each comparison vanishes
on K before applying h; this is stronger than scalar annihilation.

The quotient certificate reuses the content-pinned **full** primitive
identities from the exterior experiment, rather than claiming to rerun
their solver. The actual-cochain cocycle factory separately reconstructs
k and checks `D k + action=0` before returning a universal covector.
The certificate records this distinction explicitly.

## Scientific boundary

The sheaf pushouts provide a natural map `Λ²V→Q`. A cochain realization
of that map, with its tensor-product comparison, still has to identify
the ordered screen with the physical Higgs pairing. The null comparison
above is checked on its actual inputs; it is not a chain-map theorem
for arbitrary inputs or an implicit strict-commutativity convention.

In addition, the determinant trivialization, inherited deck linearizations,
and quotient trace must be fixed together. The common flat repair of V
must not be replaced by an independently chosen phase of a Higgs helper.
A cover residue in the declared generator is not a silently normalized
quotient coupling. None of these calculations supplies canonical matter
metrics, a stabilized common vacuum, or physical masses.

## Complete ordered residues

Two independent full reconstructions agree coefficientwise:

| Parameter | Complete scalar terms | Full differential | Ordered cover residue |
| --- | ---: | --- | --- |
| a0 | 42,302 | zero | 0 |
| a1 | 41,454 | zero | `(2673-486ω)/49` |

Both trace projections terminate at depth three. The a0 matter/Higgs-leg
term counts are 27,374/30,155; the a1 counts are 26,409/29,950. Every
primitive differential is checked before forming the sum, and the sum's
**full** differential is checked before projection. These residues are
not obtained by tracing either nonclosed matter leg separately.

The a1 result is nonzero in `Q(ω)`, so this ordered screen does not support
a permanent vanishing claim. If its pairing is identified with the
physical one, the established linear determinant reduction would give
generic rank three off `a1=0`, with nonzero normalization factors unable
to change that rank locus. This is a conditional implication, not a
physical rank assignment: the comparison and conventions above remain
required. Close that gate before an arbitrary higher-product ladder.

The content-addressed outputs are `alternate_up_higgs_quotient_cone.json`
and `alternate_up_first_order_scalar.json`. Neither chooses a P1 point
or uses measured masses, mixing angles, or fitted geometry.
