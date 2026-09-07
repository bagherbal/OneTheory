"""Test the exact local comparison required by the first deformation product.

Owns:
    Regression gates for the two chartwise pencil identities, overlap Koszul
    homotopy, and obstruction to a global homogeneous polynomial lift.

Depends on:
    The published Schoen cubics and the research diagonal-comparison experiment.

Must not:
    Treat local fractions as global polynomials, infer a higher product, select
    a carrier point, or report a Yukawa coefficient.

Phase 0:
    Integration tests for the Cech-local higher-product comparison boundary.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_diagonal_comparison import (
    OUTPUT,
    mixed_schoen_diagonal_comparison,
)


def test_second_pencil_has_two_exact_local_diagonal_lifts() -> None:
    """The two chart formulas agree through the exact Koszul syzygy."""

    result = mixed_schoen_diagonal_comparison()
    assert result.q0_cross_identity
    assert result.q1_cross_identity
    assert result.overlap_syzygy_identity
    assert result.global_coefficient_degrees == ((0, 1, -1), (3, 0, -1))
    assert not result.global_polynomial_lift_exists
    assert result.exact


def test_diagonal_comparison_artifact_keeps_the_deformation_unresolved() -> None:
    """The certificate exposes the local chain map as the next exact object."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["cech_local_comparison_required"] is True
    assert payload["global_homogeneous_polynomial_lift_exists"] is False
    assert payload["fiber_identification_by_substitution_used"] is False
    assert payload["deformation_product_computed"] is False
    assert payload["next_required_object"].startswith(
        "the full Cech-local chain comparison"
    )
