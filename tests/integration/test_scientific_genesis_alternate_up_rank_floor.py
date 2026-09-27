"""Check the exact alternate up-sector rank floor and its boundary.

Owns:
    Regression of all four nonzero mixed-block minors against the pinned
    cover traces and the exterior-filtration zero pattern.

Depends on:
    The research-only rank-floor derivation, exact Eisenstein arithmetic,
    and content-addressed generated artifacts.

Must not:
    Supply unknown second/second couplings, assert rank three, or infer
    canonically normalized physical observables.

Phase 0:
    Research-only conditional holomorphic rank regression.
"""

from __future__ import annotations

import json

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_rank_floor import (
    OUTPUT,
    alternate_up_rank_floor,
)


def test_all_mixed_block_minors_force_rank_two() -> None:
    """Each selected E/F submatrix has nonzero exact determinant."""

    payload = alternate_up_rank_floor()
    saved = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = saved.pop("artifact_digest")
    assert digest == _canonical_digest(saved)
    assert payload == saved
    assert payload["zero_first_first_entry"] is True
    assert payload["holomorphic_rank_lower_bound"] == 2
    assert payload["rank_floor_valid_for_every_nonsplit_extension"] is True
    assert payload["rank_three_established"] is False
    assert payload["complete_holomorphic_up_matrix_available"] is False
    assert payload["physical_yukawa_matrix_available"] is False

    # The four coefficients are independently computed in the upstream
    # scalar-cup experiment.  Here no unknown F--F entry is assigned.
    row = (Eisenstein(3) / 2, Eisenstein(-9, -6) / 14)
    column = (-Eisenstein(3) * OMEGA / 2, -Eisenstein(3, 9) / 14)
    expected = tuple(tuple(-b * c for c in column) for b in row)
    assert payload["two_by_two_minors_rows_F_columns_F"] == [
        [str(value) for value in pair] for pair in expected
    ]
    assert all(not value.is_zero() for pair in expected for value in pair)
    for b in row:
        for c in column:
            assert Matrix(((0, b), (c, 0)), scalar_type=Eisenstein).rank() == 2
