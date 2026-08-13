"""Test the universally lifted lower-line stability obstruction.

Owns:
    Exact section maps, zero outer-Ext pullback, positive slope identity,
    exhaustive family counts, and the next carrier frontier.

Depends on:
    Sparse Schoen Koszul complexes and the lower-line no-go classifier.

Must not:
    Extrapolate beyond candidates 4 and 24, select an extension point, or
    infer a global computable-carrier no-go.

Phase 0:
    Dimension-50/52 lower-line no-go regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_line_bundle,
)
from research.experiments.scientific_genesis.lower_line_sections import (
    SECTION_DEGREES,
    lower_line_section_components,
)
from research.experiments.scientific_genesis.next_survivor_lower_line_no_go import (
    OUTPUT,
    next_survivor_lower_line_no_go,
)
from research.experiments.scientific_genesis.pair_73_stability_wall import (
    _slope_polynomial,
)


def test_unique_lower_line_sections_are_exact_in_both_orientations() -> None:
    """Both factor sections define nonzero chain maps with square-zero targets."""

    for factor, degree in SECTION_DEGREES.items():
        source = sparse_line_bundle(0, 0, 0)
        target = sparse_line_bundle(*degree)
        components = dict(lower_line_section_components(source, factor))

        assert source.squared_zero
        assert target.squared_zero
        assert target.space(0).dimension - target.differential(0).rank() == 1
        assert components[0].rank() == 1
        assert all(
            target.differential(index).compose(component)
            == components[index + 1].compose(source.differential(index))
            for index, component in components.items()
            if index + 1 in components
        )


def test_lower_line_pullback_vanishes_for_every_family() -> None:
    """The zero chain map lifts the lower line over all 72 parameter spaces."""

    result = next_survivor_lower_line_no_go()

    assert result.checked_pair_count == 72
    assert dict(result.dimension_counts) == {50: 36, 52: 36}
    assert dict(result.orbit_space_counts) == {
        "P^49(Q(omega))": 36,
        "P^51(Q(omega))": 36,
    }
    assert result.zero_hom_section_maps
    assert result.factor_exchange_exact


def test_positive_fiber_slope_excludes_a_common_stability_chamber() -> None:
    """Two required negative line slopes sum to a strictly positive slope."""

    result = next_survivor_lower_line_no_go()
    expected = _slope_polynomial(
        schoen_geometry().quotient_divisor((0, 0, 1)),
        1,
    )

    assert result.first_orientation_left_line == (
        Rational(4),
        Rational(-1),
        Rational(1),
    )
    assert result.first_orientation_lower_line == (
        Rational(-4),
        Rational(1),
        Rational(0),
    )
    assert result.positive_sum == expected
    assert all(coefficient > 0 for _, coefficient in expected.terms)


def test_lower_line_artifact_advances_without_globalizing() -> None:
    """The content-addressed no-go retires only candidates 4 and 24."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == next_survivor_lower_line_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["candidate_blocks_refuted"] is True
    assert stored["global_computable_carrier_no_go"] is False
    assert stored["remaining_nonzero_candidate_blocks"] == [5, 25]
    assert stored["remaining_nonzero_family_count"] == 72
    assert stored["next_invariant_ext_dimensions"] == [102, 108]
