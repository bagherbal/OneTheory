"""Tests for the published universal outer mapping-cone certificate.

Owns:
    Universal specialization, split-locus, block-square, topology, descent,
    and content-addressing regression gates.

Depends on:
    The strict invariant outer basis and exact parameterized cone constructor.

Must not:
    Select a projective point, infer stability, or call the full family SU(4).

Phase 0:
    Universal algebraic-family tests only; the stable SU(4) locus remains open.
"""

import json

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.published_outer_universal_cone import (
    OUTPUT,
    published_universal_outer_cone,
)


def test_universal_outer_cone_recovers_every_exact_basis_class() -> None:
    """Coordinate specializations recover the four strict forward cocycles."""

    cone = published_universal_outer_cone()

    assert cone.mapping_cone_squared_zero
    assert cone.equivariant_descent_exact
    assert cone.local_freeness_exact
    assert cone.rank == 4
    assert cone.determinant_c1 == ("0", "0", "0")
    assert len(cone.extension.terms) == 4050
    assert tuple(
        generator.terms
        for generator in cone.split_locus_ideal.generators
    ) == tuple(
        ((tuple(int(position == index) for position in range(4)), Eisenstein(1)),)
        for index in range(4)
    )
    for index, representative in enumerate(cone.basis_representatives):
        point = tuple(
            Eisenstein(int(position == index))
            for position in range(4)
        )
        assert cone.extension.specialize(point) == representative


def test_universal_outer_cone_artifact_preserves_the_su4_gate() -> None:
    """The frozen family closes algebraically without claiming stability."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["parameters"] == ["a0", "a1", "a2", "a3"]
    assert stored["projective_non_split_space"] == "P^3(Q(omega))"
    assert stored["generated_complex"] == {
        "objects": ["V1", "V2"],
        "differential": "D_E(a)=[[D_V1,e(a)],[0,D_V2]]",
        "extension": "e(a)=a0 e_0+a1 e_1+a2 e_2+a3 e_3",
        "squared_zero": True,
        "parameter_linear": True,
    }
    assert stored["rank"] == 4
    assert stored["chern_classes"] == {
        "c1": ["0", "0", "0"],
        "c2": ["8/3", "5/3", "4"],
        "c3": "-6",
        "parameter_independent": True,
    }
    assert stored["local_freeness_locus"] == "all A^4(Q(omega))"
    assert stored["equivariant_descent_exact"] is True
    assert stored["arbitrary_extension_point_selected"] is False
    assert stored["genuine_su4_locus_computed"] is False
