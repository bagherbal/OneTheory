"""Check the exact universal matrix against its actual carrier source blocks.

Owns:
    Fail-closed prerequisite gates, source-block reconstruction, and an
    independent exact determinant expansion in the fixed quotient frame.

Depends on:
    The research matrix assembler, fixed F-F index convention, and pytest.

Must not:
    Substitute a synthetic matrix, choose an extension point, or assign a
    physical mass from a holomorphic coupling.

Phase 0:
    Regression checks for the research-only holomorphic matrix certificate.
"""

import json
import shutil
from pathlib import Path

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.scientific_genesis.alternate_up_ff_entries import GENERATED
from research.experiments.scientific_genesis.alternate_up_full_matrix import (
    _lift_path,
    write_full_up_matrix,
)
from research.experiments.scientific_genesis.alternate_up_mixed_quotient_pairing import (
    OUTPUT as MIXED,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text,
)


def test_missing_actual_coefficients_never_return_a_partial_matrix(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="complete F-F coefficient a0 is missing"):
        write_full_up_matrix(tmp_path / "holomorphic_matrix.json")


def test_computed_a0_block_cannot_stand_in_for_missing_a1_block(tmp_path: Path) -> None:
    shutil.copyfile(
        GENERATED / "alternate_up_ff_coefficient_a0.json",
        tmp_path / "alternate_up_ff_coefficient_a0.json",
    )
    with pytest.raises(FileNotFoundError, match="complete F-F coefficient a1 is missing"):
        write_full_up_matrix(tmp_path / "holomorphic_matrix.json")


@pytest.mark.parametrize("side", (-1, 2, True))
def test_actual_matter_lift_has_only_two_declared_source_sides(
    side: int, tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="source side must be row or column"):
        _lift_path(0, side, 1, tmp_path)


def test_actual_a0_slice_has_exact_rank_two_determinant() -> None:
    """The complete a0 block obeys the independent mixed-entry determinant identity."""

    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    block = json.loads((GENERATED / "alternate_up_ff_coefficient_a0.json").read_text(
        encoding="utf-8",
    ))
    row = {item["column"]: _parse_eisenstein_text(item["cover_residue"])
           for item in mixed["evaluated_entries"] if item["row"] == 0}
    column = {item["row"]: _parse_eisenstein_text(item["cover_residue"])
              for item in mixed["evaluated_entries"] if item["column"] == 0}
    a, b = (_parse_eisenstein_text(value) for value in block["cover_block"][0])
    c, d = (_parse_eisenstein_text(value) for value in block["cover_block"][1])
    determinant = -row[1] * column[1] * d + row[1] * column[2] * b
    determinant += row[2] * column[1] * c - row[2] * column[2] * a
    assert row[1] * column[1] != 0
    assert determinant == Eisenstein(0)
    assert block["complete_null_cover_residue"] == "0"
    assert block["complete_holomorphic_up_matrix_available"] is False


def test_actual_a1_slice_has_nonzero_exact_determinant() -> None:
    """A nonzero formal determinant coefficient is not a physical mass prediction."""

    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    block = json.loads((GENERATED / "alternate_up_ff_coefficient_a1.json").read_text(
        encoding="utf-8",
    ))
    row = {item["column"]: _parse_eisenstein_text(item["cover_residue"])
           for item in mixed["evaluated_entries"] if item["row"] == 0}
    column = {item["row"]: _parse_eisenstein_text(item["cover_residue"])
              for item in mixed["evaluated_entries"] if item["column"] == 0}
    a, b = (_parse_eisenstein_text(value) for value in block["cover_block"][0])
    c, d = (_parse_eisenstein_text(value) for value in block["cover_block"][1])
    determinant = -row[1] * column[1] * d + row[1] * column[2] * b
    determinant += row[2] * column[1] * c - row[2] * column[2] * a
    null = _parse_eisenstein_text(block["complete_null_cover_residue"])
    assert null != Eisenstein(0)
    assert determinant == -row[1] * column[1] * null
    assert determinant == Eisenstein(Rational(-2187, 98), Rational(-28431, 196))
    assert block["complete_holomorphic_up_matrix_available"] is False


def test_complete_holomorphic_matrix_reconstructs_from_exact_source_blocks() -> None:
    """The archived matrix agrees with a separate scalar-level expansion."""

    path = GENERATED / "alternate_up_full_holomorphic_matrix.json"
    matrix = json.loads(path.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    blocks = [json.loads((GENERATED / f"alternate_up_ff_coefficient_a{i}.json")
                         .read_text(encoding="utf-8")) for i in (0, 1)]
    assert matrix["schema"] == "alternate-up-full-holomorphic-matrix-v1"
    assert matrix["artifact_digest"] == (
        "5dca3368f127ddf90eb8e263b403e6ca74f8857a3e505930194c51a67120884f"
    )
    assert matrix["basis_order"] == mixed["basis_order"]
    assert matrix["outer_parameter_basis"] == ["a0", "a1"]
    assert matrix["cover_to_quotient_trace_factor"] == "1/9"
    assert matrix["scalar_order"] == "Higgs first in the fixed quotient volume frame"
    assert matrix["prerequisite_artifact_digests"] == {
        "ff_coefficient_a0": blocks[0]["artifact_digest"],
        "ff_coefficient_a1": blocks[1]["artifact_digest"],
        "mixed_pairing": mixed["artifact_digest"],
    }

    def terms(record: list[dict[str, object]]) -> dict[tuple[int, int], Eisenstein]:
        result: dict[tuple[int, int], Eisenstein] = {}
        for item in record:
            powers = item["powers"]
            coefficient = item["coefficient"]
            assert isinstance(powers, list) and len(powers) == 2
            assert isinstance(coefficient, str)
            result[tuple(powers)] = _parse_eisenstein_text(coefficient)
        return result

    expected: list[list[dict[tuple[int, int], Eisenstein]]] = [
        [{}, {}, {}] for _ in range(3)
    ]
    for item in mixed["evaluated_entries"]:
        expected[item["row"]][item["column"]] = {
            (0, 0): _parse_eisenstein_text(item["cover_residue"]) / 9,
        }
    for row in (1, 2):
        for column in (1, 2):
            expected[row][column] = {
                (1, 0): _parse_eisenstein_text(blocks[0]["cover_block"][row - 1][column - 1]) / 9,
                (0, 1): _parse_eisenstein_text(blocks[1]["cover_block"][row - 1][column - 1]) / 9,
            }
    actual = [[terms(entry) for entry in row] for row in matrix["matrix_entries"]]
    assert actual == expected
    assert all(matrix["matrix_entries"][row][column] for row in (1, 2)
               for column in (1, 2))

    row1, row2 = expected[0][1][0, 0], expected[0][2][0, 0]
    col1, col2 = expected[1][0][0, 0], expected[2][0][0, 0]
    determinant_coefficients = {}
    for powers in ((1, 0), (0, 1)):
        determinant_coefficients[powers] = (
            -row1 * col1 * expected[2][2][powers]
            + row1 * col2 * expected[1][2][powers]
            + row2 * col1 * expected[2][1][powers]
            - row2 * col2 * expected[1][1][powers]
        )
    assert determinant_coefficients == {
        (1, 0): Eisenstein(0),
        (0, 1): Eisenstein(Rational(-3, 98), Rational(-39, 196)),
    }
    assert terms(matrix["determinant"]) == {(0, 1): determinant_coefficients[0, 1]}
    assert terms(matrix["rank_two_minor"]) == {
        (0, 0): Eisenstein(0, Rational(-1, 36)),
    }
    null = {powers: _parse_eisenstein_text(blocks[i]["complete_null_cover_residue"]) / 9
            for i, powers in enumerate(((1, 0), (0, 1)))}
    assert terms(matrix["null_contraction"]) == {
        (0, 1): Eisenstein(Rational(297, 49), Rational(-54, 49)),
    }
    assert null[(1, 0)] == Eisenstein(0)
    assert null[(0, 1)] == terms(matrix["null_contraction"])[0, 1]
    assert matrix["all_nine_entries_derived_from_actual_carrier"] is True
    assert matrix["holomorphic_matrix_available"] is True
    assert all(matrix[key] is False for key in (
        "physical_yukawa_matrix_available", "canonical_matter_metrics_available",
        "common_vacuum_stabilized", "extension_point_selected", "observational_inputs_used",
    ))
