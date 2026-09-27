"""Regress actual localized syzygy contraction of the alternate Hom class.

Owns:
    Saved middle numerators, right mixed-arrow identities, and explicit
    minor-open/non-gluing boundaries.

Depends on:
    The persisted strict Hom cochain, selected alternate resolution, and
    exact Laurent arithmetic.

Must not:
    Identify the localized sections with a global tensor or Higgs cocycle.

Phase 0:
    Integration tests for the next Hom transport input.
"""

import json

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.sheaves import LaurentPolynomial
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import tier_a_pencil_model
from research.experiments.scientific_genesis.alternate_up_higgs_local_syzygy_section import (
    OUTPUT,
    _multiply_vector,
    _right_mixed_matrix,
    alternate_up_higgs_local_syzygy_section,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    _constituent,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)


def _polynomial(raw: list[dict[str, object]]) -> LaurentPolynomial:
    """Read one exact five-coordinate Laurent numerator from the artifact."""

    return LaurentPolynomial(
        (
            (tuple(item["exponents"]), _parse_eisenstein_text(item["coefficient"]))
            for item in raw
        ),
        variable_count=5,
        scalar_type=Eisenstein,
    )


def test_saved_sections_contract_actual_hom_blocks() -> None:
    """All 18 nonzero blocks obey the arrow-derived right differential."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    right = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    charts = {chart.name: chart for chart in tier_a_pencil_model().blowup_atlas.charts}
    assert len(payload["charts"]) == 6
    assert sum(record["block_count"] for record in payload["charts"]) == 18
    for record in payload["charts"]:
        chart = charts[record["chart"]]
        denominator = _polynomial(record["minor_denominator"])
        assert record["minor_rows"] == [0, 1]
        assert not denominator.is_zero()
        assert record["block_count"] == len(record["blocks"]) == 3
        assert {tuple(block["x_cell"]) for block in record["blocks"]} == {
            (0,), (1,), (2,)
        }
        for block in record["blocks"]:
            source = tuple(_polynomial(raw) for raw in block["syzygy_source"])
            middle = tuple(
                _polynomial(raw) for raw in block["middle_numerator_object_order"]
            )
            matrix = _right_mixed_matrix(right, chart, tuple(block["x_cell"]))
            assert any(not item.is_zero() for item in source)
            assert any(not item.is_zero() for item in middle)
            assert _multiply_vector(matrix, middle) == tuple(
                denominator * item for item in source
            )
            perturbed = (source[0] + LaurentPolynomial.one(5, scalar_type=Eisenstein), *source[1:])
            assert _multiply_vector(matrix, middle) != tuple(
                denominator * item for item in perturbed
            )


def test_section_artifact_does_not_claim_gluing_or_higgs() -> None:
    """Actual local formulas remain separate from a global physical class."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    payload.pop("artifact_digest")
    assert payload == alternate_up_higgs_local_syzygy_section()
    assert payload["minor_denominators_inverted_only_on_principal_opens"] is True
    assert payload["fiber_overlap_gluing_constructed"] is False
    assert payload["hom_to_tensor_chain_map_constructed"] is False
    assert payload["exterior_cone_higgs_cocycle_constructed"] is False
