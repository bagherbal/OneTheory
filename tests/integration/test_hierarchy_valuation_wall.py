"""Check the exact stability-wall valuation audit of the frozen carrier.

Owns:
    Regression of the extension-degree charge pattern, independent determinant
    recomputation, near-split invariant-factor orders, and the exact slope wall.

Depends on:
    The research wall-valuation audit, completed holomorphic matrix artifacts,
    production Schoen geometry, and pytest.

Must not:
    Assign a hierarchy parameter, physical metric, mass, or observed value.

Phase 0:
    Regression checks for a research-only valuation theorem.
"""

import json

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.hierarchy_valuation.wall_valuation import (
    GENERATED,
    SECTORS,
    _det3,
    audit,
    charge_solution,
    sector_matrix,
    sector_valuation,
    stability_wall,
)
from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
    _parse_eisenstein_text,
)

SECTOR_NAMES = tuple(name for name, _, _ in SECTORS)


def _certified_determinant(name: str) -> dict[tuple[int, int], Eisenstein]:
    for sector, artifact, coupling in SECTORS:
        if sector != name:
            continue
        data = json.loads((GENERATED / artifact).read_text())
        if coupling is not None:
            data = next(m for m in data["matrices"] if tuple(m["coupling"]) == coupling)
        return {
            tuple(term["powers"]): _parse_eisenstein_text(term["coefficient"])
            for term in data["determinant"]
        }
    raise KeyError(name)


@pytest.mark.parametrize("name", SECTOR_NAMES)
def test_independent_cofactor_determinant_matches_certified_artifact(name: str) -> None:
    assert _det3(sector_matrix(name)) == _certified_determinant(name)


@pytest.mark.parametrize("name", SECTOR_NAMES)
def test_every_sector_is_one_anomalous_u1_charge_pattern(name: str) -> None:
    valuation = sector_valuation(name)
    assert valuation.degree_pattern == ((None, 0, 0), (0, 1, 1), (0, 1, 1))
    assert valuation.row_charges == (-1, 0, 0)
    assert valuation.column_charges == (-1, 0, 0)
    assert valuation.offset == 1


@pytest.mark.parametrize("name", SECTOR_NAMES)
def test_near_split_orders_are_two_unsuppressed_and_one_linear(name: str) -> None:
    valuation = sector_valuation(name)
    assert valuation.constant_minor_count > 0
    assert valuation.determinant_degree == 1
    assert valuation.singular_value_orders == (0, 0, 1)


def test_vanishing_e_e_entry_is_forced_not_assumed() -> None:
    # The E-E slot is predicted at degree -1, which no holomorphic entry can have.
    rows, cols, offset = charge_solution(((None, 0, 0), (0, 1, 1), (0, 1, 1)))
    assert rows[0] + cols[0] + offset == -1


def test_allowed_entry_that_vanishes_is_rejected() -> None:
    with pytest.raises(ValueError, match="holomorphically allowed entry vanishes"):
        charge_solution(((None, 0, 0), (0, 1, None), (0, 1, 1)))


def test_inconsistent_degree_pattern_is_rejected() -> None:
    with pytest.raises(ValueError, match="single U\\(1\\) charge pattern"):
        charge_solution(((None, 0, 0), (0, 1, 2), (0, 1, 1)))


def test_first_constituent_wall_is_the_factor_exchange_plane() -> None:
    wall = stability_wall()
    assert wall.factorization_verified
    assert wall.retained_degree == str(Rational(-432))


def test_audit_assigns_no_parameter_and_uses_no_observation() -> None:
    report = audit()
    assert not report.hierarchy_parameter_assigned
    assert not report.observational_inputs_used
    assert len(report.premises) == 3
