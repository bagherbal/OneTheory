"""Guard the actual coupled quotient's evidence and scalar-evaluation boundary.

Owns:
    Cross-artifact arrow identities, retained two-equation terms, and a
    fresh full-differential check on another pair of actual local cochains.

Depends on:
    The frozen published-input resolutions, exact coupled comparison,
    and the completed actual coefficient certificate.

Must not:
    Treat constituent matter as closed in the outer cone or assign
    the prior ordered scalar screens to the new natural product.

Phase 0:
    Research-only actual-input verification with scope-inflation guards.
"""

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.alternate_up_coupled_tensor_comparison import (
    OUTPUT,
    alternate_coupled_quotient,
)
from research.experiments.scientific_genesis.alternate_up_higgs_quotient_cone import (
    OUTPUT as OLD_CONE,
)
from research.experiments.scientific_genesis.mixed_schoen_coupled_tensor import (
    coupled_quotient_vector_wedge,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import _MixedContraction
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import mixed_schoen_unit
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _verified_payload,
)


@pytest.mark.parametrize("index", (0, 1))
def test_actual_coupled_presentation_matches_the_existing_complete_cone(index: int) -> None:
    _, record = _verified_payload(OUTPUT)
    _, old = _verified_payload(OLD_CONE)
    current = record["presentations"][index]
    reference = old["parameter_coefficients"][index]
    assert current["connecting_arrow_digest"] == reference["connecting_arrow_digest"]
    assert current["connecting_arrow_term_count"] == reference["connecting_arrow_term_count"]
    model = alternate_coupled_quotient(index)
    assert len(model.source.objects) == 9
    assert len(model.quotient.objects) == 38
    assert current["source_k2_arrow_term_count"] == sum(
        t.koszul_degree == 2 for t in model.source.extension_terms
    )
    assert current["source_k2_arrow_term_count"] > 0
    assert current["quotient_is_a_vector_bundle"] is False
    assert current["complete_connecting_arrow_equal_exact"] is True


def test_another_actual_local_pair_satisfies_complete_leibniz() -> None:
    """Use noncycles different from the saved syzygy/null-matter attack."""

    model = alternate_coupled_quotient(0)
    context = _MixedContraction(model.source, mixed_schoen_unit())
    out = _MixedContraction(model.quotient, mixed_schoen_unit())
    a = SparseOuterCechCochain(((OuterCechBasis(
        context.components[(2, 0, "k0")],
        (1, 0, 0), (-4, 0, 0), (1, 0), ((0,), (0, 1), (0,)),
    ), Eisenstein(1)),))
    b = SparseOuterCechCochain(((OuterCechBasis(
        context.components[(3, 0, "k0")],
        (1, 0, 0), (0, -4, 0), (1, 0), ((0,), (1,), (0, 1)),
    ), Eisenstein(1)),))
    product = coupled_quotient_vector_wedge(a, b, model, 1, 1)
    assert out.differential(product) == (
        coupled_quotient_vector_wedge(context.differential(a), b, model, 2, 1)
        + coupled_quotient_vector_wedge(a, context.differential(b), model, 1, 2).scale(-1)
    )


def test_actual_coupled_certificate_does_not_assign_a_scalar_or_matrix() -> None:
    _, record = _verified_payload(OUTPUT)
    assert record["derived_coupled_R_to_Q_tensor_identity"] is True
    for item in record["actual_leibniz_checks"]:
        assert item["full_signed_leibniz_identity_exact"] is True
        assert item["source_right_matter_image_term_count"] > 0
        assert item["constituent_null_matter_assumed_closed_in_R"] is False
        assert item["physical_scalar_evaluated"] is False
    for key in (
        "full_carrier_scalar_pairing_evaluated", "complete_holomorphic_up_matrix_available",
        "physical_yukawa_matrix_available", "extension_point_selected", "observational_inputs_used",
    ):
        assert record[key] is False
