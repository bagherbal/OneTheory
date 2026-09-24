"""Check exact source-atlas versus synchronized constituent actions.

Owns:
    Full-summand cochain regressions for homogeneous fiber-lift changes.

Depends on:
    Certified source atlases and the selected mixed outer action.

Must not:
    Treat a constituent character comparison as a descended SU(4) carrier.

Phase 0:
    Research-only chain-frame comparison tests.
"""

import json
from dataclasses import replace

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.dp9_serre_actions import (
    _fiber_coordinate_images,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    OuterCechComponent,
    SparseOuterCechCochain,
    _components,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis import (
    mixed_schoen_outer_actions as outer_actions,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_atlas_frame_comparison import (
    OUTPUT,
    _atlas_characters,
    _atlas_frame,
    atlas_frame_comparison_audit,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    _skeleton,
    mixed_schoen_unit,
)


def _formal_basis(component: OuterCechComponent) -> OuterCechBasis:
    x_degree, u_degree, p_degree = component.ambient_degree
    return OuterCechBasis(
        component,
        (x_degree, 0, 0),
        (u_degree, 0, 0),
        (p_degree, 0),
        ((0, 1, 2), (0, 1, 2), (0, 1)),
    )


def test_atlas_common_frame_certificate_is_current() -> None:
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = stored.pop("artifact_digest")
    assert digest == _canonical_digest(stored)
    assert stored == atlas_frame_comparison_audit()
    assert stored["first_constituent_uniform_twist"] == [2, 0]
    assert stored["second_constituent_uniform_twist"] == [0, 0]
    assert stored["source_atlas_total_determinant_certified"] is False


def test_first_constituent_full_cochains_differ_by_uniform_character(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = mixed_schoen_constituents()[0]
    unit = mixed_schoen_unit()
    atlas_characters = _atlas_characters()[1]
    original_frame = outer_actions._constituent_frame
    for action in schoen_sparse_deck_actions():
        generator = action.name
        native_p = _fiber_coordinate_images(generator, 1)
        ratio = action.p_images[0][0] / native_p[0][0]
        native_action = replace(
            action,
            p_images=native_p,
            first_equation_unit=action.first_equation_unit / ratio,
            second_equation_unit=action.second_equation_unit / ratio,
        )
        for component in _components(_skeleton(first), _skeleton(unit)):
            seed = SparseOuterCechCochain(((_formal_basis(component), Eisenstein(1)),))
            mixed = outer_actions._full_action(seed, first, unit, action)

            def native_frame(factor: int, name: str):
                if factor == 1:
                    return _atlas_frame(1, name, atlas_characters[name])
                return original_frame(factor, name)

            with monkeypatch.context() as patch:
                patch.setattr(outer_actions, "_constituent_frame", native_frame)
                atlas = outer_actions._full_action(seed, first, unit, native_action)
            expected_ratio = OMEGA**2 if generator == "P" else Eisenstein(1)
            assert mixed == atlas.scale(expected_ratio)


def test_second_constituent_inverse_atlas_frame_is_common_frame() -> None:
    atlas_characters = _atlas_characters()[2]
    for generator in ("P", "T"):
        atlas_inverse = _atlas_frame(2, generator, atlas_characters[generator])
        assert atlas_inverse == outer_actions._constituent_frame(2, generator)
