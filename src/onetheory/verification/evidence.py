"""Provenance and evidence classification for production results.

Owns:
    Source provenance, evidence classes, exact-versus-numerical status, scope, and
    declared evidence records for inspected calculations.

Depends on:
    Production objects under inspection and standard-library metadata machinery; it
    remains outside the physical dependency direction.

Must not:
    Create physical objects, hide missing inputs, or let observations select an
    upstream model.

Phase 0:
    Structural module only; no scientific implementation is provided yet.
"""
