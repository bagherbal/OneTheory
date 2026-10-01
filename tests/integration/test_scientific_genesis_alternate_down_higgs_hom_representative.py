"""Check the actual down-Higgs Hom input without inferring a Higgs lift.

Owns:
    Full differential and deck replay, exact nonboundary coordinates, source
    routing, deterministic witness reproduction, and fail-closed input attacks.

Depends on:
    Original Hom transfer and atlas actions, the frozen carrier certificates,
    exact coefficient arithmetic, and the research-only witness archive.

Must not:
    Substitute character support for a cocycle, choose a physical parameter,
    or treat this Hom input as an exterior Higgs or a Yukawa matrix.

Phase 0:
    Conditional heterotic research verification only.
"""

from pathlib import Path

import pytest

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
from research.experiments.scientific_genesis import (
    alternate_down_higgs_hom_representative as down,
)
from research.experiments.scientific_genesis import alternate_up_higgs_hom_representative as hom
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
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _full_action,
    _MixedContraction,
    _perturbed_projection,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_transfer import (
    mixed_transferred_outer_hom,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)

DIGEST = "476e48e981ab66382b43d2510d7a271b2fa3f82468f885b7050edb9af3cd9276"


def test_archived_down_hom_replays_full_equations_and_exact_nonboundary_coordinates() -> None:
    """Check the literal witness, not the producer's success flags."""

    record, full = down.load_down_higgs_hom(expected_digest=DIGEST)
    assert len(full.terms) == 351
    assert record["seed_index"] == 1
    assert record["source"]["locator"] == "equation (28)"
    first = mixed_schoen_constituents()[0]
    second = _constituent(lift_joint_character_ray(
        published_constituent_deck_actions()[1], 1, OMEGA,
    ), "I6-ray-0-1", 2, (-1, 1, 0))
    context = _MixedContraction(first, second)
    assert context.differential(full).is_zero()
    assert all(basis.component.left_index == 0 for basis, _ in full.terms)
    for action in schoen_sparse_deck_actions():
        assert _full_action(full, first, second, action, (
            _common_frame(first, action), _common_frame(second, action),
        )) == full.scale(OMEGA**2)

    transferred = mixed_transferred_outer_hom(first, second)
    incoming, outgoing = dict(transferred.differentials)[0], dict(transferred.differentials)[1]
    cycles = outgoing.kernel_inclusion()
    representatives = _select_columns(
        cycles, _cohomology_complement_columns(incoming, cycles), "alternate:up-higgs:Hom",
    )
    boundaries = _independent_columns(incoming)
    seeds = tuple(_columns(representatives))
    reduced, depth = _perturbed_projection(full, context, 1)
    coordinates = _SparseSpanSolver(boundaries + seeds).coordinates(reduced)
    cohomology = tuple(coordinates.get(len(boundaries) + index, Eisenstein(0))
                       for index in range(4))
    assert cohomology == (
        Eisenstein(0), Eisenstein(1, -1) / 3, Eisenstein(0), Eisenstein(2, 1) / 3,
    )
    assert record["cohomology_coordinates"] == [str(value) for value in cohomology]
    assert record["projection_depth"] == depth == 1
    assert transferred.cohomology_dimension(1) == len(seeds) == 4
    with pytest.raises(ValueError, match="escaped the cycle span"):
        _SparseSpanSolver(boundaries).coordinates(reduced)


def test_down_hom_producer_reproduces_the_original_full_archive(tmp_path: Path) -> None:
    """A fresh original-basis reconstruction reproduces all literal coefficients."""

    path = tmp_path / down.OUTPUT.name
    saved, _ = down.load_down_higgs_hom(expected_digest=DIGEST)
    assert down.write_down_higgs_hom(path) == saved
    assert path.read_bytes() == down.OUTPUT.read_bytes()
    assert path.with_suffix(".cochains.json.gz").read_bytes() == (
        down.OUTPUT.with_suffix(".cochains.json.gz").read_bytes()
    )


@pytest.mark.parametrize("field,value", (
    ("native_hom_character", [2, 1]),
    ("repaired_higgs_source_character", [0, 1]),
    ("common_flat_twist", [0, 0]),
    ("seed_index", 0),
    ("cohomology_coordinates", ["0", "1", "0", "0"]),
    ("coefficient_field", "floating point"),
    ("source", {"locator": "eq:burt8"}),
    ("proof_sha256", "0" * 64),
    ("reduced_basis_identity", "new arbitrary basis"),
    ("higgs_exterior_cocycle_constructed", True),
    ("complete_down_matrix_available", True),
    ("extension_point_selected", True),
))
def test_rehashed_down_hom_records_cannot_change_the_routing_or_scope(
    tmp_path: Path, field: str, value: object,
) -> None:
    """A new content hash does not make an unsupported claim scientifically valid."""

    record, witnesses = _read_witnesses(
        down.OUTPUT, "alternate-down-higgs-hom-class-v1", ("strict_native_hom",),
    )
    for key in ("witnesses", "full_cochain_archive_name", "full_cochain_archive_sha256",
                "full_cochain_payload_digest"):
        record.pop(key)
    record[field] = value
    path = tmp_path / down.OUTPUT.name
    changed = _write_witnesses(path, record, witnesses)
    with pytest.raises(ValueError, match="source, frames, proof, or scope"):
        down.load_down_higgs_hom(path, expected_digest=changed["artifact_digest"])


def test_down_hom_loader_requires_a_pinned_digest_and_existing_full_witness(tmp_path: Path) -> None:
    """No fallback constructs an input when a source or archive is missing."""

    with pytest.raises(ValueError, match="expected content digest"):
        down.load_down_higgs_hom(expected_digest="0" * 64)
    path = tmp_path / down.OUTPUT.name
    with pytest.raises(FileNotFoundError):
        down.load_down_higgs_hom(path, expected_digest=DIGEST)
    path.write_bytes(down.OUTPUT.read_bytes())
    with pytest.raises(FileNotFoundError):
        down.load_down_higgs_hom(path, expected_digest=DIGEST)


@pytest.mark.parametrize("character", ((2, 1), (3, 2), (True, 2), (2, -1)))
def test_uncertified_native_hom_characters_are_rejected(character: tuple[int, int]) -> None:
    """Other sectors cannot be silently relabelled as the down Higgs."""

    with pytest.raises(ValueError):
        down._strict_hom_representative(character)


@pytest.mark.parametrize("character", ((2, False), (2, 0.0), (2.0, 2)))
def test_character_validation_precedes_cached_hom_lookup(
    character: tuple[int, int], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Python's bool/float integer-key aliases cannot bypass input validation."""

    def forbidden_lookup(_character):
        pytest.fail("a noncanonical character entered the cached Hom lookup")

    monkeypatch.setattr(hom, "_cached_strict_hom_representative", forbidden_lookup)
    with pytest.raises(ValueError):
        hom._strict_hom_representative(character)
