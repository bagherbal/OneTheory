"""Guard complete remaining flavor assembly and exact constructor reuse.

Owns:
    All actual prerequisite paths, fail-closed execution boundaries, and
    all-entry regression against the established up and neutrino matrices,
    exact source-to-position assembly checks for the remaining scalar packets,
    fixed mixed rank floors in the remaining original bases, and independent
    Fraction-pair Leibniz determinants of the archived scalar metadata.

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
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from re import fullmatch

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
ACTUAL_COEFFICIENT_DIGESTS = (
    "ab590cef3f36b64d7636c200f163a69cedaba3e878e8493f95d8695286b5ca6b",
    "c570612d6c3246000c70e03439a54ab8a950b2f9d6fa0ed29805e602316c0246",
    "abd2e360c41591ed88a24c08c43d0d385ab544e5377a80fda2914aa9cd56cca2",
    "471aaa5ce5c3b9e7b5e3d694b895711a2f3679f0919833ff6f5936b6c4a318bd",
    "cc169decddb441780b5558a46cfc08873b0877063ba073c134bfcf152e36a4a2",
    "483a57dc975323f2a689eda4a9d0eca564c277c9c412e5c9255d3375197c1eff",
    "8ae36d456eb8622f4621f6b334f701f780fbbe16bdf1ab3cb278951140bdc6a6",
    "5173a49b0460c88c35582b1194803e8d30f02cad850151737bb05ce090ddba58",
    "8ee8676a63a43fa0ac6c33a2647c2b5fd1355b3fafe0b5b1b57b1010af0c5ed9",
    "53aeb4763a0102ac808fdeb7b26ca0852b5e7a8fa9bb8dcb87b0e8595bc481ab",
    "ee64ef1b5529fec7f6fc578fc19fdd769bf7471aeaff743b4bc084b4b682d31c",
    "be715b5bc83368be3394e10c911dd618d7fccdc99c183962629b74115624b9e7",
    "0cb4a84f02e31ebefffbc0b69a64a78ef18c71a1609772ccf316f3ef96041882",
    "93d7e4037fa1b3f37f26d5d230b6c9ae9cf35c786092a85e3d1635057fdc41d4",
    "fb89c73981feb1696fb0583eee3aa51c581ee17f69cbe6cc1463b6db573d128c",
    "c302473b42759452ebac5001ccd8dca24fbb958d7162e07b768ed579c9a9280a",
)


def _fraction_pair(text):
    """Decode exact scalar strings without OneTheory's coefficient parser."""

    rational = r"[+-]?\d+(?:/\d+)?"
    if "omega" not in text:
        assert fullmatch(rational, text), text
        return Fraction(text), Fraction(0)
    match = fullmatch(rf"({rational})?([+-](?:\d+(?:/\d+)?)?)\*?omega", text)
    if match:
        constant, linear = match.groups()
        return Fraction(constant or 0), Fraction(
            linear + "1" if linear in ("+", "-") else linear,
        )
    match = fullmatch(r"([+-]?(?:\d+(?:/\d+)?)?)\*?omega", text)
    assert match, text
    linear = match[1]
    return Fraction(0), Fraction(linear + "1" if linear in ("", "+", "-") else linear)


def _independent_fraction_determinant(sector):
    """Use six permutation terms and omega^2=-1-omega outside the engine.

    The two formal parameters remain formal. Only the archived scalar
    metadata are checked here; no complete cochain replay is asserted.
    """

    zero = (Fraction(0), Fraction(0))

    def add(a, b):
        return a[0]+b[0], a[1]+b[1]

    def multiply(left, right):
        result = {}
        for e, (a, b) in left.items():
            for f, (c, d) in right.items():
                powers = tuple(x+y for x, y in zip(e, f, strict=True))
                # Reduction is independent of Eisenstein.__mul__.
                coefficient = (a*c-b*d, a*d+b*c-b*d)
                result[powers] = add(result.get(powers, zero), coefficient)
        return {e: c for e, c in result.items() if c != zero}

    digest, packet = _verified_payload(matrices.coefficients.mixed.OUTPUT)
    assert digest == matrices.coefficients.MIXED_DIGEST
    assert packet["first_first_entry_zero_by_B_wedge_B"] is True
    mixed = packet["sectors"][sector]["evaluated_entries"]
    assert [(entry["row"], entry["column"]) for entry in mixed] == [
        (0, 1), (0, 2), (1, 0), (2, 0),
    ]
    # The sole empty entry is justified by the actual certified B exterior relation.
    matrix = [[{} for _ in range(3)] for _ in range(3)]
    for entry in mixed:
        coefficient = _fraction_pair(entry["quotient_residue"])
        assert tuple(v/9 for v in _fraction_pair(entry["cover_residue"])) == coefficient
        matrix[entry["row"]][entry["column"]] = {(0, 0): coefficient}
    for index, (r, c) in enumerate((r, c) for r in (1, 2) for c in (1, 2)):
        for p, powers in ((0, (1, 0)), (1, (0, 1))):
            digest, entry = _verified_payload(matrices.coefficients.entry_path(p, sector, r, c))
            assert digest == ACTUAL_COEFFICIENT_DIGESTS[8*p+4*sector+index]
            assert (entry["parameter"], entry["sector"], entry["row"], entry["column"]) == (
                f"a{p}", sector, r, c,
            )
            coefficient = _fraction_pair(entry["quotient_residue"])
            assert tuple(v/9 for v in _fraction_pair(entry["cover_residue"])) == coefficient
            matrix[r][c][powers] = coefficient
    result = {}
    for perm in permutations(range(3)):
        parity = sum(perm[i] > perm[j] for i in range(3) for j in range(i+1, 3))
        term = {(0, 0): (Fraction((-1)**parity), Fraction(0))}
        for r, c in enumerate(perm):
            term = multiply(term, matrix[r][c])
        for powers, coefficient in term.items():
            result[powers] = add(result.get(powers, zero), coefficient)
    return {e: c for e, c in result.items() if c != zero}


@pytest.mark.parametrize("sector,expected", (
    (0, {(1, 0): (Fraction(1, 42), Fraction(-2, 21)),
         (0, 1): (Fraction(-1, 21), Fraction(-5, 84))}),
    (1, {(1, 0): (Fraction(-1, 84), Fraction(1, 21)),
         (0, 1): (Fraction(-1, 21), Fraction(-5, 84))}),
))
def test_archived_remaining_determinants_by_independent_fraction_leibniz(sector, expected):
    """Neither the four-term formula nor the exact engine computes this expectation."""

    assert _independent_fraction_determinant(sector) == expected


def test_archived_remaining_projective_walls_are_independent_over_fraction_pairs():
    """Prove distinct zeros without choosing a parameter or reading a future matrix."""

    down, lepton = (_independent_fraction_determinant(sector) for sector in (0, 1))
    a, b = down[1, 0]
    c, d = lepton[0, 1]
    first = (a*c-b*d, a*d+b*c-b*d)
    a, b = down[0, 1]
    c, d = lepton[1, 0]
    second = (a*c-b*d, a*d+b*c-b*d)
    assert first != second
    assert all(pair != (0, 0) for row in (down, lepton) for pair in row.values())


@pytest.mark.parametrize("sector", (0, 1))
def test_remaining_constructor_routes_every_actual_scalar_to_its_original_position(sector):
    """Check all nine polynomials without claiming completed witness replay.

    The expected entries are read independently from pinned actual sources.
    This checks assembly only; it does not create a complete output artifact
    or replace the mandatory constituent, product, and scalar replay gate.
    """

    digest, packet = _verified_payload(matrices.coefficients.mixed.OUTPUT)
    assert digest == matrices.coefficients.MIXED_DIGEST
    assert packet["first_first_entry_zero_by_B_wedge_B"] is True
    mixed = packet["sectors"][sector]["evaluated_entries"]
    assert [(entry["row"], entry["column"]) for entry in mixed] == [
        (0, 1), (0, 2), (1, 0), (2, 0),
    ]
    expected = {(entry["row"], entry["column"]): Polynomial.constant(
        exact(entry["quotient_residue"]), 2, scalar_type=Eisenstein,
    ) for entry in mixed}
    for entry in mixed:
        assert exact(entry["cover_residue"])/9 == exact(entry["quotient_residue"])
    expected[0, 0] = Polynomial.zero(2, scalar_type=Eisenstein)
    blocks = {}
    for index, (row, column) in enumerate((r, c) for r in (1, 2) for c in (1, 2)):
        terms = []
        for parameter, powers in ((0, (1, 0)), (1, (0, 1))):
            digest, entry = _verified_payload(matrices.coefficients.entry_path(
                parameter, sector, row, column,
            ))
            assert digest == ACTUAL_COEFFICIENT_DIGESTS[8*parameter + 4*sector + index]
            assert entry["schema"] == matrices.coefficients.SCHEMA
            assert (entry["parameter"], entry["sector"], entry["row"], entry["column"]) == (
                f"a{parameter}", sector, row, column,
            )
            cover, quotient = exact(entry["cover_residue"]), exact(entry["quotient_residue"])
            assert cover/9 == quotient
            blocks[parameter, row, column] = cover
            terms.append((powers, quotient))
        expected[row, column] = Polynomial(terms, variable_count=2, scalar_type=Eisenstein)
    actual, det, minor = matrices.established.assemble_actual_flavor_matrix(mixed, blocks)
    assert actual.rows == tuple(tuple(expected[row, column] for column in range(3))
                                for row in range(3))
    # Expand the actual sparse matrix independently of the determinant engine.
    r1, r2, c1, c2 = (expected[key] for key in ((0, 1), (0, 2), (1, 0), (2, 0)))
    separate = (-r1*c1*expected[2, 2] + r1*c2*expected[1, 2]
                + r2*c1*expected[2, 1] - r2*c2*expected[1, 1])
    assert det == separate
    assert minor == -r1*c1


def _actual_remaining_rank_coefficients(sector):
    """Independently expand actual scalar metadata, not the assembler output.

    This arithmetic check does not replay the complete matter or products.
    The live full-matrix gate must still validate every literal witness.
    """

    digest, packet = _verified_payload(matrices.coefficients.mixed.OUTPUT)
    assert digest == matrices.coefficients.MIXED_DIGEST
    mixed = {(item["row"], item["column"]): exact(item["quotient_residue"])
             for item in packet["sectors"][sector]["evaluated_entries"]}
    r1, r2, c1, c2 = (mixed[key] for key in ((0, 1), (0, 2), (1, 0), (2, 0)))
    results = []
    for parameter in (0, 1):
        block = {}
        for index, (row, column) in enumerate((r, c) for r in (1, 2) for c in (1, 2)):
            digest, item = _verified_payload(matrices.coefficients.entry_path(
                parameter, sector, row, column,
            ))
            assert digest == ACTUAL_COEFFICIENT_DIGESTS[8*parameter + 4*sector + index]
            assert item["schema"] == matrices.coefficients.SCHEMA
            assert (item["parameter"], item["sector"], item["row"], item["column"]) == (
                f"a{parameter}", sector, row, column,
            )
            assert item["quotient_residue"] == str(exact(item["cover_residue"])/9)
            block[row, column] = exact(item["quotient_residue"])
        expanded = (-r1*c1*block[2, 2] + r1*c2*block[1, 2]
                    + r2*c1*block[2, 1] - r2*c2*block[1, 1])
        null = (block[2, 2] - (c2/c1)*block[1, 2] - (r2/r1)*block[2, 1]
                + (c2/c1)*(r2/r1)*block[1, 1])
        assert expanded == -r1*c1*null
        results.append((expanded, null))
    return tuple(results)


@pytest.mark.parametrize("sector,parameter,coefficient,null", (
    (0, 0, "1/42-2/21*omega", "-36-18*omega"),
    (0, 1, "-1/21-5/84*omega", "-9+9*omega"),
    (1, 0, "-1/84+1/21*omega", "18+9*omega"),
    (1, 1, "-1/21-5/84*omega", "-9+9*omega"),
))
def test_all_remaining_actual_rank_coefficients_match_separate_scalar_expansion(
    sector, parameter, coefficient, null,
):
    assert _actual_remaining_rank_coefficients(sector)[parameter] == (
        exact(coefficient), exact(null),
    )


def test_actual_four_sector_rank_forms_have_distinct_projective_exceptions():
    """Prove the exact arithmetic locus, not an uncompleted physical matrix."""

    down = tuple(item[0] for item in _actual_remaining_rank_coefficients(0))
    lepton = tuple(item[0] for item in _actual_remaining_rank_coefficients(1))
    assert down[0] == -2*lepton[0]
    assert down[1] == lepton[1]
    assert all(not coefficient.is_zero() for row in (down, lepton) for coefficient in row)
    assert not (down[0]*lepton[1] - down[1]*lepton[0]).is_zero()
    # The established up and neutrino zero sets are the two coordinate axes.
    for sector, powers in (("up", (0, 1)), ("neutrino", (1, 0))):
        path = matrices.coefficients.engine.GENERATED / (
            f"alternate_{sector}_full_holomorphic_matrix.json"
        )
        digest, parent = _verified_payload(path)
        assert digest == PARENT_DIGESTS[sector]
        assert len(parent["determinant"]) == 1
        assert tuple(parent["determinant"][0]["powers"]) == powers
        assert not exact(parent["determinant"][0]["coefficient"]).is_zero()
    a0, a1 = (Polynomial.monomial(powers, scalar_type=Eisenstein)
              for powers in ((1, 0), (0, 1)))
    down_form = a0.scale(down[0]) + a1.scale(down[1])
    lepton_form = a0.scale(lepton[0]) + a1.scale(lepton[1])
    common_open = a0*a1*down_form*lepton_form
    assert not common_open.is_zero()
    assert all(sum(powers) == 4 for powers, _ in common_open.terms)


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


def test_actual_rank_parent_handoff_retains_both_verified_digest_headers():
    """Final serialization needs both actual hashes, not unsigned parent bodies."""

    up, neutrino = matrices._rank_parents()
    up_digest, unsigned_up = _verified_payload(matrices.UP_OUTPUT)
    assert up_digest == PARENT_DIGESTS["up"]
    assert up == {"artifact_digest": up_digest, **unsigned_up}
    assert [up["artifact_digest"], neutrino["artifact_digest"]] == [
        PARENT_DIGESTS["up"], PARENT_DIGESTS["neutrino"],
    ]


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
    """Check the completed coefficient, not the still-unreplayed full matrices."""

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
