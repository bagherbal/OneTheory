"""Test finite-pole evaluation against the actual uncompressed section data.

Owns:
    Exact operator naturality with retained Laurent poles, full-cochain fiber
    comparisons, and agreement with every archived point-matrix column.

Depends on:
    Actual source-module terms, original homotopy and perturbation, the frozen
    universal basis, and independent original evaluator artifacts.

Must not:
    Interpret operator units as physical sections, infer metric convergence,
    hide coordinate normalizations, or select extension parameters.

Phase 0:
    Research representation tests; controlled numerical sampling is unresolved.
"""

import gzip
import json

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
    _homotopy,
)
from research.experiments.scientific_genesis import alternate_metric_support_evaluation as support

regular = support.regular


@pytest.fixture(scope="module")
def engine():
    point = regular.fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    return support.SupportEvaluator(regular.fiber.fiber_frame(point, (0, 2), (0, 1, 2)))


def _units():
    """Recover operator units with multiple pole sectors from actual source terms."""

    source = regular.fiber.lifts.second._context()[0]
    target = regular.fiber.lifts.first._context()[0]
    selected = {}
    for extension in regular.fiber.lifts._inputs()[2]:
        for b, c in extension.terms:
            right = b.component.right_index
            if right >= 5:
                continue
            key = (b.component.left_index, b.component.koszul_summand,
                   tuple(e < 0 for e in b.x_monomial), tuple(map(len, b.cell)))
            if key in selected:
                continue
            dx, du, dp = source.left.objects[right].line_degree
            component = target.components[b.component.left_index, 0, b.component.koszul_summand]
            selected[key] = SparseOuterCechCochain(((OuterCechBasis(
                component, (b.x_monomial[0] + dx, *b.x_monomial[1:]),
                (b.u_monomial[0] + du, *b.u_monomial[1:]),
                (b.p_monomial[0] + dp, b.p_monomial[1]), b.cell,
            ), c),))
    return tuple(selected.values())


def test_partial_regular_encoding_commutes_with_actual_operators(engine):
    units = _units()
    assert len(units) > 10
    # Nonunit coordinates attack discarded-power errors in the operator
    # identity. These are algebraic functionals, not invented cover points.
    x = tuple(Eisenstein(c) for c in (2, 3, 5))
    u = tuple(Eisenstein(c) for c in (7, 11, 13))
    operator = support._SupportPerturbation(engine.target, x, u)

    def encode(cochain):
        return support.encode_x(regular._encode(cochain, u), x)

    for unit in units:
        assert encode(_homotopy(unit)) == _homotopy(encode(unit))
        assert encode(engine.target.perturbation(unit)) == operator.perturbation(encode(unit))
        # Compilation remains an exact linear operator on arbitrary coefficients.
        assert operator.perturbation(encode(unit).scale(Eisenstein(2, 3))) == (
            operator.perturbation(encode(unit)).scale(Eisenstein(2, 3))
        )
    assert operator.column_images


def test_finite_support_evaluator_reproduces_full_cochain_probes(engine):
    _, parent = regular.fiber._verified_payload(regular.fiber.OUTPUT)
    for col, index in enumerate(parent["actual_basis_indices"]):
        expected = [
            [[parent["actual_section_coefficients_constant_a0_a1"][p][row][col]]
             for row in range(4)] for p in range(3)
        ]
        assert [regular.fiber._matrix_record(m) for m in engine.evaluate_basis(index)] == expected
    assert len(engine.residual_values) < len(engine.unit_values)
    assert sum(len(o.column_images) for o in engine.operators) > 0


def test_poles_are_retained_until_a_valid_chart_evaluation(engine):
    unit = next(unit for unit in _units() if unit.terms[0][0].x_monomial[2] < 0)
    # A zero coordinate with a negative exponent is retained symbolically,
    # never divided by. Some regular factors can legitimately make it vanish.
    x = tuple(Eisenstein(c) for c in (1, 1, 0))
    encoded = support.encode_x(unit, x)
    assert not encoded.is_zero()
    for original, _ in unit.terms:
        for b, _ in encoded.terms:
            assert tuple(min(e, 0) for e in b.x_monomial) == tuple(
                min(e, 0) for e in original.x_monomial
            )
            assert sum(b.x_monomial) == original.component.ambient_degree[0]


def test_complementary_chart_matches_actual_full_cochain_section():
    point = regular.fiber.CoverPoint((1, 1, 1), (1, -1, 0), (1, 0), (0, 0, 0))
    frame = regular.fiber.fiber_frame(point, (0, 2), (0, 1, 2))
    engine = support.SupportEvaluator(frame)
    assert engine.evaluate_basis(2670) == frame.evaluate_basis(2670)


def test_every_column_agrees_with_the_complete_independent_point_archive(engine):
    _, payload = regular.fiber._verified_payload(regular.OUTPUT)
    columns = json.loads(gzip.decompress(regular.MATRIX.read_bytes()))
    assert payload["section_count"] == len(columns) == 5345
    for index, expected in enumerate(columns):
        assert [regular.fiber._matrix_record(m) for m in engine.evaluate_basis(index)] == expected
