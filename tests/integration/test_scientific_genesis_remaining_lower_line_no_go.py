"""Test exhaustion of the final declared computable-carrier blocks.

Owns:
    Final family counts, frozen scalar orbits, exact lower-line lifting, slope
    exclusion, scoped category exhaustion, and the next research frontier.

Depends on:
    The shared lower-line screen and final-block no-go certificate.

Must not:
    Extrapolate to general Schoen bundles, sample a polarization, or select an
    extension point.

Phase 0:
    Candidates 5/25 exact stability no-go regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.pair_73_stability_wall import (
    _slope_polynomial,
)
from research.experiments.scientific_genesis.remaining_lower_line_no_go import (
    OUTPUT,
    remaining_lower_line_no_go,
)


def test_final_screen_covers_every_frozen_projective_family() -> None:
    """Both final blocks contribute all dimension-102/108 orbit spaces."""

    result = remaining_lower_line_no_go()

    assert result.checked_pair_count == 72
    assert dict(result.dimension_counts) == {102: 36, 108: 36}
    assert dict(result.orbit_space_counts) == {
        "P^101(Q(omega))": 36,
        "P^107(Q(omega))": 36,
    }


def test_final_lower_line_lifts_for_every_parameter() -> None:
    """The exact zero Hom pullback survives both factor orientations."""

    result = remaining_lower_line_no_go()

    assert result.zero_hom_section_maps
    assert result.factor_exchange_exact
    assert result.first_orientation_left_line == (
        Rational(4),
        Rational(-1),
        Rational(2),
    )
    assert result.first_orientation_lower_line == (
        Rational(-4),
        Rational(1),
        Rational(-1),
    )


def test_final_slope_identity_makes_the_common_chamber_empty() -> None:
    """The two required negative slopes sum to the positive fiber slope."""

    result = remaining_lower_line_no_go()
    expected = _slope_polynomial(
        schoen_geometry().quotient_divisor((0, 0, 1)),
        1,
    )

    assert result.positive_sum == expected
    assert result.positive_sum == (
        result.first_orientation_left_slope
        + result.first_orientation_lower_slope
    )
    assert all(coefficient > 0 for _, coefficient in expected.terms)


def test_final_artifact_exhausts_only_the_declared_category() -> None:
    """The no-go empties the current finite search without globalizing it."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == remaining_lower_line_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["remaining_declared_blocks_refuted"] is True
    assert stored["declared_computable_carrier_category_exhausted"] is True
    assert stored["global_schoen_bundle_no_go"] is False
    assert stored["remaining_nonzero_candidate_blocks"] == []
    assert stored["remaining_nonzero_family_count"] == 0
