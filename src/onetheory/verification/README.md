# `verification`

## Purpose

Verification is the scientific firewall around production calculations. It inspects claims and artifacts without defining their physical content.

## Belongs here

`evidence.py` will classify provenance and evidence. `certificates.py` will record deterministic mathematical and numerical certificates. `gates.py` will represent accepted, failed, unresolved, and killed conditions. `audit.py` will inspect consistency, reproducibility, source, dependencies, and artifacts.

## Does not belong here

Physical laws, model implementations, guessed outputs, hidden defaults, or a mechanism that makes unresolved physics appear complete do not belong here.

## Dependencies

Verification may inspect all production layers, but core, math, physics, models, engine, and reality must not import verification. Verification must not import research.

## Promotion condition

Research may be promoted only after its result has a declared evidence class, provenance, independent certificate or convergence audit, scientific review, correct domain placement, and tests; verification records that evidence but does not create it.
