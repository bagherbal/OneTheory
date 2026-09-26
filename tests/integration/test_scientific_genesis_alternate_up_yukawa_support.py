"""Regress the alternate universal up-matrix filtration theorem.

Owns:
    Exact exterior support, determinant-degree, and nonpromotion checks.

Depends on:
    The frozen alternate carrier's research-only support calculation.

Must not:
    Treat allowed terms as nonzero couplings or a computed physical matrix.

Phase 0:
    Structural tests before any same-cone Higgs chain contraction.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_yukawa_support import (
    OUTPUT,
    _allowed_degrees,
    alternate_up_yukawa_support,
)


def test_exterior_support_forbids_e_e_and_bounds_parameter_degree() -> None:
    """Only E-F constants and F-F linear terms can reach det V."""

    assert _allowed_degrees("E", "E") == ()
    assert _allowed_degrees("E", "F") == (0,)
    assert _allowed_degrees("F", "E") == (0,)
    assert _allowed_degrees("F", "F") == (1,)
    result = alternate_up_yukawa_support()
    assert result["entry_parameter_degrees"] == [
        [[], [0], [0]],
        [[0], [1], [1]],
        [[0], [1], [1]],
    ]
    assert result["determinant_parameter_degrees_if_nonzero"] == [1]
    assert result["rank_three_established"] is False


def test_support_certificate_does_not_claim_yukawa_values() -> None:
    """Only the block shape, not a matrix coefficient, is certified."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload == alternate_up_yukawa_support()
    assert payload["lambda_coefficients_computed"] is False
    assert payload["higgs_chain_cocycle_constructed"] is False
    assert payload["yukawa_matrix_computed"] is False
