"""Test the all-orders holomorphic up-type no-go certificate.

Owns:
    Regression gates for exterior-filtration truncation, complete universal
    matrix vanishing, and the scoped transition away from the up-type branch.

Depends on:
    The content-addressed up-type no-go artifact and executable degree ledger.

Must not:
    Generalize the no-go to other sectors, select a carrier point, or infer a
    physical Yukawa statement from holomorphic vanishing.

Phase 0:
    Integration tests for the frozen carrier's up-type branch theorem.
"""

from __future__ import annotations

import json

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis.mixed_schoen_first_order_matrix import (
    filtration_allowed_orders,
)
from research.experiments.scientific_genesis.mixed_schoen_up_yukawa_no_go import (
    OUTPUT,
)


def _payload() -> dict[str, object]:
    """Load the immutable no-go artifact after checking its exact digest."""

    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest")
    assert digest == _canonical_digest(payload)
    return payload


def test_exterior_filtration_truncates_after_first_order() -> None:
    """Only tree off-diagonal and first-order lower-block slots survive typing."""

    payload = _payload()
    expected = [
        {"row": row, "column": column, "orders": list(filtration_allowed_orders(row, column))}
        for row in range(3)
        for column in range(3)
    ]

    assert payload["allowed_parameter_orders_by_slot"] == expected
    assert expected == [
        {"row": 0, "column": 0, "orders": []},
        {"row": 0, "column": 1, "orders": [0]},
        {"row": 0, "column": 2, "orders": [0]},
        {"row": 1, "column": 0, "orders": [0]},
        {"row": 1, "column": 1, "orders": [1]},
        {"row": 1, "column": 2, "orders": [1]},
        {"row": 2, "column": 0, "orders": [0]},
        {"row": 2, "column": 1, "orders": [1]},
        {"row": 2, "column": 2, "orders": [1]},
    ]
    assert payload["maximum_allowed_parameter_order"] == 1
    assert payload["parameter_orders_two_and_higher_structurally_zero"] is True
    assert payload["f5_and_higher_contributions_structurally_zero"] is True


def test_complete_universal_up_matrix_is_exactly_zero() -> None:
    """The complete branch matrix has rank zero without selecting a parameter."""

    payload = _payload()
    zero = [["0", "0", "0"]] * 3

    assert payload["tree_matrix"] == zero
    assert payload["first_order_coefficient_matrices"] == [zero, zero]
    assert payload["complete_universal_holomorphic_up_matrix"] == zero
    assert payload["complete_universal_holomorphic_up_rank"] == 0
    assert payload["complete_holomorphic_up_matrix_available"] is True
    assert payload["nontrivial_holomorphic_up_matrix_available"] is False
    assert payload["declared_up_branch_can_reach_rank_three"] is False
    assert payload["exact"] is True
    assert payload["classification"] == "SCOPED_HOLOMORPHIC_UP_NO_GO"
    assert payload["extension_point_selected"] is False
    assert payload["observational_inputs_used"] is False
