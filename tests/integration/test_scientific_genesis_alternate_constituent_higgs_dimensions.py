"""Guard the scoped cover cohomology result for two unused Serre rays.

Owns:
    Exact artifact integrity, rank arithmetic, and unresolved-physics gates.

Depends on:
    The content-addressed research certificate and finite ray screen.

Must not:
    Read cover dimension as a quotient or physical Higgs multiplicity.

Phase 0:
    Research-artifact regression checks; expensive transfer is run explicitly.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    _components,
)
from research.experiments.scientific_genesis.alternate_constituent_higgs_dimensions import (
    ALTERNATE_RAYS,
    OUTPUT,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_higgs_twist_audit import (
    determinant_twisted_second_constituent,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    _skeleton,
)


def test_outer_transfer_uses_right_to_left_hom_orientation() -> None:
    """The source-minus-target line degree identifies Hom(right, left)."""

    first = mixed_schoen_constituents()[0]
    twisted_second = determinant_twisted_second_constituent()
    component = _components(_skeleton(first), _skeleton(twisted_second))[0]
    assert component.line_degree == tuple(
        left - right
        for left, right in zip(
            first.objects[0].line_degree,
            twisted_second.objects[0].line_degree,
            strict=True,
        )
    )


def test_alternate_cover_h1_certificate() -> None:
    """Both alternate full-chain ranks yield four exact cover classes."""

    report = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = report.pop("artifact_digest")
    assert digest == _canonical_digest(report)
    assert report["schema"] == "alternate-constituent-higgs-dimensions-v2"
    assert report["hom_orientation"] == "Hom(right=V2 tensor det(V1), left=V1)"
    assert report["identity"] == (
        "Hom(V2 tensor det(V1), V1) = V1 tensor V2 for rank-two "
        "V2 with det(V2) = det(V1)^-1"
    )
    assert report["v1_determinant_cover_degree"] == [-2, 2, 0]
    assert report["v2_hom_twist_after_identity"] == [-1, 1, 0]
    cases = report["cases"]
    assert [tuple(case["ray_character_exponents"]) for case in cases] == list(
        ALTERNATE_RAYS
    )
    for case in cases:
        assert {
            degree: dimension
            for degree, dimension in case["space_dimensions"]
            if dimension
        } == {0: 129, 1: 464, 2: 426, 3: 91}
        assert case["differential_ranks"] == [[0, 129], [1, 331]]
        assert case["h1_dimension"] == 464 - 129 - 331 == 4
        assert case["squared_zero_through_degree_one"] is True
        assert case["transfer_path_depths"] == [[0, 5], [1, 7]]
        assert len(case["map_digests"]) == 2
        assert all(len(item[1]) == 64 for item in case["map_digests"])
    assert report["alternate_deck_atlases_constructed"] is False
    assert report["alternate_quotient_determinants_certified"] is False
    assert report["alternate_higgs_characters_computed"] is False
    assert report["physical_higgs_spectrum_established"] is False
