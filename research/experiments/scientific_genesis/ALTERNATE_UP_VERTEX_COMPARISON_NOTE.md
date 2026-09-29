# Local comparison criterion for the quotient product

This note isolates a necessary identification step, not a new Yukawa
coefficient. The result applies to the declared triangular complex and
its differential-invariant A wedge B quotient. It does not change the
ordered cover or average a product into a selected character.

## A literal vertex identity

Let p_v retain the components on one product-cover vertex v. All terms
of the full differential preserve or increase cover degree. A term
which lands at v must already start at v: a polynomial arrow keeps
its cell, an ordered cup has the union of its input cells, and the
Čech differential strictly increases degree. Hence

```text
p_v D = p_v D p_v.
```

After localizing on U_v, use the usual untwisted Čech contraction to v.
Its homotopy h has p_v*h=0. The full mixed perturbation, including its
vertex relation terms, is strictly triangular in the A/B object graph,
so its perturbation series is finite. The corrected inclusion I' obeys
p_v*I'=identity because every correction starts with h. Since p_v is
already a chain map to the actual vertex differential, the transferred
differential is exactly that vertex differential. The perturbed
contraction then shows that p_v is homotopic to its corrected projection
and is a local quasi-isomorphism. This is a stalkwise sheaf comparison,
not projection of global cohomology. Vertex relation terms are retained;
they are not incorrectly counted as strictly positive-cover arrows.

The differential at a vertex retains the actual parent-one relation
coefficients and the hypersurface Koszul arrows. It is not just the
split polynomial differential, and reading it does not mean that an
arbitrary constituent cochain is a closed carrier representative.

The H and T kernels have the union of their input cells as carrier.
If an output is at a vertex, every input cell is that same vertex.
H lowers cover degree by one and T by two, so both are zero there.
Equivalently, their chain diagonals on a vertex vanish: a carrier
consisting only of that vertex has no positive-degree output chains.
Consequently the complete corrected product satisfies

```text
p_v P_Q(u,w) = ordinary_local_graded_wedge(p_v u,p_v w) modulo A wedge B.
```

This is an all-input support proof, not a claim inferred from finitely
many zero samples. Regression checks use an independent local exterior
formula, all ordered Koszul pairs, both object parities, odd diagonals,
three coupled gauges and all eighteen vertex differential projections.
The tests keep terms at other vertices; they do not pretruncate inputs
before asking what the complete product restricts to.

For local coefficient degrees a,b and internal generators e_i,e_j of
degrees p_i,p_j, the structural-first sign is (-1)^(a*p_j).
Ordering the generators adds -(-1)^(p_i*p_j) when they are reversed.
An even diagonal vanishes, an odd diagonal survives with no factor two.
The independent formula also orders the exterior Koszul generators;
their repeated-generator products vanish.

## Degree-zero rigidity, including ambient Tor

The apparent need to eliminate ambient self-intersection Tor is not a
real obstruction to a degree-zero sheaf comparison. The sign of the
derived shift is decisive. Let A have no positive cohomology and let
T be a sheaf in degree zero. Then

```text
Hom_D(A,T) = Hom(H0(A),T).
```

Here is an independent proof. Represent A by a nonpositive complex
and T by an injective resolution I in nonnegative degrees. A degree-zero
map has only A0-to-I0 as a potentially nonzero component. Its cycle
equations say that it kills the image of d_A from A-1 and lands in
ker(d_I0)=T. Thus it is exactly a map H0(A)-to-T. There are no degree
minus-one Hom components: the source is nonpositive and the target
nonnegative. Therefore no boundaries identify different such maps.
This proves both existence and uniqueness. Equivalently, the negative
truncation triangle has zero Hom into T, including its positive shift.

For an ambient flat resolution C of i_*R, A=C tensor C represents the
ambient derived tensor. Its Tor is in nonpositive degrees and its H0
is i_*(R tensor_O_X R). The target is i_*Q in degree zero. Negative Tor
can therefore supply no extra degree-zero map. It need not be erased
or silently set to zero. A positive-cohomology source would be different:
it can supply higher-Ext maps, so the nonpositive condition is essential.

The regression tests make this shift distinction explicit over k[t].
For k[t]/(t), the tensor of two free resolutions has a nonzero degree
minus-one Tor class, yet degree-zero maps to its resolved sheaf have
one scalar modulo t. Homotopies change that scalar only by t*h. Shifting
the source so that its cohomology lies in degree plus one instead gives
a nonzero Ext1 map even though its H0 vanishes. Rational and Eisenstein
coefficients are both exact. These are mathematical tests, not models.

## Applying the comparison to the declared presentations

The prerequisites are faithful sheaf resolutions and a sheaf-level
chain map, not a separately guessed tensor adapter. The frozen Serre
constituents are locally free. Pushout by the actual global q_E gives
0-to-B1-to-R-to-F-to-0, so R is locally free. The complete local relation
matrix at a vertex presents that pushout: its parent-one outer row is
q_E applied to the actual E-valued relation, not a substituted extension.
Near a point of X the locally free quotient makes this matrix split
over the ambient local ring. The regular two-equation Koszul resolution
then resolves i_*R without positive or negative sheaf cohomology.

The graded local exterior resolution presents exterior-square R. Killing
A_F wedge B1 means quotienting by the actual line sheaf B1 tensor A_F.
Its map into exterior-square R is injective as a sheaf: A_F-to-F is the
nonzero Serre section on the integral smooth cover, not an everywhere
nonvanishing fibre vector. The removed relation includes its whole
Čech/Koszul line resolution, giving a short exact sequence of complexes.
Its long exact cohomology sequence has possible degree-minus-one term
equal to the kernel of B1 tensor A_F-to-exterior-square R, which is zero
by that sheaf injection. The degree-zero term is exactly Q and every
other term vanishes. This proves faithfulness even at the section's
zeros. Equivalently its two-block presentation is the verified
K/exterior-F cone. Q need not be a bundle.

The ordered-cover summands are localizations of ambient line sheaves,
hence flat. All coefficient operations multiply Laurent sections and
restrict to the union intersection; those sections remain regular there.
The H/T kernels only use faces of the same carrier. These formulas are
linear over ambient functions and commute with further localization.
The complete Leibniz identity consequently supplies a morphism of sheaf
complexes C(R) tensor C(R)-to-C(Q), not merely a map of finite samples.

The vertex comparison identifies its H0 map with the ordinary sheaf
wedge followed by the declared quotient. Degree-zero rigidity therefore
identifies the corrected product with that canonical quotient morphism
in the derived category. This uses the actual presentation and its
local-freeness hypotheses; it is not a theorem for other twisting graphs.

The source morphism V-to-R is q_E on E and identity on F. Pulling a
closed quotient Higgs through exterior-square V-to-Q gives the canonical
degree-one dual exterior class. Acyclic determinant endpoints identify
its class with the selected mixed Higgs functional, in the fixed signed
minor orientation of `ALTERNATE_UP_NATURAL_NULL_SCALAR_NOTE.md`. A complete
closed Higgs lift is still required; dimensions alone cannot replace it.

## Scope retained

The vertex comparison is established independently of a scalar result.
The canonical sheaf-product identification is derived under the declared
faithful-presentation hypotheses. Arbitrary global H2(K) additions are
not sheaf comparisons with that augmentation. The earlier five-dimensional
space of unconstrained product lifts remains real; it is not the freedom
of this natural operation. Complete actual scalar evaluation, equivariant
descent and explicitly normalized quotient trace remain separate checks.
This note certifies none of a complete matrix, a physical mass,
a selected extension point or a stabilized
vacuum. Generic regression gauges are mathematical fixtures only.
