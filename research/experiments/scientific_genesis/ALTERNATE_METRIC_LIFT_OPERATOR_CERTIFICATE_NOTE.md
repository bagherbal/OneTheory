# Independent closed-residual lift certificate

This result closes the **full universal lift-formula** verification gate,
without expanding 5,380 parameter coefficients. The alternate carrier, twist
`H=(14,16,1)`, determinant repair, and symbolic parameters remain unchanged.

## A finite verification of an infinite Laurent complex

The raw Čech differential and homotopy preserve the Laurent monomial and
object/Koszul component. Their matrices depend only on the negative support
of the monomial and the parity of the structural degree. Magnitudes of the
exponents do not enter either operation. Consequently the infinitely many
Laurent monomials reduce to `2^3 * 2^3 * 2^2 = 256` support patterns, each
with two structural parities. This is a complete finite category, not a
sample of carrier sections.

The verifier constructs differential columns by transposing oriented face
deletion, using Python integers. It constructs `Q=i p` from evaluation at
vertex zero in H0 and the unique full simplex in top cohomology; intermediate
negative supports have zero cohomology. It observes the actual homotopy's
columns without copying its cone-homotopy or tensor-trick implementation.

For all 10,816 basis columns it verifies:

```text
actual d = independently constructed incidence
d^2 = 0
d h + h d = 1-Q
h^2 = 0
Q h = h Q = 0
Q^2 = Q
d Q = Q d = 0.
```

The full operator-column transcript is content addressed. Integer identities
extend by linearity to `Q(omega)`. The observed operators are the same ones
used by the metric-lift constructor. The proof covers their whole Laurent
domain, including acyclic support blocks and both grading signs.

## An independent finite-residual argument

Let `D=d+Delta` satisfy `D^2=0`, and let `r` be a closed cochain of total
degree one. These are explicit hypotheses, not consequences of the raw
contraction certificate. Independent binomial Künneth calculations on all
24 actual target components give reduced degrees only `-3,-2,-1,0`.
Thus `Q` vanishes on the entire target degree-one space.

Put `r_0=r` and `r_(j+1)=r_j-D h r_j`. Since `D^2=0`, each residual remains
closed of degree one. Hence `Q r_j=0` and the raw contraction identity gives

```text
r_(j+1) = h d r_j - Delta h r_j
        = -(h Delta + Delta h) r_j.
```

The actual object/Koszul weight lies in `[0,4]`. Every resolution arrow
raises it; every mixed extension term has positive object gain minus Koszul
wedge loss. Equation arrows raise it by one. The raw homotopy preserves it.
The verifier checks every actual term and component, so `r_5=0` follows.
Telescoping gives `D sum(j=0..4) h r_j = r`.

Finally `h^2=0` implies `h r_(j+1)=-h Delta h r_j`. Therefore the telescoping
primitive is exactly the constructor's finite series

```text
sum(j=0..4) (-h Delta)^j h r.
```

This derivation does not invoke the transferred differential or assume
closure from four coefficient probes. It independently recovers the
closed-residual case of the [perturbation lemma](https://arxiv.org/abs/math/0403266).
The lemma's published sign convention is opposite to the repository's raw
homotopy convention; the elementary argument above fixes the signs directly.

## The complete source-module identity

Every saved V2 section is polynomial in both plane factors, supported on
the five degree-zero objects, with two P1 chart vertices. The verifier checks
this property throughout the content-addressed 2,690-section stream. On the
dense coordinate torus the corresponding cochain module is free on ten
generators over the Laurent coefficient ring: one object and one P1 chart
vertex per generator, copied identically to all nine plane-chart pairs.
The chosen generator monomial merely carries the object's required degree;
it is explicitly `x0^d_x u0^d_u mu^d_p` on the selected P1 vertex, repeated
on the nine plane-chart pairs. Every other admissible monomial is its Laurent
translate. This is not a
choice of a physical extension coordinate or a substitute section basis.

Restriction incidence, multiplication by the fixed object/equation arrows,
and the outer suffix product commute with these formal Laurent translations.
Thus verifying a module operator on its ten generators proves its identity
for all actual section monomials. The identity is a Laurent polynomial
identity, so it restricts to the admissible regular cochains on the real
cover; no pole is introduced into a physical section by this proof.

For both actual saved outer coefficients the verifier constructs the product
independently by suffix vertices. Right terms have zero object/Koszul and
plane Čech degrees. Their P1 Čech degree is zero or one, so all crossing
signs are positive. The P1 overlap has exactly one permissible prefix/suffix
factorization. No common cup/sign helper enters this construction.

All twenty generator columns satisfy `D1 E_i + E_i D2 = 0`, including the
source differential rather than testing only closed section probes. Both
products agree columnwise with the constructor's existing cup implementation.
Module linearity therefore certifies the actual constructor on the complete
source section module. In particular, `D1(E_i s)=0` for every saved closed
section `s`.

## Strict repaired averaging

Both deck generators preserve the P1 chart vertices. On a plane-global
right cochain the ordered outer suffix product is equivariant: plane vertex
choices do not alter the source value, and the P1 vertex order is unchanged.
This assertion is deliberately **not** a claim of equivariance for arbitrary
Alexander--Whitney products under arbitrary cover permutations.

The verifier rechecks strict P/T fixation of both actual outer coefficients,
diagonality of T on monomials and homogeneous frames, and the group relations
on all 24 target components. The commutation scalar depends only on the
homogeneous multidegree: independent coordinate substitution verifies order
three on every coordinate and a constant commutator unit within each factor.
Thus the component checks cover every Laurent exponent
in that component. T commutes with the raw homotopy because its monomial and
object labels are preserved.

All target resolution and extension terms assemble into the actual signed
object operator `Gamma`. Its mixed coefficients are polynomial and independent
of both plane charts; the verifier checks every chart pair and both full
frame-conjugated actions. The 288-term operator is strictly P/T fixed. The
extension coefficient sign is minus for parent degree zero and plus for
parent degree minus one. Direct substitution into the three actual mixed
term types `(parent,cech,koszul)=(0,1,0),(-1,0,0),(-1,1,1)` reproduces the
existing left-perturbation crossing signs on every input Koszul summand.
Thus its cup action is the actual target object differential, not an
unrelated equivariant matrix. Signed cover incidence is natural under the
oriented pullback; independent coordinate substitution also verifies both
Schoen equation units. Together these checks give `D1 G=G D1`.

For an invariant source section, its residual is invariant. T commutes with
the full finite primitive series. The explicit `(1+P+P^2)/3` average therefore
retains `D1 b_i+E_i s=0` and is strictly P/T fixed. Its factor is declared,
not inferred or silently replaced.

## What is now available, and what is not

The complete source-module identity and finite closed-residual theorem certify
the original executable constructor for every section index in `range(5345)`.
The H0 exact sequence supplies independence and spanning: the 2,655 injected
V1 classes form its kernel, while the 2,690 corrected V2 sections project to
the independently certified quotient basis. This works with both `a0,a1`
symbolic and without changing the nonsplit carrier into a direct sum.

Rank-four section-basis availability is now true by this structural
certificate. Complete expanded coefficient replay remains false; it is not
needed as a substitute for the module proof. Local fiber evaluation, controlled
Ricci-flat/HYM convergence, physical normalization, remaining flavor sectors,
shared vacuum stabilization, and Genesis-to-UV derivation remain unresolved.

Reproduce with:

```bash
python -m research.experiments.scientific_genesis.alternate_metric_lift_operator_certificate
```
