"""Bind local Serre pushouts to the exact dP9 blow-up atlas.

Owns:
    Chart-local locations of the I3/I6 singular-point schemes, exact fiber
    coordinates, hypersurface incidence checks, and the unit-class local
    pushout presentations used by the Tier A Serre construction.

Depends on:
    The exact cubic-pencil blow-up atlas and local polynomial Serre models.
    It records local data in atlas coordinates without inventing global
    transition functions.

Must not:
    Treat local pushouts as global vector bundles, choose an unproved global
    extension class, infer equivariant linearization, or report a completed
    dP9 Serre constituent.

Phase 0:
    Every declared local unit pushout is tied to a checked atlas chart; global
    Cech gluing, bundle transitions, and descent remain explicit gates.
"""

from __future__ import annotations

from dataclasses import dataclass

from onetheory.math.numbers import Eisenstein
from onetheory.math.sheaves import LaurentMatrix, LaurentPolynomial

from .pencil import TierAPencilModel, tier_a_pencil_model
from .serre_local import LocalSerreModel, local_serre_model


@dataclass(frozen=True, slots=True)
class AtlasSerreLocal:
    """One exact local Serre pushout located on a blow-up chart."""

    scheme: str
    point: str
    chart: str
    local_coordinates: tuple[str, str]
    fiber_coordinate: Eisenstein
    local_model: LocalSerreModel
    local_to_du: LaurentMatrix
    local_to_dv: LaurentMatrix
    punctured_cocycle: LaurentMatrix
    local_cocycle_exact: bool
    hypersurface_incidence: bool
    fiber_derivative_nonzero: bool
    global_gluing_status: str

    def as_record(self) -> dict[str, object]:
        """Serialize local atlas incidence and the pushout presentation."""

        def matrix_record(matrix: LaurentMatrix) -> list[list[list[object]]]:
            return [
                [
                    [
                        {
                            "exponents": list(exponents),
                            "coefficient": str(coefficient),
                        }
                        for exponents, coefficient in entry.terms
                    ]
                    for entry in row
                ]
                for row in matrix.rows
            ]

        return {
            "scheme": self.scheme,
            "point": self.point,
            "chart": self.chart,
            "local_coordinates": list(self.local_coordinates),
            "fiber_coordinate_nu_over_mu": str(self.fiber_coordinate),
            "local_model": self.local_model.as_record(),
            "local_to_du": matrix_record(self.local_to_du),
            "local_to_dv": matrix_record(self.local_to_dv),
            "punctured_cocycle": matrix_record(self.punctured_cocycle),
            "local_cocycle_exact": self.local_cocycle_exact,
            "hypersurface_incidence": self.hypersurface_incidence,
            "fiber_derivative_nonzero": self.fiber_derivative_nonzero,
            "global_gluing_status": self.global_gluing_status,
        }


def _point_chart(model: TierAPencilModel, point_name: str) -> tuple[str, int]:
    """Return the mu-chart and pivot containing one coordinate point."""

    pivot = {"p_a": 0, "p_b": 1, "p_c": 2}[point_name]
    chart = f"U_{pivot}_mu"
    if chart not in {item.name for item in model.blowup_atlas.charts}:
        raise ValueError("the coordinate point has no declared mu blow-up chart")
    return chart, pivot


def _local_record(
    model: TierAPencilModel,
    scheme: str,
    point_name: str,
) -> AtlasSerreLocal:
    """Construct and verify one chart-local unit pushout."""

    chart_name, _ = _point_chart(model, point_name)
    chart = next(item for item in model.blowup_atlas.charts if item.name == chart_name)
    singular = next(item for item in model.singular_points if item.point.name == point_name)
    if singular.fiber_parameter[0].is_zero():
        raise ValueError("the mu chart cannot trivialize a zero mu fiber coordinate")
    fiber_coordinate = singular.fiber_parameter[1] / singular.fiber_parameter[0]
    incidence = chart.equation.substitute((0, 0, fiber_coordinate)).is_zero()
    derivative = chart.equation.derivative(2).substitute((0, 0, fiber_coordinate))
    certificate = next(
        item
        for item in model.local_ideals
        if item.scheme == scheme and item.point == point_name
    )
    local_model = local_serre_model(scheme)
    if not certificate.verified or not local_model.locally_free:
        raise ValueError("the declared local unit pushout failed an exact local gate")
    local_to_du, local_to_dv, punctured_cocycle, cocycle_exact = _punctured_transitions(
        local_model.multiplicity,
    )
    return AtlasSerreLocal(
        scheme,
        point_name,
        chart_name,
        (certificate.linear_coordinate, certificate.nilpotent_coordinate),
        fiber_coordinate,
        local_model,
        local_to_du,
        local_to_dv,
        punctured_cocycle,
        cocycle_exact,
        incidence,
        not derivative.is_zero(),
        "global Cech gluing and Serre linearization pending",
    )


def _punctured_transitions(
    multiplicity: int,
) -> tuple[LaurentMatrix, LaurentMatrix, LaurentMatrix, bool]:
    """Construct the exact two-chart local Serre Cech transition."""

    u = LaurentPolynomial.monomial((1, 0), scalar_type=Eisenstein)
    u_inverse = LaurentPolynomial.monomial((-1, 0), scalar_type=Eisenstein)
    v_power = LaurentPolynomial.monomial((0, multiplicity), scalar_type=Eisenstein)
    v_inverse_power = LaurentPolynomial.monomial((0, -multiplicity), scalar_type=Eisenstein)
    one = LaurentPolynomial.one(2, scalar_type=Eisenstein)
    zero = LaurentPolynomial.zero(2, scalar_type=Eisenstein)
    local_to_du = LaurentMatrix(((-v_power, u_inverse), (u, zero)))
    local_to_dv = LaurentMatrix(((-v_power, zero), (u, v_inverse_power)))
    inverse_du = LaurentMatrix(((zero, u_inverse), (u, v_power)))
    punctured_cocycle = LaurentMatrix(
        ((one, u_inverse * v_inverse_power), (zero, one))
    )
    exact = (
        inverse_du.compose(local_to_du).is_identity()
        and inverse_du.compose(local_to_dv) == punctured_cocycle
    )
    return local_to_du, local_to_dv, punctured_cocycle, exact


def tier_a_atlas_serre_locals(
    model: TierAPencilModel | None = None,
) -> tuple[AtlasSerreLocal, ...]:
    """Return all six exact chart-local unit Serre presentations."""

    current = tier_a_pencil_model() if model is None else model
    return tuple(
        _local_record(current, scheme, point)
        for scheme in ("I3", "I6")
        for point in ("p_a", "p_b", "p_c")
    )


__all__ = ["AtlasSerreLocal", "tier_a_atlas_serre_locals"]
