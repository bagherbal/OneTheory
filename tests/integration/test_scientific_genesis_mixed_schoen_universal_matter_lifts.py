"""Integration tests for the minimum universal visible matter lifts."""

from __future__ import annotations

import json

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import (
    mixed_outer_cup,
)
from research.experiments.scientific_genesis.mixed_schoen_universal_matter_lifts import (
    OUTPUT,
)


def _constant_basis(left: int, right: int) -> OuterCechBasis:
    """Return a degree-zero constant full-cover Hom basis element."""

    return OuterCechBasis(
        OuterCechComponent(left, right, 0, (0, 0, 0), "k0"),
        (0, 0, 0),
        (0, 0, 0),
        (0, 0),
        ((0,), (0,), (0,)),
    )


def test_common_dga_composition_is_typed_and_exact() -> None:
    """Full-cover composition contracts only a matching middle object."""

    left = SparseOuterCechCochain(((_constant_basis(0, 1), Eisenstein(2)),))
    right = SparseOuterCechCochain(((_constant_basis(1, 2), Eisenstein(3)),))
    incompatible = SparseOuterCechCochain(
        ((_constant_basis(3, 2), Eisenstein(3)),)
    )

    assert mixed_outer_cup(left, right) == SparseOuterCechCochain(
        ((_constant_basis(0, 2), Eisenstein(6)),)
    )
    assert mixed_outer_cup(left, incompatible).is_zero()


def test_universal_matter_lift_artifact_is_exact_and_fail_closed() -> None:
    """The committed certificate binds the minimum physical matter slice."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    lifts = payload["v2_parameter_linear_lifts"]

    assert digest == _canonical_digest(payload)
    assert payload["all_coefficientwise_cone_identities_exact"] is True
    assert payload["all_lifts_strict_in_declared_characters"] is True
    assert payload["arbitrary_extension_point_selected"] is False
    assert payload["higgs_lift_computed"] is False
    assert payload["physical_slice"]["matter_character_exponents"] == [
        [2, 1],
        [1, 1],
    ]
    assert payload["physical_slice"]["required_higgs_character_exponents"] == [
        0,
        1,
    ]
    assert len(lifts) == 4
    assert all(lift["exact"] for lift in lifts)
    assert all(len(lift["parameter_coefficients"]) == 2 for lift in lifts)
