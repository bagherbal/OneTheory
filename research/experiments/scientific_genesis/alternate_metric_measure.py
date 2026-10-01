"""Exact residue and auxiliary integration measure on the actual Schoen cover.

Owns:
    Explicit affine projection charts, the double-residue coefficient, tangent
    frames, normalized Fubini--Study auxiliary densities, and quotient weights.

Depends on:
    The frozen actual cubic pencils, exact polynomial and Eisenstein arithmetic,
    independently validated cover points, and the actual geometric deck action.

Must not:
    Sample free affine coordinates as if they had the stated auxiliary law,
    guess roots, choose extension or vacuum moduli, hide volume conventions,
    or report Ricci-flat/HYM metrics or physical observables.

Phase 0:
    Research integration prerequisites only; numerical sampling remains open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from onetheory.models.heterotic_schoen.geometry import SCHOEN_COVERING_DEGREE, schoen_geometry
from research.experiments.computable_carrier.schoen_sparse_actions import schoen_sparse_deck_actions

from .alternate_metric_fiber_evaluation import CoverPoint

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/alternate_metric_measure.json"


def _variables(count):
    return tuple(Polynomial.monomial(tuple(int(i == j) for j in range(count)),
                                     scalar_type=Eisenstein) for i in range(count))


def _value(polynomial, coordinates):
    return Eisenstein.coerce(polynomial.substitute(coordinates).coefficient(()))


@dataclass(frozen=True, slots=True)
class ProjectionChart:
    """Declare pivots and eliminated coordinates; free order is (s,r,t)."""

    x_pivot: int
    x_solve: int
    u_pivot: int
    u_solve: int
    p_pivot: int

    def __post_init__(self):
        for pivot, solve in ((self.x_pivot, self.x_solve), (self.u_pivot, self.u_solve)):
            if any(type(i) is not int or not 0 <= i < 3 for i in (pivot, solve)):
                raise ValueError("plane chart indices must be integers in range three")
            if pivot == solve:
                raise ValueError("the pivot and eliminated coordinate must be distinct")
        if type(self.p_pivot) is not int or not 0 <= self.p_pivot < 2:
            raise ValueError("the P1 pivot must be an integer in range two")

    @property
    def pivots(self):
        return self.x_pivot, self.u_pivot, self.p_pivot

    @property
    def free_indices(self):
        return (3 - self.x_pivot - self.x_solve,
                3 - self.u_pivot - self.u_solve, 1 - self.p_pivot)

    @property
    def ambient_sign(self):
        x_free, u_free, _ = self.free_indices
        exponent = (self.x_pivot + self.u_pivot + self.p_pivot
                    + int(x_free > self.x_solve) + int(u_free > self.u_solve))
        return -1 if exponent % 2 else 1

    def coordinates(self, point):
        """Return (s,z,r,w,t) with each homogeneous pivot explicitly set to one."""

        if point.chart != self.pivots:
            raise ValueError("point and residue chart must have identical explicit pivots")
        x_free, u_free, p_free = self.free_indices
        return (point.x[x_free] / point.x[self.x_pivot],
                point.x[self.x_solve] / point.x[self.x_pivot],
                point.u[u_free] / point.u[self.u_pivot],
                point.u[self.u_solve] / point.u[self.u_pivot],
                point.p[p_free] / point.p[self.p_pivot])


@cache
def projection_polynomials(chart):
    """Dehomogenize the actual equations in order (s,z,r,w,t), not new pencils."""

    s, z, r, w, t = _variables(5)
    p_free = chart.free_indices[2]
    one = Polynomial.one(5, scalar_type=Eisenstein)
    x = tuple(one if i == chart.x_pivot else z if i == chart.x_solve else s
              for i in range(3))
    u = tuple(one if i == chart.u_pivot else w if i == chart.u_solve else r
              for i in range(3))
    p = tuple(t if i == p_free else one for i in range(2))
    cox = schoen_geometry().cover.cox
    return (p[0] * cox.cubic_f.substitute(x) + p[1] * cox.cubic_g.substitute(x),
            2 * p[1] * cox.cubic_f.substitute(u) + p[0] * cox.cubic_g.substitute(u))


def fiber_polynomials(chart, free_coordinates):
    """Return two univariate equations, without choosing or approximating roots."""

    if len(free_coordinates) != 3:
        raise ValueError("free coordinates must be explicitly ordered (s,r,t)")
    s, r, t = tuple(Eisenstein.coerce(c) for c in free_coordinates)
    variable = _variables(1)[0]
    f, g = projection_polynomials(chart)
    return f.substitute((s, variable, r, 0, t)), g.substitute((s, 0, r, variable, t))


def _fs_direction(coordinates, tangent):
    """Return pi times the normalized FS density along one complex direction."""

    potential = Rational(1) + sum((q.norm() for q in coordinates), Rational(0))
    length = sum((v.norm() for v in tangent), Rational(0))
    inner = sum((q.conjugate() * v for q, v in zip(coordinates, tangent, strict=True)),
                Eisenstein(0))
    return (potential * length - inner.norm()) / potential**2


def auxiliary_cover_mass():
    """Integrate Hx Hu Hp against the actual complete-intersection class."""

    x, u, p = _variables(3)
    class_ = (3 * x + p) * (3 * u + p)
    mass = Eisenstein.coerce((x * u * p * class_).coefficient((2, 2, 1)))
    if not mass.b.is_zero():
        raise ValueError("the auxiliary topological mass must be rational")
    return mass.a


@dataclass(frozen=True, slots=True)
class LocalMeasure:
    """Exact densities with pi cubed factored out, never silently approximated.

    In free-coordinate Lebesgue volume, rho_Omega = residue.norm(), while
    rho_aux = auxiliary_pi3_density / pi^3. For the normalized auxiliary
    point law A / integral(A), importance weights are pi^3 times the stored
    cover/quotient coefficients. The quotient formula applies only to
    descended invariant integrands under the declared free covering.
    """

    chart: ProjectionChart
    volume_scale: Eisenstein
    residue: Eisenstein
    tangent: Matrix
    auxiliary_pi3_density: Rational
    auxiliary_cover_mass: Rational
    covering_degree: int

    @property
    def omega_density(self):
        return self.residue.norm()

    @property
    def cover_weight_pi3_removed(self):
        return self.auxiliary_cover_mass * self.omega_density / self.auxiliary_pi3_density

    @property
    def quotient_weight_pi3_removed(self):
        return self.cover_weight_pi3_removed / self.covering_degree


def local_measure(point, chart, *, volume_scale, covering_degree):
    """Use df wedge dg wedge Omega = sigma_x wedge sigma_u wedge sigma_p.

    The positive volume is (i/8) Omega wedge conjugate(Omega). FS forms are
    (i/2pi) partial bar-partial log(sum |Z|^2), with integral_CP1 FS = 1.
    A vanishing projection Jacobian rejects this chart, not the whole variety.
    """

    scale = Eisenstein.coerce(volume_scale)
    if not isinstance(point, CoverPoint):
        raise TypeError("the measure requires a validated actual CoverPoint")
    if scale.is_zero():
        raise ValueError("an explicit nonzero volume-form scale is required")
    if type(covering_degree) is not int or covering_degree < 1:
        raise ValueError("an explicit positive integer covering degree is required")
    coordinates = chart.coordinates(point)
    f, g = projection_polynomials(chart)
    f_s, f_z, f_t = (_value(f.derivative(i), coordinates) for i in (0, 1, 4))
    g_r, g_w, g_t = (_value(g.derivative(i), coordinates) for i in (2, 3, 4))
    if f_z.is_zero() or g_w.is_zero():
        raise ValueError("the selected projection is ramified; choose an explicit valid chart")
    tangent = Matrix(((1, 0, 0), (-f_s / f_z, 0, -f_t / f_z), (0, 1, 0),
                      (0, -g_r / g_w, -g_t / g_w), (0, 0, 1)), scalar_type=Eisenstein)
    s, z, r, w, t = coordinates
    auxiliary = (_fs_direction((s, z), (Eisenstein(1), -f_s / f_z))
                 * _fs_direction((r, w), (Eisenstein(1), -g_r / g_w))
                 / (Rational(1) + t.norm())**2)
    if auxiliary <= 0:
        raise ValueError("the explicit auxiliary density must be strictly positive")
    return LocalMeasure(chart, scale, -chart.ambient_sign * scale / (f_z * g_w),
                        tangent, auxiliary, auxiliary_cover_mass(), covering_degree)


def residue_deck_characters():
    """Check actual equation semi-invariance and derive the residue characters."""

    variables = _variables(8)
    cox = schoen_geometry().cover.cox
    f = (variables[6] * cox.cubic_f.substitute(variables[:3])
         + variables[7] * cox.cubic_g.substitute(variables[:3]))
    g = (2 * variables[7] * cox.cubic_f.substitute(variables[3:6])
         + variables[6] * cox.cubic_g.substitute(variables[3:6]))
    result = {}
    for action in schoen_sparse_deck_actions():
        images = []
        determinant = Eisenstein(1)
        for coordinate_images, group in zip(
            (action.x_images, action.u_images, action.p_images),
            (variables[:3], variables[3:6], variables[6:]), strict=True,
        ):
            rows = tuple(tuple(c if exponent[j] else Eisenstein(0) for j in range(len(group)))
                         for c, exponent in coordinate_images)
            matrix = Matrix(rows, scalar_type=Eisenstein)
            determinant *= matrix.determinant()
            adjoint = Matrix(tuple(tuple(c.conjugate() for c in row)
                                   for row in zip(*rows, strict=True)), scalar_type=Eisenstein)
            if matrix.matmul(adjoint) != Matrix.identity(len(group), scalar_type=Eisenstein):
                raise ValueError("the actual deck action is not FS unitary")
            images.extend(group[exponent.index(1)] * c for c, exponent in coordinate_images)
        if (f.substitute(images) != f * action.first_equation_unit
            or g.substitute(images) != g * action.second_equation_unit):
            raise ValueError("actual equation units disagree with direct polynomial pullback")
        result[action.name] = determinant / (
            action.first_equation_unit * action.second_equation_unit
        )
    return result


def measure_artifact():
    """Record exact integration prerequisites without certifying a point sampler."""

    characters = residue_deck_characters()
    if any(character != Eisenstein(1) for character in characters.values()):
        raise ValueError("the actual volume form does not descend to the quotient")
    probes = []
    for x, u, p, pivots in (
        ((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1)),
        ((1, 1, 1), (1, -1, 0), (1, 0), (0, 0, 0)),
    ):
        point = CoverPoint(x, u, p, pivots)
        chart = ProjectionChart(pivots[0], 2, pivots[1], 2, pivots[2])
        local = local_measure(point, chart, volume_scale=Eisenstein(1),
                              covering_degree=SCHOEN_COVERING_DEGREE)
        probes.append({
            "point": {"x": list(x), "u": list(u), "p": list(p), "pivots": list(pivots)},
            "eliminated_coordinates": [2, 2],
            "residue_coefficient": str(local.residue),
            "omega_lebesgue_density": str(local.omega_density),
            "auxiliary_density_times_pi_cubed": str(local.auxiliary_pi3_density),
            "cover_importance_weight_without_pi_cubed": str(local.cover_weight_pi3_removed),
            "quotient_importance_weight_without_pi_cubed": str(local.quotient_weight_pi3_removed),
            "tangent_rows": [[str(value) for value in row] for row in local.tangent.rows],
        })
    cox = schoen_geometry().cover.cox
    payload = {
        "schema": "alternate-metric-measure-v1",
        "published_method": "https://arxiv.org/abs/0712.3563v2",
        "actual_plane_cubics": {
            name: [[list(powers), [str(value.a), str(value.b)]]
                   for powers, value in polynomial.terms]
            for name, polynomial in (("F", cox.cubic_f), ("G", cox.cubic_g))
        },
        "actual_equations": ["mu*F(x)+nu*G(x)", "2*nu*F(u)+mu*G(u)"],
        "free_coordinate_order": ["s", "r", "t"],
        "ambient_coordinate_order": ["s", "z", "r", "w", "t"],
        "residue_convention": "df wedge dg wedge Omega = sigma_x wedge sigma_u wedge sigma_p",
        "positive_volume_convention": "(i/8) Omega wedge conjugate(Omega)",
        "FS_convention": "(i/2pi) partial bar-partial log(sum |Z|^2); integral_CP1 FS = 1",
        "auxiliary_form": "A = omega_FS_x wedge omega_FS_u wedge omega_FS_p restricted to X",
        "auxiliary_cover_mass": str(auxiliary_cover_mass()),
        "mass_derivation": "coefficient Hx^2 Hu^2 Hp in Hx Hu Hp (3Hx+Hp)(3Hu+Hp)",
        "normalized_point_law": "A / integral_cover A",
        "required_point_generator": (
            "independent SU-uniform first-plane line, P1 point, second-plane line; "
            "all nine transverse intersection roots equally, with multiplicity"
        ),
        "covering_degree": SCHOEN_COVERING_DEGREE,
        "deck_residue_characters": {name: str(value) for name, value in characters.items()},
        "probe_volume_scale": "1 (declared form convention, not a physical modulus)",
        "quotient_weight_rule": (
            "pi^3 * integral_cover(A) * rho_Omega / (degree * auxiliary_density_times_pi_cubed); "
            "only for descended invariant integrands under the declared free covering"
        ),
        "exact_geometric_probes": probes,
        "exact_residue_and_auxiliary_measure_available": True,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False,
        "physical_yukawas_available": False,
        "extension_point_selected": False,
        "vacuum_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "controlled complete-intersection roots for the declared projective sampling law, "
            "then independent integration-error and Ricci-flat/HYM convergence checks"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    """Write the deterministic exact measure record after all local validations."""

    payload = measure_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = write_artifact()
    print(f"artifact_digest: {result['artifact_digest']}")
