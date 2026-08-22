"""Test exact relative pushdowns of the published Serre constituents.

Owns:
    Projection support, local point algebras, connecting-map reductions,
    elementary transformations, and comparison with published P1 signatures.

Depends on:
    The research relative-pushdown derivation and source-bound comparison data.

Must not:
    Import expected pushdowns into the derivation or identify P1 classes with
    full Schoen Cech representatives.

Phase 0:
    Relative constituent quasi-isomorphism regression tests only.
"""

import json

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.visible import point_schemes
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pushdown import (
    tier_a_pushdown_constraints,
)
from research.experiments.scientific_genesis.relative_constituent_pushdowns import (
    OUTPUT,
    projected_point_scheme,
    relative_constituent_pushdowns,
    relative_tensor_dimensions,
    write_relative_constituent_pushdowns,
)


def test_point_schemes_project_to_three_distinct_base_points() -> None:
    """Both finite schemes have exact reduced support on the elliptic base."""

    i3, i6 = point_schemes()
    first = projected_point_scheme(i3, 1)
    second = projected_point_scheme(i6, 2)
    p0 = Polynomial.monomial((1, 0), scalar_type=Eisenstein)
    p1 = Polynomial.monomial((0, 1), scalar_type=Eisenstein)

    assert first.support_equation == p0**3 + (p1**3).scale(3 + 6 * OMEGA)
    assert second.support_equation == p0**3 + (p1**3).scale(
        Eisenstein(-8) / Eisenstein(9) + OMEGA * (Eisenstein(-16) / Eisenstein(9))
    )
    assert first.support_is_reduced
    assert second.support_is_reduced
    assert first.support_deck_invariant
    assert second.support_deck_invariant
    assert first.scheme_length == 3
    assert second.scheme_length == 6


def test_affine_local_algebras_recover_reduced_and_fat_points() -> None:
    """The local monomial quotients derive all point lengths and tangent support."""

    i3, i6 = point_schemes()
    first = projected_point_scheme(i3, 1)
    second = projected_point_scheme(i6, 2)

    assert tuple(item.length for item in first.local_algebras) == (1, 1, 1)
    assert tuple(item.length for item in second.local_algebras) == (2, 2, 2)
    assert all(item.is_local_complete_intersection for item in first.local_algebras)
    assert all(item.is_local_complete_intersection for item in second.local_algebras)
    assert all(item.projection_constant_to_first_order for item in second.local_algebras)
    assert tuple(item.standard_monomials for item in second.local_algebras) == (
        ((0, 0), (0, 1)),
        ((0, 0), (1, 0)),
        ((0, 0), (0, 1)),
    )


def test_relative_maps_contract_w1_and_elementary_transform_w2() -> None:
    """The two distinct relative mechanisms produce exact quasi-isomorphisms."""

    w1, w2 = relative_constituent_pushdowns()

    assert w1.quasi_isomorphism_exact
    assert w1.connecting_map is not None
    assert w1.connecting_map.is_isomorphism
    assert w1.selected_mixed_cocycle
    assert w1.local_extension_units == (True, True, True)
    assert w1.relative_duality_used
    assert w2.quasi_isomorphism_exact
    assert w2.connecting_map is None
    assert w2.connecting_zero_by_character
    assert w2.selected_mixed_cocycle
    assert w2.local_extension_units == (True, True, True)
    assert w2.elementary_transformation is not None
    assert w2.elementary_transformation.exact


def test_derived_signatures_match_source_only_after_construction() -> None:
    """Independent relative reductions reproduce both published signatures."""

    derived = relative_constituent_pushdowns()
    source = tier_a_pushdown_constraints()
    source_signatures = tuple(
        (
            tuple((term.degree, term.character) for term in constraint.direct_terms),
            tuple((term.degree, term.character) for term in constraint.higher_terms),
        )
        for constraint in source
    )

    assert tuple(item.signature() for item in derived) == source_signatures


def test_relative_twists_are_natural_and_recover_higgs_dimensions() -> None:
    """One sheaf-level reduction controls every twist and their derived tensor."""

    w1, w2 = relative_constituent_pushdowns()

    assert tuple(w1.hypercohomology_dimensions(twist) for twist in range(-2, 3)) == (
        (0, 2, 1),
        (0, 1, 0),
        (0, 1, 0),
        (1, 2, 0),
        (2, 3, 0),
    )

    assert relative_tensor_dimensions(w1, w2) == (0, 4, 4, 0)


def test_relative_pushdown_artifact_is_content_addressed() -> None:
    """The frozen artifact records the derived result and remaining lift gate."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    fresh = write_relative_constituent_pushdowns()

    assert digest == _canonical_digest(stored)
    assert fresh["artifact_digest"] == digest
    assert stored["derived_tensor_dimensions"] == [0, 4, 4, 0]
    assert stored["derived_signatures_match_source"] is True
    assert stored["selected_mixed_constituent_cocycles_used"] is True
    assert stored["retired_maximal_minor_cones_used"] is False
    assert stored["full_schoen_cech_representatives_constructed"] is False
