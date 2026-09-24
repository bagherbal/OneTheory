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
from pathlib import Path

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis import (
    mixed_schoen_determinant_descent as descent_module,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_actions import (
    diagonal_line_full_action,
)
from research.experiments.scientific_genesis.diagonal_schoen_line_contraction import (
    strict_line_inclusion,
)
from research.experiments.scientific_genesis.mixed_schoen_determinant_descent import (
    OUTPUT,
    _same_cover_bundle_gate,
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
    twist = audit["uniform_twist_screen"]
    assert twist["common_twists_enumerated"] == 9
    assert twist["rank_four_uniform_twist"] == [1, 2]
    assert twist["exterior_square_character_shift"] == [2, 1]
    assert twist["shifted_higgs_characters"] == [
        [0, 0], [1, 2], [2, 0], [2, 2],
    ]
    assert twist["fixed_wilson_multiplicities"] == {
        "up_higgs_doublet": 0,
        "down_higgs_doublet": 0,
        "color_triplet": 0,
        "color_antitriplet": 1,
    }
    assert twist["one_higgs_zero_triplet_spectrum_preserved"] is False
    same_bundle = audit["same_cover_bundle_relinearization"]
    assert same_bundle["cross_h0_hom_dimensions"] == {
        "V1->V2": 0,
        "V2->V1": 0,
    }
    assert same_bundle["constituent_h0_endomorphism_dimensions"] == {
        "V1": 1,
        "V2": 1,
    }
    assert same_bundle["all_nonsplit_extensions_simple"] is True
    assert same_bundle["same_underlying_bundle_linearizations_are_character_twists"]
    assert same_bundle["same_underlying_bundle_su4_one_higgs_repair_available"] is False
    assert same_bundle["distinct_underlying_bundles_excluded"] is False


def test_same_bundle_gate_requires_failed_unique_twist() -> None:
    with pytest.raises(ValueError, match="unique determinant twist"):
        _same_cover_bundle_gate({
            "rank_four_uniform_twist": [1, 2],
            "one_higgs_zero_triplet_spectrum_preserved": True,
        })


def test_same_bundle_gate_rejects_nonzero_cross_hom(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    altered = json.loads(descent_module.OUTER_TRANSFER.read_text(encoding="utf-8"))
    altered["orientations"][0]["cohomology_dimensions"][3][1] = 1
    altered.pop("artifact_digest")
    altered["artifact_digest"] = _canonical_digest(altered)
    path = tmp_path / "changed-outer-transfer.json"
    path.write_text(json.dumps(altered), encoding="utf-8")
    monkeypatch.setattr(descent_module, "OUTER_TRANSFER", path)

    with pytest.raises(ValueError, match="cross-Hom H0 vanishing"):
        descent_module._same_cover_bundle_gate({
            "rank_four_uniform_twist": [1, 2],
            "one_higgs_zero_triplet_spectrum_preserved": False,
        })


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
