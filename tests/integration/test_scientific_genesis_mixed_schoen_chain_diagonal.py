"""Integration tests for the lawful mixed-Schoen chain diagonal."""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_diagonal import (
    OUTPUT,
    chain_diagonal_square_witness,
)


def test_chain_diagonal_closes_prior_discriminating_witnesses() -> None:
    """The canonical grouped tensor signs remove each prior D-squared witness."""

    witnesses = (
        chain_diagonal_square_witness(0, 0),
        chain_diagonal_square_witness(1, 1),
        chain_diagonal_square_witness(1, 10),
    )

    assert [(item.seed_term_count, item.first_image_term_count) for item in witnesses] == [
        (4, 100),
        (6, 51),
        (4, 82),
    ]
    assert all(item.squared_zero for item in witnesses)


def test_chain_diagonal_artifact_is_exhaustive_and_fail_closed() -> None:
    """The certificate audits every transfer seed without fabricating a Higgs class."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")

    assert digest == _canonical_digest(payload)
    assert payload["construction"] == {
        "diagonal_equation_count": 3,
        "full_extension_term_count": 1278,
        "independent_cover_factor_count": 4,
        "object_count": 48,
        "signed_tensor_totalization": True,
    }
    assert payload["constituent_inputs"] == {
        "all_full_cech_cocycles_exact": True,
        "retired_constituent_cones_used": False,
        "shared_cover_flattening_used": False,
    }
    assert payload["square_audit"] == {
        "all_transfer_seed_squares_zero": True,
        "degree_dimensions": [[0, 900], [1, 2180], [2, 1539], [3, 268], [4, 9]],
        "nonzero_witnesses": [],
        "witness_count": 4896,
    }
    assert payload["physical_higgs_representative_available"] is False
    assert "ambient-cohomology transfer" in payload["next_required_object"]
    assert "strict P/T action" in payload["next_required_object"]
