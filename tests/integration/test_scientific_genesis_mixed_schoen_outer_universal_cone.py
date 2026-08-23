"""Test the lawful universal mixed outer mapping cone.

Owns:
    Basis specialization, split ideal, block-square, topology, descent,
    local-freeness theorem, and generated-artifact integrity.

Depends on:
    Strict mixed invariant representatives and generic parameterized cochains.

Must not:
    Select a projective point, reuse retired representatives, infer stability,
    or call the family genuinely SU(4).

Phase 0:
    Universal lawful algebraic-family regression tests only.
"""

import json

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    OUTPUT,
    mixed_schoen_universal_outer_cone,
)


def test_universal_mixed_cone_recovers_every_strict_basis_class() -> None:
    """Coordinate specializations recover the lawful forward invariants."""

    cone = mixed_schoen_universal_outer_cone()

    assert cone.parameters == ("a0", "a1")
    assert cone.mapping_cone_squared_zero
    assert cone.equivariant_descent_exact
    assert cone.local_freeness_exact
    assert cone.rank == 4
    assert cone.determinant_c1 == ("0", "0", "0")
    assert tuple(
        generator.terms for generator in cone.split_locus_ideal.generators
    ) == (
        (((1, 0), Eisenstein(1)),),
        (((0, 1), Eisenstein(1)),),
    )
    for index, representative in enumerate(cone.basis_representatives):
        point = tuple(
            Eisenstein(int(position == index))
            for position in range(len(cone.parameters))
        )
        assert cone.extension.specialize(point) == representative


def test_universal_mixed_cone_artifact_preserves_the_su4_gate() -> None:
    """The frozen family closes algebraically without claiming stability."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["parameters"] == ["a0", "a1"]
    assert stored["parameter_count_derived_from_invariant_basis"] is True
    assert stored["projective_non_split_space"] == "P^1(Q(omega))"
    assert stored["generated_complex"] == {
        "objects": ["V1", "V2"],
        "orientation": "RHom(V2,V1)",
        "differential": "D_E(a)=[[D_V1,e(a)],[0,D_V2]]",
        "extension": "e(a)=a0 e_0+a1 e_1",
        "squared_zero": True,
        "parameter_linear": True,
    }
    assert stored["rank"] == 4
    assert stored["chern_classes"] == {
        "c1": ["0", "0", "0"],
        "c2": ["8/3", "5/3", "4"],
        "c3": "-6",
        "parameter_independent": True,
        "provenance": "published visible constituent topology",
    }
    assert stored["local_freeness_locus"] == "all A^2(Q(omega))"
    assert stored["equivariant_descent_exact"] is True
    assert stored["retired_pure_cech_representatives_used"] is False
    assert stored["arbitrary_extension_point_selected"] is False
    assert stored["genuine_su4_locus_computed"] is False
