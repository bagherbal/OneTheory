# `heterotic_schoen`

## Purpose

This package is the concrete home for the published one-Higgs heterotic Schoen carrier and calculations that directly belong to it.

## Belongs here

The modules divide the carrier into quotient geometry, observable SU(4) data, flavor and rank lifting, Ricci-flat and HYM metrics, worldsheet instantons and determinant lines, hidden-bundle construction, global consistency, carrier-specific vacuum stabilization, and the direct effective-action boundary. `geometry.py` freezes the published cover, quotient, Cox, intersection, and symmetry handoff. `visible.py` reproduces the exact point schemes, Serre rays, one-Higgs SU(4) extension metadata, Wilson-line breaking, and published spectrum counts. `consistency.py` keeps local differential anomaly data separate from the integrated Chern identity. `effective.py` reuses the same geometry and visible spectrum with the established ten-dimensional law records, symbolic K/W/f/D slots, and a complete fail-closed prerequisite graph. The published carrier is an input; downstream closure is not assumed.

## Does not belong here

Unsupported native-origin derivations, generation-carrier maps, empirical selectors, the superseded two-Higgs carrier, nonphysical witness quartics, excluded hidden-bundle routes, and generic execution or verification machinery do not belong here.

## Dependencies

The carrier modules may use core, reusable mathematics, general physics, and direct sibling carrier data. They must not import engine, reality, verification, research, tests, or observations upstream.

## Promotion condition

Research may be promoted only when the exact carrier-specific input is constructed, its status and provenance are explicit, independent mathematical or numerical evidence is available, scientific review is complete, and tests preserve unresolved dependencies instead of fabricating an object.
