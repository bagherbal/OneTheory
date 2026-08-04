"""Construct exact rank-two chart transition candidates from point schemes.

Owns:
    Deterministic three-chart transition matrices derived from the declared
    Hilbert–Burch generators, pairwise inverse checks, determinant-one checks,
    and the explicit boundary between a chart cocycle and a Serre extension.

Depends on:
    Exact production point schemes and Serre rays, plus generic Laurent
    localization and transition-cocycle mathematics.

Must not:
    Call a formal coboundary a physical Serre extension, infer a Schoen cover,
    claim stability, or reuse the published bundle’s transition functions.

Phase 0:
    Exact chart candidates are generated; their identification with a Serre
    extension on the Schoen quotient remains an explicit construction gate.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.sheaves import CoxChart, CoxChartCover, LaurentMatrix, LaurentPolynomial
from onetheory.models.heterotic_schoen.visible import PointScheme, point_schemes, serre_data


@dataclass(frozen=True, slots=True)
class SerreConstituentCandidate:
    """An exact chart-level rank-two candidate with an honest status boundary."""

    scheme: PointScheme
    twist: tuple[int, int, int]
    cover: CoxChartCover
    local_potentials: tuple[LaurentPolynomial, ...]
    transitions: tuple[tuple[int, int, LaurentMatrix], ...]
    invariant_ray_dimension: int
    extension_identification_status: str

    @property
    def cocycle(self):
        """Return the typed transition cocycle for this candidate."""

        from onetheory.math.sheaves import TransitionCocycle

        return TransitionCocycle(self.cover, 2, self.transitions)

    @property
    def determinant_one(self) -> bool:
        """Return the exact determinant-one certificate for unipotent maps."""

        scalar_type = self.transitions[0][2].rows[0][0].scalar_type
        one = LaurentPolynomial.one(3, scalar_type=scalar_type)
        zero = LaurentPolynomial.zero(3, scalar_type=scalar_type)
        return all(
            matrix.rows == ((one, matrix.rows[0][1]), (zero, one))
            for _, _, matrix in self.transitions
        )

    @property
    def pairwise_inverse(self) -> bool:
        """Return the exact inverse check on every ordered pair."""

        return all(
            self._transition(left, right).compose(self._transition(right, left)).is_identity()
            for left in range(len(self.cover.charts))
            for right in range(len(self.cover.charts))
            if left != right
        )

    def _transition(self, left: int, right: int) -> LaurentMatrix:
        """Return one ordered transition without hiding a fallback."""

        for source, target, matrix in self.transitions:
            if (source, target) == (left, right):
                return matrix
        raise KeyError((left, right))

    def as_record(self) -> dict[str, object]:
        """Return exact chart data and its unresolved Serre gate."""

        return {
            "scheme": self.scheme.name,
            "twist": list(self.twist),
            "chart_names": [chart.name for chart in self.cover.charts],
            "inverted_variables": [
                list(chart.inverted_variables) for chart in self.cover.charts
            ],
            "local_potentials": [
                {
                    "terms": [
                        {
                            "exponents": list(exponents),
                            "coefficient": str(coefficient),
                        }
                        for exponents, coefficient in potential.terms
                    ]
                }
                for potential in self.local_potentials
            ],
            "transitions": [
                {
                    "left": left,
                    "right": right,
                    "rows": [
                        [
                            {
                                "terms": [
                                    {
                                        "exponents": list(exponents),
                                        "coefficient": str(coefficient),
                                    }
                                    for exponents, coefficient in entry.terms
                                ]
                            }
                            for entry in row
                        ]
                        for row in matrix.rows
                    ],
                }
                for left, right, matrix in self.transitions
            ],
            "cocycle": self.cocycle.verifies_cocycle(),
            "pairwise_inverse": self.pairwise_inverse,
            "determinant_one": self.determinant_one,
            "invariant_ray_dimension": self.invariant_ray_dimension,
            "extension_identification_status": self.extension_identification_status,
        }


def _chart_cover() -> CoxChartCover:
    """Return the declared three-coordinate base-chart cover."""

    variables = ("a", "b", "c")
    return CoxChartCover(tuple(CoxChart(f"U_{variable}", variables, (variable,))
                               for variable in variables))


def _transition(delta: LaurentPolynomial) -> LaurentMatrix:
    """Return one exact determinant-one unipotent transition matrix."""

    one = LaurentPolynomial.one(3, scalar_type=delta.scalar_type)
    zero = LaurentPolynomial.zero(3, scalar_type=delta.scalar_type)
    return LaurentMatrix(((one, delta), (zero, one)))


def _candidate(
    scheme: PointScheme,
    twist: tuple[int, int, int],
    ray_dimension: int,
) -> SerreConstituentCandidate:
    """Construct the exact chart candidate from scheme generators."""

    cover = _chart_cover()
    local_generators = tuple(
        LaurentPolynomial.from_polynomial(generator)
        for generator in scheme.ideal_generators[: len(cover.charts)]
    )
    if len(local_generators) != len(cover.charts):
        raise ValueError("the chart candidate requires three declared generators")
    transitions = tuple(
        (left, right, _transition(local_generators[left] - local_generators[right]))
        for left in range(len(cover.charts))
        for right in range(len(cover.charts))
        if left != right
    )
    return SerreConstituentCandidate(
        scheme,
        twist,
        cover,
        local_generators,
        transitions,
        ray_dimension,
        "formal chart cocycle only; Serre identification pending",
    )


def tier_a_constituents() -> tuple[SerreConstituentCandidate, ...]:
    """Construct both Tier A chart candidates from exact I3/I6 data."""

    schemes = point_schemes()
    rays = serre_data().rays
    return (
        _candidate(schemes[0], (-1, 1, 0), len(rays[0].vector)),
        _candidate(schemes[1], (1, -1, 0), len(rays[1].vector)),
    )


__all__ = ["SerreConstituentCandidate", "tier_a_constituents"]
