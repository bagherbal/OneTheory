"""Guard the conditional determinant-repaired alternate Higgs screen.

Owns:
    Exact character shifts, fixed Wilson counts, rank-two naturality, and
    fail-closed limits on the proposed alternate carrier route.

Depends on:
    The content-addressed research character screen and exact matrix algebra.

Must not:
    Interpret a conditional character pass as a constructed stable SU(4) cone.

Phase 0:
    Research-only necessary-character regression.
"""

import json

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, PolynomialMatrix
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_constituent_character_screen import (
    OUTPUT,
)
from research.experiments.scientific_genesis.mixed_schoen_observable_spectrum import (
    WILSON_HIGGS_CHARACTERS,
)


def test_rank_two_dual_determinant_naturality() -> None:
    """Exterior contraction intertwines a nontrivial exact rank-two action."""

    action = Matrix(
        ((Eisenstein(1), Eisenstein(1)),
         (Eisenstein(1), Eisenstein(2))),
        scalar_type=Eisenstein,
    )
    wedge = Matrix(
        ((Eisenstein(0), Eisenstein(-1)),
         (Eisenstein(1), Eisenstein(0))),
        scalar_type=Eisenstein,
    )
    assert wedge @ action == (
        action.inverse().transpose().scale(action.determinant()) @ wedge
    )


def test_rank_two_naturality_is_symbolic_not_a_sample() -> None:
    """The same intertwiner identity holds over four free coefficients."""

    a, b, c, d = (
        Polynomial.monomial(
            tuple(int(index == variable) for index in range(4)),
            scalar_type=Rational,
        )
        for variable in range(4)
    )
    zero = Polynomial.zero(4, scalar_type=Rational)
    one = Polynomial.one(4, scalar_type=Rational)
    action = PolynomialMatrix(((a, b), (c, d)))
    wedge = PolynomialMatrix(((zero, -one), (one, zero)))
    determinant_dual = PolynomialMatrix(((d, -c), (-b, a)))
    assert wedge.compose(action) == determinant_dual.compose(wedge)


def test_unique_repair_leaves_only_first_ray_conditionally_triplet_free() -> None:
    """The character screen distinguishes the two rays without a cone claim."""

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == _canonical_digest(record)
    assert record["schema"] == "alternate-constituent-character-screen-v1"
    assert record["determinant_line_cohomology_h0_to_h3"] == {
        "det_v1": [0, 0, 0, 0],
        "det_v2": [0, 0, 0, 0],
    }
    first, second = record["cases"]
    assert first["ray_character_exponents"] == [0, 1]
    assert first["unique_common_determinant_cancelling_twist"] == [1, 2]
    assert first["repaired_source_characters"] == [
        [0, 1], [0, 2], [1, 2], [2, 1]
    ]
    assert first["conditional_fixed_wilson_multiplicities"] == {
        "up_higgs_doublet": 1,
        "down_higgs_doublet": 1,
        "color_triplet": 0,
        "color_antitriplet": 0,
    }
    assert second["ray_character_exponents"] == [1, 1]
    assert second["unique_common_determinant_cancelling_twist"] == [0, 2]
    assert second["conditional_fixed_wilson_multiplicities"] == {
        "up_higgs_doublet": 1,
        "down_higgs_doublet": 1,
        "color_triplet": 1,
        "color_antitriplet": 1,
    }
    for case in (first, second):
        assert case["hom_twist_uses_canonical_frame"] is True
        delta = case["original_total_determinant_character"]
        theta = case["unique_common_determinant_cancelling_twist"]
        assert [(value + 4 * shift) % 3 for value, shift in zip(
            delta, theta, strict=True
        )] == [0, 0]
        candidates = [
            (a, b) for a in range(3) for b in range(3)
            if [(value + 4 * shift) % 3 for value, shift in zip(
                delta, (a, b), strict=True
            )] == [0, 0]
        ]
        assert candidates == [tuple(theta)]
        source = tuple(tuple(character) for character in case["repaired_source_characters"])
        assert case["conditional_fixed_wilson_multiplicities"] == {
            label: source.count(tuple((-value) % 3 for value in weight))
            for label, weight in WILSON_HIGGS_CHARACTERS.items()
        }
    assert record["ray_0_1_passes_conditional_higgs_screen"] is True
    assert record["ray_1_1_fails_conditional_triplet_screen"] is True
    assert record["outer_extension_constructed"] is False
    assert record["outer_extension_equivariance_certified"] is False
    assert record["stability_chamber_certified"] is False
    assert record["equivariant_chain_map_to_tensor_constructed"] is False
    assert record["physical_higgs_cocycles_available"] is False
    assert record["physical_carrier_frozen"] is False
