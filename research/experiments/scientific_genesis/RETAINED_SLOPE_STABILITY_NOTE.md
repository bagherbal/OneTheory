# Actual stability at the retained polarization

The earlier scope result remains correct: the nine sufficient inequalities of
[Braun, He and Ovrut](https://arxiv.org/pdf/hep-th/0602073) fail at the original
descending ample twist `J=(14,16,1)`. They are not necessary conditions.
Here the same actual alternate Serre constituents allow a sharper argument.
The original 5,345 section coordinates, every cloud input and the selected
unstabilized complex/bundle-moduli point remain unchanged.

## Quantified source premises

This refinement uses the same invariant Picard lattice, Serre-ideal bounds
and source-applicability premises as `ALTERNATE_STABILITY_NOTE.md`. It does
not infer exhaustiveness from checking four examples. Equations (25)--(31)
of the source, with the corresponding I6 argument, bound every equivariant
constituent line map by the Serre subline or one of five ideal-quotient
classes. In `(tau1,tau2,phi)` coordinates those six bounds are

```
V1: (-1,1,-1), (-1,1,-2), (-4,1,2), (-3,0,1),
    (-2,-1,1), (-1,-2,2)
V2: (1,-1,-1), (1,-1,-2), (-2,-1,2), (-1,-2,1),
    (0,-3,1), (1,-4,2)
```

An excluded maximal class is not enough: all its proper descendants must
also be controlled. The negatives of the five maximal proper sublines of
`O_X` in source equation (67) bound every nonzero integral equivariant
effective divisor from below. Their **cover degrees** at `J` are

```
(0,0,1): 4032       (3,0,-1): 3168       (2,1,0): 6984
(1,2,0): 6768       (0,3,-1): 2520
```

Thus a proper descendant loses at least `2520` in determinant degree.
Character twists do not change degree. The following vanishing calculation
is on the entire cover, so it excludes every equivariant character, including
maps with the same first Chern class but a different flat character.

## Actual line maps, not positive slope guesses

Uniformly tensor each frozen constituent presentation by `O(-L)`, leaving
all Hilbert--Burch and mixed Serre arrows unchanged. Compute the degree-zero
map of the exact synchronized ambient Cech/Koszul contraction. The negative
reduced degrees vanish, so injectivity of this map proves
`Hom(O(L),Vi)=H0(Vi tensor O(-L))=0`. The four nonnegative candidates give

| Constituent | Candidate L | Cover degree | Degree-zero map | Exact rank |
| --- | --- | ---: | ---: | ---: |
| V1 | (-1,-2,2) | 1296 | 262 by 43 | 43 |
| V1 | (-4,1,2) | 648 | 28 by 3 | 3 |
| alternate V2 | (-2,-1,2) | 1080 | 563 by 93 | 93 |
| alternate V2 | (1,-4,2) | 1728 | 33 by 3 | 3 |

The artifact contains the actual sparse exact matrices and ordered bases,
not only their dimensions. An independent verifier restricts scalars to Q:
`a+b*omega` becomes the multiplication block `((a,-b),(b,a-b))` in basis
`(1,omega)`. Ordinary Fraction row elimination gives ranks `86,6,186,6`.
This independently checks rank, not the geometric construction of the map;
the latter is the existing exact mixed-arrow contraction and its certified
source geometry. No Euler characteristic is used as an H0 dimension.

After removing only the vanishing maximal classes, retaining every proper
descendant and every negative bound, all constituent line degrees satisfy
`deg(line in V1) <= -1224` and `deg(line in V2) <= -792`.
The constituent determinant degrees are respectively `-432` and `432`.

## All proper ranks in the outer extension

Use the subsheaf filtration of
[the extension-stability analysis](https://arxiv.org/pdf/hep-th/0512205),
section 2.1. For any proper saturated subsheaf F of the rank-four extension,
its intersection with V1 and image in V2 have ranks `(r1,r2)`; determinant
degrees add. Rank-one torsion-free images may be replaced by their reflexive
line hulls: maps into a locally free constituent extend across codimension
two, and this replacement does not decrease the bounding degree.

The cases `(1,0),(0,1),(2,0),(1,1),(2,1),(1,2)` have determinant-degree upper
bounds `-1224,-792,-432,-2016,-1224,-792`, respectively. They are all negative.

For `(0,2)`, the determinant map to V2 either has a nonzero effective divisor,
giving degree at most `432-2520=-2088`, or has zero divisor. In the latter
case it is an isomorphism away from codimension two. A saturated F is
reflexive; the inverse extends over that locus and gives a splitting of the
outer extension. This is impossible for every nonzero class of the already
certified alternate P1 family. This argument includes a proper rank-two
image whose quotient is supported only in codimension two; it does not
silently treat every proper image as a divisor reduction.

These seven cases prove equivariant slope stability, equivalently stability
of the descended bundle, at the actual retained polarization. Dividing cover
determinant degrees by nine and by rank preserves every strict sign. No
non-equivariant cover-stability theorem or full Kähler chamber is claimed.

## What remains physical work

The result repairs the missing **slope-stability hypothesis** for this ray,
not its numerical metric. HYM existence under the usual geometric hypotheses
is not a computed connection. Compatible controlled background geometry,
line untwisting, useful integration errors, large-twist/curvature convergence,
matter/Higgs metrics, normalized Yukawas and a common vacuum still remain.
The finite-cloud atomic no-go remains solely a statement about its old
empirical measure. The expanded all-section cloud continues unchanged.
