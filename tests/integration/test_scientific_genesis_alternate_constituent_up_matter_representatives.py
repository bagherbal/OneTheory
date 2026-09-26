"""Guard the first strict alternate-constituent up-matter slice.

Owns:
    Independent full-complex closure, deck-character, exact-rank, and saved
    artifact checks for the four I6 constituent representatives.

Depends on:
    The frozen alternate research computation and its exact sparse algebra.

Must not:
    Treat a constituent class as a cone lift or infer a Yukawa coefficient.

Phase 0:
    Research-only regression for a necessary up-type matter input.
"""

import json

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis import (
    alternate_constituent_up_matter_representatives as up_matter,
)
from research.experiments.scientific_genesis.alternate_constituent_hom_actions import (
    _common_frame,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    _constituent,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    mixed_schoen_unit,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)


def test_alternate_up_matter_is_strict_but_not_yet_cone_lifted() -> None:
    """Recheck the saved four-class certificate in the full alternate atlas."""

    result = up_matter.alternate_constituent_up_matter_representatives()
    saved = json.loads(up_matter.OUTPUT.read_text(encoding="utf-8"))
    digest = saved.pop("artifact_digest")
    assert digest == _canonical_digest(saved)
    assert result.as_record() == saved
    assert result.reduced_dimension == 18
    assert result.boundary_dimension == 189
    assert [item.character for item in result.classes] == [
        (0, 0), (0, 0), (1, 0), (1, 0),
    ]
    assert [tuple(item["repaired_carrier_character"]) for item in saved["classes"]] == [
        *([up_matter.UP_SPINOR_WILSON_WEIGHTS[0]] * 2),
        *([up_matter.UP_SPINOR_WILSON_WEIGHTS[1]] * 2),
    ]
    assert saved["outer_cone_lifts_computed"] is False
    assert saved["higgs_cocycles_computed"] is False
    assert saved["yukawa_matrix_computed"] is False

    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    contraction = _MixedContraction(second, mixed_schoen_unit())
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for item in result.classes:
        assert contraction.differential(item.full_cochain).is_zero()
        for index, name in enumerate(("P", "T")):
            frame = _common_frame(second, actions[name])
            transformed = _full_action(
                item.full_cochain,
                contraction.left,
                contraction.right,
                actions[name],
                (frame, Matrix.identity(1, scalar_type=Eisenstein)),
            )
            assert transformed == item.full_cochain.scale(OMEGA ** item.character[index])

    for character in ((0, 0), (1, 0)):
        sector = [
            item.cohomology_coordinates
            for item in result.classes
            if item.character == character
        ]
        matrix = Matrix(
            tuple(tuple(vector[row] for vector in sector) for row in range(18)),
            scalar_type=Eisenstein,
        )
        assert matrix.rank() == 2


def test_factored_projector_equals_the_full_group_average() -> None:
    """Four deck actions reproduce the exact nine-term Reynolds sum."""

    cochain = up_matter.alternate_constituent_up_matter_representatives().classes[0].full_cochain
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    contraction = _MixedContraction(second, mixed_schoen_unit())
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    frames = {
        name: (_common_frame(second, action), Matrix.identity(1, scalar_type=Eisenstein))
        for name, action in actions.items()
    }
    character = (1, 0)
    total = SparseOuterCechCochain()
    p_power = cochain
    for p_exponent in range(3):
        term = p_power
        for t_exponent in range(3):
            total = total + term.scale(
                OMEGA ** (-character[0] * p_exponent - character[1] * t_exponent)
            )
            term = _full_action(
                term, contraction.left, contraction.right, actions["T"], frames["T"]
            )
        p_power = _full_action(
            p_power, contraction.left, contraction.right, actions["P"], frames["P"]
        )
    assert up_matter._project(cochain, character, contraction, actions, frames) == (
        total.scale(Eisenstein(1) / 9)
    )
