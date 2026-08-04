# Unit tests

## Purpose

This directory is reserved for focused tests of promoted mathematical primitives, core policies, and general physical objects once those objects have real implementations.

## Belongs here

Deterministic tests for exact arithmetic, linear algebra, geometry, homological constructions, units, precision policy, and general law objects belong here when their contracts are established.

## Does not belong here

Open research calculations, synthetic physical data, observational selection, integration workflows, or tests that silently choose normalization conventions do not belong here.

## Dependencies

Unit tests may import the production layer under test and lower allowed dependencies. They must not be imported by production or use research as a hidden source of expected results.

## Promotion condition

Research mathematics may be promoted only after a reproducible result has an independent certificate, explicit conventions, scientific review, and a stable production API that these tests can exercise.
