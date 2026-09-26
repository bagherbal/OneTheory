"""Regress local inversion of the frozen alternate quotient duality map.

Owns:
    Principal-open inverse identities, orientation failure, and claim scope.

Depends on:
    Exact alternate Pluecker pairings and the local-inverse certificate.

Must not:
    Infer a global Hom-to-tensor cochain or physical Higgs state.

Phase 0:
    Integration tests for the next exact chain-map ingredient.
"""

import json

from onetheory.math.numbers import OMEGA
from onetheory.math.sheaves import LaurentMatrix
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import tier_a_pencil_model
from research.experiments.scientific_genesis.alternate_constituent_duality_local_inverse import (
    OUTPUT,
    alternate_constituent_duality_local_inverse,
    inverse_numerator,
    principal_open_inverse_identity,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_schoen_determinant_pairing import (
    _matrix_scale,
    plucker_pairing,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)
from research.experiments.scientific_genesis.published_constituent_overlap_transitions import (
    _relation_columns,
)


def test_all_minor_open_inverses_close_exactly() -> None:
    """Each alternate chart has ten exact local inverse formulas."""

    result = alternate_constituent_duality_local_inverse()
    assert result["principal_open_count"] == 60
    assert len(result["principal_open_row_pairs"]) == 6
    assert all(len(pairs) == 10 for pairs in result["principal_open_row_pairs"].values())
    assert result["inverse_identity_exact"] is True
    assert result["two_term_chain_map_exact"] is True
    assert result["all_principal_opens_nonempty_at_witness"] is True
    assert result["dual_syzygy_contraction_count"] == 60
    assert result["dual_syzygy_contraction_exact"] is True
    assert result["combined_local_hom_to_quotient_identity_exact"] is True


def test_a_wrong_inverse_orientation_fails() -> None:
    """The sign in the inverse numerator is fixed by the Pluecker form."""

    alternate = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    chart = tier_a_pencil_model().blowup_atlas.charts[0]
    pairing = plucker_pairing(_relation_columns(alternate, chart))
    assert principal_open_inverse_identity(pairing, 0, 1)
    numerator = inverse_numerator(0, 1)
    wrong = LaurentMatrix(tuple(
        tuple(-entry for entry in row) for row in numerator.rows
    ))
    assert pairing.compose(wrong).compose(pairing) != _matrix_scale(
        pairing, pairing.rows[0][1]
    )


def test_local_inverse_artifact_stops_before_higgs_transport() -> None:
    """The exact local roof does not silently become a global cocycle."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload == alternate_constituent_duality_local_inverse()
    assert payload["hom_to_tensor_cech_koszul_map_constructed"] is False
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
    assert payload["yukawa_matrix_computed"] is False
