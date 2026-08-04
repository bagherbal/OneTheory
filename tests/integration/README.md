# Integration tests

## Purpose

This directory will test direct compositions across the production dependency graph, including state construction, graph evaluation, simulation trajectories, and terminal observable assembly.

## Belongs here

Integration scenarios for verified model components and explicit unresolved prerequisite chains belong here. Simulation tests must use the same laws and state containers as scientific computation.

## Does not belong here

Rendering software, alternate simplified physics, speculative bridges, guessed missing nodes, or tests that turn observational agreement into an upstream selector do not belong here.

## Dependencies

Integration tests may import the production composition root and declared fixtures from approved data paths. Production code must not import tests or integration helpers.

## Promotion condition

Research may be promoted into an integrated path only after every direct dependency is certified, reproducible, reviewed, and covered by tests that preserve fail-closed behavior for missing inputs.
