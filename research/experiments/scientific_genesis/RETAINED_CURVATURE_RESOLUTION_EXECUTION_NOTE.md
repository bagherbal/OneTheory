# Executed same-input resolution sensitivity

## COMPUTED discovery result

Both declared cases completed levels 16, 20 and 24, preserving the captured
streams, physical root ancestry, named frame, all 5345 sections, fixed H1,
extension point and reference background. Their original level-16 geometry and
curvature reproduced exactly. The original cloud checkpoints were not changed.

| Original ordinal | H1 L1, level 16 | Level 20 | Level 24 |
| --- | ---: | ---: | ---: |
| 526 | 38695192.869766615 | 8298.108102910535 | 1345.5249444566948 |
| 1360 | 5332261.81624054 | 936276.1551972331 | 942684.9617137238 |

At point 526, H0 L1 also changes from 468.506174 to 17.526862 and 14.149837.
The maximum affine-coordinate displacement from level 16 to level 24 is about
4.23e-5. The H1 reference weight changes only from 1071.940654 to 1071.936539.
This case has not reached a resolution plateau: even levels 20 and 24 differ
substantially. A well-behaved fiber condition alone does not control input error.

At point 1360, H0 L1 remains about 35.9232. The maximum coordinate displacement
is about 2.01e-6. The H1 fiber condition drops from 20.89 to 2.32 and 2.315, while
the refined million-scale curvature persists. Levels 20 and 24 differ by about
0.68 percent; this observation is not an error bound or proof of a limiting value.

Executed packet digests:

- 526: `8ef99ba30b04be60b9820f6a75ecaed3767bcb4a22e4491aa78d742b21071604`.
- 1360: `d8017c86955b985a5e5793374811e07f63873e638bfefbf4242d1ae7df553c07`.

## DERIVED conditional continuum constraint

There is a sharper interpretation than calling the enormous old empirical
residual physical instability. Assume the section matrix is genuinely globally
generating on the exact carrier, H is a constant positive-definite section form,
the Chern connection is evaluated exactly, and the Kähler class is the declared
J with c1(V tensor L_J)=4J. These are mathematical premises, not a claim that the
binary64, finite-cell experiment already satisfies them accurately.

In the constant whitened frame, the contracted twisted curvature A is positive
semidefinite: its first-jet expression is the contraction of R_i R_j^dagger
against a positive Hermitian background inverse. For its four eigenvalues,

`sum |lambda_i - trace(A)/4| <= (3/2) trace(A)`.

To prove this without an eigenvalue approximation, write the absolute sum as
the maximum over the 16 sign choices. Each coefficient of lambda_i is
`sign_i - sum(signs)/4 <= 3/2`; each lambda_i is nonnegative. The bound is sharp
on a rank-one positive matrix. This argument is checked in exact rational
arithmetic, not sampled eigenvalue fixtures.

Chern-Weil and the declared normalization give the exact trace integral
`32256 pi`, volume `1344`, and average trace `24 pi`. Consequently the correctly
integrated reference residual used by this experiment obeys `tau <= 9/2` for
every such H, regardless of slope stability or convergence of an iteration.
The old empirical H1 value 3977.48 cannot be that continuum integral under these
premises. This excludes that interpretation, not the carrier or its HYM existence.
The normalization and distinction between balanced and HYM convergence use the
[generalized Donaldson algorithm reference](https://arxiv.org/pdf/1103.3041).

## Next scientific edge

The experiment proves substantial finite-input sensitivity at these cases,
not that all of the complete-profile discrepancy has one cause. Further
same-input levels are justified at 526; 1360 also needs precision and arithmetic
control before its apparent plateau is trusted. A valid global comparison must
recompute the complete declared population at its declared resolution, retaining
failures and every weight. Never substitute these two refined cases into the old
mean. Sampling adaptation, full-factor conditioning and accuracy of the trial
operator itself remain open. Keep the independent 16384-point workload intact.
No H2, controlled HYM solution, matter/Higgs metrics, canonical Yukawas or common
stabilized vacuum follows from these diagnostic cases.
