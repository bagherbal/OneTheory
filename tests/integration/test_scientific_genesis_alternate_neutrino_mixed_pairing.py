"""Independently verify the actual alternate Dirac-neutrino mixed slice.

Owns:
    Full archived cycle and character checks, separate Hom composition,
    direct traces, exact reproduction, archive attacks, and missing-scope gates.

Depends on:
    The frozen alternate carrier, its original exact sparse engines, published
    Wilson provenance, and complete literal neutrino cochain witnesses.

Must not:
    Import quark values as neutrino values, fill the F-F block, or infer
    physical Dirac masses, a Majorana mechanism, metrics, or a chosen vacuum.

Phase 0:
    Research-only partial holomorphic verification, conditional on heterotic UV.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions
from research.experiments.scientific_genesis import (
    alternate_constituent_up_matter_representatives as matter_inputs,
)
from research.experiments.scientific_genesis import alternate_neutrino_mixed_pairing as neutrino
from research.experiments.scientific_genesis.alternate_constituent_hom_actions import _common_frame
from research.experiments.scientific_genesis.alternate_constituent_up_cone_matter_lifts import (
    _first_representatives_for,
)
from research.experiments.scientific_genesis.alternate_up_higgs_hom_representative import (
    load_alternate_up_higgs_hom_full_cochain,
)
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import _contract
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    MixedConstituentObject,
    _constituent,
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_outer_yoneda import compose_outer_cochains
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
    _perturbed_projection,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    MixedSchoenUnit,
    mixed_schoen_unit,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)


def _saved():
    return neutrino.load_mixed_pairing(
        expected_digest="1bc8020db27e9f7a3c7ee7a7abf4ab0c456903c993eab27b0038cad5e12e6049",
    )


def test_actual_neutrino_cycles_have_their_own_strict_characters_and_bases() -> None:
    """Check all six full witnesses; reconstructed seeds must match literally."""

    record, witnesses = _saved()
    first, second = neutrino.matter_classes()
    assert [item.as_record() for item in first] == record["first_constituent_classes"]
    assert [item.as_record((1, 2)) for item in second] == record["second_constituent_classes"]
    assert [item.seed_index for item in first] == [0, 1]
    assert [item.seed_index for item in second] == [2, 4, 1, 3]
    ray = lift_joint_character_ray(published_constituent_deck_actions()[1], 1, OMEGA)
    actual_second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    actions = {item.name: item for item in schoen_sparse_deck_actions()}
    for side, character in enumerate(((2, 1), (2, 2))):
        selected = [item for item in second if item.character == character]
        assert Matrix(tuple(tuple(item.cohomology_coordinates[i] for item in selected)
                            for i in range(18)), scalar_type=Eisenstein).rank() == 2
        named = [(f"first_side{side}", first[side], mixed_schoen_constituents()[0])]
        named.extend((f"second_side{side}_family{family}", item, actual_second)
                     for family, item in enumerate(selected, start=1))
        for name, item, constituent in named:
            cycle = witnesses[name]
            context = _MixedContraction(constituent, mixed_schoen_unit())
            assert cycle == item.full_cochain
            assert context.differential(cycle).is_zero()
            for index, generator in enumerate(("P", "T")):
                frame = (_common_frame(constituent, actions[generator]),
                         Matrix.identity(1, scalar_type=Eisenstein))
                assert _full_action(cycle, context.left, context.right,
                                    actions[generator], frame) == cycle.scale(
                    OMEGA ** character[index],
                )


def test_neutrino_scalars_equal_the_separate_hom_composer_in_the_fixed_order() -> None:
    """No quotient product is used by the independent evaluation path."""

    record, witnesses = _saved()
    first = mixed_schoen_constituents()[0]
    ray = lift_joint_character_ray(published_constituent_deck_actions()[1], 1, OMEGA)
    second = _constituent(ray, "I6-ray-0-1", 2, (-1, 1, 0))
    determinant = MixedSchoenUnit("det V1", 0, (-2, 2, 0), (
        MixedConstituentObject("det V1", 0, (-2, 2, 0)),
    ))
    hom_context = _MixedContraction(first, second)
    matter_context = _MixedContraction(second, determinant)
    target = _MixedContraction(first, determinant)
    hom = load_alternate_up_higgs_hom_full_cochain()
    assert hom_context.differential(hom).is_zero()
    expected = (Eisenstein(0, 3), Eisenstein(-3) / 2,
                -Eisenstein(3, 9) / 14, Eisenstein(0, 3))
    for item, value in zip(record["evaluated_entries"], expected, strict=True):
        row, column = item["row"], item["column"]
        side, family = (1, column) if row == 0 else (0, row)
        cycle = witnesses[f"second_side{side}_family{family}"]
        assert matter_context.differential(cycle).is_zero()
        evaluated = compose_outer_cochains(hom, cycle, target.components,
            left_middle=hom_context.right, right_middle=matter_context.left)
        assert target.differential(evaluated).is_zero()
        independent = _contract(witnesses[f"first_side{1-side}"], evaluated).scale(-1)
        scalar = witnesses[f"r{row}_c{column}_scalar"]
        reverse = witnesses[f"r{row}_c{column}_reverse"]
        primitive = witnesses[f"r{row}_c{column}_exchange_primitive"]
        assert scalar == independent
        assert neutrino.pairing._scalar_context().differential(scalar).is_zero()
        assert neutrino.pairing._scalar_context().differential(primitive) == (
            reverse + scalar.scale(-1)
        )
        assert neutrino.pairing.direct_ordered_scalar_residue(scalar) == value
        projection, _ = _perturbed_projection(scalar, neutrino.pairing._scalar_context(), 3)
        assert projection == {0: value}
        assert item["cover_residue"] == str(value)
        assert item["quotient_residue"] == str(value * Rational(1, 9))


def test_neutrino_producer_reproduces_metadata_and_archive_bytes(tmp_path: Path) -> None:
    """Recompute all entries rather than manufacture a complete matrix."""

    record, _ = _saved()
    target = tmp_path / neutrino.OUTPUT.name
    assert neutrino.write_mixed_pairing(target) == record
    assert target.read_bytes() == neutrino.OUTPUT.read_bytes()
    assert target.with_suffix(".cochains.json.gz").read_bytes() == (
        neutrino.OUTPUT.with_suffix(".cochains.json.gz").read_bytes()
    )
    entries = {(item["row"], item["column"]): _parse_eisenstein_text(item["quotient_residue"])
               for item in record["evaluated_entries"]}
    for i in (1, 2):
        for j in (1, 2):
            assert record["exact_known_two_by_two_minors"][f"rows_0_{i}_columns_0_{j}"] == str(
                -entries[0, j] * entries[i, 0],
            )
    assert "matrix" not in record
    assert record["complete_holomorphic_neutrino_matrix_available"] is False
    assert record["majorana_mechanism_derived"] is False


@pytest.mark.parametrize("characters", ((), ((0, 0), (0, 0)), ((True, 0),),
                                        ((0.0, 0),), ((3, 0),), ((0,),)))
def test_requested_characters_cannot_hide_invalid_or_ambiguous_sectors(characters) -> None:
    """A reusable projector requires explicit canonical ordered characters."""

    for validate in (matter_inputs._require_characters, _first_representatives_for,
                     matter_inputs._strict_i6_representatives):
        with pytest.raises(ValueError, match="distinct canonical"):
            validate(characters)


@pytest.mark.parametrize("flag", (
    "second_second_entries_assigned", "complete_holomorphic_neutrino_matrix_available",
    "physical_yukawa_matrix_available", "majorana_mechanism_derived", "observational_inputs_used",
))
def test_even_self_rehashed_witnesses_cannot_enable_missing_physics(
    flag: str, tmp_path: Path,
) -> None:
    """Archive integrity alone cannot authorize a different scientific scope."""

    record, _ = _saved()
    record[flag] = True
    record.pop("artifact_digest")
    record["artifact_digest"] = _canonical_digest(record)
    target = tmp_path / neutrino.OUTPUT.name
    target.write_text(json.dumps(record), encoding="utf-8")
    target.with_suffix(".cochains.json.gz").write_bytes(
        neutrino.OUTPUT.with_suffix(".cochains.json.gz").read_bytes(),
    )
    with pytest.raises(ValueError, match="trusted scope"):
        neutrino.load_mixed_pairing(target, expected_digest=record["artifact_digest"])


def test_changed_archive_or_untrusted_digest_is_rejected(tmp_path: Path) -> None:
    """The read-only consumer never replaces damaged evidence by a fresh solve."""

    record, _ = _saved()
    with pytest.raises(ValueError, match="trusted scope"):
        neutrino.load_mixed_pairing(expected_digest="untrusted")
    target = tmp_path / neutrino.OUTPUT.name
    target.write_bytes(neutrino.OUTPUT.read_bytes())
    target.with_suffix(".cochains.json.gz").write_bytes(
        neutrino.OUTPUT.with_suffix(".cochains.json.gz").read_bytes() + b"corrupt",
    )
    with pytest.raises(ValueError, match="exact content"):
        neutrino.load_mixed_pairing(target, expected_digest=record["artifact_digest"])
