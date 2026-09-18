"""Test the exact reverse universal mixed outer cone.

Owns:
    Reverse basis recovery, projective dimension, topology, split locus,
    descent gates, and generated-artifact integrity.

Depends on:
    The six strict reverse invariant representatives and universal cone engine.

Must not:
    Select a reverse extension point, infer stability, or call the family a
    genuine SU(4) carrier.

Phase 0:
    Reverse algebraic-family regression tests only.
"""

import json

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_reverse_outer_universal_cone import (
    OUTPUT,
    mixed_schoen_reverse_universal_outer_cone,
)


def test_reverse_cone_recovers_all_six_strict_classes() -> None:
    """Coordinate points recover exactly the reverse invariant basis."""

    cone = mixed_schoen_reverse_universal_outer_cone()

    assert cone.parameters == ("b0", "b1", "b2", "b3", "b4", "b5")
    assert (cone.subobject_name, cone.quotient_name) == ("V2", "V1")
    assert cone.mapping_cone_squared_zero
    assert cone.equivariant_descent_exact
    assert cone.local_freeness_exact
    assert cone.rank == 4
    assert cone.determinant_c1 == ("0", "0", "0")
    assert tuple(
        generator.terms for generator in cone.split_locus_ideal.generators
    ) == tuple(
        (
            (
                tuple(int(position == index) for position in range(6)),
                Eisenstein(1),
            ),
        )
        for index in range(6)
    )


def test_reverse_cone_artifact_stops_before_the_stability_gate() -> None:
    """The reverse P5 certificate does not promote an uncomputed stable locus."""

    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")

    assert digest == _canonical_digest(stored)
    assert stored["parameters"] == ["b0", "b1", "b2", "b3", "b4", "b5"]
    assert stored["projective_non_split_space"] == "P^5(Q(omega))"
    assert stored["generated_complex"] == {
        "objects": ["V2", "V1"],
        "orientation": "RHom(V1,V2)",
        "differential": "D_E(b)=[[D_V2,e(b)],[0,D_V1]]",
        "extension": "e(b)=b0 e_0+b1 e_1+b2 e_2+b3 e_3+b4 e_4+b5 e_5",
        "squared_zero": True,
        "parameter_linear": True,
    }
    assert stored["extension_sequence"] == "0 -> V2 -> E_reverse -> V1 -> 0"
    assert stored["local_freeness_locus"] == "all A^6(Q(omega))"
    assert stored["descent_locus"] == "all A^6(Q(omega))"
    assert stored["genuine_su4_locus_computed"] is False
    assert stored["exact_reverse_stability_locus_computed"] is False
    assert stored["published_stability_scope"] == {
        "arxiv_id": "hep-th/0602073",
        "version": "v1",
        "source_archive_sha256": (
            "8e38123b9d2de8751deecbf295015497ab2ed891244215455fffe756bebf0aea"
        ),
        "result": (
            "a nonempty reverse stable subcone exists across the marginal wall"
        ),
        "used_as_existence_only": True,
    }
