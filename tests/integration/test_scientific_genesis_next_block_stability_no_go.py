"""Test the exact next-topology-block stability exclusion.

Owns:
    Exhaustive six/eight-dimensional counts, restriction support, exact line
    slopes, Kahler-cone positivity, and the scoped no-go boundary.

Depends on:
    Complete invariant and automorphism artifacts plus the deterministic
    next-block stability classifier.

Must not:
    Extrapolate beyond candidates 14 and 34, use sampled positivity, select an
    Ext point, or call the scoped result a global computable-carrier no-go.

Phase 0:
    Next-topology-block tests only; later topology blocks remain open.
"""

import json

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.next_block_stability_no_go import (
    OUTPUT,
    next_block_stability_no_go,
)


def test_next_block_exhausts_both_factor_orientations() -> None:
    """Candidates 14 and 34 contribute all 72 independently computed pairs."""

    result = next_block_stability_no_go()
    record = result.as_record()

    assert result.checked_pair_count == 72
    assert result.block_pair_ranges == ((14, 469, 504), (34, 1189, 1224))
    assert dict(result.dimension_counts) == {6: 36, 8: 36}
    assert [block["pair_count"] for block in record["candidate_blocks"]] == [36, 36]
    assert record["invariant_ext_dimension_counts"] == {"6": 36, "8": 36}


def test_every_ext_basis_misses_the_right_line_restriction() -> None:
    """All support profiles force the right Serre line to lift universally."""

    result = next_block_stability_no_go()
    restriction = set(result.right_line_restriction_indices)

    assert result.right_line_restriction_indices == (4, 9, 14, 19)
    assert len(result.support_profiles) == 3
    assert all(set(profile).isdisjoint(restriction) for profile in result.support_profiles)
    record = result.as_record()
    assert record["source_parent_hom_degree"] == -1
    assert record["source_parent_hom_type"] == "Hom(F0_right,F1_left)"
    assert record["right_serre_line_lifts_for_every_parameter"] is True


def test_right_line_slope_is_symbolically_positive_on_the_kahler_cone() -> None:
    """Coefficient positivity proves instability without a sampled polarization."""

    result = next_block_stability_no_go()
    expected = Polynomial(
        {
            (2, 0, 0): Rational(1, 3),
            (1, 1, 0): Rational(2),
            (1, 0, 1): Rational(2),
            (0, 2, 0): Rational(5, 3),
            (0, 1, 1): Rational(10),
        },
        variable_count=3,
    )

    assert result.first_orientation_slope == expected
    assert all(coefficient > 0 for _, coefficient in expected.terms)
    assert result.as_record()["strictly_positive_on_kahler_cone"] is True
    assert result.as_record()["sampled_polarization_used"] is False


def test_next_block_artifact_remains_a_scoped_no_go() -> None:
    """The exact block retirement leaves later topology blocks open."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == next_block_stability_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["next_topology_block_refuted"] is True
    assert stored["global_computable_carrier_no_go"] is False
    assert stored["arbitrary_pair_selected"] is False
    assert stored["arbitrary_extension_point_selected"] is False
