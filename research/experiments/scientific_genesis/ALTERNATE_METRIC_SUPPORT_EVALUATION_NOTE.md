# Finite pole-sector point evaluation

This is a computational representation of the **same** certified universal
section basis, not a new bundle or a simplified physical model. The original
regular-u point evaluator is retained as an independent archive producer.
The deficiency is its repeated expansion of positive first-plane powers while
compiling a point matrix; geometric sampling cannot afford to repeat that
work indiscriminately.

## The partial-coefficient encoding

For a first-plane monomial with exponent vector `m`, write

```text
n_i = min(m_i,0), r_i = max(m_i,0), x^m = x^n x^r.
```

Only `x^r` is evaluated at the explicitly supplied coordinate tuple `X`.
Every negative exponent in `n` is retained symbolically. Thus a coordinate
can be zero without evaluating a Laurent pole or pretending that the term
was regular there. Terms whose positive factor evaluates to zero vanish
as contributions to the final point functional.

The original target component has a fixed nonnegative first-plane ambient
degree `d`, checked over all actual components. Its negative exponent vector
is encoded by assigning the dummy power `d-sum(n)` to the **first regular
coordinate index**, leaving other regular powers zero. This explicit policy
is solely an internal homogeneous-degree encoding. It is not a physical
fiber basis, a frame normalization, or a geometric coordinate choice. An
encoded cochain is never exported as a physical section.

The raw incidence and homotopy matrices depend only on negative support and
structural parity. The dummy monomial has exactly the original negative
support, so this encoding commutes with both raw operators. The independent
finite support certificate verifies their full integer matrices.

## Applying the actual arrows

Every actual target arrow is polynomial in the plane factors. For one
encoded unit `b`, use the original perturbation on that unit, with coefficient
one. An output exponent is `b.x_monomial + arrow_x`. Subtract the source's
artificial positive exponent vector to recover `n + arrow_x`.

Encode that vector again: retain every remaining pole, evaluate every
nonnegative power, and assign the new dummy degree in the target component.
The arrow cannot turn a regular coordinate into a pole because its exponents
are nonnegative. This proves the identity

```text
encode(Delta(c)) = Delta_encoded(encode(c))
```

for the actual polynomial-arrow operator, including transitions in which a
negative exponent becomes regular. Actual u-arrow coefficients are evaluated
as in the separately certified regular-u evaluator. Original components,
cover cells, P1 powers, Koszul degrees, and all structural signs remain
unchanged. Unit images are computed with the original operator once, then
extended by exact linearity; they are not guessed from dimensions.

Combining this identity with homotopy naturality proves equality for the
entire previously certified finite lifting series. No closedness is asserted
for an encoded intermediate cochain; actual basis closedness remains a
separate established input.

## Finiteness and reuse

The initial x poles come from the finite actual outer coefficients; global
source sections have no plane poles. Homotopy preserves exponents and
polynomial arrows cannot deepen a plane pole. Negative exponent values thus
lie in finite intervals independent of positive source powers. Component
degrees, cover cells, and the bounded lifting filtration determine the
remaining finite bookkeeping. Positive magnitudes are evaluated as
coefficients rather than generating new raw homotopy states.

At each supplied point, the wrapper compiles the actual perturbation column
of each encountered encoded unit once. It also reuses identical encoded
residuals exactly. A cache hit is equality of explicit mathematical data, not
an assumption about similar sections or fitted coefficients. The original
section indices and both symbolic extension coefficients are preserved.

## Deck phases and local frames

Each of the three Reynolds channels uses `P^k(X)` and `P^k(U)` with the actual
monomial substitutions, including Eisenstein phases. Before applying the
original full deck action, remove only the phase belonging to artificial
positive powers. The phase of every retained negative x power must remain.

After pullback, local evaluation ignores the dummy positive x/u numerator,
but evaluates the retained poles and genuine P1 powers on the explicitly
chosen valid chart. All original homogeneous line-frame denominators and
the actual quotient projections remain in force. This is not automatic
normalization and is not a direct-sum approximation to the nonsplit bundle.

## Independent attacks and scientific scope

Tests compare operator naturality on units drawn from actual source arrows,
using nonunit exact coordinates to detect discarded factors and arbitrary
Eisenstein scalars to test compiled-column linearity. These operator tests
are mathematical functionals, not invented points on the Schoen cover.

Physical section-value checks compare all coefficients of the four archived
full-cochain probes and a nonzero section on a distinct complementary cover
chart. The complete comparison against the independently produced point-matrix
archive now passes for all 5,345 columns and all constant/a0/a1 coefficients.
The five-test run completed in 2,969.63 seconds. This establishes agreement
at the archived point; it does not establish practical multi-point throughput
or controlled numerical sampling. The original producer remains available.

This representation can reduce exact evaluation work. It does not supply
controlled numerical roots, a sampling measure, Ricci-flat/HYM convergence,
harmonic representatives, a stabilized common vacuum, or physical Yukawas.
All such dependencies remain explicitly unresolved.
