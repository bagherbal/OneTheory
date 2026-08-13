"""Test the exact mixed-sign minimum forced chamber.

Owns:
    Exhaustive family and orbit counts, symbolic inequalities, rational chamber
    certificates, factor exchange, and the boundary before full stability.

Depends on:
    Exact invariant/action artifacts and the mixed-sign chamber derivation.

Must not:
    Treat necessary forced-subobject inequalities as sufficient stability,
    choose a physical polarization, or select an extension coordinate.

Phase 0:
    Necessary-chamber regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_sign_minimum_chamber import (
    OUTPUT,
    mixed_sign_minimum_chamber,
)


def test_mixed_sign_minimum_covers_both_factor_orientations() -> None:
    """Candidates 15 and 35 contribute all 72 directly projective families."""

    result = mixed_sign_minimum_chamber()

    assert result.block_pair_ranges == ((15, 505, 540), (35, 1225, 1260))
    assert result.checked_pair_count == 72
    assert dict(result.dimension_counts) == {18: 36, 24: 36}
    assert dict(result.orbit_space_counts) == {
        "P^17(Q(omega))": 36,
        "P^23(Q(omega))": 36,
    }


def test_left_line_and_constituent_share_one_exact_wall() -> None:
    """Twice the line Chern class at twice the rank gives the same slope."""

    result = mixed_sign_minimum_chamber()

    assert result.left_line_slope == result.left_constituent_slope
    assert result.left_line_slope.terms == (
        ((2, 0, 0), Rational(-1, 3)),
        ((1, 1, 0), Rational(2)),
        ((1, 0, 1), Rational(-2)),
        ((0, 2, 0), Rational(-2, 3)),
        ((0, 1, 1), Rational(-4)),
    )


def test_rational_family_certifies_a_strict_common_chamber() -> None:
    """The exact ray t greater than seven halves makes every forced slope negative."""

    result = mixed_sign_minimum_chamber()
    record = result.as_record()

    assert result.witness == (Rational(2), Rational(1), Rational(4))
    assert result.witness_values == (Rational(-30), Rational(-30), Rational(-1, 3))
    assert record["common_forced_subobject_chamber_nonempty"] is True
    assert record["first_orientation"]["one_parameter_certificate"]["condition"] == "t>7/2"
    assert record["factor_exchanged_orientation"]["coordinate_rule"] == "exchange j1 and j2"


def test_chamber_artifact_stops_before_full_stability() -> None:
    """The necessary chamber keeps all additional saturated subsheaves open."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == mixed_sign_minimum_chamber().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["full_slope_stability_proved"] is False
    assert stored["additional_saturated_subsheaves_classified"] is False
    assert stored["arbitrary_extension_point_selected"] is False
    assert stored["physical_polarization_selected"] is False
