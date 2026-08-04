"""Exact linear and multilinear algebra primitives.

Owns:
    Matrices, vectors, tensors, rank, determinants, kernels, nullspaces, and exact
    linear operations needed by later mathematical and physical domains.

Depends on:
    Core policy and reusable mathematics, especially exact scalar types; it does not
    depend on physics or concrete carrier modules.

Must not:
    Hide basis choices, fabricate matrices, infer physical spectra, or assign meaning
    to an algebraic rank coincidence.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
