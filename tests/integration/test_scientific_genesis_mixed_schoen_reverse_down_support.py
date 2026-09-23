"""Guard the scoped exterior support of the reverse down matrix."""

from __future__ import annotations

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_down_support import (
    OUTPUT,
    reverse_down_support,
    surviving_degrees,
)


def test_reverse_exterior_support() -> None:
    """Only the central linear slot survives certified tree zeroes."""

    expected = {
        (0, 0): (1,),
        (0, 1): (0,),
        (0, 2): (0,),
        (1, 0): (0,),
        (2, 0): (0,),
        (1, 1): (),
        (1, 2): (),
        (2, 1): (),
        (2, 2): (),
    }
    assert {
        (row, column): surviving_degrees(row, column)
        for row in range(3)
        for column in range(3)
    } == expected
    for slot in ((-1, 0), (0, 3)):
        with pytest.raises(ValueError, match="family index"):
            surviving_degrees(*slot)


def test_reverse_support_artifact() -> None:
    """Regenerate the content-addressed scope without assigning a coupling."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    assert digest == _canonical_digest(stored)
    assert stored == reverse_down_support()
    assert stored["exterior_forced_zero_slots"] == [
        [1, 1], [1, 2], [2, 1], [2, 2]
    ]
    assert stored["tree_boundary_zero_slots"] == [
        [0, 1], [0, 2], [1, 0], [2, 0]
    ]
    assert stored["only_unresolved_slot"] == [0, 0]
    assert stored["matrix_rank_upper_bound"] == 1
    assert stored["central_coefficient_computed"] is False
    assert stored["nontrivial_holomorphic_matrix_available"] is False
