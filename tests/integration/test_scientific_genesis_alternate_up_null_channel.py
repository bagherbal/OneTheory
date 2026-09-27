"""Regress the exact alternate up-sector null-channel homotopies.

Owns:
    Full Yoneda-boundary reconstruction and an independent formal
    determinant identity for the known mixed blocks.

Depends on:
    Exact production polynomial algebra, saved cover traces, and the
    research-only alternate common-cover Hom complex.

Must not:
    Substitute guessed F--F coefficients, assert rank three, or call
    the cover matrix a normalized physical Yukawa.

Phase 0:
    Research-only compression of the next determinant calculation.
"""

from __future__ import annotations

import json

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, polynomial_determinant
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.alternate_up_null_channel import (
    OUTPUT,
    alternate_up_null_channels,
)


def test_both_null_yoneda_channels_have_exact_full_primitives() -> None:
    """The two strict null combinations are full boundaries, not just ratios."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    channels = alternate_up_null_channels()
    assert [channel.as_record() for channel in channels] == payload["null_channels"]
    assert [channel.matter_character for channel in channels] == [(0, 0), (1, 0)]
    assert [channel.seed5_over_seed0 for channel in channels] == [
        Eisenstein(2, -1) / 7,
        Eisenstein(-3, -2) / 7,
    ]
    assert all(len(channel.null_evaluation.terms) == 144 for channel in channels)
    assert all(len(channel.primitive.terms) == 90 for channel in channels)
    assert payload["determinant_prefactor"] == "9/4*omega"
    assert payload["determinant_sensitive_unknown_coefficients"] == 2
    assert payload["null_to_null_coefficients_computed"] is False
    assert payload["rank_three_established"] is False


def test_formal_determinant_is_only_the_null_to_null_pairing() -> None:
    """Check the sign with four independent symbolic F--F entries."""

    b0 = Eisenstein(3) / 2
    b1 = Eisenstein(-9, -6) / 14
    c0 = -Eisenstein(0, 3) / 2
    c1 = -Eisenstein(3, 9) / 14
    variables = tuple(
        Polynomial.monomial(
            tuple(int(index == position) for position in range(4)),
            scalar_type=Eisenstein,
        )
        for index in range(4)
    )
    zero = Polynomial.zero(4, scalar_type=Eisenstein)
    def constant(value: Eisenstein) -> Polynomial:
        return Polynomial.constant(value, 4, scalar_type=Eisenstein)
    determinant = polynomial_determinant((
        (zero, constant(b0), constant(b1)),
        (constant(c0), variables[0], variables[1]),
        (constant(c1), variables[2], variables[3]),
    ))
    left_null = (-c1 / c0, Eisenstein(1))
    right_null = (-b1 / b0, Eisenstein(1))
    projected = sum(
        (
            variables[2 * row + column].scale(
                -b0 * c0 * left_null[row] * right_null[column]
            )
            for row in range(2) for column in range(2)
        ),
        zero,
    )
    assert determinant == projected
    assert -b0 * c0 == Eisenstein(0, 9) / 4
