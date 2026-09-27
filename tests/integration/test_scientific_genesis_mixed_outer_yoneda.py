"""Check signed outer composition before using it for physical cochains."""

from __future__ import annotations

import json

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis.alternate_up_yoneda_evaluation import (
    OUTPUT,
    _ratio,
    alternate_up_yoneda_evaluation,
)
from research.experiments.scientific_genesis.mixed_outer_yoneda import (
    compose_outer_cochains,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
)


def _basis(
    left: int, right: int, summand: str,
    cell: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
) -> OuterCechBasis:
    """Create a degree-zero line frame solely for a graded product test."""

    degree = {"k0": (0, 0, 0), "k1_x": (3, 0, 1), "k1_u": (0, 3, 1), "k2": (3, 3, 2)}[summand]
    component = OuterCechComponent(left, right, 0, degree, summand)
    return OuterCechBasis(
        component, (0, 0, 0), (0, 0, 0), (0, 0), cell
    )


def test_koszul_composition_is_antisymmetric() -> None:
    """The two equation generators anticommute on a common cover cell."""

    cell = ((0,), (0,), (0,))
    x = SparseOuterCechCochain(((_basis(0, 0, "k1_x", cell), Eisenstein(1)),))
    u = SparseOuterCechCochain(((_basis(0, 0, "k1_u", cell), Eisenstein(1)),))
    target = _basis(0, 0, "k2", cell).component
    components = {(0, 0, "k2"): target}
    middle = MixedSchoenUnit()
    forward = compose_outer_cochains(
        x, u, components, left_middle=middle, right_middle=middle
    )
    backward = compose_outer_cochains(
        u, x, components, left_middle=middle, right_middle=middle
    )
    assert forward.terms == ((_basis(0, 0, "k2", cell), Eisenstein(1)),)
    assert backward == forward.scale(-1)


def test_alexander_whitney_endpoint_is_required() -> None:
    """Noncomposable cover cells cannot create an artificial cup term."""

    left = SparseOuterCechCochain((
        (_basis(0, 0, "k0", ((0, 1), (0,), (0,))), Eisenstein(1)),
    ))
    right = SparseOuterCechCochain((
        (_basis(0, 0, "k0", ((2,), (0,), (0,))), Eisenstein(1)),
    ))
    target = _basis(0, 0, "k0", ((0,), (0,), (0,))).component
    middle = MixedSchoenUnit()
    assert compose_outer_cochains(
        left, right, {(0, 0, "k0"): target},
        left_middle=middle, right_middle=middle,
    ).is_zero()


def test_distinct_middle_frames_are_rejected() -> None:
    """Equal-looking but unconnected middle complexes are not identified."""

    cell = ((0,), (0,), (0,))
    identity = SparseOuterCechCochain((
        (_basis(0, 0, "k0", cell), Eisenstein(1)),
    ))
    target = _basis(0, 0, "k0", cell).component
    with pytest.raises(ValueError, match="identical middle complex"):
        compose_outer_cochains(
            identity, identity, {(0, 0, "k0"): target},
            left_middle=MixedSchoenUnit(),
            right_middle=MixedSchoenUnit(),
        )


def test_actual_alternate_hom_evaluations_survive_cohomology() -> None:
    """Recompute all four exact Yoneda images and fixed-basis ratios."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    assert payload["schema"] == "alternate-up-yoneda-evaluation-v1"
    assert payload["all_full_cycles_exact"] is True
    assert payload["all_nonboundary_exact"] is True
    assert payload["cohomological_ratios_exact"] is True
    assert payload["same_cone_higgs_cocycle_constructed"] is False
    assert payload["holomorphic_yukawa_entries_computed"] is False
    evaluations = alternate_up_yoneda_evaluation()
    assert [item.as_record() for item in evaluations] == payload["evaluations"]
    assert [item.character for item in evaluations] == [
        (0, 0), (0, 0), (1, 0), (1, 0)
    ]
    assert all(len(item.full_cochain.terms) == 207 for item in evaluations)
    assert all(item.nonboundary_exact for item in evaluations)
    assert _ratio(evaluations[0], evaluations[1]) == Eisenstein(2, -1) / 7
    assert _ratio(evaluations[2], evaluations[3]) == Eisenstein(-3, -2) / 7
