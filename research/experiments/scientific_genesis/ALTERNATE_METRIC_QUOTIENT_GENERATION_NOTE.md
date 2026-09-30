# Quotient generation at a declared enlarged twist

This is a mathematical prerequisite for metrics on the frozen alternate
heterotic carrier, conditional on that selected UV realization. It does
not select an extension coordinate, Kähler modulus, or vacuum. The twist
`H=(14,16,10)` is deliberately larger than the earlier trial
`H0=(5,7,1)`; no generation claim is made at `H0` on the quotient.

## Both actual constituents generate on the cover at `H0`

The first constituent's cover generation and `H^1=0` were established
from its actual Serre/Hilbert–Burch sequence in the preceding
certificate. The alternate second constituent is the *ray (0,1)*
`I6` Serre object, not the published reference ray. Its exact line
degrees at `H0` are `A2=(6,6,0)`, four `F0=(6,3,2)`, and three
`F1=(6,2,2)`. For `A2`, the ambient two-equation Koszul terms have
`H0(K0)=784`, zero `K1` cohomology, and `H1(K2)=100`, with no other
cohomology. The exact two short sequences give `H^1(cover,A2)=0`
and `h0(cover,A2)=684`. The nonnegative `A2` and `F0` lines are
restrictions of basepoint-free ambient lines. The Hilbert–Burch
surjection from the sum of `F0` lines generates the ideal quotient.
The Serre long exact sequence lifts all of its sections because
`H^1(A2)=0`; its subline fills the residual fiber. Thus the actual
second constituent is generated on the cover. This argument uses
neither a guessed two-term matrix for the non-split middle term nor
the reference carrier's section count.

## Orbit separation gives invariant evaluation

The published `Z3 × Z3` action is free, so each cover orbit has nine
distinct points in the ambient `P2 × P2 × P1`. Fix a target point in
one orbit. For each of the other eight points, at least one projective
factor differs. Choose a linear form in that factor vanishing at the
other point but nonzero at the target. Their product vanishes at all
eight other points and not at the target. Multiplying by linear forms
nonzero at the target pads each factor to degree nine. Consequently
the complete ambient system `O(9,9,9)` separates *every* deck orbit,
not merely sampled orbits. Restriction to the cover preserves these
values.

The exact coordinate lifts have scalar commutator `omega^2` on each
`P2` factor and `1` on `P1`. Therefore `O(9,9,9)` has commuting
order-three lifts and descends. The tensor product with the already
descending `H0` is `H=(14,16,10)` and also descends. For either
equivariant constituent generated on the cover at `H0`, multiply a
global section attaining any chosen fiber vector by an orbit-
separating section. This makes the evaluation map at the direct sum
of all nine orbit fibers surjective. Averaging over the finite group
is exact in characteristic zero, so invariant global sections
surject onto the invariant orbit fiber, which is the fiber of the
descended constituent. Both actual constituents are therefore
globally generated **on the quotient at `H`**. This is an existence
proof and does not construct an explicit invariant section basis.

## The rank-four family

At `H`, every ambient Koszul term for each line of the actual first
constituent has cohomology only in degree zero. Exactness of the
two-equation Koszul sheaf resolution gives higher-cohomology
vanishing for those restricted lines; the genuine Hilbert–Burch and
Serre sequences then give `H^1(X,V1(H))=0` on the cover and hence on
the quotient. The quotient-level extension criterion lifts sections
from `V2(H)` and fills the `V1(H)` kernel. Thus every member of the
frozen alternate non-split `P1` family is globally generated at `H`.

The exact evidence is in
`data/generated/scientific_genesis/alternate_metric_quotient_generation.json`.
This closes the global-generation *prerequisite*, not the metric
calculation. No Ricci-flat metric, HYM connection, matter metric,
canonical normalization, selected common vacuum, or physical Yukawa
is produced. The Genesis-to-heterotic implication remains unresolved.
