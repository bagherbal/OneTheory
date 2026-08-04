# Unit tests

## Purpose

This directory contains focused tests of promoted mathematical primitives and will
later cover core policies and general physical objects. The first implementation
under test is the exact rational and Eisenstein-number foundation in `math/numbers.py`.

## Belongs here

Deterministic tests for exact arithmetic, linear algebra, geometry, homological constructions, units, precision policy, and general law objects belong here when their contracts are established. Property tests should exercise algebraic laws without importing migration sources.

## Does not belong here

Open research calculations, synthetic physical data, observational selection, integration workflows, or tests that silently choose normalization conventions do not belong here.

## Dependencies

Unit tests may import the production layer under test and lower allowed dependencies. They must not be imported by production or use research as a hidden source of expected results.

## Promotion condition

Research mathematics may be promoted only after a reproducible result has an independent certificate, explicit conventions, scientific review, and a stable production API that these tests can exercise.
