"""Test the necessary chamber for the next surviving carrier block.

Owns:
    Exhaustive topology profiles, exact forced-slope relations, rational
    chamber witnesses, factor exchange, and the unresolved stability boundary.

Depends on:
    The rank-20 restriction artifact and exact descended slope machinery.

Must not:
    Promote forced inequalities to full stability, select an Ext point, or
    treat a rational witness as a physical polarization.

Phase 0:
    Next-survivor necessary-chamber regression tests only.
"""

import json

from onetheory.math.numbers import Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.next_survivor_forced_chamber import (
    OUTPUT,
    next_survivor_forced_chamber,
)


def test_forced_chamber_covers_both_factor_orientations() -> None:
    """All 72 candidate-4/24 families share two exchanged slope profiles."""

    result = next_survivor_forced_chamber()

    assert result.checked_pair_count == 72
    assert dict(result.dimension_counts) == {50: 36, 52: 36}
    assert result.factor_exchange_exact is True


def test_rank_two_slope_reduces_to_the_preimage_inequality() -> None:
    """The rank-two condition is exactly redundant in the forced chamber."""

    result = next_survivor_forced_chamber()

    assert result.left_constituent_slope == (
        result.right_line_preimage_slope.scale(3)
    )
    assert result.as_record()["slope_relation"] == (
        "mu(V_left)=3*mu(preimage(L_right))"
    )


def test_exact_rational_witness_makes_every_forced_slope_negative() -> None:
    """A rational point certifies a nonempty necessary Kähler chamber."""

    result = next_survivor_forced_chamber()

    assert result.witness == (Rational(5), Rational(1), Rational(7))
    assert result.witness_values == (
        Rational(-1),
        Rational(-54),
        Rational(-18),
    )
    assert all(value < 0 for value in result.witness_values)


def test_chamber_artifact_preserves_the_open_stability_gate() -> None:
    """The content-addressed result claims necessity but not full stability."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert stored == next_survivor_forced_chamber().as_record()
    assert digest == _canonical_digest(stored)
    assert stored["common_forced_subobject_chamber_nonempty"] is True
    assert stored["full_slope_stability_proved"] is False
    assert stored["additional_saturated_subsheaves_classified"] is False
    assert stored["arbitrary_extension_point_selected"] is False
