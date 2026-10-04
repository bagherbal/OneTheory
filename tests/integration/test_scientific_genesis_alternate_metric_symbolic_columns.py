"""Attack original coefficient-ring compilation with independent full cochains.

Owns:
    Exact archive comparisons, uncertain off-center functional checks, original
    operator naturality, chart/zero safety and immutable source identity checks.

Depends on:
    The original section archive, full corrected cochains, raw-arrow Gaussian
    quotient, certified frames and exact symbolic coefficient-ring compilation.

Must not:
    Treat probe coverage as full execution, arithmetic witnesses as selected
    moduli, or polynomial evaluation as a converged physical metric.

Phase 0:
    Research compiler verification; sampling and physical normalization are open.
"""

import gzip
import json
from dataclasses import FrozenInstanceError, replace
from functools import cache

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial
from onetheory.math.sheaves import LaurentPolynomial
from research.experiments.scientific_genesis import alternate_metric_symbolic_columns as module
from tests.integration.test_scientific_genesis_alternate_metric_bounded_support import (
    actual_units as source_units,
)
from tests.integration.test_scientific_genesis_alternate_metric_bounded_support import (
    exact_engine,
)
from tests.integration.test_scientific_genesis_uncertain_cover_frames import (
    _contains,
    _dehomogenized_coefficients,
    _full_boundary,
    _functional,
    _specialize,
)


@cache
def _compiler(chart=(0, 0, 0)):
    return module.SymbolicCompiler(chart)


@cache
def _exact():
    return exact_engine.__wrapped__().frame


@pytest.fixture(scope="module")
def actual_units():
    return source_units.__wrapped__()


@pytest.mark.parametrize("index", (0, 1273, 2655, 3790, 5344))
def test_symbolic_columns_match_independently_archived_exact_sections(index):
    frame = _exact()
    compiled = _compiler(frame.point.chart).compile_basis(index)
    actual = compiled.evaluate(frame, source_signature=module._source_signature())
    expected = json.loads(gzip.decompress(module.original.support.regular.MATRIX.read_bytes()))
    assert [[str(c.center) for row in m for c in row] for m in actual] == (
        [[row[0] for row in m] for m in expected[index]])
    assert all(c.radius == 0 for m in actual for row in m for c in row)
    assert compiled.basis_index == index
    assert all(isinstance(p, Polynomial) and p.scalar_type is Eisenstein
               for group in (compiled.constant_generators, *compiled.first_parameter_generators)
               for p in group)


@pytest.mark.parametrize("domain_index", (0, 9, 12))
def test_same_compiled_column_contains_independent_native_full_cochain_functionals(domain_index):
    _, _, frame = module.domains.declared_frames()[domain_index]
    compiler = _compiler()
    column = compiler.compile_basis(2655)
    before = len(compiler.functional_values), len(compiler.unit_values)
    coefficients = compiler.evaluate_basis(frame, 2655)
    assert (len(compiler.functional_values), len(compiler.unit_values)) == before
    assert compiler.compile_basis(2655) is column
    section = module.domains.original_section(2655)
    contexts = (module.original.fiber.lifts.first._context()[0],
                module.original.fiber.lifts.second._context()[0])
    for offset in (0, 1):
        values = _functional(frame, offset)
        constant = (_dehomogenized_coefficients(section.first_constant, values,
                                                frame.point, contexts[0])
                    + _dehomogenized_coefficients(section.second_constant, values,
                                                  frame.point, contexts[1]))
        corrections = tuple(_dehomogenized_coefficients(c, values, frame.point, contexts[0])
                            + (Eisenstein(0),) * 5 for c in section.first_coefficients)
        for a0, a1 in ((Eisenstein(1), OMEGA), (OMEGA, Eisenstein(2, -1))):
            _, quotient = _full_boundary(values, frame, a0, a1)
            full = Matrix(tuple((c + a0*x + a1*y,) for c, x, y in zip(
                constant, *corrections, strict=True)), scalar_type=Eisenstein)
            _contains(_specialize(coefficients, a0, a1), quotient.matmul(full))


def test_symbolic_operator_uses_original_unit_columns_and_regular_ring(actual_units):
    compiler = _compiler()
    # Compilation is in the explicitly normalized chart coefficient ring.
    # Nonpivot coordinates are arbitrary exact arithmetic witnesses, not
    # selected geometric points; only certified chart pivots equal one.
    coordinates = tuple(module.original.bounds.Ball(Eisenstein(
        1 if index in compiler.normalized_pivots else value), 0, 80)
        for index, value in enumerate((2, 3, 5, 7, 11, 13, 17, 19)))

    def evaluate(cochain):
        return module.original.BoundedCoefficients(tuple((b,
            module.original.bounds.polynomial_value(p, coordinates)) for b, p in cochain.terms),
            bits=80)

    # The representative unit set includes every encountered original support
    # pattern in the actual outer source, rather than selected physical data.
    assert len(actual_units) > 10
    for power in range(3):
        xs, us = coordinates[:3], coordinates[3:6]
        for _ in range(power):
            xs = module.original._pullback(xs, compiler.action.x_images)
            us = module.original._pullback(us, compiler.action.u_images)
        operator = module.original._BoundedPerturbation(compiler.target, xs, us)
        for unit in actual_units:
            terms = []
            for b, c in unit.terms:
                source = module.original.OuterCechBasis(b.component, b.x_monomial,
                    (sum(b.u_monomial), 0, 0), b.p_monomial, b.cell)
                encoded, positive = module.original.support._x_pole_encoding(source)
                terms.append((encoded, compiler.channel_monomial(power, positive, b.u_monomial, c)))
            symbolic = module.PolynomialCoefficients(tuple(terms))
            assert evaluate(module._homotopy(symbolic)) == (
                module.original.bounded_homotopy(evaluate(symbolic)))
            assert evaluate(compiler.operators[power].perturbation(symbolic)) == (
                operator.perturbation(evaluate(symbolic)))


@pytest.mark.parametrize("chart", ((0, 0), (True, 0, 0), (3, 0, 0), (0, 0, 2), [0, 0, 0]))
def test_invalid_or_aliased_charts_fail_closed(chart):
    with pytest.raises(ValueError, match="chart pivots"):
        module.SymbolicCompiler(chart)


@pytest.mark.parametrize("index", (-1, 5345, True, 0.0))
def test_original_basis_range_is_not_relabeled(index):
    with pytest.raises(ValueError, match="ORIGINAL basis"):
        _compiler().compile_basis(index)


def test_compiled_source_identity_is_immutable_and_not_a_point_stream_digest(monkeypatch):
    compiler = _compiler()
    column = compiler.compile_basis(0)
    assert isinstance(column.source_signature, tuple)
    assert all(isinstance(part, tuple) for part in column.source_signature)
    with pytest.raises(FrozenInstanceError):
        column.basis_index = 1
    with pytest.raises(ValueError, match="source identity and chart"):
        column.evaluate(_exact(), source_signature=column.source_signature)
    frame = module.domains.declared_frames()[0][2]
    with pytest.raises(ValueError, match="source identity and chart"):
        column.evaluate(frame, source_signature=())
    with pytest.raises(TypeError, match="quotient frame"):
        column.evaluate(object(), source_signature=column.source_signature)
    monkeypatch.setattr(module, "_source_signature", lambda: ())
    with pytest.raises(ValueError, match="source changed"):
        compiler.evaluate_basis(frame, 0)


def test_chart_normalization_never_inverts_a_zero_nonpivot():
    compiler = _compiler()
    pivot = module._monomial((-7, 0, 0, -3, 0, 0, -2, 0))
    assert compiler._regular_polynomial(pivot) == Polynomial.one(8, scalar_type=Eisenstein)
    with pytest.raises(ValueError, match="pole escaped"):
        compiler._regular_polynomial(module._monomial((0, -1, 0, 0, 0, 0, 0, 0)))
    value = compiler._regular_polynomial(module._monomial((0, 1, 0, 0, 0, 0, 0, 0)))
    assert value.substitute((1, 0, 2, 1, 3, 4, 1, 5)).is_zero()
    with pytest.raises(ValueError, match="regular coordinate"):
        compiler.channel_monomial(0, (-1, 0, 0), (0, 0, 0))


def test_symbolic_coefficients_are_exact_and_only_remove_exact_zeros(actual_units):
    basis = actual_units[0].terms[0][0]
    one = module._monomial((0,) * 8)
    coefficient = module.PolynomialCoefficients(((basis, one), (basis, one.scale(-1))))
    assert coefficient.is_zero()
    coefficient = module.PolynomialCoefficients(((basis, one.scale(Eisenstein(Rational(1, 3)))),))
    with pytest.raises(FrozenInstanceError):
        coefficient.terms = ()
    with pytest.raises(TypeError, match="coefficient ring"):
        module.PolynomialCoefficients(((basis, LaurentPolynomial.one(8)),))
    with pytest.raises(ValueError, match="Laurent poles"):
        module.PolynomialCoefficients(((basis, module._monomial((-1,) + (0,) * 7)),))
    with pytest.raises(TypeError, match="representation"):
        coefficient + object()


@pytest.mark.parametrize("change", (
    {"basis_index": True}, {"constant_generators": ()},
    {"first_parameter_generators": ()}, {"chart": (True, 0, 0)},
    {"constant_generators": (Polynomial.one(8),) * 9},
    {"source_signature": ((["mutable", "pair"],), ())},
))
def test_compiled_columns_reject_aliases_mutable_shapes_and_wrong_scalar_rings(change):
    with pytest.raises(ValueError):
        replace(_compiler().compile_basis(0), **change)


def test_removing_original_dummy_phase_changes_the_exact_functional(monkeypatch):
    compiler = _compiler()
    compiler.compile_basis(2655)
    key, expected = next((key, value) for key, value in compiler.functional_values.items()
                         if key[0] == 1 and any(not p.is_zero() for p in value))
    original_phase = module.original._artificial_deck_phase
    monkeypatch.setattr(module.original, "_artificial_deck_phase",
                        lambda *args: original_phase(*args) * OMEGA)
    compiler.functional_values.pop(key)
    try:
        wrong = compiler._functional(*key)
        assert wrong != expected
        assert wrong == tuple(p.scale(Eisenstein(1) / OMEGA) for p in expected)
    finally:
        compiler.functional_values[key] = expected


@pytest.mark.parametrize("attack", ("index_alias", "shape", "duplicate", "coefficient_alias",
                                   "wrong_pivot", "nonzero_outer", "extra_field"))
def test_independent_symbolic_stream_parser_rejects_aliased_or_reinterpreted_columns(attack):
    column = _compiler().compile_basis(0)
    record = module.column_record(column)
    if attack == "index_alias":
        record["basis_index"] = False
    elif attack == "shape":
        record["constant_generators"] = []
    elif attack == "extra_field":
        record["geometry_selector"] = "invented"
    else:
        if attack == "nonzero_outer":
            record["first_parameter_generators"][0][0] = [[[0] * 8, ["1", "0"]]]
        else:
            nonzero = next(p for p in record["constant_generators"] if p)
            if attack == "duplicate":
                nonzero.append(nonzero[0])
            elif attack == "coefficient_alias":
                nonzero[0][1][0] = 1
            else:
                nonzero[0][0][0] = 1
    with pytest.raises((ValueError, TypeError)):
        module.parse_column(record, index=0, chart=column.chart,
                            source_signature=column.source_signature)


def test_truncated_symbolic_archive_is_not_complete_execution(tmp_path):
    column = _compiler().compile_basis(0)
    path = tmp_path / "one-column.gz"
    path.write_bytes(gzip.compress(module.archive._canonical(module.column_record(column)) + b"\n"))
    with pytest.raises(ValueError, match="all 5345"):
        module.verify_archive(path, chart=column.chart, source_signature=column.source_signature)


def test_cached_bounded_polynomial_evaluation_retains_correlated_uncertainty():
    x = module.original.bounds.Ball(Eisenstein(0), Rational(1, 1024), 80)
    coordinates = (x,) + (x._coerce(1),) * 7
    p = Polynomial.monomial((2,) + (0,) * 7, scalar_type=Eisenstein)
    result = module._bounded_polynomial_value(p, coordinates)
    assert result.radius > 0
    for value in (Eisenstein(Rational(1, 2048)), OMEGA * Rational(1, 1024)):
        assert result.contains(value**2)
    with pytest.raises(ValueError, match="dimensions"):
        module._bounded_polynomial_value(p, coordinates[:3])


def test_symbolic_functionals_reject_wrong_target_and_channel_identity():
    compiler = _compiler()
    compiler.compile_basis(2655)
    _, basis = next(iter(compiler.functional_values))
    for channel in (-1, 3, True, 0.0):
        with pytest.raises(ValueError, match="Reynolds channel"):
            compiler._functional(channel, basis)
    wrong = replace(basis, component=replace(basis.component, right_index=777))
    with pytest.raises(ValueError, match="incompatible original target"):
        compiler._functional(0, wrong)


def test_global_section_identity_never_uses_a_numeric_point_or_chart(monkeypatch):
    before = module.section_basis_identity()

    def no_numeric_inputs():
        raise AssertionError("numerical domain metadata is not an original section identity")

    monkeypatch.setattr(module.domains, "_parents", no_numeric_inputs)
    assert module.section_basis_identity() == before
    assert before["constituent_counts"] == [2655, 2690]
    assert before["section_count"] == 5345
    assert before["parameter_ring"] == "Q(omega)[a0,a1]"
    assert before["parameter_order"] == ["a0", "a1"]
    assert before["numeric_point_or_chart_input"] is False
    assert "chart_pivots" not in before and "exact_column_stream_sha256" not in before


def test_global_identity_rechecks_original_archives_when_inputs_are_cached(monkeypatch):
    module.section_basis_identity()
    _, first = module.original.fiber._verified_payload(module.original.fiber.lifts.first.OUTPUT)
    path = module.domains.ROOT / first["section_archive"]
    original_digest = module.archive._file_digest
    monkeypatch.setattr(module.archive, "_file_digest",
                       lambda p: "changed" if p == path else original_digest(p))
    with pytest.raises(ValueError, match="global section archive changed"):
        module.section_basis_identity()
