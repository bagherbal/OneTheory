"""Guard actual remaining matter execution and the reused full lift checker.

Owns:
    Source identity, explicit index/worker boundaries, absent-input rejection,
    and actual neutrino regressions of the extracted common replay algorithm.

Depends on:
    Pinned original constituent witnesses and full archived neutrino corrections.

Must not:
    Insert missing corrections, treat test controls as physical inputs, or
    infer a complete flavor matrix from constituent or corrected matter classes.

Phase 0:
    Conditional research regression; new correction certificates require replay.
"""

import json

import pytest

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
)
from research.experiments.scientific_genesis import alternate_remaining_flavor_matter_lifts as lifts
from research.experiments.scientific_genesis.alternate_neutrino_full_matrix import _verified_lift
from research.experiments.scientific_genesis.mixed_schoen_matter_representatives import (
    _cochain_digest,
)

D0_DIGEST = "1d4a931761d341544ee256e0d1550be434bde41ac3d0a51588b02540d02b6d29"


def test_remaining_lift_inputs_are_the_four_original_archived_classes() -> None:
    classes, parents = lifts._inputs()
    record, witnesses = lifts.constituents.load_remaining_flavor_matter(
        expected_digest=lifts.MATTER_DIGEST,
    )
    assert set(classes) == {(0, 1), (0, 2), (1, 1), (1, 2)}
    assert [matter.character for matter in classes.values()] == [(1, 1)]*2 + [(2, 0)]*2
    assert [matter.seed_index for matter in classes.values()] == [2, 4, 0, 5]
    assert parents["actual_remaining_matter"] == lifts.MATTER_DIGEST
    for (sector, family), matter in classes.items():
        full = witnesses[f"second_sector{sector}_family{family}"]
        assert matter.full_cochain == full
        assert _cochain_digest((full,)) == record["second_constituent_classes"][
            sector*2 + family-1
        ]["full_digest"]


@pytest.mark.parametrize("parameter,sector,family", (
    (-1, 0, 1), (2, 0, 1), (True, 0, 1), (1.0, 0, 1),
    (0, -1, 1), (0, 2, 1), (0, True, 1), (0, 1.0, 1),
    (0, 0, 0), (0, 0, 3), (0, 0, True), (0, 0, 1.0),
))
def test_remaining_matter_indices_cannot_relabel_an_original_basis(
    parameter, sector, family,
) -> None:
    with pytest.raises(ValueError):
        lifts.lift_path(parameter, sector, family)


@pytest.mark.parametrize("workers", (-1, 0, 3, True, 1.0, None))
def test_remaining_execution_rejects_undeclared_workers_before_input_or_solver(
    monkeypatch, workers,
) -> None:
    def forbidden_inputs():
        raise AssertionError("invalid execution must fail before physical input access")

    monkeypatch.setattr(lifts, "_inputs", forbidden_inputs)
    with pytest.raises(ValueError, match="exactly one or two workers"):
        lifts.write_matter_lifts(0, workers=workers)


def test_remaining_absent_checkpoint_has_no_solver_or_replay_fallback(
    tmp_path, monkeypatch,
) -> None:
    def forbidden_calculation(*args, **kwargs):
        raise AssertionError("missing checkpoint must not start a physical calculation")

    monkeypatch.setattr(lifts, "_coefficient_job", forbidden_calculation)
    monkeypatch.setattr(lifts.engine, "checked_quotient_matter_lift", forbidden_calculation)
    with pytest.raises(FileNotFoundError):
        lifts.replay_matter_lift(0, 0, 1, expected_digest="0"*64, directory=tmp_path)


@pytest.mark.parametrize("parameter,digest", (
    (0, "ffc2ff3bdab420bfc9b16ffd1892aa4b84c2896808f976a09ffbca604d6a1379"),
    (1, "d20d9d68689a66e769a4c637efc8abb365fcb4021990dc021126302e8824004d"),
))
def test_common_checker_keeps_actual_neutrino_equations_and_pushouts(parameter, digest) -> None:
    """The shared checker retains the previously verified actual witnesses."""

    actual = _verified_lift(parameter, 0, 1, lifts.engine.GENERATED)
    assert actual.checkpoint_digest == digest
    assert actual.matter.character == (2, 1)
    assert actual.matter.seed_index == 2
    assert len(actual.constant.terms) == 378
    assert len(actual.constituent_correction.terms) == (27001, 24016)[parameter]
    assert len(actual.line_correction.terms) == (13071, 11397)[parameter]


@pytest.mark.parametrize("parameter,sector,family,seed,e_terms,b_terms,digest", (
    pytest.param(0, 0, 1, 2, 27001, 13071, D0_DIGEST, id="a0-d1"),
    pytest.param(0, 0, 2, 4, 26682, 12855,
                 "3b508c5e6b9c24d5eb433b9cf187d06c767fe13d5ec7d5afd977a9b8d4afb1c4", id="a0-d2"),
    pytest.param(0, 1, 1, 0, 27616, 13302,
                 "8b7644c50e4ea0e2d4ff89ba35c111d0c5611599f63e289fac506c58b76202a7", id="a0-e1"),
    pytest.param(0, 1, 2, 5, 26779, 12708,
                 "1683484cb1a51168f7c3506adf38a831fad65e87485906fa2873501544e3c631", id="a0-e2"),
    pytest.param(1, 0, 1, 2, 24016, 11397,
                 "eb3f71dec8372883e3b132fc877e2870c271a5d58628f2941c59b059e2a983da", id="a1-d1"),
    pytest.param(1, 0, 2, 4, 23782, 11163,
                 "09aaa371e465124fd344fb3a4fc421d51d1164fbf7e8330a45fcbffd31df9b52", id="a1-d2"),
    pytest.param(1, 1, 1, 0, 25216, 11973,
                 "572637f5986124caece4159531611e592e6177f9166b1d2806f048ed65e91c86", id="a1-e1"),
    pytest.param(1, 1, 2, 5, 23868, 11310,
                 "064e7fd324f2ba23dff2a51dddd7969397b083de6061ba338dc2301218c5ad44", id="a1-e2"),
))
def test_actual_remaining_corrections_replay_full_original_equations_and_atlas(
    parameter, sector, family, seed, e_terms, b_terms, digest,
) -> None:
    """Each new actual correction is verified without rerunning a producer solve."""

    actual = lifts.replay_matter_lift(parameter, sector, family, expected_digest=digest)
    assert actual.checkpoint_digest == digest
    assert actual.matter.character == ((1, 1), (2, 0))[sector]
    assert actual.matter.seed_index == seed
    assert len(actual.constant.terms) == 378
    assert len(actual.constituent_correction.terms) == e_terms
    assert len(actual.line_correction.terms) == b_terms


@pytest.mark.parametrize("field,value", (
    ("character", [2, 1]), ("sector_label", "nu^c"), ("seed_index", 4),
    ("outer_parameter_basis", ["a1", "a0"]), ("yukawa_entries_assigned", True),
    ("physical_yukawas_available", True), ("extension_point_selected", True),
))
def test_remaining_rehashed_correction_cannot_change_routing_or_scope(
    tmp_path, field, value,
) -> None:
    path = lifts.lift_path(0, 0, 1)
    record = json.loads(path.read_text())
    record.pop("artifact_digest")
    record[field] = value
    record["artifact_digest"] = _canonical_digest(record)
    altered = tmp_path / path.name
    altered.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="actual input, basis, or scope"):
        lifts.load_matter_lift(
            0, 0, 1, expected_digest=record["artifact_digest"], directory=tmp_path,
        )
