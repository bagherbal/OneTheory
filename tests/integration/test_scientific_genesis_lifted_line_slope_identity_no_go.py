"""Test the lifted-line slope-identity no-go.

Owns:
    Exhaustive family counts, typed restriction selectors, exact slope identity,
    factor exchange, scoped exclusion, and the next carrier frontier.

Depends on:
    Invariant/action artifacts and the lifted-line identity classifier.

Must not:
    Extrapolate beyond candidates 16 and 36, sample a polarization, select an
    extension point, or infer a global computable-carrier no-go.

Phase 0:
    Lifted-line identity no-go regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.lifted_line_slope_identity_no_go import (
    OUTPUT,
    lifted_line_slope_identity_no_go,
)


def test_identity_no_go_covers_both_factor_orientations() -> None:
    """Candidates 16 and 36 contribute every dimension-42/48 family."""

    result = lifted_line_slope_identity_no_go()

    assert result.block_pair_ranges == ((16, 541, 576), (36, 1261, 1296))
    assert result.checked_pair_count == 72
    assert dict(result.dimension_counts) == {42: 36, 48: 36}
    assert dict(result.orbit_space_counts) == {
        "P^41(Q(omega))": 36,
        "P^47(Q(omega))": 36,
    }


def test_all_typed_source_profiles_miss_right_line_precomposition() -> None:
    """Hom degrees minus one and zero miss their exact source columns."""

    result = lifted_line_slope_identity_no_go()
    record = result.as_record()

    assert result.support_profile_sizes == (19, 29, 29)
    assert result.minus_one_restriction_selectors == ((-1, 4), (-1, 9), (-1, 14))
    assert result.zero_restriction_selectors == (
        (0, 4),
        (0, 9),
        (0, 14),
        (0, 19),
        (0, 24),
    )
    assert record["all_restriction_support_intersections_empty"] is True
    assert record["right_serre_line_lifts_for_every_parameter"] is True


def test_positive_slope_identity_makes_the_common_chamber_empty() -> None:
    """Two required negative slopes have a strictly positive linear combination."""

    result = lifted_line_slope_identity_no_go()
    expected = Polynomial(
        {
            (1, 1, 0): Rational(12),
            (0, 2, 0): Rational(6),
            (0, 1, 1): Rational(36),
        },
        variable_count=3,
    )

    assert result.positive_combination == expected
    assert result.positive_combination == (
        result.first_orientation_preimage_slope.scale(9)
        + result.first_orientation_lifted_line_slope.scale(3)
    )
    assert all(coefficient > 0 for _, coefficient in expected.terms)
    assert result.as_record()["common_necessary_chamber"] == "empty"


def test_identity_no_go_advances_without_globalizing() -> None:
    """The scoped theorem advances to dimension 50 and keeps later blocks open."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == lifted_line_slope_identity_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["lifted_line_identity_block_refuted"] is True
    assert stored["global_computable_carrier_no_go"] is False
    assert stored["next_invariant_ext_dimension"] == 50
    assert stored["next_candidate_blocks"] == [4, 24]
