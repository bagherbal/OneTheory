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

from research.experiments.computable_carrier.dp9_hypersurface import (
    dP9_hypersurface_hom_comparison,
    tier_a_dp9_hypersurface_comparisons,
)
from research.experiments.computable_carrier.dp9_linebundles import dp9_line_bundle


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
