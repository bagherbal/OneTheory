# `src`

## Purpose

This directory contains the installable Python package in a `src` layout. It separates importable production code from tests, migration sources, research experiments, and data artifacts.

## Belongs here

Only the `onetheory` package and its six architectural layers belong here: universal core policy, reusable mathematics, general physics, concrete models, execution machinery, and external verification.

## Does not belong here

Paper text, the standalone verifier, unresolved experiments, observations, generated outputs, command-line code, or a second implementation of a scientific result do not belong here. Production modules must not import `research`.

## Dependencies

The package follows the documented lower-to-higher dependency direction. The source layout itself has no runtime dependency beyond Python during Phase 0.

## Promotion condition

Research may be promoted into this directory only after reproducibility, an independent mathematical or numerical certificate, scientific review, and placement in the real owning domain have all been completed.
