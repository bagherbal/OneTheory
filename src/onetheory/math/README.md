# `math`

## Purpose

Math contains exact, reusable mathematics independent of OneTheory’s physical interpretation.

## Belongs here

`numbers.py` owns strict rational and Q(ω) arithmetic. `linear.py` owns immutable exact rectangular matrices and vectors, products, RREF, rank, nullspaces, inverses, determinants, and integer powers. `polynomials.py` owns normalized sparse arithmetic, exact substitutions, polynomial-matrix determinants and maximal minors, and univariate division, derivatives, and monic GCDs. Ideals and elimination remain future work. `finite.py` owns finite fields and exhaustive actions; `lattices.py` root and Mordell–Weil lattices; `geometry.py` divisors, intersections, Chern and curve data; and `homological.py` Čech, Koszul, DGA, homotopy, and transferred-product machinery.

## Does not belong here

Physical meanings assigned to coincidences, Schoen-specific assumptions, observed-data fitting, speculative bridges, or unsupported family interpretations do not belong here.

## Dependencies

Math may use core policy and other reusable mathematics, but not physics, models, engine, reality, verification, research, or observations.

## Promotion condition

Research may be promoted only after exact conventions, reproducibility, independent mathematical certification, scientific review, and tests establish that the result is reusable mathematics rather than an unresolved physical claim.
