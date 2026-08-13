"""Test the exact current-minimum stability exclusion.

Owns:
    Exhaustive block counts, descended constituent evidence, exact forced-line
    slopes, Kahler-cone positivity, and the scoped no-go boundary.

Depends on:
    Complete carrier artifacts and the deterministic current-minimum classifier.

Must not:
    Extrapolate beyond candidates 8 and 28, sample positivity, select an Ext
    point, or call the scoped result a global computable-carrier no-go.

Phase 0:
    Current-minimum tests only; later topology blocks remain open.
"""

import json

from onetheory.math.numbers import Rational
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.current_minimum_stability_no_go import (
    OUTPUT,
    current_minimum_stability_no_go,
)


def test_current_minimum_exhausts_both_topology_blocks() -> None:
    """Candidates 8 and 28 contribute every one of their 72 exact families."""

    result = current_minimum_stability_no_go()
    record = result.as_record()

    assert result.block_pair_ranges == ((8, 253, 288), (28, 973, 1008))
    assert result.checked_pair_count == 72
    assert dict(result.dimension_counts) == {8: 36, 10: 36}
    assert dict(result.orbit_space_counts) == {
        "P^7(Q(omega))": 36,
        "P^9(Q(omega))": 36,
    }
    assert [block["pair_count"] for block in record["candidate_blocks"]] == [36, 36]


def test_forced_left_line_is_positive_on_the_full_kahler_cone() -> None:
    """Exact coefficient positivity excludes every polarization in the cone."""

    result = current_minimum_stability_no_go()
    expected = Polynomial(
        {
            (2, 0, 0): Rational(1, 3),
            (1, 1, 0): Rational(4),
            (1, 0, 1): Rational(2),
            (0, 2, 0): Rational(5, 3),
            (0, 1, 1): Rational(10),
        },
        variable_count=3,
    )

    assert result.first_orientation_line_c1 == (Rational(5), Rational(1), Rational(0))
    assert result.first_orientation_slope == expected
    assert all(coefficient > 0 for _, coefficient in expected.terms)
    assert result.as_record()["strictly_positive_on_kahler_cone"] is True
    assert result.as_record()["sampled_polarization_used"] is False


def test_no_go_uses_the_forced_constituent_line_for_every_parameter() -> None:
    """The Serre and outer inclusions make the positive line unavoidable."""

    record = current_minimum_stability_no_go().as_record()

    assert record["forced_subbundle_composition"] == "L_left -> V_left -> V_E"
    assert record["forced_line_descends_for_every_pair"] is True
    assert record["extension_parameter_dependence"] == "none"
    assert record["right_line_restriction_required"] is False
    assert record["every_pair_unstable"] is True


def test_current_minimum_artifact_remains_a_scoped_no_go() -> None:
    """The exact retirement advances rather than closes the carrier search."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == current_minimum_stability_no_go().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["current_minimum_and_companion_block_refuted"] is True
    assert stored["global_computable_carrier_no_go"] is False
    assert stored["arbitrary_pair_selected"] is False
    assert stored["arbitrary_extension_point_selected"] is False
