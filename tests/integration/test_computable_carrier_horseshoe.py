"""Test exact Tier A polynomial horseshoe presentations.

Owns:
    Rank-four presentation maps, exact short-term sequence identities,
    non-boundary representatives, and dP9 chart Fitting checks.

Depends on:
    Projective Tier A Hom audits, polynomial free-module maps, and the explicit
    six-chart dP9 atlas.

Must not:
    Call raw projective Hom classes equivariant, identify a horseshoe with a
    descended Schoen bundle, or infer stability, spectrum, or physical Chern
    data from the base presentation.

Phase 0:
    The raw rank-four horseshoe frontier is exact; invariant descent and all
    downstream physical gates remain unresolved.
"""

from functools import cache

from research.experiments.computable_carrier.horseshoe import (
    tier_a_horseshoe_presentations,
)
from research.experiments.computable_carrier.projective_hom_search import (
    tier_a_projective_hom_pair_audits,
)


@cache
def _horseshoes():
    """Build the complete declared Tier A horseshoe frontier once."""

    return tier_a_horseshoe_presentations(tier_a_projective_hom_pair_audits())


def test_tier_a_horseshoes_are_explicit_and_exact() -> None:
    """Every raw projective class yields a rank-four presentation gate."""

    horseshoes = _horseshoes()

    assert len(horseshoes) == 30
    assert {item.audit.left.scheme for item in horseshoes} == {"I3"}
    assert {item.audit.right.scheme for item in horseshoes} == {"I6"}
    assert all(item.rank == 4 for item in horseshoes)
    assert all(item.presentation_gate for item in horseshoes)
    assert all(item.complex.squared_zero for item in horseshoes)
    assert all(item.homogeneous for item in horseshoes)
    assert all(item.representative_is_nonboundary for item in horseshoes)


def test_tier_a_horseshoes_pass_local_freeness_without_descent() -> None:
    """Chart Fitting covers pass while the invariant outer space stays empty."""

    horseshoes = _horseshoes()

    assert all(item.short_exact_free_terms for item in horseshoes)
    assert all(item.local_freeness_on_atlas for item in horseshoes)
    assert all(len(item.fitting_certificates) == 6 for item in horseshoes)
    assert all(item.audit.invariant_ext_one_dimension == 0 for item in horseshoes)
    assert all(item.determinant_degree == -6 for item in horseshoes)
    assert all(not item.as_record()["equivariant"] for item in horseshoes)
