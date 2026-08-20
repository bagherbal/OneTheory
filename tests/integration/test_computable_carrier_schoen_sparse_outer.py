"""Test sparse exact cover maps, deck invariants, and explicit cocycles.

Owns:
    Regression checks for sparse exact rank, sparse Koszul square-zero, and a
    representative full Schoen cover totalization with invariant cocycles.

Depends on:
    The research-only sparse cover calculation and declared monomial rays.

Must not:
    Treat one cover-level vanishing as a quotient-invariant no-go or select a
    rank-four physical extension.

Phase 0:
    Invariant cover cocycles are exact; no rank-four extension is constructed.
"""

import json
from hashlib import sha256

from onetheory.math.homological import VectorSpace
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_sparse_outer import (
    SparseMap,
    sparse_line_bundle,
    sparse_outer_hom,
)
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    sparse_outer_deck_audit,
    sparse_outer_invariant_audit,
    sparse_outer_invariant_cocycles,
)
from research.experiments.computable_carrier.tier_b_monomial_topology import (
    tier_b_monomial_topology_screen,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    _clear_worker_caches,
    declared_schoen_outer_candidate_data,
)
from research.experiments.computable_carrier.tier_b_serre_extensions import (
    tier_b_serre_eigenrays,
)


def test_sparse_rank_uses_exact_eisenstein_column_elimination() -> None:
    """Sparse rank stays exact under deterministic sparsest-first ordering."""

    domain = VectorSpace("domain", ("d0", "d1", "d2"), Eisenstein)
    codomain = VectorSpace("codomain", ("c0", "c1"), Eisenstein)
    matrix = SparseMap(
        domain,
        codomain,
        (((0, Eisenstein(1)), (1, Eisenstein(1))), ((1, Eisenstein(1)), (2, Eisenstein(1)))),
    )

    assert matrix.rank() == 2
    kernel = matrix.kernel_inclusion()
    assert kernel.domain.dimension == 1
    assert matrix.compose(kernel).is_zero()


def test_sparse_line_bundle_reproduces_small_koszul_shapes() -> None:
    """Sparse line complexes preserve the exact small cover dimensions."""

    trivial = sparse_line_bundle(0, 0, 0)
    fiber = sparse_line_bundle(0, 0, -1)

    assert trivial.squared_zero
    assert fiber.squared_zero
    assert [trivial.space(degree).dimension for degree in range(4)] == [1, 0, 0, 1]
    assert [fiber.space(degree).dimension for degree in range(4)] == [0, 0, 2, 2]
    assert all(
        len(label) < 80
        for line in (trivial, fiber)
        for degree in range(4)
        for label in line.space(degree).basis
    )


def test_sparse_line_bundle_retains_boundary_koszul_degrees() -> None:
    """Boundary maps preserve the complete-intersection Euler characteristic."""

    line = sparse_line_bundle(-3, -4, 2)
    dimensions = []
    for degree in range(4):
        incoming = line.differential(degree - 1).rank()
        outgoing = line.differential(degree).rank()
        dimensions.append(line.space(degree).dimension - incoming - outgoing)

    assert line.squared_zero
    assert dimensions == [0, 0, 72, 3]
    assert sum((-1) ** degree * value for degree, value in enumerate(dimensions)) == 69
    assert all(
        line.space(degree).dimension
        - line.differential(degree - 1).rank()
        - line.differential(degree).rank()
        == 0
        for degree in (-2, -1, 4, 5)
    )


def test_representative_schoen_cover_outer_ext_is_exact_and_zero() -> None:
    """One surviving topology has a certified vanishing cover Ext-one."""

    _clear_worker_caches()
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

    assert outer.left.polynomial_factor == "x"
    assert outer.right.polynomial_factor == "x"
    assert outer.squared_zero
    assert outer.cover_ext_one_dimension == 0
    action = sparse_outer_deck_audit(outer)
    assert action.exact
    _clear_worker_caches()


def test_nonzero_cover_ext_has_explicit_invariant_cocycles() -> None:
    """The smallest nonzero cover case has four exact invariant classes."""

    _clear_worker_caches()
    candidate_index, candidate, left_rays, right_rays = (
        declared_schoen_outer_candidate_data()[2]
    )
    outer = sparse_outer_hom(
        left_rays[0],
        right_rays[0],
        candidate.left_factor,
        candidate.left_twist,
        candidate.right_factor,
        candidate.right_twist,
    )
    invariant = sparse_outer_invariant_audit(outer)
    cocycles = sparse_outer_invariant_cocycles(invariant)
    record = cocycles.as_record()

    assert candidate_index == 3
    assert outer.cover_ext_one_dimension == 36
    invariant_dimensions = {
        degree: basis.invariant.dimension for degree, basis in invariant.bases
    }
    assert [invariant_dimensions[degree] for degree in range(-1, 5)] == [
        0,
        0,
        60,
        146,
        90,
        8,
    ]
    assert all(invariant_dimensions[degree] == 0 for degree in (-3, -2, 5, 6))
    assert invariant.invariant_ext_one_dimension == 4
    assert cocycles.representatives.domain.dimension == 4
    assert [len(item["terms"]) for item in record["representatives"]] == [
        12,
        12,
        12,
        12,
    ]
    assert cocycles.exact
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
    assert sha256(canonical.encode("utf-8")).hexdigest() == (
        "11cb539694bb29da8415203c4381d7b78bbc576ed7a99aaf173f1b71bef94a46"
    )
    _clear_worker_caches()
