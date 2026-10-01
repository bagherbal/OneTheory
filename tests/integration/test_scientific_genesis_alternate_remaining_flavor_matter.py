"""Independently replay the remaining exact flavor constituent inputs.

Owns:
    Original full differential and atlas checks, exact nonboundary coordinates,
    deterministic archive reproduction, and fail-closed routing/scope attacks.

Depends on:
    Actual six-cochain archives, the frozen constituent complexes, original
    transfer and deck engines, exact coefficient arithmetic, and pytest.

Must not:
    Assign a Yukawa coefficient, select moduli, replace Q/L classes, or infer
    corrected matter states or physical masses from constituent cycles alone.

Phase 0:
    Conditional heterotic input verification only.
"""

from pathlib import Path

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer_actions import (
    _independent_columns,
    _SparseSpanSolver,
)
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions
from research.experiments.computable_carrier.schoen_sparse_outer_actions import (
    _cohomology_complement_columns,
    _columns,
    _select_columns,
)
from research.experiments.scientific_genesis import alternate_remaining_flavor_matter as matter
from research.experiments.scientific_genesis.alternate_constituent_hom_actions import _common_frame
from research.experiments.scientific_genesis.alternate_up_ff_entries import (
    _read_witnesses,
    _write_witnesses,
)
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    _constituent,
    mixed_schoen_constituents,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
    _perturbed_projection,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    mixed_schoen_unit,
    mixed_transferred_outer_hom,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)

DIGEST = "363c8bc51e58fd6177943b89fdac08b760c5059bf09b1ba7e64b84414a53a8dc"
NAMES = ("first_sector0", "first_sector1", "second_sector0_family1",
         "second_sector0_family2", "second_sector1_family1", "second_sector1_family2")


def test_actual_remaining_constituents_replay_full_equations_and_nonboundary_coordinates() -> None:
    """Direct full equations do not use the producer's success flags."""

    record, witnesses = matter.load_remaining_flavor_matter(expected_digest=DIGEST)
    first = mixed_schoen_constituents()[0]
    second = _constituent(lift_joint_character_ray(
        published_constituent_deck_actions()[1], 1, OMEGA,
    ), "I6-ray-0-1", 2, (1, -1, 0))
    for constituent, items, dimension in (
        (first, record["first_constituent_classes"], 9),
        (second, record["second_constituent_classes"], 18),
    ):
        context = _MixedContraction(constituent, mixed_schoen_unit())
        transferred = mixed_transferred_outer_hom(constituent, context.right)
        incoming, outgoing = dict(transferred.differentials)[0], dict(transferred.differentials)[1]
        cycles = outgoing.kernel_inclusion()
        representatives = _select_columns(
            cycles, _cohomology_complement_columns(incoming, cycles), "original remaining H1 order",
        )
        boundaries, seeds = _independent_columns(incoming), tuple(_columns(representatives))
        solver = _SparseSpanSolver(boundaries + seeds)
        for index, item in enumerate(items):
            name = f"first_sector{index}" if dimension == 9 else (
                f"second_sector{index // 2}_family{1 + index % 2}"
            )
            full = witnesses[name]
            character = item["character" if dimension == 9 else "constituent_character"]
            assert len(full.terms) == (360 if dimension == 9 else 378)
            assert context.differential(full).is_zero()
            actions = {action.name: action for action in schoen_sparse_deck_actions()}
            for position, name in enumerate(("P", "T")):
                action = actions[name]
                assert _full_action(full, constituent, context.right, action, (
                    _common_frame(constituent, action), Matrix.identity(1, scalar_type=Eisenstein),
                )) == full.scale(OMEGA ** character[position])
            reduced, _ = _perturbed_projection(full, context, 1)
            coordinates = solver.coordinates(reduced)
            actual = tuple(coordinates.get(len(boundaries) + column, Eisenstein(0))
                           for column in range(dimension))
            assert actual == tuple(
                _parse_eisenstein_text(c) for c in item["cohomology_coordinates"]
            )
            assert any(not value.is_zero() for value in actual)
            with pytest.raises(ValueError, match="escaped the cycle span"):
                _SparseSpanSolver(boundaries).coordinates(reduced)
        assert transferred.cohomology_dimension(1) == dimension
    for character in ((1, 1), (2, 0)):
        selected = [item for item in record["second_constituent_classes"]
                    if item["constituent_character"] == list(character)]
        assert Matrix(tuple(tuple(_parse_eisenstein_text(item["cohomology_coordinates"][column])
                                  for item in selected) for column in range(18)),
                      scalar_type=Eisenstein).rank() == 2


def test_missing_constituent_sector_producer_reproduces_exact_original_archive(
    tmp_path: Path,
) -> None:
    """Fresh extraction retains the original seeds and all literal coefficients."""

    path = tmp_path / matter.OUTPUT.name
    saved, _ = matter.load_remaining_flavor_matter(expected_digest=DIGEST)
    assert matter.write_remaining_flavor_matter(path) == saved
    assert path.read_bytes() == matter.OUTPUT.read_bytes()
    assert path.with_suffix(".cochains.json.gz").read_bytes() == (
        matter.OUTPUT.with_suffix(".cochains.json.gz").read_bytes()
    )


@pytest.mark.parametrize("field,value", (
    ("native_matter_characters", [[0, 0], [1, 0]]),
    ("common_flat_twist", [0, 0]),
    ("source", {"version": "unpublished"}),
    ("basis_convention", "unreported reordering"),
    ("full_cone_matter_corrections_computed", True),
    ("physical_yukawas_available", True),
    ("extension_point_selected", True),
))
def test_rehashed_remaining_inputs_cannot_change_the_scientific_scope(
    tmp_path: Path, field: str, value: object,
) -> None:
    record, witnesses = _read_witnesses(
        matter.OUTPUT, "alternate-remaining-flavor-matter-v1", NAMES,
    )
    for key in ("witnesses", "full_cochain_archive_name", "full_cochain_archive_sha256",
                "full_cochain_payload_digest"):
        record.pop(key)
    record[field] = value
    path = tmp_path / matter.OUTPUT.name
    changed = _write_witnesses(path, record, witnesses)
    with pytest.raises(ValueError, match="routing, basis, proof, or scope"):
        matter.load_remaining_flavor_matter(path, expected_digest=changed["artifact_digest"])


def test_remaining_input_loader_has_no_missing_archive_fallback(tmp_path: Path) -> None:
    path = tmp_path / matter.OUTPUT.name
    with pytest.raises(FileNotFoundError):
        matter.load_remaining_flavor_matter(path, expected_digest=DIGEST)
    path.write_bytes(matter.OUTPUT.read_bytes())
    with pytest.raises(FileNotFoundError):
        matter.load_remaining_flavor_matter(path, expected_digest=DIGEST)
    with pytest.raises(ValueError, match="expected content digest"):
        matter.load_remaining_flavor_matter(expected_digest="0" * 64)
