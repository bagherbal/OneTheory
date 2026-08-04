"""Evaluation of exact and numerical graph nodes.

Owns:
    The future orchestration of exact evaluation, controlled numerical evaluation,
    tolerance and convergence reporting, and fail-closed prerequisite handling.

Depends on:
    Core, reusable mathematics, general physics, and engine graph and state machinery;
    it must not depend on concrete models.

Must not:
    Choose a scientific approximation silently, return placeholders, or invent an
    unresolved prerequisite.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
