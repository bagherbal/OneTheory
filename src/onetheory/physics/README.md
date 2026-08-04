# `physics`

## Purpose

Physics contains general physical laws and concepts that do not depend on the selected Schoen realization.

## Belongs here

Spacetime, quantum kinematics, fields, gauge theory, matter and flavor, gravity, heterotic string principles, vacuum structure, and terminal observable interfaces belong in the named modules. `gauge.py` now owns exact group and representation metadata, `matter.py` owns immutable particle multiplets and spectra, and `strings.py` owns compactification, bundle, Wilson-line, and published-input descriptors. The modules provide homes for laws used by both general computation and concrete models.

## Does not belong here

Concrete Schoen geometry or bundles, measured-data selectors, native-origin bridges, failed routes, guessed coefficients, and simulation-only duplicate physics do not belong here.

## Dependencies

Physics may depend on core and reusable mathematics. It must remain independent of concrete models, engine execution, verification, research, and observations.

## Promotion condition

Research may be promoted only when the law has a precise domain, provenance or derivation, explicit exact or numerical policy, independent certificate where needed, review, and tests at its declared scope.
