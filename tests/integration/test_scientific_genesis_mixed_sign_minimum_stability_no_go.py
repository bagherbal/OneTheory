"""Test the exact mixed-sign minimum stability no-go.

Owns:
    Exhaustive family counts, typed right-line restriction, lifted-line slope
    positivity, prior-chamber supersession, and the next carrier frontier.

Depends on:
    Exact invariant/action artifacts and the mixed-sign no-go classifier.

Must not:
    Extrapolate beyond candidates 15 and 35, sample positivity, select an Ext
    point, or claim a global computable-carrier no-go.

Phase 0:
    Mixed-sign minimum no-go regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_sign_minimum_stability_no_go import (
    OUTPUT,
    mixed_sign_minimum_stability_no_go,
)


def test_no_go_covers_every_family_in_both_factor_orientations() -> None:
    """Both mixed-sign blocks contribute all 72 exact projective families."""

    result = mixed_sign_minimum_stability_no_go()

    assert result.block_pair_ranges == ((15, 505, 540), (35, 1225, 1260))
    assert result.checked_pair_count == 72
    assert dict(result.dimension_counts) == {18: 36, 24: 36}
    assert dict(result.orbit_space_counts) == {
        "P^17(Q(omega))": 36,
        "P^23(Q(omega))": 36,
    }


def test_every_cocycle_misses_the_right_line_restriction_columns() -> None:
    """Precomposition vanishes on all three exact Hom support profiles."""

    result = mixed_sign_minimum_stability_no_go()
    restriction = set(result.right_line_restriction_indices)

    assert result.right_line_restriction_indices == (4, 9, 14)
    assert len(result.support_profiles) == 3
    assert all(set(profile).isdisjoint(restriction) for profile in result.support_profiles)
    assert result.as_record()["right_serre_line_lifts_for_every_parameter"] is True


def test_lifted_right_line_is_positive_on_the_full_kahler_cone() -> None:
    """The additional line destabilizes even inside the necessary chamber."""

    result = mixed_sign_minimum_stability_no_go()
    record = result.as_record()

    assert result.first_orientation_right_line_c1 == (
        Rational(5),
        Rational(1),
        Rational(-2),
    )
    assert all(
        coefficient > 0
        for _, coefficient in result.first_orientation_right_line_slope.terms
    )
    assert record["strictly_positive_on_kahler_cone"] is True
    assert record["necessary_forced_chamber_was_not_sufficient"] is True


def test_mixed_sign_no_go_artifact_advances_without_globalizing() -> None:
    """The scoped exclusion advances to dimension 42 and keeps later blocks open."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == mixed_sign_minimum_stability_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["mixed_sign_minimum_refuted"] is True
    assert stored["global_computable_carrier_no_go"] is False
    assert stored["next_invariant_ext_dimension"] == 42
    assert stored["next_candidate_blocks"] == [16, 36]
