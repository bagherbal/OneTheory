# `core`

## Purpose

Core contains universal engineering primitives required by every later layer.

## Belongs here

`units.py` will own dimensions, units, conversions, and dimensional-consistency policy. `precision.py` owns exact-versus-numerical policy, tolerances, exact-input admission, and convergence rules. `errors.py` owns explicit missing-input, convention, normalization, convergence, dimension, and dependency failures.

## Does not belong here

Physics models, scientific claims, certificate registries, project history, observations, and carrier-specific conventions do not belong here. Core must not become a general utility drawer for higher-layer concepts.

## Dependencies

Core depends only on standard-library and universal core machinery. It is the bottom of the production graph and imports no other OneTheory layer.

## Promotion condition

Research may be promoted here only when a primitive is general rather than carrier-specific, has explicit semantics and failure behavior, carries reproducible tests and review, and does not smuggle a scientific interpretation into an engineering abstraction.
