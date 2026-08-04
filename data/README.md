# `data`

## Purpose

This directory separates traceable inputs, terminal observations, and reproducible generated outputs from executable production code.

## Belongs here

`published` holds immutable source-backed carrier and mathematical metadata; `observations` holds measured quantities used only for terminal comparison and falsification; `generated` holds declared-input outputs produced reproducibly by code.

## Does not belong here

Hidden geometry selectors, fitted coefficients, undocumented normalization choices, synthetic physical results, or source code do not belong here. Observations must not be imported upstream by geometry, bundle, vacuum, or rank-lifting code.

## Dependencies

Production may eventually consume approved published manifests and generated outputs only when they are declared inputs. Observations are terminal consumers of predictions, not upstream dependencies.

## Promotion condition

Research data may be promoted only with provenance, immutable manifests, exact or numerical status, reproducibility evidence, review, and a declared owning production computation. Generated data must never become an undeclared source input.
