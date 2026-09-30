"""Keep the universal holomorphic matrix unavailable until its real block exists.

Owns:
    The fail-closed prerequisite gate, undeclared-family rejection, and
    exact determinant of the computed a0 holomorphic slice.

Depends on:
    The research matrix assembler, fixed F-F index convention, and pytest.

Must not:
    Substitute a synthetic matrix, choose an extension point, or assign a
    physical mass from a holomorphic coupling.

Phase 0:
    The full result is only certified after the live carrier calculation and
    fresh archive replay have produced both coefficient blocks.
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
