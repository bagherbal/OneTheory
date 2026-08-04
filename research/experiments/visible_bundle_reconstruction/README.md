# Visible carrier reconstruction

This experiment is the reproducible reconstruction boundary for the published
one-Higgs heterotic Schoen visible bundle. It combines the frozen source
manifest with the exact production geometry, Hilbert–Burch point schemes,
Serre kernel actions, and the published cohomology dimensions into a
content-addressed `VisibleCarrierArtifact`.

It does not promote research data into `src/onetheory`, choose an extension
class, or manufacture Čech cocycles, transition functions, section matrices,
or conic maps. The retrieved primary sources give the sheaf definitions and
dimension statements, but do not serialize the four invariant Ext cocycles or
the later 404-section evaluation matrix. Those omissions are recorded as an
explicit unresolved prerequisite, not represented by synthetic values.

Run the reproducer from the repository root with the virtual environment
active:

```bash
python -m research.experiments.visible_bundle_reconstruction.reconstruct \
  --output data/generated/visible_carrier/visible_carrier_artifact.json
```

Promotion requires independently certified chain-level data and review of the
artifact status. Until then this experiment remains outside the production
dependency graph.
