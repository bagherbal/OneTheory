# Natural Higgs quotient: class, product, and trace are separate gates

Use the frozen alternate family `0→E→V(a)→F→0`, not a new carrier or
an arbitrarily chosen point of its projective parameter line. Its actual
global signed-minor map is `q_E:E→B₁`. Pushing out gives the bundle
extension `0→B₁→R(a)→F→0`. Exterior functoriality and the actual Serre
quotient `F→I₆B₂` give

```text
0 → B₁⊗F → Λ²R(a) → det F → 0
       ↓       ↓        ║
0 → K     → Q(a)    → det F → 0,     K=B₁⊗I₆B₂.
```

There is a natural sheaf morphism `Φ:Λ²V(a)→Q(a)`. K and Q are coherent
sheaves, not additional physical bundles. No fibrewise subbundle assertion
is made at the zero scheme of the Serre section. The existing quotient
cone computes the signed two-slot connecting arrows on the actual graded
F resolution; a full cochain realization of Φ remains a distinct gate.

## Uniqueness at the cohomology-class level

The alternating graded line data of the actual rank-two constituents give
`det E=(-2,2,0)` and `det F=(2,-2,0)` in the declared cover basis. Existing
determinant-filtration certificates show that both lines are acyclic.
A fresh check with the standard ambient Čech basis finds no basis vector
in any possible total degree `-2,…,5` for either line: one object has
internal degree zero, the Koszul degrees are `0,-1,-2`, and the ambient
cover has Čech degrees `0,…,5`. Thus every ambient-cohomology term is
zero before any transferred differential is applied. This check does
not assume cancellation of a large differential or numerical convergence.

Independently, the ambient Koszul line degrees give a short vanishing proof:

| Line | k₀ | k₁,x | k₁,u | k₂ |
| --- | --- | --- | --- | --- |
| det E | (-2,2,0) | (-5,2,-1) | (-2,-1,-1) | (-5,-1,-2) |
| det F | (2,-2,0) | (-1,-2,-1) | (2,-5,-1) | (-1,-5,-2) |

Each triple has a P² factor of degree -1 or -2, or a P¹ factor of degree
-1. Such a factor has no cohomology in any degree. Künneth therefore kills
every ambient group, and the bounded Koszul spectral sequence has zero
limit. The exact regression derives both determinant degrees from the
graded objects and also checks that the unit line is not declared acyclic.

Apply derived Hom into O to `0→K→Q→det F→0`. Since
`(det F)*=det E` is acyclic, restriction induces an isomorphism

```text
Ext¹(Q,O) → Ext¹(K,O).
```

Consequently the actual closed h_K class has a unique class lift through
the natural sheaf Q. This is uniqueness modulo boundaries, not a unique
Čech representative or a licence to choose a correction sign. The saved
full primitive identities `Dκν+h_Kδν=0` supply representatives of a lift
on the implemented quotient cone. They must not substitute for proving
that a proposed matter-product map realizes the natural sheaf morphism Φ.

On the middle exterior-filtration term, pullback by Φ restricts to
`E⊗F → B₁⊗I₆B₂`. The signed-minor row agrees with the fixed rank-two
determinant pairing in the certified local Plücker orientations. Hence
the pullback of the natural class restricts to the original strict Hom
Higgs class. The acyclic determinant endpoints identify this middle class
with a class in `H¹((Λ²V)*)`. The repaired trivial determinant gives
`(Λ²V)*≅Λ²V`. These sheaf-level statements identify the class; they do
not by themselves evaluate its pairing on specific cochain products.

## No freely chosen quotient-line character

The full global q_E row has 54 terms, one polynomial map on every product
cover vertex. Acting with the declared E frame and initially trivial B₁
frame gives a scalar multiple μq_E. Equivariance forces the B₁ frame to
be μ⁻¹. The exact full-row checks force frames `(ω,1)` for `(P,T)`;
they are not selected to reproduce the one-Higgs constraint.

The quotient K frame is the inherited B₁ frame times the actual F/A frame.
The exterior F frame expands ordinary graded exterior monomials, retaining
odd diagonals and their factors of two. Full h_K and connecting-arrow
covariance must be checked in these frames, not inferred from a determinant
character alone. Their dedicated artifact records the outcome.

The native covector character is `(2,0)`. A common flat twist χ=(1,2)
acts on an exterior-square covector with weight -2, giving
`(2,0)-2χ=(0,2) mod 3`. The repaired determinant is neutral, so the
covector-to-forward-Higgs identification preserves that character. No
arbitrary phase average or change of primitive sign is needed to choose
the cohomology-class lift.

## Attack the ordered candidate rather than declare it physical

The ordered three-term null scalar is full closed for both outer
coefficients. Its cover residues are `0` and `(2673-486ω)/49`. This alone
does not identify the candidate with the product induced by Φ.

A necessary attack exchanges the actual two matter inputs while keeping
h_K and κν unchanged. The expected physical sign is positive: exchange
of two degree-one classes and exchange of their two exterior bundle slots
each contribute a minus sign. The exchange experiment records the actual
reverse closure defect and residue. When the residues agree, it requires
an exact primitive of `reverse-forward`, checked by the full differential.
A failure refutes this particular ordered comparison, not the carrier or
heterotic theory. No symmetrizing average is allowed to conceal it.

Both actual exchange tests pass. The reversed scalars have 42,299 and
41,442 terms, are full closed, and retain residues `0` and
`(2673-486ω)/49`. Their differences from the forward scalars contain
37,786 and 37,198 terms. Full checked primitives contain 21,964 and
21,817 terms, with homotopy depth three in each case. The compressed,
content-addressed archive preserves both forward and reverse scalars,
the unchanged exterior primitives, and these exchange primitives. Its
loader rechecks the full differentials rather than rerunning the solver.
These are exact boundaries for the declared null inputs, not an all-input
derived tensor comparison or independent external proof of that map.

The trace has an independent check. In the scalar O_X Koszul resolution,
H³ is the ambient k₂ H⁵ monomial with all eight exponents -1 on the full
ordered cell. Koszul perturbations strictly lower the subset while the
Čech homotopy preserves it, so every positive-order projection correction
misses k₂. The literal coefficient is therefore the ordered cover residue
of a full cycle, independently of the HPL projection algorithm. This
functional refuses noncycles and has trace one on the declared cover
generator. It does not choose a physical or quotient normalization.

The exact single-coefficient evaluator in the existing common-cover
algebra follows the same cup definition without materializing every
output. A target cell fixes the right suffix of each left prefix. Its
Koszul subset fixes the complementary right subset, and its exponents
fix the inverse right monomial. If that monomial is not regular on the
required suffix, it cannot occur in the right cochain. The remaining
coefficient sum uses the declared Čech/Koszul crossing signs. Tests compare
it with full convolution and the independent Hom composer over the small
Koszul sign table, shifted objects, and exact cancellations. This operation
can evaluate a coefficient of a noncycle; it is not a trace or a closure
certificate. A residue still requires the independent closed-scalar gate.

Even a passing exchange attack does not prove the all-input derived
tensor comparison, representative independence, or its compatibility
with Φ. A closed lift of a matter product can still differ by a K class;
the uniqueness of the Higgs-class lift does not remove that ambiguity.
Those product gates must close before the nonzero a₁ screen is assigned
to a physical holomorphic determinant or a complete matrix.

The first indeterminacy checks are now exact, without confusing an
E*-valued boundary with a line boundary. Both actual 90-term primitives
have only the A-row component. Retargeting to `B₁⁻¹` preserves every
component, monomial, and coefficient, and its full line differential
equals the actual ordered product `h∪b_null`. Thus these particular
null products really are boundaries in the line subobject.

The inverse quotient line has complete cover cohomology `(0,0,9,0)`.
Its only nonzero ambient group is the k₁,u term with line degree
`(1,-4,-2)` and ambient cohomological degree three. No differential can
enter or leave the resulting single total degree two. Therefore H¹ is
zero and the line primitive is unique modulo boundaries. This argument
does not say that every boundary in E* has the same property.

The actual ideal quotient also gives `Hom(det F,K)=0`: the complete
ambient Hom complex has dimensions 108 and 72 only in total degrees one
and two, with no degree-zero group. The exact transferred computation
agrees. Consequently a morphism between the relevant sheaf extensions
with fixed endpoint maps is unique **if it exists**. The difference of
two such morphisms factors through `det F→K`, which must be zero.

The remaining group has also been computed, rather than assumed absent.
The complete ambient K complex has dimensions `90,152,70,8` in total
degrees zero through three. Exact transfer gives cover cohomology
`H⁰,…,H³(K)=(0,5,5,0)`. In particular H²(K) is five-dimensional. This
is the full cover group, not a selected-character dimension or an assertion
that every class occurs as a reachable comparison correction.

These results are stored in `alternate_up_null_line_homotopies.json`,
including the real short primitive terms. They may remove the contribution
of some reachable tensor homotopies. They do not identify a proposed
matter-product lift merely because it is closed: its possible H²(K)
difference is not the degree-zero Hom group just computed. Complete
comparison indeterminacy and agreement with Φ remain open.

## A limited consequence: independence of the matter lift

For the **natural sheaf product**, the checked null line boundaries do
remove the choice of a lift in `H¹(R)`. Two lifts of the same F class
differ by the image of some `α∈H¹(B₁)` in the exact sequence for R.
Changing one matter lift changes its exterior product, after projection
to Q, by the mixed class `α⊗b` in H²(K), with the declared grading sign.
Pairing this with the restricted Higgs class h_K is the cup of α with
`h∪b∈H²(B₁⁻¹)`. For either actual null b, that latter class is zero by
the full line primitive identity, so its trace is zero. If both lifts
change, the additional B₁/B₁ product is zero because `Λ²B₁=0`.

Thus the natural null-pairing value is independent of the choice of
matter lifts, without assuming H¹(B₁)=0. This argument is in sheaf
cohomology with its natural exterior product; it is not an assertion of
strict commutativity of the ordered Čech cochains. It removes lift-choice
indeterminacy, not the discrepancy between an arbitrary closed candidate
product and Φ. That latter discrepancy may still be an H²(K) class
which does not arise from changing either matter lift. The implemented
ordered scalar still needs the natural product comparison.

Nor can every H²(K) discrepancy be declared trace-invisible. On the smooth
projective Calabi--Yau cover, Serre duality pairs `Ext¹(K,O)` perfectly
with H²(K), with values in H³(O). The h_K class is nonzero: a boundary
on K would pull back to a boundary for the already certified nonboundary
strict Higgs on `B₁⊗F`. Its functional on H²(K) is therefore nonzero.
Some K-class change can change the residue. This is a class-level
statement about the full cover group, not a claim that such a change is
reachable by a legitimate natural-product comparison. It rules out
discarding that remaining gate solely from the null line homotopies.

## The raw product fails a representative-independence attack

There is now an actual failure, not just a possible ambiguity. Project the
local section `x₁ u₀⁻⁴ p₀` in F's first even Hilbert--Burch generator
onto native character `(0,0)`, using the fixed exact deck frames. This
gives a three-term degree-zero cochain c. Its full differential has 15
terms and is strictly in that same character. Replacing the left null
matter representative b_L by `b_L+D_F c` preserves its cohomology class,
closure, and character. No new physical input or extension point is chosen.

The original raw null wedge is closed. Its boundary variation
`W(D_F c,b_R)` has 284 terms and a 124-term full differential. Hence the
raw ordered wedge does not even preserve cycles under this exact change
of representative. The 48-term Leibniz defect

```text
L = D_ext W(c,b_R) - W(D_F c,b_R)
D_ext L = -D_ext W(D_F c,b_R)
```

is saved in full, along with c, its boundary, and the closure defect.
This refutes the raw wedge as an all-input cohomological product on the
actual F model. It does not refute the carrier, the original closed scalar
screens, or the existence of the natural physical product.

## A derived repair on the even-object sector

The missing coefficient-order homotopy can be constructed in the fixed
ordered cover. On simplex chains use

```text
H[i,j] = -[i,j] ⊗ [i,j]
H[i,j,k] = [i,j,k] ⊗ ([i,j]+[j,k]) - [i,k] ⊗ [i,j,k].
```

Contraction to the first ordered vertex derives these formulas. Direct
chain boundaries give `∂H+H∂=AW-τAW`. On the three-factor cover, telescope
with `Hx⊗AWu⊗AWp + τAWx⊗Hu⊗AWp + τAWx⊗τAWu⊗Hp`, retaining the
tensor-operator and output-braiding signs. Independent chain enumeration
verifies this identity on all 147 cells, not just selected matter inputs.

For scalar Koszul cochains the totalization sign is
`(-1)^(s_left+s_right+Cech_degree(left)*s_right)`, in addition to the
Koszul coefficient-product sign. Here s is the structural Koszul degree.
The resulting H has total degree -1 and satisfies

```text
dH(a,b) + H(da,b) + (-1)^|a| H(a,db)
    = a∪b - (-1)^(|a||b|) b∪a.
```

Full scalar tests include the hypersurface-equation differential. This
operation refuses matrix components; it cannot interchange their order.

In the even-object sector of F, let α_j be the actual scalar arrow from
the j-th generator into the single even A target. These arrows are full
degree-one cycles. The mixed differential's stored parent-zero term has
the opposite sign to its left action, so α is **minus** that stored
coefficient. This follows directly from the existing differential, not a
choice made to repair a scalar residue; h and κ are unchanged.

For even-object inputs the raw wedge defect is the coefficient commutator
`(α_j∪u_i-(-1)^|u|u_i∪α_j)∪v_j` in `e_i∧A`. Therefore define

```text
P(u,v) = W(u,v) - Σ_(i,j) H(α_j,u_i)∪v_j · (e_i∧A).
```

The scalar homotopy cancels the commutator. Additional twisting terms land
in `A∧A=0`, because the target has no self-arrow. This proves the signed
Leibniz identity on this even sector. Full Cech--Koszul regression tests
include noncycles and every Koszul subset pair; unsupported odd objects
and a non-nilpotent target are explicitly rejected.

For the actual attack, `P(D_F c,b_R)=D_ext W(c,b_R)` exactly. The
corrected boundary wedge has 302 terms and zero full differential. The
actual original null wedge receives zero correction and remains the same
2,997-term cochain. Thus this repair passes the exhibited boundary attack
without changing its original scalar inputs. The corrected cochains and
their scoped flags are recorded in `alternate_up_exterior_boundary_attack.json`.

This is not yet the complete tensor comparison. Syzygy representatives
and the outer cone require their own compatible correction. In particular
the natural map Φ and all-input physical pairing remain unresolved, and
the five-dimensional H²(K) ambiguity has not been removed. No rank-three
conclusion, full matrix, or physical observable is assigned here.

For a ninefold finite étale map π, a quotient trace is cover trace divided
by nine **if** the holomorphic volume form and descended sections are
declared to obey the corresponding pullback conventions. No such factor
is silently inserted here. Determinant orientation, the Higgs/matter
bases, and this descent convention must be explicit together. Canonical
metrics, a common vacuum, and low-energy observables remain unavailable.
