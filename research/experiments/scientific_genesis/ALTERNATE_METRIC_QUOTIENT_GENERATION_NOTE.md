# Quotient generation at a declared enlarged twist

This is a mathematical prerequisite for metrics on the frozen alternate
heterotic carrier, conditional on that selected UV realization. It does
not select an extension coordinate, Kähler modulus, or vacuum. The twist
`H=(14,16,1)` is deliberately larger in the two `P2` degrees than the trial
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
distinct points. In fact their projections to `P2_x × P2_u` are also
distinct. Fix `(x,u)`. The two Schoen equations are homogeneous linear
equations in the shared base coordinates `(mu,nu)`, so their common
fiber in `P1` is empty, one point, or all of `P1`. If a nonidentity
deck element fixed `(x,u)` in the image, it would preserve a nonempty
fiber. It would fix the sole point of a point fiber; on a full `P1`
fiber its projective action has an eigenline and hence a fixed point.
Either contradicts the free action on the cover. Thus no nonidentity
deck element fixes a projected point.

Fix a target projected point in an orbit. For each of the other eight
projected points, at least one `P2` coordinate differs. Choose a
linear form in that factor vanishing at the other point but nonzero at
the target. Their product vanishes at all eight others and not at the
target. Multiplying by linear forms nonzero at the target pads *both*
`P2` factors to degree nine. Consequently `O(9,9,0)` separates every
deck orbit, not merely sampled orbits. Restriction to the cover
preserves these values.

The exact coordinate lifts have scalar commutator `omega^2` on each
`P2` factor and `1` on `P1`. Therefore `O(9,9,0)` has commuting
order-three lifts and descends. The tensor product with the already
descending `H0` is `H=(14,16,1)` and also descends. All its ambient
multidegrees are positive, so this is an ample mathematical twist.
For either
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

At `H`, the first Serre subline `A=(13,17,0)` has the same exact
Koszul support pattern as at the trial twist: `K1` vanishes and
`H1(K2)` injects into `H0(K0)`, so `H1(A)=0`. Every ambient Koszul
term for each first Hilbert–Burch line has cohomology only in degree
zero. Exactness of the two-equation Koszul sheaf resolution gives
higher-cohomology vanishing for those restricted lines; the genuine
Hilbert–Burch and
Serre sequences then give `H^1(X,V1(H))=0` on the cover and hence on
the quotient. The quotient-level extension criterion lifts sections
from `V2(H)` and fills the `V1(H)` kernel. Thus every member of the
frozen alternate non-split `P1` family is globally generated at `H`.

Exact line-cohomology arithmetic gives cover `H0` dimensions
`23,895` and `24,210` for the two constituents. Their higher
cohomology vanishes; holomorphic Lefschetz for the free ninefold
quotient gives invariant dimensions `2,655` and `2,690`, hence
`5,345` rank-four sections. These are dimensions, not constructed
section vectors. The previous all-factor separator `O(9,9,9)` needed
`13,373` quotient sections; dropping its unnecessary `P1` degree
substantially reduces the computational target without sacrificing
the global-generation theorem.

The exact evidence is in
`data/generated/scientific_genesis/alternate_metric_quotient_generation.json`.
This closes the global-generation *prerequisite*, not the metric
calculation. No Ricci-flat metric, HYM connection, matter metric,
canonical normalization, selected common vacuum, or physical Yukawa
is produced. The Genesis-to-heterotic implication remains unresolved.
