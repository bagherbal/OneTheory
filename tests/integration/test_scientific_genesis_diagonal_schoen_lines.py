"""Test the exact diagonal complete-intersection Schoen line engine.

Owns:
    Equivalence regressions between the common-base and diagonal fiber-product
    presentations at the exact line-cohomology level.

Depends on:
    The two research-only sparse Schoen line engines.

Must not:
    Treat line equivalence as a bundle lift or a physical Higgs calculation.

Phase 0:
    Exact line-level diagonal synchronization is tested.
"""

from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_line_bundle,
)
from research.experiments.scientific_genesis.diagonal_schoen_lines import (
    diagonal_schoen_line_bundle,
)


def _common_dimensions(degrees: tuple[int, int, int]) -> tuple[int, int, int, int]:
    line = sparse_line_bundle(*degrees)
    return tuple(
        line.space(degree).dimension
        - line.differential(degree - 1).rank()
        - line.differential(degree).rank()
        for degree in range(4)
    )  # type: ignore[return-value]


def test_diagonal_presentation_reproduces_exact_schoen_line_cohomology() -> None:
    """The diagonal and common-base complete intersections agree exactly."""

    for degrees in ((0, 0, 0), (0, 0, -1), (-3, -4, 2)):
        diagonal = diagonal_schoen_line_bundle(*degrees)

        assert diagonal.squared_zero
        assert diagonal.geometric_dimensions == _common_dimensions(degrees)
        assert all(
            diagonal.cohomology_dimension(degree) == 0
            for degree in (-3, -2, -1, 4, 5, 6)
        )


def test_diagonal_boundary_case_preserves_exact_euler_characteristic() -> None:
    """The four-factor model retains the top boundary map and Euler value."""

    line = diagonal_schoen_line_bundle(-3, -4, 2)

    assert line.geometric_dimensions == (0, 0, 72, 3)
    assert sum(
        (-1) ** degree * dimension
        for degree, dimension in enumerate(line.geometric_dimensions)
    ) == 69
