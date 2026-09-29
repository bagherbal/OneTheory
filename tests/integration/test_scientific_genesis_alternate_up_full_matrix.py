"""Keep the universal holomorphic matrix unavailable until its real block exists.

Owns:
    The fail-closed prerequisite gate for both actual F-F coefficient
    archives and rejection of undeclared family labels.

Depends on:
    The research matrix assembler, fixed F-F index convention, and pytest.

Must not:
    Substitute a synthetic matrix, choose an extension point, or assign a
    physical mass from a holomorphic coupling.

Phase 0:
    The full result is only certified after the live carrier calculation and
    fresh archive replay have produced both coefficient blocks.
"""

from pathlib import Path

import pytest

from research.experiments.scientific_genesis.alternate_up_full_matrix import (
    _lift_path,
    write_full_up_matrix,
)


def test_missing_actual_coefficients_never_return_a_partial_matrix(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="complete F-F coefficient a0 is missing"):
        write_full_up_matrix(tmp_path / "holomorphic_matrix.json")


@pytest.mark.parametrize("side", (-1, 2, True))
def test_actual_matter_lift_has_only_two_declared_source_sides(
    side: int, tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="source side must be row or column"):
        _lift_path(0, side, 1, tmp_path)
