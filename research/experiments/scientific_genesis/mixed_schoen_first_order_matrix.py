"""Assemble the universal first-order up-type Yukawa coefficient matrix.

Owns:
    All eight source-derived lower-block coefficients, their embedding into two
    three-family parameter matrices, and the exact generic polynomial rank.

Depends on:
    The complete indexed higher-product coefficient, the certified tree-level
    matrix, and the frozen two-direction universal carrier family.

Must not:
    Select an extension point, infer equality between local bases, omit a
    coefficient, call a truncated expansion complete, or import observations.

Phase 0:
    Research-only universal first-order matrix on the lawful flavor path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, polynomial_determinant
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_first_higher_product import (
    OUTPUT as FIRST_COEFFICIENT_ARTIFACT,
)
from .mixed_schoen_first_higher_product import (
    FirstHigherProductCoefficient,
    higher_product_coefficient,
)
from .mixed_schoen_universal_matter_lifts import (
    OUTPUT as UNIVERSAL_MATTER_ARTIFACT,
)
from .mixed_schoen_yukawa_trace import OUTPUT as TREE_MATRIX_ARTIFACT

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_first_order_matrix.json"
PARAMETERS = ("a0", "a1")
LOCAL_FAMILY_INDICES = (1, 2)
MATTER_FILTRATION_TERMS = {
    0: ((0, (1, 0)),),
    1: ((0, (0, 1)), (1, (1, 0))),
    2: ((0, (0, 1)), (1, (1, 0))),
}
HIGGS_FILTRATION_TERMS = ((0, (1, 1)), (1, (2, 0)))


def filtration_allowed_orders(row: int, column: int) -> tuple[int, ...]:
    """Return every parameter order reaching determinant bidegree (2,2)."""

    try:
        row_terms = MATTER_FILTRATION_TERMS[row]
        column_terms = MATTER_FILTRATION_TERMS[column]
    except KeyError as error:
        raise ValueError("three-family indices must lie between zero and two") from error
    return tuple(
        sorted(
            {
                row_order + column_order + higgs_order
                for row_order, row_degree in row_terms
                for column_order, column_degree in column_terms
                for higgs_order, higgs_degree in HIGGS_FILTRATION_TERMS
                if (
                    row_degree[0] + column_degree[0] + higgs_degree[0],
                    row_degree[1] + column_degree[1] + higgs_degree[1],
                )
                == (2, 2)
            }
        )
    )


def first_order_filtration_allows(row: int, column: int) -> bool:
    """Return whether exterior bidegree permits one first-order matrix slot."""

    return 1 in filtration_allowed_orders(row, column)


FIRST_ORDER_SLOTS = tuple(
    (row, column)
    for row in range(3)
    for column in range(3)
    if first_order_filtration_allows(row, column)
)
STRUCTURAL_ZERO_SLOTS = tuple(
    (row, column)
    for row in range(3)
    for column in range(3)
    if not first_order_filtration_allows(row, column)
)


def _verified_digest(path: Path, gate: str) -> str:
    """Return an upstream digest after its declared exact gate passes."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest


def _polynomial_record(polynomial: Polynomial) -> list[dict[str, object]]:
    """Serialize one sparse parameter polynomial without a formatting convention."""

    return [
        {"exponents": list(exponents), "coefficient": str(coefficient)}
        for exponents, coefficient in polynomial.terms
    ]


@dataclass(frozen=True, slots=True)
class FirstOrderUpMatrix:
    """The complete parameter-linear coefficient of the up-type matrix."""

    coefficients: tuple[FirstHigherProductCoefficient, ...]

    def __post_init__(self) -> None:
        expected = tuple(
            (parameter, row, column)
            for parameter in PARAMETERS
            for row, column in FIRST_ORDER_SLOTS
        )
        actual = tuple(
            (
                coefficient.parameter,
                coefficient.row_local_family_index,
                coefficient.column_local_family_index,
            )
            for coefficient in self.coefficients
        )
        if actual != expected:
            raise ValueError("the first-order coefficient basis is incomplete")

    def coefficient_matrix(self, parameter: str) -> Matrix:
        """Return one exact three-family parameter coefficient matrix."""

        if parameter not in PARAMETERS:
            raise ValueError("the carrier parameter is unavailable")
        values = {
            (
                coefficient.row_local_family_index,
                coefficient.column_local_family_index,
            ): coefficient.residue
            for coefficient in self.coefficients
            if coefficient.parameter == parameter
        }
        return Matrix(
            tuple(
                tuple(
                    values.get((row, column), Eisenstein(0))
                    for column in range(3)
                )
                for row in range(3)
            ),
            scalar_type=Eisenstein,
        )

    @property
    def universal_lower_determinant(self) -> Polynomial:
        """Return the exact lower-block determinant over Q(omega)[a0,a1]."""

        variables = tuple(
            Polynomial.monomial(
                (int(index == 0), int(index == 1)),
                scalar_type=Eisenstein,
            )
            for index in range(2)
        )
        coefficient_matrices = tuple(
            self.coefficient_matrix(parameter) for parameter in PARAMETERS
        )
        lower = tuple(
            tuple(
                sum(
                    (
                        variables[index].scale(matrix[row][column])
                        for index, matrix in enumerate(coefficient_matrices)
                    ),
                    start=Polynomial.zero(2, scalar_type=Eisenstein),
                )
                for column in LOCAL_FAMILY_INDICES
            )
            for row in LOCAL_FAMILY_INDICES
        )
        return polynomial_determinant(lower)

    @property
    def generic_rank(self) -> int:
        """Return the exact generic rank of the parameter-linear matrix."""

        if not self.universal_lower_determinant.is_zero():
            return 2
        if any(
            not coefficient.residue.is_zero()
            for coefficient in self.coefficients
        ):
            return 1
        return 0

    @property
    def exact(self) -> bool:
        """Return whether every indexed coefficient and matrix gate passes."""

        return (
            len(self.coefficients) == 8
            and all(coefficient.exact for coefficient in self.coefficients)
            and all(
                self.coefficient_matrix(parameter).row_count == 3
                and self.coefficient_matrix(parameter).column_count == 3
                for parameter in PARAMETERS
            )
            and self.generic_rank in (0, 1, 2)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize all coefficient evidence and the universal rank result."""

        matrices = {
            parameter: [
                [
                    str(self.coefficient_matrix(parameter)[row][column])
                    for column in range(3)
                ]
                for row in range(3)
            ]
            for parameter in PARAMETERS
        }
        return {
            "parameter_basis": list(PARAMETERS),
            "matrix_expansion": "Y^(1)(a)=a0 M0+a1 M1",
            "first_order_slots": [list(slot) for slot in FIRST_ORDER_SLOTS],
            "structural_zero_slots": [
                list(slot) for slot in STRUCTURAL_ZERO_SLOTS
            ],
            "structural_zero_reason": (
                "the constant V1 family and every first-order correction place "
                "at least three factors in rank-two V1 outside the V2-V2 block"
            ),
            "coefficient_matrices": matrices,
            "coefficients": [
                coefficient.as_record() for coefficient in self.coefficients
            ],
            "universal_lower_determinant": _polynomial_record(
                self.universal_lower_determinant
            ),
            "generic_first_order_rank": self.generic_rank,
            "all_eight_coefficients_exact": self.exact,
            "complete_first_order_up_matrix_available": self.exact,
            "complete_holomorphic_up_matrix_available": False,
            "extension_point_selected": False,
            "observational_inputs_used": False,
            "next_required_object": (
                "the next mathematically allowed higher product needed to "
                "escape the certified first-order rank bound"
            ),
        }


@cache
def mixed_schoen_first_order_matrix() -> FirstOrderUpMatrix:
    """Derive every first-order coefficient over the frozen parameter basis."""

    coefficients = tuple(
        higher_product_coefficient(parameter, row, column)
        for parameter in range(len(PARAMETERS))
        for row, column in FIRST_ORDER_SLOTS
    )
    result = FirstOrderUpMatrix(coefficients)
    if not result.exact:
        raise ValueError("the complete first-order matrix certificate failed")
    return result


def write_first_order_matrix(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed universal first-order matrix certificate."""

    result = mixed_schoen_first_order_matrix()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-first-order-up-matrix-v1",
        "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {
            "tree_matrix": _verified_digest(
                TREE_MATRIX_ARTIFACT,
                "complete_tree_level_up_matrix_available",
            ),
            "universal_matter": _verified_digest(
                UNIVERSAL_MATTER_ARTIFACT,
                "all_coefficientwise_cone_identities_exact",
            ),
            "first_complete_coefficient": _verified_digest(
                FIRST_COEFFICIENT_ARTIFACT,
                "exact",
            ),
        },
        **result.as_record(),
    }
    payload["classification"] = (
        "SCOPED_FIRST_ORDER_NO_GO"
        if result.generic_rank == 0
        else "SCOPED_FIRST_ORDER_RANK_BOUND"
    )
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
    """Regenerate the complete exact universal first-order matrix."""

    payload = write_first_order_matrix()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"generic_first_order_rank: {payload['generic_first_order_rank']}")
    print(f"classification: {payload['classification']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "FIRST_ORDER_SLOTS",
    "FirstOrderUpMatrix",
    "OUTPUT",
    "PARAMETERS",
    "STRUCTURAL_ZERO_SLOTS",
    "filtration_allowed_orders",
    "first_order_filtration_allows",
    "mixed_schoen_first_order_matrix",
    "write_first_order_matrix",
]
