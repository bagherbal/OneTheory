# Quotient-level global-generation reduction

Let `X` be the descended Schoen quotient and let the frozen alternate
carrier have its exact sequence of locally free sheaves

```text
0 -> V1 -> V -> V2 -> 0.
```

For any explicitly declared descending line bundle `H`, twisting gives
`0 -> A=V1(H) -> E=V(H) -> B=V2(H) -> 0`. The following standard
criterion is exact and independent of the extension coordinate:

```text
A and B globally generated on X, and H^1(X,A)=0
    => E globally generated on X.
```

Proof: the long exact cohomology sequence makes
`H^0(X,E) -> H^0(X,B)` surjective when `H^1(X,A)=0`. At every point
`x`, any vector of `E_x` first maps to a vector of `B_x`. Lift a global
section of `B` attaining that vector to a global section of `E`.
The residual vector lies in `A_x`, where it is attained by a global
section of `A`. Thus global sections of `E` span every fiber. The
argument holds for every member of the universal non-split P1 family
once the three premises hold uniformly; it does not choose an
extension point.

The conditions must be checked **on the quotient**, in the correctly
descended equivariant frames. Cover-level generation by arbitrary
sections is insufficient: those sections may fail to descend or span
the invariant quotient fibers. In characteristic zero, the quotient
cohomology obstruction can be computed exactly as the invariant part of
the cover group, `H^1(X,A) = H^1(X_tilde, pi^*A)^G`, but the two
evaluation-surjectivity conditions still require exact quotient-level
certificates. A finite set of sampled points or section dimensions alone
cannot prove them.

This reduction does not reuse the published reference carrier's
`192+212=404` dimension ledger, its four `e_A` cocycles, or its
`H*=(5,7,1)` section claim as alternate-carrier inputs. The alternate
P1 has different constituent arrows even where graded line objects
agree. Before numerical metric work, the next exact calculation is to
choose a descending positive twist by a declared mathematical criterion,
construct the actual `V1(H)` and `V2(H)` quotient section spaces, prove
their fiberwise generation, and prove `H^1(X,V1(H))=0`. If any premise
fails, the criterion is inconclusive; a different twist or direct
rank-four evaluation/Fitting calculation is then needed.

No global-generation result, Ricci-flat metric, HYM connection, or
physical normalization is claimed by this note.
