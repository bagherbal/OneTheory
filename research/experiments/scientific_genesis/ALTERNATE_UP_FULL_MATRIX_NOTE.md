# Complete alternate holomorphic up matrix

The selected alternate one-Higgs Schoen carrier is a non-split rank-four
SU(4) family over the nonzero projective coordinates `[a0:a1]`, conditional
on the heterotic UV realization and the audited sufficient stability
chamber. No projective point is selected. This note concerns its exact
holomorphic up-sector coupling, not physical masses.

The row basis is `E(0,0), F(0,0):seed0, F(0,0):seed5`; the column basis is
`E(1,0), F(1,0):seed0, F(1,0):seed5`. All entries lie in
`Q(omega)[a0,a1]`, where `omega^2+omega+1=0`. The Higgs goes first in the
fixed quotient volume frame, whose cover-to-quotient trace factor is `1/9`.
With `w=omega`, the exact matrix is

```text
Y_hol = [
  [0,                         -1/6,                     1/14+w/21],
  [-w/6,                      (181/18+5w/2)a0+(617/18+31w/6)a1,
                              (11/21-1223w/126)a0+(-1399/126-95w/126)a1],
  [-1/42-w/14,                (-347/63-1249w/126)a0+(1235/126-55w/63)a1,
                              (-97/441-55w/147)a0+(65/18+w/9)a1],
]
```

The E–E entry vanishes by the exterior filtration. Four mixed entries
are constant and come from the already certified Higgs-first quotient
pairing. Each of the remaining four entries is linear in the outer
extension parameters. The producer evaluated both coefficients from
actual full E matter lifts, their global quotient pushouts, the same
Higgs class, and complete scalar cochains. It then freshly replayed all
eight F–F entry archives, including each literal differential, deck
character, product, trace, and natural-null cochain equality. A separate
regression expands the determinant directly from the two source blocks.

Writing the mixed row as `(r1,r2)`, mixed column as `(c1,c2)`, and the
F–F block as `[[A,B],[C,D]]`, exact expansion gives

```text
det(Y_hol) = -r1*c1*D + r1*c2*B + r2*c1*C - r2*c2*A
           = (-3/98 - 39*omega/196) a1.
```

The constant `E/F` minor is `-omega/36`, so the formal matrix has rank
two on `a1=0` and rank three on `a1!=0`. Its exact null contraction is
`(297/49-54*omega/49)a1`. These statements hold in the declared fixed
bases and normalization; a change of field basis or Higgs-volume frame
changes entry values without changing the rank locus.

The content-addressed result is
`data/generated/scientific_genesis/alternate_up_full_holomorphic_matrix.json`
with digest
`5dca3368f127ddf90eb8e263b403e6ca74f8857a3e505930194c51a67120884f`.
The independent scalar-level regression is
`tests/integration/test_scientific_genesis_alternate_up_full_matrix.py`.
The exact replay is
`python -m research.experiments.scientific_genesis.alternate_up_full_matrix`;
it is expensive because it re-evaluates all eight full cochain witnesses.

This closes one conditional holomorphic-matrix gate only. Positive matter
and Higgs metrics, canonical normalization, the common stabilized vacuum,
the other flavor sectors, low-energy observables, and the foundational
Genesis-to-heterotic implication remain unresolved. No measured quantity
entered the matrix or selected an extension point.
