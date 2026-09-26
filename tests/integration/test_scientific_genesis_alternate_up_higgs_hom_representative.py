"""Guard the alternate up-Higgs-relevant Hom class without promoting it.

Owns:
    Reproduction of the strict full Hom cycle, deck character, nonboundary
    coordinate, and determinant-frame character calculation.

Depends on:
    The alternate Hom experiment and exact common-Schoen action machinery.

Must not:
    Treat a Hom representative as a tensor or exterior-square Higgs cocycle.

Phase 0:
    Research-only regression for the next physical Higgs prerequisite.
"""

import json

from onetheory.math.numbers import OMEGA
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis import (
    alternate_up_higgs_hom_representative as hom_route,
)
from research.experiments.scientific_genesis.alternate_constituent_hom_actions import (
    _common_frame,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    _constituent,
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _verified_payload,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)


def test_alternate_up_higgs_hom_is_strict_but_not_a_higgs_cocycle() -> None:
    """Rebuild the saved Hom class and check full differential and actions."""

    saved = json.loads(hom_route.OUTPUT.read_text(encoding="utf-8"))
    digest = saved.pop("artifact_digest")
    assert digest == _canonical_digest(saved)
    result = hom_route.alternate_up_higgs_hom_representative()
    assert result.as_record() == saved
    assert saved["hom_character"] == [2, 0]
    assert saved["repaired_higgs_forward_character"] == [0, 2]
    assert saved["repaired_higgs_source_character"] == [0, 1]
    assert saved["higgs_tensor_chain_map_constructed"] is False
    assert saved["exterior_cone_higgs_cocycle_constructed"] is False
    assert saved["yukawa_matrix_computed"] is False
    assert any(not value.is_zero() for value in result.cohomology_coordinates)

    _cone_digest, cone = _verified_payload(hom_route.CONE)
    determinant = tuple(cone["determinant_character_before_common_twist"])
    twist = tuple(cone["common_flat_character_twist"])
    assert tuple(
        (hom_component + determinant[index] + 2 * twist[index]) % 3
        for index, hom_component in enumerate(hom_route.HOM_CHARACTER)
    ) == (0, 2)

    first = mixed_schoen_constituents()[0]
    ray = lift_joint_character_ray(
        published_constituent_deck_actions()[1], OMEGA**0, OMEGA**1
    )
    second = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    contraction = _MixedContraction(first, second)
    assert contraction.differential(result.full_cochain).is_zero()
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for index, name in enumerate(("P", "T")):
        transformed = _full_action(
            result.full_cochain,
            first,
            second,
            actions[name],
            (_common_frame(first, actions[name]), _common_frame(second, actions[name])),
        )
        assert transformed == result.full_cochain.scale(OMEGA ** hom_route.HOM_CHARACTER[index])
