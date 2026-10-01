"""Independently check actual local universal rank-four section evaluation.

Owns:
    Direct arrow specialization, symbolic boundary and frame identities,
    exact point/normalization rejection, and actual section-spanning evidence.

Depends on:
    The actual research fiber evaluator, saved constituent/outer data, and
    independent sparse-polynomial determinant and product calculations.

Must not:
    Choose physical moduli, turn four columns into a global metric certificate,
    infer numerical convergence, or identify holomorphic and physical Yukawas.

Phase 0:
    Research fiber-evaluation tests only; physical metrics remain unavailable.
"""

import hashlib
import json
from dataclasses import FrozenInstanceError

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.math.polynomials import Polynomial, PolynomialMatrix, determinant
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _eisenstein_text,
)
from research.experiments.scientific_genesis import alternate_metric_fiber_evaluation as fiber


def _point(chart=1):
    if chart == 1:
        return fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    return fiber.CoverPoint((1, 1, 1), (1, -1, 0), (1, 0), (0, 0, 0))


def _polynomial_matrix(coefficients):
    """Construct the parameter matrix in a distinct polynomial arithmetic path."""

    return PolynomialMatrix(tuple(tuple(sum((
        Polynomial.monomial(m, matrix[i][j], scalar_type=Eisenstein)
        for m, matrix in zip(((0, 0), (1, 0), (0, 1)), coefficients, strict=True)
    ), Polynomial.zero(2, scalar_type=Eisenstein)) for j in range(coefficients[0].column_count))
        for i in range(coefficients[0].row_count)))


def _direct_relations(point, context):
    """Specialize raw arrow data, without invoking the complex differential."""

    objects = context.left.objects
    rows = [[Eisenstein(0) for o in objects if o.position == -1]
            for o in objects if o.position == 0]
    offset = len(rows)
    for arrow in context.left.resolution_arrows:
        coordinates = point.x if arrow.factor == 1 else point.u
        value = arrow.polynomial.substitute(coordinates).coefficient(())
        rows[arrow.target][arrow.source - offset] += value * point.line_frame(
            objects[arrow.source].line_degree,
        ) / point.line_frame(objects[arrow.target].line_degree)
    for term in context.left.extension_terms:
        if term.cell != point.cell or term.koszul_degree != 0 or term.cech_degree != 0:
            continue
        assert term.parent_degree == 1
        rows[term.target][term.source - offset] += term.coefficient * point.monomial(
            term.x_monomial + term.u_monomial + term.p_monomial,
        ) * point.line_frame(objects[term.source].line_degree) / point.line_frame(
            objects[term.target].line_degree,
        )
    return Matrix(rows, scalar_type=Eisenstein)


def _polynomial_section_value(record, point, dimension):
    """Dehomogenize saved sections in five variables, independently of Laurent evaluation."""

    pivots = (point.chart[0], 3 + point.chart[1], 6 + point.chart[2])
    coordinates = (*point.x, *point.u, *point.p)
    affine = tuple(c / coordinates[pivot] for group, pivot in zip(
        (range(3), range(3, 6), range(6, 8)), pivots, strict=True,
    ) for i in group if i != pivot for c in (coordinates[i],))
    polynomials = [Polynomial.zero(5, scalar_type=Eisenstein) for _ in range(dimension)]
    for index, monomial, chart, coefficient in record["terms"]:
        if chart == point.chart[2]:
            powers = tuple(e for i, e in enumerate(monomial) if i not in pivots)
            polynomials[index] += Polynomial.monomial(powers, Eisenstein(*coefficient),
                                                      scalar_type=Eisenstein)
    return Matrix(tuple((p.substitute(affine).coefficient(()),) for p in polynomials),
                  scalar_type=Eisenstein)


@pytest.mark.parametrize("chart", (0, 1))
def test_relations_are_the_actual_vertex_arrows_not_a_direct_sum(chart):
    point = _point(chart)
    first = fiber.lifts.first._context()[0]
    second = fiber.lifts.second._context()[0]
    b1, b2, outer = fiber.local_presentation(point)
    assert b1 == _direct_relations(point, first)
    assert b2 == _direct_relations(point, second)
    assert b1.rank() == 2 and b2.rank() == 3
    for parameter, extension in enumerate(fiber.lifts._inputs()[2]):
        rows = [[Eisenstein(0) for _ in range(3)] for _ in range(4)]
        for basis, coefficient in extension.terms:
            c = basis.component
            if basis.cell != point.cell or c.koszul_summand != "k0" or c.object_degree != 1:
                continue
            assert c.left_index < 4 and c.right_index >= 5
            rows[c.left_index][c.right_index - 5] += coefficient * point.monomial(
                basis.x_monomial + basis.u_monomial + basis.p_monomial,
            ) * point.line_frame(second.left.objects[c.right_index].line_degree) / point.line_frame(
                first.left.objects[c.left_index].line_degree,
            )
        assert outer[parameter] == Matrix(rows, scalar_type=Eisenstein)
    assert all(not e.is_zero() for e in outer)


@pytest.mark.parametrize("chart", (0, 1))
def test_symbolic_fiber_quotient_annihilates_all_actual_boundaries(chart):
    point = _point(chart)
    choices = fiber.admissible_pivots(point)
    frame = fiber.fiber_frame(point, choices[0][0], choices[1][0])
    b = _polynomial_matrix(frame.relations)
    q = _polynomial_matrix(frame.projections)
    assert q.compose(b).is_zero()
    pivots = frame.first_pivots + tuple(4 + i for i in frame.second_pivots)
    assert determinant(tuple(b.rows[i] for i in pivots)) == Polynomial.monomial(
        (0, 0), frame.relation_minor, scalar_type=Eisenstein,
    )
    assert not frame.relation_minor.is_zero()
    assert frame.projections[0].matmul(frame.inclusion) == Matrix.identity(
        4, scalar_type=Eisenstein,
    )
    assert all(p.matmul(frame.inclusion).is_zero() for p in frame.projections[1:])


def test_explicit_quotient_frame_changes_obey_inverse_and_cocycle_identities():
    point = _point()
    choices = fiber.admissible_pivots(point)
    frames = tuple(fiber.fiber_frame(point, choices[0][i], choices[1][i]) for i in range(3))
    transitions = {
        (i, j): _polynomial_matrix(frames[i].transition_to(frames[j]))
        for i in range(3) for j in range(3)
    }
    for i in range(3):
        assert transitions[i, i].rows == tuple(tuple(Polynomial.monomial(
            (0, 0), int(row == col), scalar_type=Eisenstein,
        ) for col in range(4)) for row in range(4))
        for j in range(3):
            assert transitions[i, j].compose(_polynomial_matrix(frames[i].projections)).rows == (
                _polynomial_matrix(frames[j].projections).rows
            )
            for k in range(3):
                assert transitions[j, k].compose(transitions[i, j]).rows == transitions[i, k].rows


def test_projective_rescaling_preserves_declared_chart_line_coefficients():
    point = _point()
    rescaled = fiber.CoverPoint(tuple(2 * c for c in point.x), tuple(OMEGA * c for c in point.u),
                               tuple(5 * c for c in point.p), point.chart)
    assert fiber.local_presentation(rescaled) == fiber.local_presentation(point)
    record = fiber.lifts._inputs()[1][0][0]
    context = fiber.lifts.first._context()[0]
    assert fiber.compact_coordinates(record, rescaled, context) == fiber.compact_coordinates(
        record, point, context,
    )
    expanded = fiber.lifts.first.expand_section(fiber.lifts._compact(record))
    assert fiber.local_coordinates(expanded, point, context) == fiber.compact_coordinates(
        record, point, context,
    )
    with pytest.raises(ValueError, match="incompatible"):
        fiber.local_coordinates(expanded, point, fiber.lifts.second._context()[0])


def test_exact_point_pole_and_fiber_basis_choices_fail_closed():
    with pytest.raises(ValueError, match="both actual Schoen"):
        fiber.CoverPoint((1, 1, 1), (1, 1, 1), (1, 1), (0, 0, 0))
    with pytest.raises(ValueError, match="absent"):
        fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 0))
    with pytest.raises(ValueError, match="integer"):
        fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (True, 0, 1))
    with pytest.raises(TypeError):
        fiber.CoverPoint((1.0, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    point = _point()
    with pytest.raises(ValueError, match="pole"):
        point.monomial((0, 0, -1, 0, 0, 0, 0, 0))
    with pytest.raises(ValueError, match="distinct"):
        fiber.fiber_frame(point, (0, 0), (0, 1, 2))
    frame = fiber.fiber_frame(point, (0, 2), (0, 1, 2))
    with pytest.raises(FrozenInstanceError):
        frame.basis_labels = ("hidden choice",)
    other_point = _point(0)
    other_pivots = fiber.admissible_pivots(other_point)
    other_frame = fiber.fiber_frame(other_point, other_pivots[0][0], other_pivots[1][0])
    with pytest.raises(ValueError, match="same point"):
        frame.transition_to(other_frame)


def test_actual_four_section_archive_spans_for_all_symbolic_parameters():
    payload = json.loads(fiber.OUTPUT.read_text())
    digest = payload.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                               ).encode()).hexdigest()
    frame = fiber.fiber_frame(_point(), (0, 2), (0, 1, 2))
    assert payload["actual_basis_indices"] == list(fiber.spanning_indices(frame))
    assert payload["quotient_coefficients_constant_a0_a1"] == list(map(
        fiber._matrix_record, frame.projections,
    ))
    assert payload["relation_coefficients_constant_a0_a1"] == list(map(
        fiber._matrix_record, frame.relations,
    ))
    coefficients = tuple(Matrix(tuple(tuple(_eisenstein_text(c) for c in row) for row in rows),
                                scalar_type=Eisenstein)
                         for rows in payload["actual_section_coefficients_constant_a0_a1"])
    streams = fiber.lifts._inputs()[1]
    for column, index in enumerate(payload["actual_basis_indices"]):
        if index < 2655:
            local = _polynomial_section_value(streams[0][index], frame.point, 4)
            ambient = Matrix((*local.rows, *((Eisenstein(0),),) * 5), scalar_type=Eisenstein)
            expected = frame.projections[0].matmul(ambient)
            assert tuple(row[column] for row in coefficients[0].rows) == tuple(
                row[0] for row in expected.rows
            )
            assert all(row[column].is_zero() for m in coefficients[1:] for row in m.rows)
        else:
            local = _polynomial_section_value(streams[1][index - 2655], frame.point, 5)
            ambient = Matrix((*((Eisenstein(0),),) * 4, *local.rows), scalar_type=Eisenstein)
            expected = frame.projections[0].matmul(ambient)
            assert tuple(row[column] for row in coefficients[0].rows) == tuple(
                row[0] for row in expected.rows
            )
            assert all(m[i][column].is_zero() for m in coefficients[1:] for i in (2, 3))
    assert determinant(_polynomial_matrix(coefficients).rows) == Polynomial.monomial(
        (0, 0), _eisenstein_text(payload["actual_section_determinant_all_parameters"]),
        scalar_type=Eisenstein,
    )
    assert not coefficients[0].determinant().is_zero()
    for key in ("numerical_metrics_available", "physical_yukawas_available",
                "extension_point_selected", "observational_inputs_used",
                "complete_5345_column_point_matrix_materialized"):
        assert payload[key] is False
