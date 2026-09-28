"""Check actual short line homotopies before a natural product comparison.

Owns:
    Full null-line differential identities, complete indeterminacy groups,
    and content-pinned serialization of the real short primitives.

Depends on:
    Actual alternate carrier inputs and existing exact mixed Hom machinery.

Must not:
    Infer a physical Yukawa from a line boundary or a vanishing Hom group.

Phase 0:
    Research regressions for structural null-product inputs only.
"""

from __future__ import annotations

from research.experiments.scientific_genesis.alternate_up_first_order_scalar import (
    alternate_null_matter,
)
from research.experiments.scientific_genesis.alternate_up_higgs_hom_representative import (
    load_alternate_up_higgs_hom_full_cochain,
)
from research.experiments.scientific_genesis.alternate_up_null_channel import (
    OUTPUT as NULL_CHANNELS,
)
from research.experiments.scientific_genesis.alternate_up_null_line_homotopies import (
    OUTPUT,
    inverse_quotient_line,
    null_line_cohomology_dimensions,
    null_line_homotopies,
    quotient_map_indeterminacy,
    quotient_product_indeterminacy,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import (
    mixed_outer_cup_coefficient,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _cochain_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _representative,
    _verified_payload,
)


def test_actual_null_primitives_are_full_line_homotopies() -> None:
    """The checked E-valued homotopy has no omitted non-line component."""

    channels = null_line_homotopies()
    _, pinned = _verified_payload(NULL_CHANNELS)
    assert [channel.as_record() for channel in channels] == pinned["null_channels"]
    context = _MixedContraction(inverse_quotient_line(), mixed_schoen_unit())
    for channel in channels:
        assert len(channel.primitive.terms) == 90
        assert len(channel.null_evaluation.terms) == 144
        assert {basis.component.left_index for basis, _ in channel.primitive.terms} == {0}
        assert context.differential(channel.primitive) == channel.null_evaluation
        assert context.differential(channel.null_evaluation).is_zero()


def test_line_primitive_and_endpoint_map_indeterminacy_groups() -> None:
    """These are complete cover groups, not selected-character vanishings."""

    assert inverse_quotient_line().twist == (1, -1, -1)
    assert null_line_cohomology_dimensions() == (0, 0, 9, 0)
    ambient, hom_dimension = quotient_map_indeterminacy()
    assert dict(ambient) == {
        -3: 0, -2: 0, -1: 0, 0: 0, 1: 108, 2: 72, 3: 0, 4: 0, 5: 0,
    }
    assert hom_dimension == 0
    product_ambient, product_dimensions = quotient_product_indeterminacy()
    assert dict(product_ambient) == {
        -3: 0, -2: 0, -1: 0, 0: 90, 1: 152, 2: 70, 3: 8, 4: 0, 5: 0,
    }
    assert product_dimensions == (0, 5, 5, 0)


def test_actual_short_witness_archive_remains_nonphysical() -> None:
    """Decode real primitive terms; ambiguity facts do not assign a product."""

    _, record = _verified_payload(OUTPUT)
    assert record["schema"] == "alternate-up-null-line-homotopies-v1"
    for witness, actual in zip(record["null_line_witnesses"], null_line_homotopies(), strict=True):
        restored = _representative({
            "terms": witness["full_primitive_terms"], "term_count": witness["primitive_term_count"],
        })
        assert restored == actual.primitive
        assert _cochain_digest((restored,)) == witness["primitive_digest"]
        assert witness["primitive_has_only_line_support"] is True
        assert witness["full_line_primitive_identity_exact"] is True
        assert witness["ordered_higgs_null_matter_evaluation_exact"] is True
    assert record["line_primitive_unique_modulo_boundaries"] is True
    assert record["identity_endpoint_extension_map_unique_if_it_exists"] is True
    assert record["K_h0_to_h3"] == [0, 5, 5, 0]
    assert record["remaining_matter_product_H2K_dimension"] == 5
    for field in (
        "natural_matter_product_comparison_certified",
        "complete_comparison_indeterminacy_eliminated",
        "physical_null_coefficients_computed", "complete_holomorphic_up_matrix_available",
        "physical_yukawa_matrix_available", "extension_point_selected", "observational_inputs_used",
    ):
        assert record[field] is False


def test_inverse_coefficients_match_actual_null_yoneda_products() -> None:
    """Use full carrier-derived products, not only mathematical sign fixtures."""

    h = load_alternate_up_higgs_hom_full_cochain()
    for channel, matter in zip(null_line_homotopies(), alternate_null_matter(), strict=True):
        for index in (0, len(channel.null_evaluation.terms) // 2, -1):
            basis, value = channel.null_evaluation.terms[index]
            assert mixed_outer_cup_coefficient(h, matter, basis) == value
