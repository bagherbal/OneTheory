"""Evaluate actual universal metric sections in explicitly framed fibers.

Owns:
    Exact cover points, chart line frames, the actual nine-generator/five-relation
    presentation, symbolic rank-four quotient frames, and section evaluation.

Depends on:
    Frozen Schoen equations, both actual twisted constituent complexes, saved
    outer coefficients, the certified universal section constructor, and exact
    Eisenstein linear algebra.

Must not:
    Choose an extension point or vacuum, hide a fiber basis, replace nonsplit
    relations by a direct sum, infer numerical metrics, or use observations.

Phase 0:
    Research-only local evaluation; Ricci-flat/HYM convergence remains open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from itertools import combinations

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)

from . import alternate_metric_outer_lifts as lifts
from .alternate_metric_lift_operator_certificate import OUTPUT as LIFT_CERTIFICATE
from .mixed_schoen_common_dga import mixed_outer_cup
from .mixed_schoen_outer_universal_cone import _verified_payload

OUTPUT = lifts.first.ROOT / (
    "data/generated/scientific_genesis/alternate_metric_fiber_evaluation.json"
)


def _value(polynomial, coordinates):
    return Eisenstein.coerce(polynomial.substitute(coordinates).coefficient(()))


@dataclass(frozen=True, slots=True)
class CoverPoint:
    """An exact point on the actual cover with three explicitly chosen pivots."""

    x: tuple[Eisenstein, ...]
    u: tuple[Eisenstein, ...]
    p: tuple[Eisenstein, ...]
    chart: tuple[int, int, int]

    def __post_init__(self):
        if (not isinstance(self.chart, tuple) or len(self.chart) != 3
            or any(type(i) is not int or not 0 <= i < size
                   for i, size in zip(self.chart, (3, 3, 2), strict=True))):
            raise ValueError("an explicit integer cover chart is required")
        for name, size, pivot in zip(("x", "u", "p"), (3, 3, 2), self.chart, strict=True):
            coordinates = tuple(Eisenstein.coerce(c) for c in getattr(self, name))
            if len(coordinates) != size or coordinates[pivot].is_zero():
                raise ValueError("a projective coordinate group is absent from the chosen chart")
            object.__setattr__(self, name, coordinates)
        cox = schoen_geometry().cover.cox
        equations = (
            self.p[0] * _value(cox.cubic_f, self.x) + self.p[1] * _value(cox.cubic_g, self.x),
            2 * self.p[1] * _value(cox.cubic_f, self.u) + self.p[0] * _value(cox.cubic_g, self.u),
        )
        if any(not value.is_zero() for value in equations):
            raise ValueError("the exact point does not satisfy both actual Schoen equations")

    @property
    def cell(self):
        return tuple((i,) for i in self.chart)

    def line_frame(self, degree):
        """Declare x_i^dx u_j^du p_k^dp, without projective rescaling."""

        result = Eisenstein(1)
        for coordinates, pivot, exponent in zip(
            (self.x, self.u, self.p), self.chart, degree, strict=True,
        ):
            result *= coordinates[pivot] ** exponent
        return result

    def monomial(self, exponents):
        """Evaluate a Laurent coefficient regular on the explicit chart."""

        if len(exponents) != 8:
            raise ValueError("a cover monomial needs eight homogeneous exponents")
        result = Eisenstein(1)
        for coordinates, pivot, powers in zip(
            (self.x, self.u, self.p), self.chart,
            (exponents[:3], exponents[3:6], exponents[6:]), strict=True,
        ):
            for index, (coordinate, exponent) in enumerate(zip(coordinates, powers, strict=True)):
                if type(exponent) is not int or (exponent < 0 and index != pivot):
                    raise ValueError("a Laurent pole escaped the explicitly inverted pivot")
                result *= coordinate ** exponent
        return result


def local_coordinates(cochain, point, context):
    """Project the total complex to Cech-zero/Koszul-zero local generators."""

    result = [Eisenstein(0) for o in context.left.objects if o.position == 0]
    for basis, coefficient in cochain.terms:
        component = basis.component
        key = component.left_index, component.right_index, component.koszul_summand
        if context.components.get(key) != component:
            raise ValueError("a cochain uses an incompatible constituent or homogeneous basis")
        if (basis.cell != point.cell or component.koszul_summand != "k0"
            or context.left.objects[component.left_index].position != 0):
            continue
        index = component.left_index
        result[index] += coefficient * point.monomial(
            basis.x_monomial + basis.u_monomial + basis.p_monomial,
        ) / point.line_frame(context.left.objects[index].line_degree)
    return tuple(result)


def relation_generator(point, context, index):
    """Use one declared homogeneous line frame as a local relation generator."""

    obj = context.left.objects[index]
    if obj.position != -1:
        raise ValueError("a local relation must come from the actual degree-minus-one object")
    monomials = tuple(tuple(degree if j == pivot else 0 for j in range(size))
                      for degree, pivot, size in zip(obj.line_degree, point.chart, (3, 3, 2),
                                                     strict=True))
    return SparseOuterCechCochain(((OuterCechBasis(
        context.components[index, 0, "k0"], *monomials, point.cell,
    ), Eisenstein(1)),))


def _columns(columns):
    return Matrix(tuple(zip(*columns, strict=True)), scalar_type=Eisenstein)


@cache
def local_presentation(point):
    """Extract actual D1, D2 and E0/E1 columns, retaining all Serre corrections."""

    first = lifts.first._context()[0]
    second = lifts.second._context()[0]
    first_indices = tuple(i for i, o in enumerate(first.left.objects) if o.position == -1)
    second_indices = tuple(i for i, o in enumerate(second.left.objects) if o.position == -1)
    if first_indices != (4, 5) or second_indices != (5, 6, 7):
        raise ValueError("the actual rank-four presentation object ordering changed")
    first_generators = tuple(relation_generator(point, first, i) for i in first_indices)
    second_generators = tuple(relation_generator(point, second, i) for i in second_indices)
    b1 = _columns(tuple(local_coordinates(first.differential(g), point, first)
                        for g in first_generators))
    b2 = _columns(tuple(local_coordinates(second.differential(g), point, second)
                        for g in second_generators))
    outer = tuple(_columns(tuple(local_coordinates(mixed_outer_cup(e, g), point, first)
                                 for g in second_generators)) for e in lifts._inputs()[2])
    if b1.rank() != 2 or b2.rank() != 3:
        raise ValueError("actual constituent relations do not give rank-two fibers at this point")
    return b1, b2, outer


def admissible_pivots(point):
    """List nonzero minors; the caller must explicitly select the fiber frame."""

    b1, b2, _outer = local_presentation(point)
    return tuple(
        tuple(rows for rows in combinations(range(b.row_count), b.column_count)
              if not Matrix(tuple(b[i] for i in rows),
                            scalar_type=Eisenstein).determinant().is_zero())
        for b in (b1, b2)
    )


def _quotient(b, pivots):
    if (not isinstance(pivots, tuple) or len(pivots) != b.column_count
        or len(set(pivots)) != len(pivots)
        or any(type(i) is not int or not 0 <= i < b.row_count for i in pivots)):
        raise ValueError("explicit distinct relation pivot rows are required")
    nonpivots = tuple(i for i in range(b.row_count) if i not in pivots)
    inverse = Matrix(tuple(b[i] for i in pivots), scalar_type=Eisenstein).inverse()
    selector = Matrix(tuple(tuple(int(i == j) for j in range(b.row_count)) for i in pivots),
                      scalar_type=Eisenstein)
    remainder = Matrix(tuple(b[i] for i in nonpivots), scalar_type=Eisenstein)
    inclusion = Matrix(tuple(tuple(int(i == j) for j in range(b.row_count)) for i in nonpivots),
                       scalar_type=Eisenstein)
    return (inclusion - remainder.matmul(inverse).matmul(selector),
            inverse.matmul(selector), nonpivots)


@dataclass(frozen=True, slots=True)
class FiberFrame:
    """An explicit quotient frame over Q(omega)[a0,a1], not a physical metric."""

    point: CoverPoint
    first_pivots: tuple[int, int]
    second_pivots: tuple[int, int, int]
    basis_labels: tuple[str, ...]
    relations: tuple[Matrix, Matrix, Matrix]
    projections: tuple[Matrix, Matrix, Matrix]
    inclusion: Matrix
    relation_minor: Eisenstein

    def evaluate_basis(self, index):
        """Return constant/a0/a1 fiber columns of one actual universal section."""

        section = lifts.universal_section(index)
        first = lifts.first._context()[0]
        second = lifts.second._context()[0]
        ambient = (_columns((local_coordinates(section.first_constant, self.point, first)
                             + local_coordinates(section.second_constant, self.point, second),)),
                   *(_columns((local_coordinates(c, self.point, first) + (Eisenstein(0),) * 5,))
                     for c in section.first_coefficients))
        for q in self.projections[1:]:
            for v in ambient[1:]:
                if not q.matmul(v).is_zero():
                    raise ValueError("a universal fiber section acquired quadratic terms")
        return (self.projections[0].matmul(ambient[0]),
                *(self.projections[0].matmul(v) + q.matmul(ambient[0])
                  for q, v in zip(self.projections[1:], ambient[1:], strict=True)))

    def transition_to(self, other):
        """Return explicit constant/a0/a1 transition coefficients on this chart."""

        if self.point != other.point:
            raise ValueError("frame transitions require the same point and chart normalization")
        return tuple(q.matmul(self.inclusion) for q in other.projections)


def fiber_frame(point, first_pivots, second_pivots):
    """Eliminate five actual relations with an explicit block-triangular minor."""

    b1, b2, outer = local_presentation(point)
    p1, _split1, free1 = _quotient(b1, first_pivots)
    p2, split2, free2 = _quotient(b2, second_pivots)
    constant_b = Matrix(tuple((*b1[i], *([0] * 3)) for i in range(4))
                        + tuple((*([0] * 2), *b2[i]) for i in range(5)), scalar_type=Eisenstein)
    param_b = tuple(Matrix(tuple((*([0] * 2), *e[i]) for i in range(4))
                           + ((0,) * 5,) * 5, scalar_type=Eisenstein) for e in outer)
    constant_q = Matrix(tuple((*p1[i], *([0] * 5)) for i in range(2))
                        + tuple((*([0] * 4), *p2[i]) for i in range(2)), scalar_type=Eisenstein)
    corrections = tuple(p1.matmul(e).matmul(split2).scale(-1) for e in outer)
    param_q = tuple(Matrix(tuple((*([0] * 4), *c[i]) for i in range(2))
                           + ((0,) * 9,) * 2, scalar_type=Eisenstein) for c in corrections)
    free = free1 + tuple(4 + i for i in free2)
    inclusion = Matrix(tuple(tuple(int(i == j) for j in free) for i in range(9)),
                       scalar_type=Eisenstein)
    if (not constant_q.matmul(constant_b).is_zero()
        or constant_q.matmul(inclusion) != Matrix.identity(4, scalar_type=Eisenstein)):
        raise ValueError("the actual constant fiber quotient identity failed")
    for q, b in zip(param_q, param_b, strict=True):
        if (not (constant_q.matmul(b) + q.matmul(constant_b)).is_zero()
            or not q.matmul(inclusion).is_zero()):
            raise ValueError("an actual universal parameter quotient identity failed")
        for other_b in param_b:
            if not q.matmul(other_b).is_zero():
                raise ValueError("a quadratic boundary survived the actual fiber quotient")
    minor = Matrix(tuple(constant_b[i] for i in first_pivots + tuple(4 + j for j in second_pivots)),
                   scalar_type=Eisenstein).determinant()
    objects = lifts.first._context()[0].left.objects, lifts.second._context()[0].left.objects
    labels = tuple(f"V1:{objects[0][i].name}" for i in free1) + tuple(
        f"V2:{objects[1][i].name}" for i in free2
    )
    return FiberFrame(point, first_pivots, second_pivots, labels,
                      (constant_b, *param_b), (constant_q, *param_q), inclusion, minor)


def compact_coordinates(record, point, context):
    """Evaluate saved plane-global terms without their nine identical copies."""

    values = [Eisenstein(0) for o in context.left.objects if o.position == 0]
    for index, monomial, chart, coefficient in record["terms"]:
        if chart == point.chart[2]:
            values[index] += Eisenstein(*coefficient) * point.monomial(monomial) / point.line_frame(
                context.left.objects[index].line_degree,
            )
    return tuple(values)


def spanning_indices(frame):
    """Record the first two independent actual columns in each constituent."""

    b1, b2, _outer = local_presentation(frame.point)
    p1 = _quotient(b1, frame.first_pivots)[0]
    p2 = _quotient(b2, frame.second_pivots)[0]
    contexts = lifts.first._context()[0], lifts.second._context()[0]
    selected = []
    for block, (stream, context, projection) in enumerate(zip(
        lifts._inputs()[1], contexts, (p1, p2), strict=True,
    )):
        columns = []
        indices = []
        for index, record in enumerate(stream):
            coordinates = compact_coordinates(record, frame.point, context)
            column = projection.matmul(_columns((coordinates,)))
            values = tuple(row[0] for row in column.rows)
            if _columns((*columns, values)).rank() > len(columns):
                columns.append(values)
                indices.append(index + (2655 if block else 0))
            if len(columns) == 2:
                break
        if len(columns) != 2:
            raise ValueError("the actual constituent section stream fails to span this fiber")
        selected.extend(indices)
    return tuple(selected)


def _matrix_record(matrix):
    return [[str(value) for value in row] for row in matrix.rows]


def write_fiber_evaluation():
    """Archive actual symbolic fiber columns and exact local quotient identities."""

    lift_digest, lift_record = _verified_payload(LIFT_CERTIFICATE)
    if (not lift_record.get("full_universal_lift_formula_certified")
        or not lift_record.get("rank_four_section_basis_available")):
        raise ValueError("the independently certified full universal basis is required")
    # This point is an algebraic evaluation probe, not a geometry/vacuum selector.
    # G(1,-1,0)=0, F(1,1,1)=0, and mu=0 certify both actual cover equations.
    point = CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    frame = fiber_frame(point, (0, 2), (0, 1, 2))
    indices = spanning_indices(frame)
    coefficients = []
    for index in indices:
        coefficients.append(frame.evaluate_basis(index))
        print(f"actual_fiber_section_evaluated: {index}", flush=True)
    matrices = tuple(_columns(tuple(tuple(row[0] for row in column[p].rows)
                                    for column in coefficients)) for p in range(3))
    determinant = matrices[0].determinant()
    # Injected V1 columns have no parameter dependence; lifted V2 columns have
    # constant V2 coordinates. Hence this determinant is constant for ALL a0,a1.
    if (determinant.is_zero()
        or any(any(not matrices[0][i][j].is_zero() for i in (2, 3)) for j in (0, 1))
        or any(any(not m[i][j].is_zero() for i in (2, 3) for j in range(4))
               or any(not m[i][j].is_zero() for i in range(4) for j in (0, 1))
               for m in matrices[1:])):
        raise ValueError("the four actual universal fiber columns fail the spanning identity")
    payload = {
        "schema": "alternate-metric-fiber-evaluation-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "parameter_basis": ["a0", "a1"], "coefficient_field": "Q(omega)",
        "prerequisite_artifact_digests": {**lifts._inputs()[0], "lift_certificate": lift_digest},
        "generating_twist_cover_degree": [14, 16, 1],
        "point": {"x": list(map(str, point.x)), "u": list(map(str, point.u)),
                  "p": list(map(str, point.p)), "chart": list(point.chart)},
        "point_role": "exact evaluation probe; not a chosen vacuum or extension point",
        "line_frame_rule": "x_i^dx u_j^du p_k^dp, with the three chart pivots explicit",
        "fiber_basis_labels": list(frame.basis_labels),
        "first_pivot_rows": list(frame.first_pivots),
        "second_pivot_rows": list(frame.second_pivots),
        "relation_coefficients_constant_a0_a1": list(map(_matrix_record, frame.relations)),
        "quotient_coefficients_constant_a0_a1": list(map(_matrix_record, frame.projections)),
        "relation_minor_all_parameters": str(frame.relation_minor),
        "actual_basis_indices": list(indices),
        "actual_section_coefficients_constant_a0_a1": list(map(_matrix_record, matrices)),
        "actual_section_determinant_all_parameters": str(determinant),
        "local_rank_four_evaluator_available": True,
        "all_parameter_boundary_quotient_identities_exact": True,
        "actual_four_section_spanning_probe_exact": True,
        "complete_5345_column_point_matrix_materialized": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "observational_inputs_used": False,
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    temporary.replace(OUTPUT)
    return payload


if __name__ == "__main__":
    report = write_fiber_evaluation()
    print(f"artifact_digest: {report['artifact_digest']}")
