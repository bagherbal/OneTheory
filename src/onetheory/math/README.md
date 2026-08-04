# `math`

## Purpose

Math contains exact, reusable mathematics independent of OneTheory’s physical interpretation.

## Belongs here

`numbers.py` owns strict rational and Q(ω) arithmetic. `linear.py` owns immutable exact rectangular matrices and vectors, products, RREF, rank, nullspaces, inverses, determinants, and integer powers. `polynomials.py` owns normalized sparse arithmetic, exact substitutions, polynomial-matrix determinants and maximal minors, and univariate division, derivatives, and monic GCDs. `finite.py` owns prime fields, finite forms, exhaustive enumeration, invertible maps, and deterministic finite orbits. `lattices.py` owns integral Gram lattices, exact pairings and roots, prime reduction, affine quadratic shells, and integer-action orbits. Ideals and elimination remain future work; `geometry.py` owns divisors, intersections, Chern and curve data; and `homological.py` Čech, Koszul, DGA, homotopy, and transferred-product machinery.

## Does not belong here

Physical meanings assigned to coincidences, Schoen-specific assumptions, observed-data fitting, speculative bridges, or unsupported family interpretations do not belong here.

## Dependencies

Math may use core policy and other reusable mathematics, but not physics, models, engine, reality, verification, research, or observations.

## Promotion condition

Research may be promoted only after exact conventions, reproducibility, independent mathematical certification, scientific review, and tests establish that the result is reusable mathematics rather than an unresolved physical claim.
