"""Attack the explicit witness boundaries of the actual F-F evaluator.

Owns:
    Fixed-index validation, deterministic exact witness serialization,
    missing-input rejection, content-addressed corruption checks, and fresh
    replay of both coefficientwise four-lift carrier matter blocks.

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


@pytest.mark.parametrize(
    "parameter,side,family,character,seed,correction_terms,line_terms,digest",
    (
        pytest.param(0, 0, 1, (0, 0), 0, 27640, 13326,
                     "b2fd30e6b26c8140ff52c41604e161d7fe39e83fd5edbafd63a224e0489094ea",
                     id="a0-row-seed0"),
        pytest.param(0, 0, 2, (0, 0), 5, 26779, 12708,
                     "d76441a381f99bee8419ce380a06e1786c7d8eb4347543b2535b96f35df7673d",
                     id="a0-row-seed5"),
        pytest.param(0, 1, 1, (1, 0), 0, 27564, 13278,
                     "d6ca93a2ffb79b652a709fe17cb275b1a9032b85d394a816b5348e23b51ef303",
                     id="a0-column-seed0"),
        pytest.param(0, 1, 2, (1, 0), 5, 26779, 12708,
                     "08871357a32bcfef583b2ebdb897817a9ce2cb4a49873444039a936e5cb69a69",
                     id="a0-column-seed5"),
        pytest.param(1, 0, 1, (0, 0), 0, 25244, 11961,
                     "77f04729847dc58ec78314fc1c6fb92017c5a999475dd7047e6f50ee2b837526",
                     id="a1-row-seed0"),
        pytest.param(1, 0, 2, (0, 0), 5, 23868, 11310,
                     "b32e6cc80c8492e01ffd896c2d77edb5e74a0967a4c962daf0263e64a84c5d03",
                     id="a1-row-seed5"),
        pytest.param(1, 1, 1, (1, 0), 0, 25220, 11973,
                     "fe0abbfd3110e15dfc6a8bd02ae5c8e54aabc881c5dfc33668cc3080d5481bd4",
                     id="a1-column-seed0"),
        pytest.param(1, 1, 2, (1, 0), 5, 23868, 11310,
                     "76c8051802c5be7be5a56edbba44ac62978a2501391bb734ee14348d4936e7df",
                     id="a1-column-seed5"),
    ),
)
def test_actual_ff_matter_lifts_replay_full_source_and_deck(
    parameter: int, side: int, family: int, character: tuple[int, int], seed: int,
    correction_terms: int, line_terms: int, digest: str,
) -> None:
    """Four necessary inputs do not themselves assign a direct F-F entry."""

    lift = _verified_lift(parameter, side, family, GENERATED)
    assert lift.matter.character == character
    assert lift.matter.seed_index == seed
    assert len(lift.constant.terms) == 378
    assert len(lift.constituent_correction.terms) == correction_terms
    assert len(lift.line_correction.terms) == line_terms
    assert lift.checkpoint_digest == digest
