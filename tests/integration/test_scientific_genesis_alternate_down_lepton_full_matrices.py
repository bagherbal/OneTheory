"""Guard complete remaining flavor assembly and exact constructor reuse.

Owns:
    All actual prerequisite paths, fail-closed execution boundaries, and
    all-entry regression against the established up and neutrino matrices,
    and exact fixed mixed rank floors in the remaining original bases.

Depends on:
    Pinned original scalar packets, the shared exact matrix constructor,
    and the conditional down/lepton orchestration.

Must not:
    Supply synthetic physical entries, certify uncomputed down/lepton ranks,
    choose an extension point, or infer physical normalization.

Phase 0:
    Research assembly guards; remaining coefficients still require full replay.
"""

from copy import deepcopy
from pathlib import Path

import pytest

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, determinant
from research.experiments.scientific_genesis import alternate_down_lepton_full_matrices as matrices
from research.experiments.scientific_genesis.alternate_up_full_matrix import _polynomial_record
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text as exact,
)
from research.experiments.scientific_genesis.mixed_schoen_outer_universal_cone import (
    _verified_payload,
)

PARENT_DIGESTS = {
    "up": "5dca3368f127ddf90eb8e263b403e6ca74f8857a3e505930194c51a67120884f",
    "neutrino": "40e5e45b6be980d49c432dbc707c496be56728731cd9b6f9d71d4cf08d8909eb",
}


def _actual_inputs(sector):
    """Read established actual inputs, checking each parent certificate's pins."""

    directory = matrices.coefficients.engine.GENERATED
    digest, parent = _verified_payload(
        directory / f"alternate_{sector}_full_holomorphic_matrix.json",
    )
    assert digest == PARENT_DIGESTS[sector]
    mixed_path = directory / f"alternate_{sector}_mixed_{'quotient_pairing' if sector == 'up'
                                                      else 'pairing'}.json"
    mixed_digest, packet = _verified_payload(mixed_path)
    if sector == "neutrino":
        assert mixed_digest == parent["prerequisite_artifact_digests"]["constant_mixed_pairing"]
    else:
        assert mixed_digest == parent["prerequisite_artifact_digests"]["mixed_pairing"]
    blocks = {}
    for parameter in (0, 1):
        if sector == "up":
            block_digest, block = _verified_payload(
                directory / f"alternate_up_ff_coefficient_a{parameter}.json",
            )
            assert block_digest == parent["prerequisite_artifact_digests"][
                f"ff_coefficient_a{parameter}"
            ]
        for row in (1, 2):
            for column in (1, 2):
                path = directory / f"alternate_{sector}_ff_a{parameter}_r{row}_c{column}.json"
                coefficient_digest, coefficient = _verified_payload(path)
                if sector == "neutrino":
                    assert coefficient_digest == parent["prerequisite_artifact_digests"][path.stem]
                else:
                    assert coefficient_digest == block["entry_artifact_digests"][2*(row-1)+column-1]
                assert coefficient["quotient_residue"] == str(
                    exact(coefficient["cover_residue"]) / 9,
                )
                blocks[parameter, row, column] = exact(coefficient["cover_residue"])
    return parent, packet["evaluated_entries"], blocks


@pytest.mark.parametrize("sector", ("up", "neutrino"))
def test_shared_constructor_reproduces_every_established_actual_matrix_entry(sector):
    """Extraction preserves all nine polynomials, determinants, and fixed minors."""

    parent, mixed, blocks = _actual_inputs(sector)
    matrix, determinant, minor = matrices.established.assemble_actual_flavor_matrix(mixed, blocks)
    assert [[_polynomial_record(value) for value in row] for row in matrix.rows] == (
        parent["matrix_entries"]
    )
    assert _polynomial_record(determinant) == parent["determinant"]
    assert _polynomial_record(minor) == parent["rank_two_minor"]


@pytest.mark.parametrize("sector,left_ratio,right_ratio", (
    (0, "-3/7-2/7*omega", "7*omega"),
    (1, "7", "2/7-1/7*omega"),
))
def test_remaining_actual_mixed_blocks_have_the_declared_exact_rank_floor(
    sector, left_ratio, right_ratio,
):
    """Scalar checks use the actual mixed packet, not the matrix constructor."""

    digest, packet = _verified_payload(matrices.coefficients.mixed.OUTPUT)
    assert digest == matrices.coefficients.MIXED_DIGEST
    assert packet["first_first_entry_zero_by_B_wedge_B"] is True
    entries = {(item["row"], item["column"]): exact(item["quotient_residue"])
               for item in packet["sectors"][sector]["evaluated_entries"]}
    minor = -entries[0, 1]*entries[1, 0]
    assert minor == exact("1/756+1/252*omega")
    assert not minor.is_zero()
    assert entries[2, 0] - exact(left_ratio)*entries[1, 0] == exact("0")
    assert entries[0, 2] - exact(right_ratio)*entries[0, 1] == exact("0")


@pytest.mark.parametrize("sector", (0, 1))
def test_remaining_rank_lifting_is_exactly_the_actual_mixed_null_channel(sector):
    """Four indeterminates prove an identity; they are not physical F-F inputs."""

    digest, packet = _verified_payload(matrices.coefficients.mixed.OUTPUT)
    assert digest == matrices.coefficients.MIXED_DIGEST
    mixed = {(item["row"], item["column"]): exact(item["quotient_residue"])
             for item in packet["sectors"][sector]["evaluated_entries"]}
    def constant(value):
        return Polynomial.constant(value, 4, scalar_type=Eisenstein)

    a11, a12, a21, a22 = (Polynomial.monomial(
        tuple(int(position == index) for position in range(4)), scalar_type=Eisenstein,
    ) for index in range(4))
    left, right = mixed[2, 0]/mixed[1, 0], mixed[0, 2]/mixed[0, 1]
    minor = -mixed[0, 1]*mixed[1, 0]
    abstract = (
        (Polynomial.zero(4, scalar_type=Eisenstein), constant(mixed[0, 1]), constant(mixed[0, 2])),
        (constant(mixed[1, 0]), a11, a12),
        (constant(mixed[2, 0]), a21, a22),
    )
    null_channel = a22 - a12.scale(left) - a21.scale(right) + a11.scale(left*right)
    assert determinant(abstract) == null_channel.scale(minor)
    assert len(null_channel.terms) == 4
    assert all(sum(powers) == 1 for powers, _ in null_channel.terms)


def test_actual_down_a0_block_has_a_nonzero_exact_determinant_coefficient():
    """Check the completed coefficient only; a1 and leptons stay unavailable."""

    pins = (
        "ab590cef3f36b64d7636c200f163a69cedaba3e878e8493f95d8695286b5ca6b",
        "c570612d6c3246000c70e03439a54ab8a950b2f9d6fa0ed29805e602316c0246",
        "abd2e360c41591ed88a24c08c43d0d385ab544e5377a80fda2914aa9cd56cca2",
        "471aaa5ce5c3b9e7b5e3d694b895711a2f3679f0919833ff6f5936b6c4a318bd",
    )
    digest, packet = _verified_payload(matrices.coefficients.mixed.OUTPUT)
    assert digest == matrices.coefficients.MIXED_DIGEST
    mixed = {(item["row"], item["column"]): exact(item["quotient_residue"])
             for item in packet["sectors"][0]["evaluated_entries"]}
    block = {}
    for index, (row, column) in enumerate((r, c) for r in (1, 2) for c in (1, 2)):
        coefficient_digest, item = _verified_payload(matrices.coefficients.entry_path(
            0, 0, row, column,
        ))
        assert coefficient_digest == pins[index]
        assert item["quotient_residue"] == str(exact(item["cover_residue"])/9)
        block[row, column] = exact(item["quotient_residue"])
    r1, r2, c1, c2 = (mixed[key] for key in ((0, 1), (0, 2), (1, 0), (2, 0)))
    coefficient = (-r1*c1*block[2, 2] + r1*c2*block[1, 2]
                   + r2*c1*block[2, 1] - r2*c2*block[1, 1])
    null = block[2, 2] - (c2/c1)*block[1, 2] - (r2/r1)*block[2, 1]
    null += (c2/c1)*(r2/r1)*block[1, 1]
    assert coefficient == -r1*c1*null == exact("1/42-2/21*omega")
    assert null == exact("-36-18*omega")
    assert not coefficient.is_zero()


@pytest.mark.parametrize("fault", ("missing", "extra", "bool_key", "inexact", "order", "bool_row"))
def test_shared_constructor_rejects_missing_or_retyped_actual_inputs(fault):
    """Corrupt copies of actual inputs cannot acquire hidden coefficient defaults."""

    _, mixed, blocks = _actual_inputs("neutrino")
    mixed = deepcopy(mixed)
    if fault == "missing":
        blocks.pop((0, 1, 1))
    elif fault == "extra":
        blocks[0, 1, 0] = blocks[0, 1, 1]
    elif fault == "bool_key":
        blocks[False, 1, 1] = blocks.pop((0, 1, 1))
    elif fault == "inexact":
        blocks[0, 1, 1] = str(blocks[0, 1, 1])
    elif fault == "order":
        mixed.reverse()
    else:
        mixed[0]["row"] = False
    with pytest.raises(ValueError, match="four ordered mixed and eight exact coefficients"):
        matrices.established.assemble_actual_flavor_matrix(mixed, blocks)


@pytest.mark.parametrize("workers", (-1, 0, 3, True, 1.0, None))
def test_complete_matrix_worker_gate_precedes_all_input_access(monkeypatch, workers):
    def forbidden_input(*args):
        raise AssertionError("invalid workers must not read source packets")

    monkeypatch.setattr(matrices, "required_sources", forbidden_input)
    with pytest.raises(ValueError, match="one or two workers"):
        matrices.write_full_matrices(workers=workers)


def test_complete_matrix_names_all_thirty_four_original_prerequisites():
    sources = matrices.required_sources()
    assert len(sources) == len(set(sources)) == 34
    assert sources[:16] == tuple(
        matrices.coefficients.entry_path(p, s, r, c)
        for p in (0, 1) for s in (0, 1) for r in (1, 2) for c in (1, 2)
    )
    assert sources[16:32] == tuple(
        matrices.coefficients._lift_source(p, s, side, family)[0]
        for p in (0, 1) for s in (0, 1) for side in (0, 1) for family in (1, 2)
    )
    assert sources[32:] == (matrices.coefficients.mixed.OUTPUT,
                           matrices.coefficients.mixed.down.OUTPUT)


@pytest.mark.parametrize("index", range(34))
@pytest.mark.parametrize("archive", (False, True))
def test_every_missing_literal_prerequisite_stops_before_replay(
    monkeypatch, tmp_path, index, archive,
):
    """Mock only file presence; no scalar, cochain, or physical result is supplied."""

    output = tmp_path / matrices.OUTPUT.name
    sources = matrices.required_sources(output.parent)
    missing = sources[index].with_suffix(".cochains.json.gz") if archive else sources[index]
    monkeypatch.setattr(Path, "is_file", lambda path: path != missing)

    def forbidden_replay(*args, **kwargs):
        raise AssertionError("incomplete sources must not reach metadata or scalar evaluation")

    monkeypatch.setattr(matrices.established, "_source_snapshot", forbidden_replay)
    monkeypatch.setattr(matrices, "_replay", forbidden_replay)
    with pytest.raises(FileNotFoundError, match="actual complete flavor prerequisite is missing"):
        matrices.write_full_matrices(output)
    assert not output.exists()


def test_reading_an_absent_complete_output_never_computes_a_missing_matrix(tmp_path, monkeypatch):
    def forbidden_calculation(*args, **kwargs):
        raise AssertionError("read-only missing output must not start a calculation")

    monkeypatch.setattr(matrices, "_replay", forbidden_calculation)
    monkeypatch.setattr(matrices, "_rank_parents", forbidden_calculation)
    with pytest.raises(FileNotFoundError):
        matrices.load_full_matrices(tmp_path / matrices.OUTPUT.name, expected_digest="0"*64)
