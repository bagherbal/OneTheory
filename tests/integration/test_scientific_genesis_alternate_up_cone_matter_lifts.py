"""Check the exact alternate universal-cone up-matter slice.

Owns:
    Artifact integrity, first-constituent atlas classes, and one independent
    direct cone-identity recheck against a saved coefficient digest.

Depends on:
    The frozen alternate cone, exact common DGA, and research lift generator.

Must not:
    Infer a physical Higgs representative or a Yukawa value from matter lifts.

Phase 0:
    Research-only regression for the minimum up-sector cone classes.
"""

from __future__ import annotations

import json

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)
from research.experiments.scientific_genesis import (
    alternate_constituent_up_cone_matter_lifts as cone_matter,
)
from research.experiments.scientific_genesis import (
    alternate_constituent_up_matter_representatives as up_matter,
)
from research.experiments.scientific_genesis.alternate_constituent_hom_actions import (
    _common_frame,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_common_dga import (
    mixed_outer_cup,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _cochain_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _representative,
    _verified_payload,
)


def _saved() -> dict[str, object]:
    """Read only a correctly content-addressed exact lift record."""

    saved = json.loads(cone_matter.OUTPUT.read_text(encoding="utf-8"))
    digest = saved.pop("artifact_digest")
    assert digest == _canonical_digest(saved)
    return saved


def test_alternate_up_cone_artifact_keeps_higgs_and_yukawa_open() -> None:
    """Require all six matter classes without claiming the missing pairing."""

    saved = _saved()
    assert saved["schema"] == "alternate-constituent-up-cone-matter-lifts-v1"
    assert saved["carrier_parameter_basis"] == ["a0", "a1"]
    assert saved["carrier_locus"] == "P^1(Q(omega)) x K^s"
    assert saved["common_flat_twist"] == [1, 2]
    assert saved["pre_twist_character_sectors"] == [[0, 0], [1, 0]]
    assert saved["universal_visible_family_dimension_per_character"] == 3
    assert saved["all_coefficientwise_cone_identities_exact"] is True
    assert saved["all_lifts_strict_in_declared_characters"] is True
    assert saved["arbitrary_extension_point_selected"] is False
    assert saved["higgs_cocycle_computed"] is False
    assert saved["holomorphic_yukawa_matrix_computed"] is False
    assert [item["character"] for item in saved["first_constituent_constant_classes"]] == [
        [0, 0], [1, 0],
    ]
    assert [item["character"] for item in saved["second_constituent_parameter_linear_lifts"]] == [
        [0, 0], [0, 0], [1, 0], [1, 0],
    ]
    for lift in saved["second_constituent_parameter_linear_lifts"]:
        coefficients = lift["parameter_coefficients"]
        assert [item["parameter"] for item in coefficients] == ["a0", "a1"]
        assert all(item["product_cycle_exact"] is True for item in coefficients)
        assert all(item["coefficientwise_cone_identity_exact"] is True for item in coefficients)
        assert all(item["strict_alternate_character_exact"] is True for item in coefficients)
        assert all(item["correction_term_count"] > 0 for item in coefficients)


def test_first_constituent_classes_reproduce_in_the_alternate_atlas() -> None:
    """Rebuild both constant classes and recheck full differential/action."""

    saved = _saved()
    classes = cone_matter._first_representatives()
    assert [item.as_record() for item in classes] == saved["first_constituent_constant_classes"]
    first = mixed_schoen_constituents()[0]
    contraction = _MixedContraction(first, mixed_schoen_unit())
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for item in classes:
        assert contraction.differential(item.full_cochain).is_zero()
        for index, name in enumerate(("P", "T")):
            transformed = _full_action(
                item.full_cochain,
                contraction.left,
                contraction.right,
                actions[name],
                (_common_frame(first, actions[name]), Matrix.identity(1, scalar_type=Eisenstein)),
            )
            assert transformed == item.full_cochain.scale(OMEGA ** item.character[index])


def test_first_cone_correction_reproduces_its_exact_identity() -> None:
    """Recompute one parameter coefficient and check the block differential."""

    saved = _saved()
    matter = up_matter.alternate_constituent_up_matter_representatives().classes[0]
    _digest, invariant = _verified_payload(cone_matter.INVARIANTS)
    raw = invariant["strict_full_cech_representatives"]
    extension = _representative(raw[0])
    first = mixed_schoen_constituents()[0]
    unit = mixed_schoen_unit()
    contraction = _MixedContraction(first, unit)
    result = cone_matter._coefficient(
        "a0", matter, extension, contraction, mixed_transferred_outer_hom(first, unit)
    )
    expected = saved["second_constituent_parameter_linear_lifts"][0][
        "parameter_coefficients"
    ][0]
    assert result.as_record() == expected
    product = mixed_outer_cup(extension, matter.full_cochain)
    assert _cochain_digest((product,)) == expected["product_digest"]
    assert (contraction.differential(result.correction) + product).is_zero()
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for index, name in enumerate(("P", "T")):
        transformed = _full_action(
            result.correction,
            contraction.left,
            contraction.right,
            actions[name],
            (_common_frame(first, actions[name]), Matrix.identity(1, scalar_type=Eisenstein)),
        )
        assert transformed == result.correction.scale(OMEGA ** matter.character[index])
