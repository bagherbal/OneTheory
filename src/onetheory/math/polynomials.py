"""Exact polynomial and elimination machinery.

Owns:
    Polynomial arithmetic, ideals, minors, elimination utilities, and Hilbert–Burch
    style algebraic operations over declared coefficient systems.

Depends on:
    Core policy and reusable exact mathematics, including numbers and linear algebra.

Must not:
    Treat witness polynomials as physical observables, smuggle in carrier assumptions,
    or use fitted coefficients as derived algebraic input.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
