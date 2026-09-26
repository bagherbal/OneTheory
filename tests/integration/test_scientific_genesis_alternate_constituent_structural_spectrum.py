"""Guard the exact alternate observable structural-spectrum implication.

Owns:
    Recomputed determinant repair, equivariant Higgs characters, Wilson
    multiplicities, matter counts, and all-parameter research status.

Depends on:
    The alternate spectrum experiment and its content-addressed artifact.

Must not:
    Treat the structural spectrum as explicit cocycles, Yukawas, or a
    foundational prediction independent of selected Wilson data.

Phase 0:
    Research-only regression for the first viable observable component.
"""

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_structural_spectrum import (
    OUTPUT,
    _fourier_characters,
    alternate_constituent_structural_spectrum,
)


def test_alternate_structural_spectrum_closes_without_chain_claims() -> None:
    """The live implication must reproduce the exact saved certificate."""

    saved = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = saved.pop("artifact_digest")
    assert digest == _canonical_digest(saved)
    assert saved == alternate_constituent_structural_spectrum()
    assert saved["parameter_locus"] == "P^1(Q(omega)) x K^s"
    assert saved["every_nonzero_extension_parameter"] is True
    assert saved["arbitrary_extension_point_selected"] is False
    assert saved["determinant_endpoints_acyclic"] is True
    assert saved["higgs_h1_equivariantly_identified_with_constituent_tensor"] is True
    assert saved["hom_characters_independently_recovered_by_fourier_traces"] is True
    assert saved["hom_fourier_characters"] == [[0, 0], [1, 2], [2, 0], [2, 2]]
    assert saved["cover_higgs_h0_to_h3"] == [0, 4, 4, 0]
    assert saved["higgs_forward_characters"] == [[0, 1], [0, 2], [1, 2], [2, 1]]
    assert saved["fixed_wilson_higgs_multiplicities"] == {
        "up_higgs_doublet": 1,
        "down_higgs_doublet": 1,
        "color_triplet": 0,
        "color_antitriplet": 0,
    }
    assert saved["matter_cover_h0_to_h3"] == [0, 27, 0, 0]
    assert saved["matter_deck_regular_multiplicity"] == 3
    assert saved["observable_wilson_projection"] == {
        "families": 3,
        "right_handed_neutrinos": 3,
        "anti_families": 0,
        "higgs_pairs": 1,
        "massless_color_triplets": 0,
        "charged_exotic_blocks_from_16_and_10": 0,
    }
    assert saved["observable_charged_structural_spectrum_passes"] is True
    assert saved["explicit_cone_matter_cocycles_computed"] is False
    assert saved["explicit_cone_higgs_cocycles_computed"] is False
    assert saved["holomorphic_yukawa_matrix_computed"] is False


def test_fourier_check_rejects_a_corrupted_deck_action() -> None:
    """The second character path must fail if the action breaks group laws."""

    corrupted = {
        "P": [
            ["2", "0", "0", "0"],
            ["0", "1", "0", "0"],
            ["0", "0", "1", "0"],
            ["0", "0", "0", "1"],
        ],
        "T": [
            ["1", "0", "0", "0"],
            ["0", "1", "0", "0"],
            ["0", "0", "1", "0"],
            ["0", "0", "0", "1"],
        ],
    }
    with pytest.raises(ValueError, match="deck group laws"):
        _fourier_characters(corrupted)
