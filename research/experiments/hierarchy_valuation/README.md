# `hierarchy_valuation`

## Purpose

This experiment asks which moduli degenerations of a frozen heterotic carrier
can produce parametric Yukawa hierarchies, and holds the registered program
for testing the proposed universal hierarchy parameter

```text
epsilon^4 = (9/5) * (14/431) * (1/(8 pi))      epsilon = 0.219619476873...
```

from the migration draft (section 3.11), without letting that number enter any
upstream calculation. The program, its kill criteria, and its validation are
in [`PLAN.md`](PLAN.md).

The first exact result is `wall_valuation.py`. All four completed holomorphic
matrices of the frozen alternate carrier have the single anomalous-U(1) degree
pattern `[[-,0,0],[0,1,1],[0,1,1]]` in the extension parameters (E-E forced to
vanish), and the first-constituent slope is exactly
`6 (j1 - j2)(j1 + j2 + 6 j3)`, so the stability wall is the plane `j1 = j2`.
Near that wall the extension modulus acts as a Froggatt--Nielsen flavon, but
every sector has invariant-factor orders `(0,0,1)`: two unsuppressed families
and one family suppressed by exactly one power. Under the three premises
recorded in the report, this carrier's bundle modulus cannot generate the
draft's `(8,4,0)`, `(5,3,0)` or `(1,2,3)` valuations.

```bash
python -m research.experiments.hierarchy_valuation.wall_valuation
```

## Belongs here

Exact valuation and invariant-factor audits, asymptotic matter-metric scaling
studies along declared Kähler or complex-structure degenerations, carrier
charge-pattern screens, and pre-registered estimator definitions for any
hierarchy parameter.

## Does not belong here

Fitted unit cores, a numerical hierarchy parameter inserted into metric or
vacuum work, measured masses or mixings used as inputs, selected moduli, or
an identification of the draft parameter with a physical quantity before its
derivation exists.

## Dependencies

The experiment reads completed content-addressed holomorphic matrix artifacts
and production Schoen geometry. Production code must never import it.

## Promotion condition

A valuation theorem may be promoted only after its premises (stability at the
wall, D-flat flavon identification, finite split-bundle metrics) are certified,
independently reviewed, and tested in the owning production flavor module.
No hierarchy-parameter value is promotable without a derived origin and a
registered blind comparison.
