"""Guard the scoped determinant obstruction for alternate atlas rays.

Owns:
    Content-addressed character arithmetic, scalar-residue evidence, and
    explicit limits of the fixed-linearization no-go.

Depends on:
    The exact alternate determinant experiment and its generated certificate.

Must not:
    Generalize the obstruction to other linearisations or identify Higgs states.

Phase 0:
    Research-only regression for a conditional determinant no-go.
"""

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_determinant_descent import (
    OUTPUT,
)


def test_fixed_alternate_atlas_pairs_have_nontrivial_determinants() -> None:
    """Both exact character sums obstruct SU(4) in the declared scope."""

    report = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = report.pop("artifact_digest")
    assert digest == _canonical_digest(report)
    assert report["schema"] == "alternate-constituent-determinant-descent-v1"
    assert [case["ray_character_exponents"] for case in report["cases"]] == [
        [0, 1], [1, 1]
    ]
    assert [case["total_determinant_character"] for case in report["cases"]] == [
        [2, 1], [0, 1]
    ]
    for case in report["cases"]:
        left, right = case["constituent_determinant_characters"]
        assert case["total_cover_line_degree"] == [0, 0, 0]
        assert case["total_determinant_character"] == [
            (first + second) % 3
            for first, second in zip(left, right, strict=True)
        ]
        assert case["geometric_scalar_h3_character"] == [0, 0]
        assert case["scalar_h3_character"] == case["total_determinant_character"]
        assert case["equivariantly_trivial_determinant"] is False
    assert report["fixed_linearization_su4_excluded_for_both_rays"] is True
    assert report["conditional_on_equivariant_outer_extension"] is True
    assert report["outer_extension_constructed"] is False
    assert report["other_linearizations_or_bundles_excluded"] is False
    assert report["physical_higgs_spectrum_computed"] is False
