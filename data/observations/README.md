# `data/observations`

## Purpose

This directory holds measured quantities used for terminal comparison, uncertainty accounting, and falsification.

## Belongs here

Later entries may include measured masses, mixing angles, CP observables, couplings, and other declared experimental quantities with provenance, units, uncertainties, and release metadata.

## Does not belong here

Geometry selectors, bundle selectors, deformation selectors, fitted production coefficients, synthetic fixtures, or data that silently enters vacuum construction do not belong here.

## Dependencies

Observation data are consumed only after a prediction has been produced. Geometry, compactification, bundle, metric, vacuum, and rank-lifting code must remain independent of this directory.

## Promotion condition

An observation may be promoted here only with a traceable source, declared convention and uncertainty model, immutable manifest, review, and an explicit terminal comparison or falsification role.
