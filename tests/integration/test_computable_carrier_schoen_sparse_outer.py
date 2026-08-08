"""Test sparse exact cover maps and one outer Hom certificate.

Owns:
    Regression checks for sparse exact rank, sparse Koszul square-zero, and a
    representative full Schoen cover outer totalization.

Depends on:
    The research-only sparse cover calculation and declared monomial rays.

Must not:
    Treat one cover-level vanishing as a quotient-invariant no-go or select a
    rank-four physical extension.

Phase 0:
    The sparse calculation is a cover-level gate; quotient action remains open.
"""

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    sparse_line_bundle,
    sparse_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    sparse_outer_deck_audit,
)
from research.experiments.computable_carrier.tier_b_monomial_topology import (
    tier_b_monomial_topology_screen,
)
from research.experiments.computable_carrier.tier_b_serre_extensions import (
    tier_b_serre_eigenrays,
)


def test_sparse_rank_uses_exact_eisenstein_column_elimination() -> None:
    """Sparse rank agrees with the exact rank of a small dependent matrix."""

    domain = VectorSpace("domain", ("d0", "d1", "d2"), Eisenstein)
    codomain = VectorSpace("codomain", ("c0", "c1"), Eisenstein)
    matrix = SparseMap(
        domain,
        codomain,
        (((0, Eisenstein(1)), (1, Eisenstein(1))), ((1, Eisenstein(1)), (2, Eisenstein(1)))),
    )

    assert matrix.rank() == 2


def test_sparse_line_bundle_reproduces_small_koszul_shapes() -> None:
    """Sparse line complexes preserve the exact small cover dimensions."""

    trivial = sparse_line_bundle(0, 0, 0)
    fiber = sparse_line_bundle(0, 0, -1)

    assert trivial.squared_zero
    assert fiber.squared_zero
    assert [trivial.space(degree).dimension for degree in range(4)] == [1, 0, 0, 1]
    assert [fiber.space(degree).dimension for degree in range(4)] == [0, 0, 2, 2]


def test_representative_schoen_cover_outer_ext_is_exact_and_zero() -> None:
    """One surviving topology has a certified vanishing cover Ext-one."""

    topology = tier_b_monomial_topology_screen().surviving_topology_candidates[0]
    left_rays = tier_b_serre_eigenrays(target_line_shift=-6)
    right_rays = tier_b_serre_eigenrays(target_line_shift=0)
    left = next(
        ray for ray in left_rays if ray.cokernel.scheme.name.endswith("-1")
    )
    right = next(
        ray for ray in right_rays if ray.cokernel.scheme.name.endswith("-1")
    )

    outer = sparse_outer_hom(
        left,
        right,
        topology.left_factor,
        topology.left_twist,
        topology.right_factor,
        topology.right_twist,
    )

    assert outer.squared_zero
    assert outer.cover_ext_one_dimension == 0
    action = sparse_outer_deck_audit(outer)
    assert action.exact
