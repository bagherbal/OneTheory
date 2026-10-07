# `math`

## Purpose

Math contains exact, reusable mathematics independent of OneTheory’s physical interpretation.

## Belongs here

`numbers.py` owns strict rational and Q(ω) arithmetic. `linear.py` owns immutable exact rectangular matrices and vectors, products, RREF, rank, nullspaces, inverses, determinants, and integer powers. `polynomials.py` owns normalized sparse arithmetic, exact substitutions, polynomial matrices, free modules, chain maps and homotopies, determinantal and Fitting ideals, scoped monomial saturation, rank loci, determinants and maximal minors, and univariate division, derivatives, and monic GCDs. `sections.py` owns generic multigraded Cox monomials, homogeneous ideal quotient normal forms, exact pullbacks, deterministic bases, and finite section actions. `finite.py` owns prime fields, finite forms, exhaustive enumeration, invertible maps, and deterministic finite orbits. `lattices.py` owns integral Gram lattices, exact pairings and roots, prime reduction, affine quadratic shells, and integer-action orbits. `geometry.py` owns named-basis divisors and curves, symmetric intersections, exact characteristic classes, volumes, slopes, and explicit normalization conversion. `homological.py` owns basis-aware graded spaces, typed exact maps, complexes, homology, homotopies, cones, direct sums, and signed totalization. `cech.py` owns constant and typed restricted Čech complexes, standard-projective Laurent-monomial complexes, exact alternating differentials, and deterministic primitives for coboundaries. `sheaves.py` owns generic Laurent localization, named Cox charts, chart-localized free modules and maps, transition matrices, and cocycle checks. Carrier-specific sheafification, unrestricted saturation, elimination, and physical bundle claims remain outside reusable mathematics.

## Does not belong here

Physical meanings assigned to coincidences, Schoen-specific assumptions, observed-data fitting, speculative bridges, unsupported family interpretations, physical sheaf claims, DGAs, and transferred products do not belong here. Generic exact localization and Čech incidence machinery is allowed; a carrier-specific cover or transition system requires independent certification.

## Dependencies

Math may use core policy and other reusable mathematics, but not physics, models, engine, reality, verification, research, or observations.

## Finite-complex conventions

Homological coordinates always carry their named ordered basis and coefficient
field. An omitted construction name may be generated; an explicitly invalid name
is rejected. Shifting by `k` moves degree `n` to `n+k` and multiplies the
differential by `(-1)^k`. Chain differentials lower degree; cochain differentials
raise it. The cone of `A → B` orders `B` before the shifted `A`, with differential
blocks `((d_B, f), (0, -d_A))`. Bicomplex directions commute before totalization,
which uses `d_horizontal + (-1)^p d_vertical`. Cohomology representatives follow
the declared basis and deterministic exact elimination; they are not a canonical
geometric choice. These constructions require no sheaf or physical bundle data.

## Promotion condition

Research may be promoted only after exact conventions, reproducibility, independent mathematical certification, scientific review, and tests establish that the result is reusable mathematics rather than an unresolved physical claim.
