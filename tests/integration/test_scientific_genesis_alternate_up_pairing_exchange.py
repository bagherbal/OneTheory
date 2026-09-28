"""Check a direct ordered residue and the actual matter-exchange comparison.

Owns:
    Independent top-Laurent coefficient fixtures, refusal of noncycles,
    full exchange reconstruction, and exact archived witness verification.

Depends on:
    The standard Schoen scalar complex, existing inclusion machinery,
    pinned alternate scalar screens, and the pairing-exchange experiment.

Must not:
    Call mathematical fixtures physical states or promote a symmetric
    ordered screen into the physical Higgs pairing without its own proof.

Phase 0:
    Research-only necessary tests of the physical pairing identification.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
    _include,
    _reduced_basis,
)
from research.experiments.scientific_genesis import alternate_up_pairing_exchange as exchange_module
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import (
    _scalar_context,
)
from research.experiments.scientific_genesis.alternate_up_pairing_exchange import (
    OUTPUT,
    direct_ordered_scalar_residue,
    load_alternate_up_pairing_cochains,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _cochain_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_actions import (
    _perturbed_inclusion,
    _perturbed_projection,
)


@pytest.mark.parametrize("coefficient", (Eisenstein(1), Eisenstein(2, -5) / 7))
def test_direct_laurent_residue_matches_a_completed_generator(coefficient: Eisenstein) -> None:
    """The fixture's completion does not enter the independent coefficient rule."""

    context = _scalar_context()
    entry = _reduced_basis(context.left_skeleton, context.right_skeleton, 3)[0]
    completed, _ = _perturbed_inclusion(_include(entry), context)
    scalar = completed.scale(coefficient)
    assert context.differential(scalar).is_zero()
    assert direct_ordered_scalar_residue(scalar) == coefficient
    projection, _ = _perturbed_projection(scalar, context, 3)
    assert projection == {0: coefficient}


def test_direct_residue_rejects_an_uncompleted_top_cochain() -> None:
    """A visible top coefficient is not permission to trace a noncycle."""

    context = _scalar_context()
    entry = _reduced_basis(context.left_skeleton, context.right_skeleton, 3)[0]
    raw = _include(entry)
    assert not context.differential(raw).is_zero()
    with pytest.raises(ValueError, match="cannot trace a nonclosed scalar"):
        direct_ordered_scalar_residue(raw)


def test_direct_residue_vanishes_on_a_full_scalar_boundary() -> None:
    """Use a k2 Cech-degree-four input, not an imposed zero residue."""

    context = _scalar_context()
    basis = OuterCechBasis(
        context.components[(0, 0, "k2")],
        (-1, -1, -1), (-2, -1, 0), (-1, -1),
        ((0, 1, 2), (0, 1), (0, 1)),
    )
    primitive = SparseOuterCechCochain(((basis, Eisenstein(3, 2)),))
    assert basis.total_degree == 2
    boundary = context.differential(primitive)
    assert not boundary.is_zero()
    assert context.differential(boundary).is_zero()
    assert direct_ordered_scalar_residue(boundary) == Eisenstein(0)


def test_direct_residue_rejects_the_wrong_total_degree() -> None:
    """The trace is a degree-three scalar functional, not a generic sum."""

    context = _scalar_context()
    basis = OuterCechBasis(
        context.components[(0, 0, "k0")], (0, 0, 0), (0, 0, 0), (0, 0),
        ((0,), (0,), (0,)),
    )
    with pytest.raises(ValueError, match="degree-three ordered O_X scalar"):
        direct_ordered_scalar_residue(SparseOuterCechCochain(((basis, Eisenstein(1)),)))


@pytest.mark.parametrize("parameter_index", (0, 1))
def test_full_archived_pairing_witnesses_satisfy_their_actual_identities(
    parameter_index: int,
) -> None:
    """Decode full cochains and recompute differentials without a primitive solve."""

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    coefficient = record["parameter_coefficients"][parameter_index]
    forward, reverse, primitive, exchange = load_alternate_up_pairing_cochains(parameter_index)
    assert not primitive.is_zero()
    assert _cochain_digest((forward,)) == coefficient["forward_scalar_digest"]
    assert str(direct_ordered_scalar_residue(forward)) == coefficient[
        "forward_direct_laurent_residue"
    ]
    if coefficient["reverse_scalar_closed_exact"]:
        assert str(direct_ordered_scalar_residue(reverse)) == coefficient["reverse_cover_residue"]
    if exchange is not None:
        assert coefficient["exchange_difference_boundary_exact"] is True
        assert _scalar_context().differential(exchange) == reverse + forward.scale(-1)
    assert coefficient["physical_higgs_identification_certified"] is False


def test_archive_loader_refuses_an_unavailable_parameter_before_reading() -> None:
    """A missing extension direction cannot trigger an implicit fallback."""

    with pytest.raises(ValueError, match="exchange parameter index is unavailable"):
        load_alternate_up_pairing_cochains(2)


@pytest.mark.parametrize("field", (
    "symmetrizing_average_used", "primitive_sign_changed",
    "physical_higgs_identification_certified", "complete_holomorphic_up_matrix_available",
    "physical_yukawa_matrix_available", "extension_point_selected", "observational_inputs_used",
))
def test_archived_scope_cannot_be_promoted_by_rehashing(field: str, tmp_path: Path) -> None:
    """A valid digest does not turn a necessary comparison into physical data."""

    record = json.loads(OUTPUT.read_text(encoding="utf-8"))
    record.pop("artifact_digest")
    record[field] = True
    record["artifact_digest"] = _canonical_digest(record)
    changed = tmp_path / OUTPUT.name
    changed.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="pairing-exchange prerequisite changed"):
        load_alternate_up_pairing_cochains(0, changed)


def test_missing_archive_does_not_start_a_fallback_solve(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Full witnesses are declared inputs, not an optional result cache."""

    def forbidden_solver(*args: object) -> None:
        raise AssertionError("the archive loader must not solve a missing physical prerequisite")

    monkeypatch.setattr(exchange_module, "alternate_up_exterior_primitive", forbidden_solver)
    declared = tmp_path / OUTPUT.name
    declared.write_bytes(OUTPUT.read_bytes())
    with pytest.raises(FileNotFoundError):
        load_alternate_up_pairing_cochains(0, declared)


def test_changed_compressed_witness_is_rejected_before_decoding(tmp_path: Path) -> None:
    """The loader rejects the exact declared archive's changed bytes."""

    declared = tmp_path / OUTPUT.name
    declared.write_bytes(OUTPUT.read_bytes())
    archive = declared.with_suffix(".cochains.json.gz")
    archive.write_bytes(OUTPUT.with_suffix(".cochains.json.gz").read_bytes() + b"altered")
    with pytest.raises(ValueError, match="does not match its declared digest"):
        load_alternate_up_pairing_cochains(0, declared)
