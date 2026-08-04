# `onetheory`

## Purpose

This package is the executable scientific engine’s architectural root. Its modules will represent mathematical objects, physical laws, concrete carrier data, dependency evaluation, simulation state, and verification boundaries.

## Belongs here

The sole composition root is `reality.py`; the remaining modules belong to `core`, `math`, `physics`, `models`, `engine`, or `verification`. Package initializers remain intentionally quiet and do not re-export future symbols.

## Does not belong here

Paper chapters, historical ledgers, speculative bridges, failed physical routes, guessed observables, synthetic fixtures, rendering code, or unresolved research implementations do not belong in the production package. No module may claim a complete reality model while required inputs are open.

## Dependencies

Lower layers feed higher layers: core supports mathematics, mathematics supports general physics, models realize physics, engine evaluates direct dependencies, and reality composes models with engine machinery. Verification inspects production from outside.

## Promotion condition

A research result may enter its owning module only when its scope, provenance, exact or numerical mode, normalization conventions, reproducibility artifact, and independent certificate have passed scientific review and tests.
