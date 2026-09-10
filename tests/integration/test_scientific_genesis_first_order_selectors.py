"""Test exact bounds on indexed first-order research inputs.

Owns:
    Regression gates that reject carrier directions and local-family indices
    outside the frozen source-derived bases before expensive reconstruction.

Depends on:
    The indexed matter, Higgs, and V2 determinant-pairing entry points.

Must not:
    Select an extension point, fabricate a local family, or evaluate a Yukawa.

Phase 0:
    Integration tests for the finite first-order input domain.
"""

from __future__ import annotations

import pytest

from research.experiments.scientific_genesis.mixed_schoen_higgs_leg_deformation import (
    higgs_leg_deformation,
)
from research.experiments.scientific_genesis.mixed_schoen_matter_leg_deformation import (
    matter_leg_deformation,
)
from research.experiments.scientific_genesis.mixed_schoen_v2_pluecker_chain_map import (
    local_v2_pluecker_pairing,
)


@pytest.mark.parametrize("parameter_index", [-1, 2])
def test_higgs_selector_rejects_unknown_parameter(parameter_index: int) -> None:
    """The Higgs leg accepts only the two certified extension directions."""

    with pytest.raises(ValueError, match="parameter index is unavailable"):
        higgs_leg_deformation(parameter_index)


@pytest.mark.parametrize(
    ("parameter_index", "row_index", "column_index"),
    [(2, 1, 1), (0, 0, 1), (0, 1, 3)],
)
def test_matter_selector_rejects_unknown_basis_input(
    parameter_index: int,
    row_index: int,
    column_index: int,
) -> None:
    """The matter leg cannot expand the finite parameter or family bases."""

    with pytest.raises(ValueError):
        matter_leg_deformation(parameter_index, row_index, column_index)


@pytest.mark.parametrize(("row_index", "column_index"), [(0, 1), (1, 3)])
def test_pluecker_selector_rejects_unknown_local_family(
    row_index: int,
    column_index: int,
) -> None:
    """The determinant pairing accepts only source-derived local classes."""

    with pytest.raises(ValueError, match="indices must be one or two"):
        local_v2_pluecker_pairing(row_index, column_index)
