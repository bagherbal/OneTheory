"""Test the exact scalar target of the mixed-Schoen determinant trace.

Owns:
    Regression gates for determinant cancellation, adjunction, the unique top
    residue generator, and the explicit missing contraction boundary.

Depends on:
    The lawful constituent resolutions and diagonal line-cohomology transfer.

Must not:
    Invent an alternating contraction or interpret the residue generator as a
    Yukawa coefficient.

Phase 0:
    Integration tests for the exact scalar trace target only.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_scalar_trace import (
    OUTPUT,
    mixed_schoen_scalar_trace_target,
)


def test_determinants_cancel_into_the_unique_top_residue() -> None:
    """Virtual determinants and adjunction identify one scalar target."""

    target = mixed_schoen_scalar_trace_target()
    assert target.constituent_ranks == (2, 2)
    assert target.determinant_degrees == ((-2, 2, 0), (2, -2, 0))
    assert target.determinant_product_degree == (0, 0, 0)
    assert target.equation_degree_sum == (3, 2, 3, 2)
    assert target.ambient_canonical_degree == (-3, -2, -3, -2)
    assert target.structure_sheaf_cohomology == (1, 0, 0, 1)
    assert target.top_subset == (0, 1, 2)
    assert target.top_ambient_degree == (-3, -2, -3, -2)
    assert target.top_monomials == (
        (-1, -1, -1),
        (-1, -1),
        (-1, -1, -1),
        (-1, -1),
    )
    assert target.exact


def test_scalar_target_artifact_does_not_fabricate_the_contraction() -> None:
    """A one-dimensional residue target does not imply a bundle pairing."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["target"]["top_reduced_dimension"] == 1
    assert payload["coordinate_residue_target_available"] is True
    assert payload["alternating_determinant_contraction_available"] is False
    assert payload["holomorphic_yukawa_matrix_available"] is False
    assert payload["next_required_object"].startswith(
        "an exact alternating chain contraction"
    )
