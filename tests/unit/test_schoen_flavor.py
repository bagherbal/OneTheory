"""Test the exact holomorphic tree-level flavor theorem.

Owns:
    Symbolic determinant zero, generic rank two, exact null vectors, common
    one-plus-two support, explicit coefficient admission, and CP obstruction.

Depends on:
    `onetheory.models.heterotic_schoen.flavor`, exact Rational values, and pytest.

Must not:
    Treat coefficients as measured masses, construct physical Yukawas, normalize
    matter metrics, or import observations into the carrier.

Phase 0:
    Holomorphic support tests only; canonical normalization and physical mixing
    remain unresolved.
"""

from __future__ import annotations

import pytest

from onetheory.core.errors import MissingPhysicalInput
from onetheory.math.linear import Matrix, Vector
from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.flavor import (
    COMMON_DGA_MISSING_CHAIN,
    F3_COMMON_CYCLIC_CERTIFICATES,
    F3_COMMON_CYCLIC_PROVENANCE,
    binary_gram_certificate,
    common_dga_input_status,
    compile_f3_common_cyclic_package,
    complete_forward_slice_obstruction,
    degree_three_obstruction,
    direct_order_five_exclusion,
    finite_frontier_status,
    star_triangular_typing_identifiability,
    tree_level_flavor,
    tree_yukawa_texture,
)


def test_tree_level_flavor_is_symbolically_rank_two_with_exact_nulls() -> None:
    result = tree_level_flavor()
    matrix = tree_yukawa_texture(2, 3, 5, 7)
    right, left = result.up.exact_null_vectors({"a": 2, "b": 3, "c": 5, "d": 7})

    assert result.up.determinant.is_zero()
    assert result.down.determinant.is_zero()
    assert result.up.generic_rank == 2
    assert result.up.family_block_sizes == (1, 2)
    assert matrix @ right == Vector((0, 0, 0))
    assert matrix.transpose() @ left == Vector((0, 0, 0))


def test_tree_level_flavor_remains_holomorphic_and_fail_closed() -> None:
    result = tree_level_flavor()

    assert not result.physical
    assert result.ckm_cp_obstructed
    with pytest.raises(MissingPhysicalInput):
        result.up.evaluate({"a": 1, "b": 2, "c": 3})
    with pytest.raises(TypeError):
        tree_yukawa_texture(0.5, 1, 2, 3)


def test_scoped_low_order_exclusions_and_frontier_counts_are_exact() -> None:
    forward = complete_forward_slice_obstruction()
    degree_three = degree_three_obstruction()
    order_five = direct_order_five_exclusion()
    status = finite_frontier_status()

    assert forward.certified
    assert degree_three.certified
    assert order_five.total_count == 42
    assert order_five.all_zero
    assert status["generic_residue_count"] == 24
    assert status["direction_refined_residue_count"] == 20
    assert status["first_simultaneous_test_count"] == 4
    assert status["star_triangular_typing_identifiable"] is False


def test_binary_gram_frontier_certificate_recomputes_exact_identities() -> None:
    active = Matrix(
        ((Eisenstein(0), Eisenstein(1)), (Eisenstein(1), Eisenstein(0))),
        scalar_type=Eisenstein,
    )
    transport = Matrix(
        ((Eisenstein(1), Eisenstein(0), Eisenstein(1)),
         (Eisenstein(0), Eisenstein(1), Eisenstein(1))),
        scalar_type=Eisenstein,
    )
    certificate = binary_gram_certificate(active, transport)

    assert certificate["all_exact_checks_pass"]
    assert star_triangular_typing_identifiability().typing_is_identifiable is False


def test_raw_common_cyclic_compiler_collapses_both_orientations() -> None:
    def sector(label: str) -> dict[str, object]:
        return {
            "basis": {
                "A": (f"{label}_a",),
                "H": (f"{label}_h",),
                "B": (f"{label}_b0", f"{label}_b1"),
            },
            "M0": ((0, 1), (1, 0)),
            "a": (1,),
            "H": (1,),
            "b_active": ((1, 0), (0, 1)),
            "effective_FE_B": ((1, 0), (0, 1)),
            "tau_AHB": (((1, 1),),),
            "tau_BHA": (((1,),), ((1,),)),
        }

    package = {
        "object": "F3CommonCyclicTracePackage",
        "field": "Q(omega)",
        "package_class": "synthetic_test",
        "certificates": {name: True for name in F3_COMMON_CYCLIC_CERTIFICATES},
        "provenance": {name: "0" * 64 for name in F3_COMMON_CYCLIC_PROVENANCE},
        "sectors": {"u": sector("u"), "d": sector("d")},
    }
    result = compile_f3_common_cyclic_package(package)

    assert result["all_orientation_pairs_equal"]
    assert result["oriented_contraction_count"] == 8
    assert result["independent_normalized_scalar_count"] == 4


def test_common_dga_status_preserves_the_first_missing_input() -> None:
    status = common_dga_input_status()

    assert status["physical_carrier_package_available"] is False
    assert status["first_missing_input"] == COMMON_DGA_MISSING_CHAIN[0]
    assert status["prerequisite_chain"] == COMMON_DGA_MISSING_CHAIN
