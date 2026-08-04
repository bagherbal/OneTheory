# `physics`

## Purpose

Physics contains general physical laws and concepts that do not depend on the selected Schoen realization.

## Belongs here

Spacetime, quantum kinematics, fields, gauge theory, matter and flavor, gravity, heterotic string principles, vacuum structure, and terminal observable interfaces belong in the named modules. The general kernel now provides arbitrary-dimensional pseudo-Riemannian tensors and forms, exterior calculus and Hodge records, typed action terms, gauge covariance records, chiral matter and symbolic Yukawa maps, canonical quantum relations, Einstein-law contracts, convention-frozen ten-dimensional heterotic action terms, compactification/HYM conditions, explicit KK modes, Wilson-line projections, and reduction provenance. `gauge.py` owns exact group, connection, and anomaly metadata; `matter.py` owns immutable particle multiplets, generations, and interaction checks; `strings.py` owns ten-dimensional fields, frames, bundles, Wilson lines, and published-input descriptors; `compactification.py` owns generic reduction types; and `vacuum.py` owns symbolic N=1 effective-action structures.

## Does not belong here

Concrete Schoen geometry or bundles, measured-data selectors, native-origin bridges, failed routes, guessed coefficients, and simulation-only duplicate physics do not belong here.

## Dependencies

Physics may depend on core and reusable mathematics and may compose its own general-law modules. It remains independent of concrete models, engine execution, verification, research, and observations.

## Promotion condition

Research may be promoted only when the law has a precise domain, provenance or derivation, explicit exact or numerical policy, independent certificate where needed, review, and tests at its declared scope.
