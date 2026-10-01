# Actual down-Higgs Hom input

This construction is conditional on the frozen heterotic realization. It is
not an exterior-square Higgs, a Yukawa matrix, a mass prediction, or a choice
of extension parameters.

## Character routing

The Wilson action in equation (28) of
[hep-th/0512177v3](https://arxiv.org/html/hep-th/0512177v3) assigns the down
doublet the forward weight `(0,1)`. The source/cohomology convention is
`source = -forward mod 3`, so its source weight is `(0,2)`.
The published source archive is pinned by the existing manifest SHA-256
`ad4ea10b3d765553ccdd072922a6bda619866ea814c532b8ffe74ddafc7fe73f`.

In the frozen alternate I6 ray `(0,1)`, the native determinant character is
`(2,1)` and the common flat twist is `t=(1,2)`. A native class of character
`h` in `Hom(V2 tensor det(V1), V1)` therefore has repaired Higgs weight

```text
h + (2,1) + 2t = h + (1,2) mod 3.
```

The required class is consequently `h=(2,2)`, not `(2,1)`. Equivalently,
the reciprocal quotient covector has weight `h-2t=(0,1)`. The two formulas
agree because the repaired determinant character is zero. This is a frame
calculation, not an identification of the up and down Higgs cocycles.

## Exact class

Use the original four-dimensional reduced Hom complex and its original
ordered complement to the boundary space. The existing full inclusion and
deck projector select the first nonboundary seed in character `(2,2)`:
seed 1, with reduced cohomology coordinates

```text
(0, (1-omega)/3, 0, (2+omega)/3).
```

Its full cochain has 351 exact terms. Verify the original differential
annihilates it and both original full atlas actions multiply it by `omega^2`.
Project every original seed; the nonzero cohomology images span exactly one
dimension. No new basis permutation or normalization is introduced. The full
witness, not only its reduced coordinates, is archived content-addressably.

The separate regression checks the full differential and both atlas actions
directly on the archived witness, reconstructs the reduced boundary/complement
span, and checks the quoted coordinates. It also reconstructs the old up
class, which must retain its previous packet exactly.

## Remaining physical edge

This input alone does not solve the exterior-cone lifting equation. The actual
down-Higgs quotient covector and its parameter-linear correction are required
before down-quark or charged-lepton coupling evaluations. Metrics, a common
stabilized vacuum, Majorana data, physical Yukawas, and observations remain
outside this result.
