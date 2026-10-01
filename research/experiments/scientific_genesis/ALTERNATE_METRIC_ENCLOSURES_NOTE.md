# From roots to bounded local geometry

This prerequisite propagates the existing certified parameter roots into
the actual cover's chart coordinates and integration densities. It also
evaluates exact local Laurent cochains coefficientwise. It does not supply
the universal rank-four quotient frame, the complete bounded section
matrix, a point-sampling law, or a converged metric.

## Reuse and missing capability

The exact scalar norms, sparse polynomial derivatives, actual-pencil root
certificates, projection equations, residue normalization, and archived
constituent cochains are reused. The exact `CoverPoint` constructor rejects
nonmembers; feeding it approximate root centers would be invalid. Existing
point-functional section compression likewise uses exact field values,
not error enclosures. No enclosure arithmetic was found in the repository.
The new arithmetic is research-only and limited to this prerequisite.

The [Arb inclusion principle](https://arblib.org/using.html) is useful context:
enclosures must contain every permitted input value, but their tightness
is not guaranteed. This implementation uses rational **circular** bounds
with Q(omega) centers, not Arb's floating rectangular complex balls. Its
elementary bounds are derived below; no Arb dependency is added.

## Exact center, explicit uncertain radius

Let `B(c,r)` be the closed complex disk of radius r. Center arithmetic is
exact Q(omega) arithmetic. Addition adds radii. Multiplication uses

```text
|(c+e)(d+f)-cd| <= |c|*s + |d|*r + r*s,
|e| <= r, |f| <= s.
```

The previous integer-square-root routine supplies outward rational modulus
bounds. If a lower bound L on |c| exceeds r, then

```text
|1/(c+e)-1/c| <= r/(L*(L-r)).
```

Otherwise inversion fails explicitly. Norms lie in
`[max(0,L-r)^2, (U+r)^2]`. Conjugation preserves radii. Integer powers
compose these inclusion-preserving operations; negative powers require
certified inversion. Real interval arithmetic uses all endpoint products,
with reciprocal intervals permitted only when zero is excluded.

Positive radii and nonsingleton interval endpoints are rounded outward
onto a caller-declared dyadic mesh after every operation. This controls
denominator growth while adding only declared, bounded error. Exact
radius-zero scalars and exact singleton intervals are never rounded.
Different bound precisions cannot be combined silently. No tolerance,
automatic precision increase, chart fallback, or hidden normalization is
provided. Correlations can widen bounds; a rejected enclosure does not
prove a geometric singularity or a physical no-go.

## Actual projective points, not center points

For each certified root disk, line coordinates are
`v0 + alpha*v1`, or `alpha*v0 + v1` in the complementary parameter chart.
The exact infinity marker gives the corresponding fixed line vector.
All nine root pairs are retained. Each homogeneous group is normalized
only at the caller's declared pivot, after its ball excludes zero. The
pivot becomes identically one, rather than an uncertain evaluation of q/q.

The new bounded-point type retains the actual `IntersectionRoots`
certificate. Its geometric membership follows from the exact restrictions
of both frozen pencils. Merely enclosing zero in an equation residual
would not prove membership. Neither its centers nor independent arithmetic
test perturbations are admitted as exact cover points or physical samples.

The supplied projection chart declares eliminated coordinates. Evaluation
of the **existing** projection polynomials and their derivatives bounds
the actual Jacobians and implicit derivatives. Division excludes zero
throughout each enclosure. The original residue convention and explicit
volume-form scale are unchanged.

For the first FS direction, with v=dz/ds, the exact Gram identity is

```text
(1+|s|^2+|z|^2)(1+|v|^2)-|conj(s)+conj(z)*v|^2
  = 1+|v|^2+|s*v-z|^2.
```

This manifestly positive formula reduces cancellation in interval bounds.
The second plane has the analogous expression. Their product divided by
`(1+|t|^2)^2` is the auxiliary density with pi cubed removed. The squared
residue gives the Omega density. The same topological auxiliary cover
mass and separately declared covering degree give the cover and quotient
importance intervals. Pi cubed remains symbolic. These weights apply to
descended integrands under the previously stated measure contract.

## Coefficients and independent checks

Laurent evaluation permits negative exponents only at explicitly inverted
pivots. It filters the actual local Cech-zero/Koszul-zero generator terms
with their compatible component basis. Since homogeneous pivots are one,
the declared local line frames equal one. No bundle metric, quotient
frame, or extension point is inserted. Generic local cochain access can
bound each universal parameter coefficient separately once supplied;
constructing and efficiently bounding the complete universal fiber matrix
is still a separate gate.

Tests independently evaluate exact circle perturbations and signed
interval endpoints. They check the density formula with the uncancelled
Gram expression, not the enclosure algorithm's positive identity. Both
old exact cover probes recover the exact existing densities and quotient
weights, without approximation. All nine branches of both configurations
have positive density bounds, including infinity, and finer root disks
yield nested, narrower density intervals in these probes. Actual expanded
constituent cochain bounds agree with independent compact-archive
evaluation at the exact probe and contain nonzero-error functionals at
finite and infinity branches. These functionals test algebra, not sampling.
Complementary parameter charts give a unique matching of all nine enclosed
points. A genuinely ramified projection of an otherwise regular point is
rejected; an explicitly supplied unramified projection then succeeds.

The content-addressed artifact records all 18 bounded geometric densities
plus four actual constituent generator-coordinate probes per configuration.
The V2 blocks are **not** their universal outer lifts. The bounded universal
quotient-frame, complete-section, controlled sampling, numerical metric,
and physical prediction flags remain false. Next: bound the actual
universal quotient frames and complete section evaluator; control
SU-uniform proposal precision and integration error; then establish
Ricci-flat/HYM convergence. The common vacuum, remaining Yukawa sectors,
and Genesis-to-UV implication remain unresolved.
