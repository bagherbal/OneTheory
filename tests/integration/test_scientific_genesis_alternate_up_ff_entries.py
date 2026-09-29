"""Attack the explicit witness boundaries of the actual F-F evaluator.

Owns:
    Fixed-index validation, deterministic exact witness serialization,
    missing-input rejection, content-addressed corruption checks, and fresh
    replay of the first actual coefficientwise carrier matter lift.

Depends on:
    The research F-F evaluator and tiny mathematical archive fixtures.

Must not:
    Treat archive fixtures as physical matter, assign missing F-F entries,
    or infer scalar closure from a valid content hash.

Phase 0:
    Evaluator regression tests only; actual coefficient results require the
    carrier calculation and independent coefficientwise verification.
"""

import gzip
import hashlib
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
)
from research.experiments.scientific_genesis.alternate_up_ff_entries import (
    GENERATED,
    _read_witnesses,
    _write_witnesses,
    ff_entry_path,
    write_ff_coefficient,
)
from research.experiments.scientific_genesis.alternate_up_full_matrix import _verified_lift
from research.experiments.scientific_genesis.alternate_up_mixed_scalar_trace import _scalar_context


@pytest.mark.parametrize("parameter", (-1, 2, True, 0.0))
def test_undeclared_formal_coefficients_fail_before_any_solver(parameter: object) -> None:
    with pytest.raises(ValueError, match="declared a0 or a1"):
        write_ff_coefficient(parameter)  # type: ignore[arg-type]


@pytest.mark.parametrize("row,column", ((0, 1), (3, 1), (True, 1), (1, 0), (1, 3), (1, True)))
def test_a_missing_or_relabelled_family_cannot_be_named(row: int, column: int) -> None:
    with pytest.raises(ValueError, match="fixed seed basis"):
        ff_entry_path(0, row, column)


def test_exact_archives_are_deterministic_and_do_not_imply_physics(tmp_path: Path) -> None:
    """This one-term noncycle is only an archive fixture, never a physical result."""

    basis = OuterCechBasis(
        _scalar_context().components[(0, 0, "k0")],
        (0, 0, 0), (0, 0, 0), (0, 0), ((0,), (0,), (0,)),
    )
    value = SparseOuterCechCochain(((basis, Eisenstein(2, 1)),))
    path = tmp_path / "mathematical_archive_fixture.json"
    record = {"schema": "mathematical-archive-fixture", "physical_result": False}
    first = _write_witnesses(path, record, {"value": value, "zero": SparseOuterCechCochain()})
    archive = path.with_suffix(".cochains.json.gz").read_bytes()
    second = _write_witnesses(path, record, {"value": value, "zero": SparseOuterCechCochain()})
    assert first == second
    assert path.with_suffix(".cochains.json.gz").read_bytes() == archive
    loaded, witnesses = _read_witnesses(path, record["schema"], ("value", "zero"))
    assert loaded["physical_result"] is False
    assert _canonical_digest(loaded) == first["artifact_digest"]
    assert witnesses == {"value": value, "zero": SparseOuterCechCochain()}


def test_absent_explicit_witnesses_do_not_trigger_computation(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _read_witnesses(tmp_path / "missing.json", "mathematical-archive-fixture", ("value",))


def test_archive_corruption_is_rejected_before_cochain_reconstruction(tmp_path: Path) -> None:
    path = tmp_path / "mathematical_archive_fixture.json"
    _write_witnesses(path, {"schema": "mathematical-archive-fixture"}, {
        "zero": SparseOuterCechCochain(),
    })
    path.with_suffix(".cochains.json.gz").write_bytes(b"corrupt archive")
    with pytest.raises(ValueError, match="changed its exact content"):
        _read_witnesses(path, "mathematical-archive-fixture", ("zero",))


def test_a_rehashed_archive_still_requires_its_declared_witnesses(tmp_path: Path) -> None:
    path = tmp_path / "mathematical_archive_fixture.json"
    record = _write_witnesses(path, {"schema": "mathematical-archive-fixture"}, {
        "zero": SparseOuterCechCochain(),
    })
    archive_path = path.with_suffix(".cochains.json.gz")
    full = json.loads(gzip.decompress(archive_path.read_bytes()))
    full.pop("artifact_digest")
    full["cochains"] = {}
    full["artifact_digest"] = _canonical_digest(full)
    archive = gzip.compress(json.dumps(full).encode(), mtime=0)
    archive_path.write_bytes(archive)
    record.pop("artifact_digest")
    record["full_cochain_archive_sha256"] = hashlib.sha256(archive).hexdigest()
    record["full_cochain_payload_digest"] = full["artifact_digest"]
    record["artifact_digest"] = _canonical_digest(record)
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="declared full witnesses"):
        _read_witnesses(path, "mathematical-archive-fixture", ("zero",))


def test_first_actual_ff_matter_lift_replays_full_source_and_deck() -> None:
    """No direct F-F entry is assigned by this single necessary input."""

    lift = _verified_lift(0, 0, 1, GENERATED)
    assert lift.matter.character == (0, 0)
    assert lift.matter.seed_index == 0
    assert len(lift.constant.terms) == 378
    assert len(lift.constituent_correction.terms) == 27640
    assert len(lift.line_correction.terms) == 13326
    assert lift.checkpoint_digest == (
        "b2fd30e6b26c8140ff52c41604e161d7fe39e83fd5edbafd63a224e0489094ea"
    )
