"""Test the selected mixed determinant's exact quotient-descent gate.

Owns:
    Alternating degree, frame character, and scalar top-character regressions.

Depends on:
    The research determinant audit and exact Schoen line action.

Must not:
    Confuse cover c1 with equivariant triviality or refute a distinct carrier.

Phase 0:
    Scoped obstruction tests for the current selected linearizations.
"""

import json

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_actions import (
    diagonal_line_full_action,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_contraction import (
    strict_line_inclusion,
)
from research.experiments.scientific_genesis.mixed_schoen_determinant_descent import (
    OUTPUT,
    determinant_descent_audit,
)
from research.experiments.scientific_genesis.mixed_schoen_yukawa_trace import (
    scalar_residue,
)


def test_selected_mixed_determinant_has_nontrivial_quotient_character() -> None:
    audit = determinant_descent_audit()

    assert audit["constituent_cover_line_degrees"] == [[-2, 2, 0], [2, -2, 0]]
    assert audit["total_cover_line_degree"] == [0, 0, 0]
    assert audit["constituent_determinant_characters"] == [[1, 0], [1, 1]]
    assert audit["total_determinant_character"] == [2, 1]
    assert audit["equivariantly_trivial_determinant_certified"] is False
    assert audit["quotient_su4_certified_by_this_gate"] is False
    assert audit["published_carrier_refuted"] is False


def test_scalar_top_class_detects_the_same_frame_character() -> None:
    top, _depth = strict_line_inclusion(
        (0, 0, 0, 0), 3, ((0, Eisenstein(1)),)
    )
    actions = {action.name: action for action in schoen_sparse_deck_actions()}

    assert scalar_residue(top)[0] == Eisenstein(1)
    for frame, expected in (((0, 0), ("1", "1")), ((2, 1), ("-1-omega", "omega"))):
        residues = tuple(
            str(scalar_residue(diagonal_line_full_action(top, actions[name], frame))[0])
            for name in ("P", "T")
        )
        assert residues == expected


def test_determinant_obstruction_artifact_is_current() -> None:
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored == determinant_descent_audit()
