# Ordered reciprocal exterior products

This calculation uses the actual frozen alternate I6 resolution and the
reciprocal covectors already constructed in `alternate_up_dual_higgs_inputs.py`:

```text
h     : F → B₁⁻¹  (total degree 1)
q(eν) : F → B₁    (total degree 1), ν=0,1.
```

No extension point is selected. These are the two coefficients of the
universal extension, not two new physical inputs.

## Exterior basis and differential

F has five middle objects of internal degree zero and three syzygies of
degree minus one. Its derived exterior square therefore has 10 even-even,
15 even-odd, and 6 odd-odd objects. An odd diagonal is retained. The convention
is the ordinary exterior monomial, **not** a divided power:

```text
vᵢ ∧ vⱼ = -(-1)^(pᵢ pⱼ) vⱼ ∧ vᵢ
d(v ∧ v) = 2 dv ∧ v              when p_v is odd.
```

An internal arrow of degree s acts on the second slot with sign
`(-1)^(p_first s)`. The construction retains the full mixed coefficient of
every constituent extension term. Its result has 42 polynomial arrows and
2,349 mixed extension terms.

The cover cup is not commutative, so this construction is not asserted to
work for arbitrary twisted complexes. Here every non-polynomial arrow lands
in the same even A object. Cross terms containing two such arrows land in
`A∧A=0`; polynomial coefficients are global degree-zero sections and commute
with the cover cup. The remaining curvature terms are induced from the
already-closed constituent differential. The full implementation independently
checks its square on a regular Laurent generator in all 31×4 object/Koszul
components. All 124 witnesses vanish. Small exact fixtures additionally
differentiate the odd-square and external Koszul signs independently.

## Ordered evaluation

For covectors α and β of total degrees a and b, evaluation on an ordered
pair `i<j` is

```text
(-1)^(a pⱼ) αᵢ ∪ βⱼ
  - (-1)^(pᵢ pⱼ + a pᵢ) αⱼ ∪ βᵢ.
```

An odd diagonal is evaluated with multiplicity two. The coefficient cup adds
the product-cover Alexander–Whitney sign, the Koszul inversion sign, and
`(-1)^(Cech_degree(α) Koszul_degree(β))`. Every input and output is checked
against the declared line and total degree.

The order used here is **h first, q(eν) second**. The saved h annihilates A.
Consequently its right constituent-extension action is zero; the remaining
extension terms are associated in the order `h ∪ q ∪ extension`. Associativity
is available without using a nonexistent strict cover commutativity. No
symmetrization of the two cochain orders is silently imposed.

The actual products have 191,628 and 169,983 terms. Both are nonzero, total
degree two, and exactly closed under the complete exterior differential.
Their mathematical target is `Hom(Λ²F,O)`, a resolution of
`det(F)⁻¹=det(E)=(-2,2,0)`. It is not replaced by a literal one-object line
until a comparison is constructed.

## Primitive boundary

The checked identity is `D kν = h ∧ q(eν)` in this full resolution.
The compact polynomial-only incoming map is insufficient: it omits the
transferred constituent extension. The primitive search retains actual full
transfer on the 144 A-supported degree-one columns. The other columns of the
compact backbone are used only to propose a preimage. This candidate operator
is not itself a globally certified transferred differential. A proposed
primitive may be returned only after its full differential exactly reproduces
the actual product. A failed preimage or failed full identity raises an error;
there is no substitute coefficient or default value.

Both actual solves pass. Their primitives have 90,756 and 82,458 terms.
Each reduced preimage has support 450; projection and inclusion terminate
at depth three, and the correction homotopy terminates at depth two. The
complete identities are checked after recombining the lift and homotopy,
not merely in reduced coordinates. The content-pinned witness is
`alternate_up_exterior_higgs_action.json`; the computation and full
reconstruction regression use the corresponding Python module and test.

Even successful primitives do not supply a Yukawa matrix. Their sign must
be identified with the full exterior-cone Higgs correction and combined with
both matter-leg terms. Neither null-to-null coefficient, rank three, the full
up matrix, quotient trace normalization, matter metrics, nor a common vacuum
is inferred from this exterior calculation.
