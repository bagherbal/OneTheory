"""Test the exact zero-fiber-twist dP9 hypersurface comparison.

Owns:
    Regression checks for the bidegree-(3,1) Koszul restriction and all six
    projective ray-pair Hom presentations.

Depends on:
    The research dP9 hypersurface comparison.

Must not:
    Treat the zero-fiber-twist result as arbitrary dP9 sheafification,
    quotient descent, or a physical carrier certificate.

Phase 0:
    The declared hypersurface comparison is exact; nonzero fiber twists and
    global quotient work remain unresolved.
"""

from __future__ import annotations

import pytest

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from research.experiments.computable_carrier.dp9_actions import dp9_deck_action_audit
from research.experiments.computable_carrier.dp9_homology import (
    dp9_derived_hom,
    tier_a_dp9_derived_homs,
)
from research.experiments.computable_carrier.dp9_hypersurface import (
    dP9_hypersurface_hom_comparison,
    tier_a_dp9_hypersurface_comparisons,
)
from research.experiments.computable_carrier.dp9_linebundles import (
    dp9_line_bundle,
)
from research.experiments.computable_carrier.projective_hom_search import (
    tier_a_projective_hom_pair_audits,
)


def test_dp9_koszul_correction_vanishes_for_zero_fiber_twist() -> None:
    """The O_P1(-1) correction vanishes for every Hom term."""

    comparisons = tier_a_dp9_hypersurface_comparisons()

    assert len(comparisons) == 6
    assert all(item.hypersurface_bidegree == (3, 1) for item in comparisons)
    assert all(item.koszul_source_fiber_degree == -1 for item in comparisons)
    assert all(item.koszul_correction_vanishes for item in comparisons)
    assert all(item.restriction_is_exact for item in comparisons)
    assert all(item.dP9_matches_projective for item in comparisons)
    assert all(item.line_bundle_cones_squared_zero for item in comparisons)
    assert all(len(item.line_bundles) == 48 for item in comparisons)


def test_dp9_comparison_rejects_unproved_fiber_twists() -> None:
    """The comparison fails closed instead of assuming another fiber twist."""

    comparison = tier_a_dp9_hypersurface_comparisons()[0]

    with pytest.raises(ValueError, match="fiber degree zero only"):
        dP9_hypersurface_hom_comparison(
            comparison.parent,
            comparison.projective,
            fiber_degree=1,
        )


def test_dp9_line_bundle_cone_supports_nonzero_fiber_twists() -> None:
    """The reusable line-bundle engine handles a nonzero twist independently."""

    line_bundle = dp9_line_bundle(-3, 1)

    assert line_bundle.squared_zero is True
    assert line_bundle.cohomology_dimensions == ((0, 0), (1, 8), (2, 0), (3, 0))


def test_dp9_line_bundle_multiplication_is_a_chain_map() -> None:
    """Base-polynomial multiplication preserves the exact cone differential."""

    source = dp9_line_bundle(0, 0)
    target = dp9_line_bundle(1, 0)
    coordinate = Polynomial.monomial((1, 0, 0), scalar_type=Eisenstein)
    multiplication = source.multiplication(target, coordinate)

    assert multiplication.source == source.complex
    assert multiplication.target == target.complex
    assert multiplication.component(0).domain == source.complex.spaces.space(0)
    assert multiplication.component(0).codomain == target.complex.spaces.space(0)


def test_dp9_totalization_matches_projective_h1_for_all_ray_pairs() -> None:
    """The six exact zero-fiber totalizations reproduce projective H1=5."""

    audits = tier_a_projective_hom_pair_audits()
    totals = tier_a_dp9_derived_homs(audits)

    assert len(totals) == 6
    assert all(item.squared_zero for item in totals)
    assert all(item.all_line_bundles_squared_zero for item in totals)
    assert all(item.total_h1_dimension == 5 for item in totals)

    actions = tuple(dp9_deck_action_audit(item) for item in totals)

    assert all(item.actions_commute for item in actions)
    assert all(item.actions_order_three for item in actions)
    assert all(item.invariant_dimension == 0 for item in actions)


def test_dp9_totalization_accepts_a_single_parent_pair() -> None:
    """One parent pair exposes the exact signed bicomplex total directly."""

    comparison = tier_a_dp9_hypersurface_comparisons()[0]
    total = dp9_derived_hom(comparison.parent)

    assert total.bicomplex.totalize() == total.total
    assert total.total_h1_dimension == comparison.projective.ext_one_dimension
