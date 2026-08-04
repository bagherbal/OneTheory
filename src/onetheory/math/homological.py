"""Homological and derived-algebra primitives.

Owns:
    Chain complexes, cochains, Čech and Koszul constructions, DGAs, homotopies,
    transferred products, and explicit contraction data.

Depends on:
    Core policy and reusable exact mathematics, including linear and polynomial
    structures; it remains independent of physical model interpretation.

Must not:
    Use an abstract complex as a physical bridge, hide basis or sign conventions, or
    claim a carrier calculation without declared input data.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
