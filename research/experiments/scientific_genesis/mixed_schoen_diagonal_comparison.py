"""Resolve the local pencil comparison at the higher-product frontier.

Owns:
    The exact two-chart comparison between the common-Schoen second pencil and
    its independent-fiber diagonal presentation, including overlap homotopy.

Depends on:
    The published Schoen cubic pencil, exact polynomial arithmetic, and the
    three-equation diagonal complete-intersection convention.

Must not:
    Divide by a homogeneous coordinate globally, fabricate a chain map, select
    a carrier point, or report a deformation product before its Cech lift.

Phase 0:
    Research-only derivation of the missing local chain-comparison coefficients.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/mixed_schoen_diagonal_comparison.json"
)
VARIABLES = ("u0", "u1", "u2", "p0", "p1", "q0", "q1")


def _embed_u(polynomial: Polynomial) -> Polynomial:
    """Embed one exact u-cubic into the seven-variable comparison ring."""

    if polynomial.variable_count != 3:
        raise ValueError("the Schoen pencil coefficients must be ternary cubics")
    return Polynomial(
        (
            ((*exponents, 0, 0, 0, 0), coefficient)
            for exponents, coefficient in polynomial.terms
        ),
        variable_count=len(VARIABLES),
        scalar_type=Eisenstein,
    )


def _variable(index: int) -> Polynomial:
    """Return one named coordinate of the exact comparison ring."""

    return Polynomial.monomial(
        tuple(int(position == index) for position in range(len(VARIABLES))),
        scalar_type=Eisenstein,
    )


@dataclass(frozen=True, slots=True)
class DiagonalPencilComparison:
    """Exact local lift and overlap data for the second Schoen pencil."""

    common_pencil: Polynomial
    independent_pencil: Polynomial
    diagonal_equation: Polynomial
    q0_cross_identity: bool
    q1_cross_identity: bool
    overlap_syzygy_identity: bool
    global_coefficient_degrees: tuple[tuple[int, int, int], ...]

    @property
    def global_polynomial_lift_exists(self) -> bool:
        """Return whether homogeneous polynomial coefficients can have the required degrees."""

        return all(
            all(component >= 0 for component in degree)
            for degree in self.global_coefficient_degrees
        )

    @property
    def exact(self) -> bool:
        """Return the two local identities, overlap homotopy, and obstruction gate."""

        return (
            self.q0_cross_identity
            and self.q1_cross_identity
            and self.overlap_syzygy_identity
            and not self.global_polynomial_lift_exists
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the local formulas without promoting the unfinished chain map."""

        return {
            "schema": "mixed-schoen-diagonal-comparison-v1",
            "coefficient_field": "Q(omega)",
            "polynomial_variable_order": list(VARIABLES),
            "equations": {
                "common_second_pencil": "F_p=2*f(u)*p1+g(u)*p0",
                "independent_second_pencil": "G_q=2*f(u)*q1+g(u)*q0",
                "diagonal": "delta=p0*q1-p1*q0",
            },
            "local_chain_coefficients": {
                "q0_nonzero": {
                    "G_q": "p0/q0",
                    "delta": "-2*f(u)/q0",
                },
                "q1_nonzero": {
                    "G_q": "p1/q1",
                    "delta": "g(u)/q1",
                },
            },
            "cross_multiplied_identities": {
                "q0*F_p-p0*G_q=-2*f(u)*delta": self.q0_cross_identity,
                "q1*F_p-p1*G_q=g(u)*delta": self.q1_cross_identity,
            },
            "overlap_difference": {
                "G_q_coefficient": "delta/(q0*q1)",
                "delta_coefficient": "-G_q/(q0*q1)",
                "koszul_syzygy_exact": self.overlap_syzygy_identity,
            },
            "required_global_coefficient_multidegrees_u_p_q": [
                list(degree) for degree in self.global_coefficient_degrees
            ],
            "global_homogeneous_polynomial_lift_exists": (
                self.global_polynomial_lift_exists
            ),
            "cech_local_comparison_required": True,
            "fiber_identification_by_substitution_used": False,
            "extension_point_selected": False,
            "deformation_product_computed": False,
            "exact": self.exact,
            "next_required_object": (
                "the full Cech-local chain comparison applying these two chart "
                "coefficients and their overlap homotopy to the universal "
                "matter-correction cochains"
            ),
        }


@cache
def mixed_schoen_diagonal_comparison() -> DiagonalPencilComparison:
    """Derive both local pencil lifts and their exact overlap syzygy."""

    cox = schoen_geometry().cover.cox
    f = _embed_u(cox.cubic_f)
    g = _embed_u(cox.cubic_g)
    p0, p1, q0, q1 = (_variable(index) for index in range(3, 7))
    common = f * p1.scale(2) + g * p0
    independent = f * q1.scale(2) + g * q0
    diagonal = p0 * q1 - p1 * q0
    zero = Polynomial.zero(len(VARIABLES), scalar_type=Eisenstein)
    q0_identity = q0 * common - p0 * independent + f * diagonal.scale(2)
    q1_identity = q1 * common - p1 * independent - g * diagonal
    overlap = diagonal * independent - independent * diagonal
    return DiagonalPencilComparison(
        common,
        independent,
        diagonal,
        q0_identity == zero,
        q1_identity == zero,
        overlap == zero,
        (
            (0, 1, -1),
            (3, 0, -1),
        ),
    )


def write_mixed_schoen_diagonal_comparison(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed local diagonal-comparison certificate."""

    comparison = mixed_schoen_diagonal_comparison()
    if not comparison.exact:
        raise ValueError("the local Schoen diagonal comparison failed")
    payload = cast(dict[str, object], comparison.as_record())
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
    """Regenerate the exact local diagonal-comparison artifact."""

    payload = write_mixed_schoen_diagonal_comparison()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(
        "global_homogeneous_polynomial_lift_exists: "
        f"{payload['global_homogeneous_polynomial_lift_exists']}"
    )
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DiagonalPencilComparison",
    "OUTPUT",
    "mixed_schoen_diagonal_comparison",
    "write_mixed_schoen_diagonal_comparison",
]
