"""Enclose the actual universal rank-four quotient in explicitly named frames.

Owns:
    Actual local relation cochains, determinant-certified pivot elimination,
    constant/a0/a1 quotient bounds, transitions, and on-demand section bounds.

Depends on:
    The original constituent differential, outer cup and section constructor,
    exact polynomial determinants, and certified geometric circular enclosures.

Must not:
    Replace nonsplit relations by a direct sum, hide pivot choices, accept
    residual inclusion as an identity proof, choose extension parameters,
    or claim a complete bounded matrix, sampling law, or converged metric.

Phase 0:
    Research-only universal fiber bounds; controlled integration remains open.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from functools import cache

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, determinant

from . import alternate_metric_enclosures as bounds
from . import alternate_metric_fiber_evaluation as fiber
from .mixed_schoen_common_dga import mixed_outer_cup

OUTPUT = bounds.OUTPUT.with_name("alternate_metric_bounded_fibers.json")


def _shape(matrix):
    if not matrix or not matrix[0] or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("a nonempty rectangular enclosure matrix is required")
    if any(not isinstance(c, bounds.Ball) or c.bits != matrix[0][0].bits
           for row in matrix for c in row):
        raise ValueError("all matrix entries require the same declared bound precision")
    return len(matrix), len(matrix[0])


def _sum(values, zero):
    result = zero
    for value in values:
        result = result + value
    return result


def _columns(columns):
    result = tuple(zip(*columns, strict=True))
    _shape(result)
    return result


def _multiply(left, right):
    lr, lc = _shape(left)
    rr, rc = _shape(right)
    if lc != rr or left[0][0].bits != right[0][0].bits:
        raise ValueError("matrix multiplication has incompatible dimensions or precision")
    zero = left[0][0]._coerce(0)
    return tuple(tuple(_sum((left[i][k] * right[k][j] for k in range(lc)), zero)
                       for j in range(rc)) for i in range(lr))


def _add(left, right):
    if _shape(left) != _shape(right):
        raise ValueError("matrix addition has incompatible dimensions")
    return tuple(tuple(a + b for a, b in zip(x, y, strict=True))
                 for x, y in zip(left, right, strict=True))


def _negative(matrix):
    return tuple(tuple(-c for c in row) for row in matrix)


@cache
def _determinant_formula(size):
    """Reuse the exact polynomial determinant rather than reimplement its signs."""

    if type(size) is not int or not 1 <= size <= 3:
        raise ValueError("actual constituent pivot determinants have sizes one through three")
    variables = tuple(Polynomial.monomial(tuple(int(i == j) for j in range(size**2)),
                                          scalar_type=Eisenstein) for i in range(size**2))
    return determinant(tuple(variables[i * size:(i + 1) * size] for i in range(size)))


def _determinant(matrix):
    rows, columns = _shape(matrix)
    if rows != columns:
        raise ValueError("pivot determinant requires a square matrix")
    return bounds.polynomial_value(_determinant_formula(rows),
                                    tuple(c for row in matrix for c in row))


def _inverse(matrix):
    """Adjugate enclosure, admitted only when its determinant excludes zero.

    This is not midpoint inversion or a small-residual heuristic. The exact
    adjugate identity holds throughout every accepted matrix enclosure.
    """

    size, columns = _shape(matrix)
    if size != columns:
        raise ValueError("pivot inversion requires a square matrix")
    inverse_det = _determinant(matrix).inverse()
    if size == 1:
        return ((inverse_det,),)
    return tuple(tuple(_determinant(tuple(tuple(matrix[r][c] for c in range(size) if c != i)
                                           for r in range(size) if r != j))
                       * ((-1)**(i + j)) * inverse_det
                       for j in range(size)) for i in range(size))


def _quotient(matrix, pivots):
    rows, columns = _shape(matrix)
    if (not isinstance(pivots, tuple) or len(pivots) != columns
        or any(type(i) is not int or not 0 <= i < rows for i in pivots)
        or len(set(pivots)) != columns):
        raise ValueError("explicit distinct constituent relation pivot rows are required")
    free = tuple(i for i in range(rows) if i not in pivots)
    scalar = matrix[0][0]._coerce
    selector = tuple(tuple(scalar(int(i == j)) for j in range(rows)) for i in pivots)
    inclusion = tuple(tuple(scalar(int(i == j)) for j in range(rows)) for i in free)
    split = _multiply(_inverse(tuple(matrix[i] for i in pivots)), selector)
    remainder = tuple(matrix[i] for i in free)
    projection = _add(inclusion, _negative(_multiply(remainder, split)))
    return projection, split, free


@cache
def _relation_cochains(chart):
    """Compile ORIGINAL differential/cup columns once per declared cover chart."""

    first = fiber.lifts.first._context()[0]
    second = fiber.lifts.second._context()[0]
    indices = tuple(
        tuple(i for i, o in enumerate(c.left.objects) if o.position == -1)
        for c in (first, second)
    )
    if indices != ((4, 5), (5, 6, 7)):
        raise ValueError("the actual nine-generator/five-relation ordering changed")
    generators = tuple(tuple(fiber.relation_generator_in_chart(chart, context, i)
                             for i in objects)
                       for context, objects in zip((first, second), indices, strict=True))
    relations = tuple(tuple(context.differential(g) for g in inputs)
                      for context, inputs in zip((first, second), generators, strict=True))
    outer = tuple(tuple(mixed_outer_cup(e, g) for g in generators[1])
                  for e in fiber.lifts._inputs()[2])
    return first, second, relations, outer


def local_presentation(point):
    """Bound every original local relation coefficient, including both outer blocks."""

    if not isinstance(point, bounds.BoundedCoverPoint):
        raise TypeError("an actual certified bounded cover point is required")
    first, second, relations, outer = _relation_cochains(point.chart)
    b1, b2 = tuple(_columns(tuple(bounds.local_cochain_coordinates(c, point, context)
                                 for c in columns))
                   for context, columns in zip((first, second), relations, strict=True))
    extensions = tuple(_columns(tuple(bounds.local_cochain_coordinates(c, point, first)
                                      for c in columns)) for columns in outer)
    return b1, b2, extensions


@dataclass(frozen=True, slots=True)
class BoundedFiberFrame:
    """An actual universal quotient with explicit rows and named free generators.

    Parameter coefficients are kept in the order (constant,a0,a1). Membership
    and identities follow from the original exact construction and the block
    elimination theorem, not from interval residuals containing zero.
    """

    point: bounds.BoundedCoverPoint
    first_pivots: tuple[int, int]
    second_pivots: tuple[int, int, int]
    basis_labels: tuple[str, ...] = field(init=False)
    relations: tuple = field(init=False)
    projections: tuple = field(init=False)
    inclusion: tuple = field(init=False)
    relation_minor: bounds.Ball = field(init=False)

    def __post_init__(self):
        b1, b2, outer = local_presentation(self.point)
        p1, _split1, free1 = _quotient(b1, self.first_pivots)
        p2, split2, free2 = _quotient(b2, self.second_pivots)
        scalar = self.point.x[0]._coerce
        z, one = scalar(0), scalar(1)
        b0 = tuple((*row, z, z, z) for row in b1) + tuple((z, z, *row) for row in b2)
        bi = tuple(tuple((z, z, *row) for row in e) + ((z,) * 5,) * 5 for e in outer)
        q0 = tuple((*row, z, z, z, z, z) for row in p1)
        q0 += tuple((z, z, z, z, *row) for row in p2)
        corrections = tuple(_negative(_multiply(_multiply(p1, e), split2)) for e in outer)
        qi = tuple(tuple((z, z, z, z, *row) for row in c) + ((z,) * 9,) * 2
                   for c in corrections)
        free = free1 + tuple(4 + i for i in free2)
        inclusion = tuple(tuple(one if i == j else z for j in free) for i in range(9))
        minor = (_determinant(tuple(b1[i] for i in self.first_pivots))
                 * _determinant(tuple(b2[i] for i in self.second_pivots)))
        if minor.center.norm() <= minor.radius**2:
            raise ZeroDivisionError("the universal relation-minor enclosure may contain zero")
        objects = fiber.lifts.first._context()[0].left.objects
        second_objects = fiber.lifts.second._context()[0].left.objects
        labels = tuple(f"V1:{objects[i].name}" for i in free1)
        labels += tuple(f"V2:{second_objects[i].name}" for i in free2)
        for name, value in (("basis_labels", labels), ("relations", (b0, *bi)),
                            ("projections", (q0, *qi)), ("inclusion", inclusion),
                            ("relation_minor", minor)):
            object.__setattr__(self, name, value)

    def evaluate_basis(self, index):
        """Bound an ORIGINAL universal section on demand, without selecting a0,a1.

        This uses the full original cochain constructor. It does not yet give
        compressed full-basis throughput or materialize the 5345-column matrix.
        """

        return self._evaluate_section(fiber.lifts.universal_section(index))

    def _evaluate_section(self, section):
        """Reuse an original already-constructed cochain; never a center specialization."""

        if not isinstance(section, fiber.lifts.UniversalMetricSection):
            raise TypeError("the original universal section coefficient object is required")
        first, second = fiber.lifts.first._context()[0], fiber.lifts.second._context()[0]
        scalar = self.point.x[0]._coerce
        zero_tail = (scalar(0),) * 5
        ambient = (_columns((bounds.local_cochain_coordinates(section.first_constant,
                                                              self.point, first)
                             + bounds.local_cochain_coordinates(section.second_constant,
                                                                 self.point, second),)),
                   *(_columns((bounds.local_cochain_coordinates(c, self.point, first) + zero_tail,))
                     for c in section.first_coefficients))
        return (_multiply(self.projections[0], ambient[0]), *(
            _add(_multiply(self.projections[0], v), _multiply(q, ambient[0]))
            for q, v in zip(self.projections[1:], ambient[1:], strict=True)
        ))

    def transition_to(self, other):
        if not isinstance(other, BoundedFiberFrame) or self.point != other.point:
            raise ValueError("frame transitions require the identical certified point and chart")
        return tuple(_multiply(q, self.inclusion) for q in other.projections)


def _matrix_record(matrix):
    return [[bounds._ball_record(c) for c in row] for row in matrix]


def fiber_artifact():
    """Archive declared complete-frame probes, not a metric or sampled trajectory."""

    parent_digest, parent = fiber._verified_payload(bounds.OUTPUT)
    if parent.get("schema") != "alternate-metric-enclosures-v1":
        raise ValueError("the certified geometric enclosure prerequisite is absent")
    root_digest, root_parent = fiber._verified_payload(bounds.roots.OUTPUT)
    exact_fiber_digest, _exact_fiber = fiber._verified_payload(fiber.OUTPUT)
    records = []
    from fractions import Fraction

    sections = tuple(fiber.lifts.universal_section(i) for i in (0, 2655))
    for raw in root_parent["actual_configurations"]:
        def scalar(pair):
            return Eisenstein(Fraction(pair[0]), Fraction(pair[1]))

        lines = tuple(bounds.roots.ProjectiveLine(*(tuple(scalar(c) for c in v) for v in raw[key]))
                      for key in ("first_line", "second_line"))
        policy = bounds.roots.RootPolicy(Fraction(1, 2**30), 60, 80, 128)
        intersection = bounds.roots.intersection_roots(
            *lines, tuple(scalar(c) for c in raw["P1_point"]),
            parameter_pivots=(raw["first"]["parameter_pivot"], raw["second"]["parameter_pivot"]),
            policy=policy,
        )
        pair = (0, 0) if raw["name"] == "finite_chart" else ("infinity", 0)
        chart = (0, 0, 0) if raw["name"] == "finite_chart" else (1, 0, 1)
        point = bounds.BoundedCoverPoint(intersection, pair, chart, 80)
        # Mathematical frame choices are declared, never chosen by measured data.
        frame = BoundedFiberFrame(point, (0, 2), (0, 1, 2))
        records.append({
            "name": raw["name"], "root_pair": list(pair), "chart_pivots": list(chart),
            "first_pivot_rows": list(frame.first_pivots),
            "second_pivot_rows": list(frame.second_pivots),
            "fiber_basis_labels": list(frame.basis_labels),
            "relations_constant_a0_a1": [_matrix_record(m) for m in frame.relations],
            "projections_constant_a0_a1": [_matrix_record(m) for m in frame.projections],
            "inclusion": _matrix_record(frame.inclusion),
            "relation_minor": bounds._ball_record(frame.relation_minor),
            "actual_universal_section_probes": [{
                "basis_index": section.basis_index,
                "coefficient_columns_constant_a0_a1": [
                    _matrix_record(m) for m in frame._evaluate_section(section)
                ],
            } for section in sections],
        })
    payload = {
        "schema": "alternate-metric-bounded-fibers-v1",
        "enclosure_artifact_digest": parent_digest, "root_artifact_digest": root_digest,
        "original_fiber_evaluation_artifact_digest": exact_fiber_digest,
        "parameter_basis": ["a0", "a1"], "bound_bits": 80,
        "construction": "same actual differential and outer cup; determinant-certified elimination",
        "actual_frame_probes": records,
        "bounded_universal_fiber_frame_available": True,
        "on_demand_original_cochain_section_bounds_available": True,
        "complete_bounded_5345_column_matrix_materialized": False,
        "compressed_complete_section_enclosure_engine_available": False,
        "bounded_section_and_density_evaluation_available": False,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "vacuum_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "extend the certified finite-support evaluator to bounded full-basis evaluation; "
            "control SU-uniform proposal precision and integration error, then metric convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    payload = fiber_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = write_artifact()
    print(f"artifact_digest: {result['artifact_digest']}")
