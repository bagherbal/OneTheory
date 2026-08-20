"""Tests for the frozen invariant outer Čech representative certificate.

Owns:
    Content addressing, source-independent action gates, invariant dimensions,
    and explicit full-complex representative metadata.

Depends on:
    The generated invariant certificate and deterministic digest utility.

Must not:
    Recompute the expensive transfer in routine tests, select an extension
    coordinate, or promote cover representatives to a physical rank-four bundle.

Phase 0:
    Frozen exact-certificate tests only; outer extension selection remains open.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_outer_cech_invariants import (
    OUTPUT,
)


def test_published_outer_invariant_artifact_is_exact_and_content_addressed() -> None:
    """Both action representations and every full representative close exactly."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["schema"] == "published-outer-cech-invariants-v1"
    assert stored["expected_invariant_dimensions_used_as_action_inputs"] is False
    assert stored["relative_character_fitted"] is False
    assert stored["all_representatives_explicit"] is True
    assert stored["outer_extension_coordinate_selected"] is False
    assert stored["rank_four_bundle_constructed"] is False
    assert stored["synchronized_constituent_frame_characters"] == {
        "V1": {"P": "-1-omega", "T": "1"},
        "V2": {"P": "-1-omega", "T": "1"},
    }

    for direction, cover_dimension, invariant_dimension in (
        ("forward", 36, 4),
        ("reverse", 72, 8),
    ):
        record = stored[direction]
        assert record["cover_h1_dimension"] == cover_dimension
        assert record["invariant_h1_dimension"] == invariant_dimension
        assert record["cohomology_action"]["order_three_and_commuting"] is True
        assert record["images_are_cycles"] is True
        assert record["full_representatives_are_cycles"] is True
        assert record["full_representatives_are_strictly_invariant"] is True
        assert record["exact"] is True
        assert len(record["reduced_representatives"]) == invariant_dimension
        assert len(record["full_cech_koszul_representatives"]) == invariant_dimension
        assert all(
            representative["term_count"] == len(representative["terms"])
            and representative["term_count"] > 0
            for representative in record["full_cech_koszul_representatives"]
        )


def test_full_representative_labels_expose_the_common_complex_coordinates() -> None:
    """Serialized cocycles retain object, Koszul, monomial, and cover-cell labels."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    expected = {
        "left_object",
        "right_object",
        "object_degree",
        "line_degree",
        "koszul_summand",
        "x_monomial",
        "u_monomial",
        "p_monomial",
        "cell",
    }
    for direction in ("forward", "reverse"):
        for representative in stored[direction]["full_cech_koszul_representatives"]:
            assert all(set(term["basis"]) == expected for term in representative["terms"])
