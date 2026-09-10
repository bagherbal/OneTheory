"""Prove exact holomorphic up-type vanishing on the frozen carrier branch.

Owns:
    The finite exterior-filtration truncation theorem combining the complete
    tree and first-order matrices into the full universal up-type result.

Depends on:
    Exact parameter-linear matter lifts, the complete tree matrix, the complete
    first-order matrix, and rank-two constituent exterior degrees.

Must not:
    Extend the theorem to another flavor sector or carrier branch, select a
    projective parameter, infer physical couplings, or import observations.

Phase 0:
    Research-only branch-wide holomorphic up-type no-go certificate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_first_order_matrix import (
    OUTPUT as FIRST_ORDER_ARTIFACT,
)
from .mixed_schoen_first_order_matrix import filtration_allowed_orders
from .mixed_schoen_universal_matter_lifts import (
    OUTPUT as UNIVERSAL_MATTER_ARTIFACT,
)
from .mixed_schoen_yukawa_trace import OUTPUT as TREE_MATRIX_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_up_yukawa_no_go.json"
ZERO_MATRIX = (("0", "0", "0"),) * 3


def _verified_payload(path: Path, gate: str) -> tuple[str, dict[str, object]]:
    """Load one prerequisite only after its digest and exact gate pass."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest, payload


@dataclass(frozen=True, slots=True)
class UniversalUpYukawaNoGo:
    """Finite proof that the universal up matrix vanishes to every order."""

    tree_artifact_digest: str
    matter_artifact_digest: str
    first_order_artifact_digest: str
    allowed_orders: tuple[tuple[int, int, tuple[int, ...]], ...]
    tree_matrix: tuple[tuple[str, ...], ...]
    first_order_matrices: tuple[tuple[tuple[str, ...], ...], ...]

    @property
    def maximum_allowed_order(self) -> int:
        """Return the largest exterior-compatible parameter order."""

        return max(
            (
                order
                for _row, _column, orders in self.allowed_orders
                for order in orders
            ),
            default=-1,
        )

    @property
    def exact(self) -> bool:
        """Return whether truncation and every retained coefficient are zero."""

        return (
            self.allowed_orders
            == tuple(
                (row, column, filtration_allowed_orders(row, column))
                for row in range(3)
                for column in range(3)
            )
            and self.maximum_allowed_order == 1
            and self.tree_matrix == ZERO_MATRIX
            and self.first_order_matrices == (ZERO_MATRIX, ZERO_MATRIX)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the finite all-orders truncation and scoped conclusion."""

        return {
            "prerequisite_artifact_digests": {
                "tree_matrix": self.tree_artifact_digest,
                "universal_matter_lifts": self.matter_artifact_digest,
                "first_order_matrix": self.first_order_artifact_digest,
            },
            "constituent_ranks": {"V1": 2, "V2": 2},
            "triangular_extension_action": "V2 -> V1",
            "matter_representative_orders": {
                "constant_family": {"0": [1, 0]},
                "lifted_families": {"0": [0, 1], "1": [1, 0]},
            },
            "higgs_representative_orders": {
                "0": [1, 1],
                "1": [2, 0],
            },
            "determinant_target_bidegree": [2, 2],
            "allowed_parameter_orders_by_slot": [
                {"row": row, "column": column, "orders": list(orders)}
                for row, column, orders in self.allowed_orders
            ],
            "maximum_allowed_parameter_order": self.maximum_allowed_order,
            "parameter_orders_two_and_higher_structurally_zero": (
                self.maximum_allowed_order < 2
            ),
            "f5_and_higher_contributions_structurally_zero": (
                self.maximum_allowed_order < 2
            ),
            "tree_matrix": [list(row) for row in self.tree_matrix],
            "first_order_coefficient_matrices": [
                [list(row) for row in matrix]
                for matrix in self.first_order_matrices
            ],
            "complete_universal_holomorphic_up_matrix": [
                list(row) for row in ZERO_MATRIX
            ],
            "complete_universal_holomorphic_up_rank": 0,
            "complete_holomorphic_up_matrix_available": self.exact,
            "nontrivial_holomorphic_up_matrix_available": False,
            "declared_up_branch_can_reach_rank_three": False,
            "exact": self.exact,
            "classification": "SCOPED_HOLOMORPHIC_UP_NO_GO",
            "extension_point_selected": False,
            "observational_inputs_used": False,
            "scope": (
                "the frozen one-sided P1 extension branch and its selected "
                "up-type matter/Higgs characters only"
            ),
            "next_required_object": (
                "the lowest-complexity untested Yukawa sector on the same "
                "carrier, beginning with its exact Wilson character support"
            ),
        }


def universal_up_yukawa_no_go() -> UniversalUpYukawaNoGo:
    """Derive the all-orders no-go from exact artifacts and finite typing."""

    tree_digest, tree_payload = _verified_payload(
        TREE_MATRIX_ARTIFACT,
        "complete_tree_level_up_matrix_available",
    )
    matter_digest, matter_payload = _verified_payload(
        UNIVERSAL_MATTER_ARTIFACT,
        "all_coefficientwise_cone_identities_exact",
    )
    first_digest, first_payload = _verified_payload(
        FIRST_ORDER_ARTIFACT,
        "complete_first_order_up_matrix_available",
    )
    if matter_payload.get("carrier_parameter_basis") != ["a0", "a1"]:
        raise ValueError("the universal matter parameter basis changed")
    tree_record = tree_payload.get("up_type_tree_matrix")
    if not isinstance(tree_record, dict):
        raise ValueError("the tree-level matrix record is unavailable")
    coefficient_matrices = first_payload.get("coefficient_matrices")
    if not isinstance(coefficient_matrices, dict):
        raise ValueError("the first-order coefficient matrices are unavailable")
    result = UniversalUpYukawaNoGo(
        tree_digest,
        matter_digest,
        first_digest,
        tuple(
            (row, column, filtration_allowed_orders(row, column))
            for row in range(3)
            for column in range(3)
        ),
        tuple(tuple(str(value) for value in row) for row in tree_record["matrix"]),
        tuple(
            tuple(
                tuple(str(value) for value in row)
                for row in coefficient_matrices[parameter]
            )
            for parameter in ("a0", "a1")
        ),
    )
    if not result.exact:
        raise ValueError("the universal up-type truncation theorem failed")
    return result


def write_up_yukawa_no_go(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed universal holomorphic no-go certificate."""

    payload: dict[str, object] = {
        "schema": "mixed-schoen-universal-up-yukawa-no-go-v1",
        "coefficient_field": "Q(omega)",
        **universal_up_yukawa_no_go().as_record(),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact all-orders up-type no-go certificate."""

    payload = write_up_yukawa_no_go()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"classification: {payload['classification']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "OUTPUT",
    "UniversalUpYukawaNoGo",
    "universal_up_yukawa_no_go",
    "write_up_yukawa_no_go",
]
