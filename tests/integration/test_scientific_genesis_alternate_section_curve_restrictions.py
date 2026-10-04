"""Independently verify the actual exceptional-section restriction family.

Owns:
    Fraction-pair quotient arithmetic, independent multiplication ranks and
    determinants, original Čech-gauge comparisons, and scientific-scope attacks.

Depends on:
    The frozen alternate carrier's source cochains, exact pencil algebra, and
    the completed restriction execution; no numerical root solver is used.

Must not:
    Turn vanishing visible zero modes into a normalized Pfaffian, identify
    the two basepoint factors, or infer hidden data, integration, or a vacuum.

Phase 0:
    Conditional geometric verification only; physical amplitudes remain missing.
"""

import copy
import json
from dataclasses import replace
from fractions import Fraction

import pytest

from research.experiments.scientific_genesis import alternate_section_curve_restrictions as module
from research.experiments.scientific_genesis.published_constituent_full_cech import (
    ConstituentFullCochain,
)

EXECUTION_DIGEST = "be61e8b06310006085f889b4f6cffe6c80d0810997f38703890ebd0988a63f2e"
ZERO, ONE = (Fraction(0), Fraction(0)), (Fraction(1), Fraction(0))


def _pair(value):
    return Fraction(str(value.a)), Fraction(str(value.b))


def _add(a, b):
    return a[0]+b[0], a[1]+b[1]


def _neg(a):
    return -a[0], -a[1]


def _multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]-a[1]*b[1]


def _inverse(a):
    norm = a[0]**2-a[0]*a[1]+a[1]**2
    return (a[0]-a[1])/norm, -a[1]/norm


def _dense(terms, size):
    values = [ZERO]*size
    for degree, pair in terms:
        values[degree] = tuple(Fraction(c) for c in pair)
    return tuple(values)


def _product(a, b, modulus):
    """Direct coefficient convolution and long reduction, without Polynomial."""

    n = len(modulus)-1
    coefficients = [ZERO]*(2*n-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            coefficients[i+j] = _add(coefficients[i+j], _multiply(x, y))
    assert modulus[-1] == ONE
    for degree in range(2*n-2, n-1, -1):
        leading = coefficients[degree]
        for j, coefficient in enumerate(modulus[:-1]):
            index = degree-n+j
            coefficients[index] = _add(coefficients[index], _neg(_multiply(leading, coefficient)))
    return tuple(coefficients[:n])


def _power(a, exponent, modulus):
    if exponent < 0:
        return _power(_unit_inverse(a, modulus), -exponent, modulus)
    result = (ONE, *(ZERO for _ in range(len(a)-1)))
    for _ in range(exponent):
        result = _product(result, a, modulus)
    return result


def _matrix(a, modulus):
    n = len(a)
    z = (ZERO, ONE, *(ZERO for _ in range(n-2)))
    columns = tuple(_product(a, _power(z, i, modulus), modulus) for i in range(n))
    return tuple(tuple(column[row] for column in columns) for row in range(n))


def _eliminate(matrix):
    """Independent rectangular Gaussian elimination over Fraction pairs."""

    rows = [list(row) for row in matrix]
    pivots, determinant = [], ONE
    for column in range(len(rows[0])):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i][column] != ZERO), None)
        if pivot is None:
            continue
        row = len(pivots)
        if pivot != row:
            rows[row], rows[pivot] = rows[pivot], rows[row]
            determinant = _neg(determinant)
        value = rows[row][column]
        determinant = _multiply(determinant, value)
        rows[row] = [_multiply(c, _inverse(value)) for c in rows[row]]
        for i in range(len(rows)):
            if i != row:
                factor = rows[i][column]
                rows[i] = [_add(c, _neg(_multiply(factor, p)))
                           for c, p in zip(rows[i], rows[row], strict=True)]
        pivots.append(column)
        if len(pivots) == len(rows):
            break
    return tuple(tuple(row) for row in rows), tuple(pivots), determinant


def _unit_inverse(a, modulus):
    n = len(a)
    augmented = tuple((*row, ONE if i == 0 else ZERO)
                      for i, row in enumerate(_matrix(a, modulus)))
    rows, pivots, _ = _eliminate(augmented)
    assert pivots == tuple(range(n))
    return tuple(row[-1] for row in rows)


def _evaluate_terms(terms, coordinates, modulus):
    result = (ZERO,)*len(coordinates[0])
    for monomial, coefficient in terms:
        value = (coefficient, *(ZERO for _ in range(len(result)-1)))
        for coordinate, power in zip(coordinates, monomial, strict=True):
            value = _product(value, _power(coordinate, power, modulus), modulus)
        result = tuple(_add(x, y) for x, y in zip(result, value, strict=True))
    return result


@pytest.fixture(scope="module")
def execution():
    return module.read_restrictions(expected_digest=EXECUTION_DIGEST)


def _algebra(record):
    modulus = _dense(record["modulus"], 10)
    x, y = (_dense(record[key], 9) for key in ("coordinate_x", "coordinate_y"))
    return modulus, (x, y, (ONE, *(ZERO for _ in range(8))))


@pytest.mark.parametrize("index", (0, 1))
@pytest.mark.parametrize("vertex", (0, 1, 2))
def test_original_cech_gauges_independently_give_the_saved_nonsplit_class(execution, index, vertex):
    """Read full original cochains; do not reuse the producer's restriction extractor."""

    modulus, coordinates = _algebra(execution)
    constituent = module._contexts()[1][index]
    extension = constituent.full.alignment.action.derived.extension
    generators = tuple(_evaluate_terms(((m, _pair(c)) for m, c in p.terms), coordinates, modulus)
                       for p in extension.scheme.resolution.generators)
    rows = [[] for _ in generators]
    for basis, coefficient in constituent.full.representative.terms:
        if (basis.component.parent_degree == 0 and basis.component.koszul_degree == 0
            and basis.cell == ((vertex,), (0, 1)) and basis.fiber_monomial == (-1, -1)):
            rows[basis.component.bundle_index].append((basis.base_monomial, _pair(coefficient)))
    h = tuple(_evaluate_terms(terms, coordinates, modulus) for terms in rows)
    delta = _product(h[0], _unit_inverse(generators[0], modulus), modulus)
    actual = _dense(execution["constituents"][index]["restricted_ext_class"], 9)
    assert delta == actual
    for value, generator in zip(h, generators, strict=True):
        assert _product(actual, generator, modulus) == value
    assert module.restricted_class(constituent, module._contexts()[0].base_locus,
                                   vertex=vertex, generator_index=0)[0].representative.terms


@pytest.mark.parametrize("index", (0, 1))
def test_exact_unit_and_norm_use_independent_fraction_pair_elimination(execution, index):
    modulus, _coordinates = _algebra(execution)
    result = execution["constituents"][index]
    value = _dense(result["restricted_ext_class"], 9)
    inverse = _dense(result["restricted_ext_inverse"], 9)
    assert _product(value, inverse, modulus) == (ONE, *(ZERO for _ in range(8)))
    assert _unit_inverse(value, modulus) == inverse
    _rows, pivots, determinant = _eliminate(_matrix(value, modulus))
    assert pivots == tuple(range(9))
    assert determinant == tuple(Fraction(c) for c in result["multiplication_determinant"])
    assert determinant != ZERO


@pytest.mark.parametrize("index,generator", [(0, i) for i in range(3)]
                         + [(1, i) for i in range(4)])
def test_every_original_ideal_split_gives_the_same_class(execution, index, generator):
    model, constituents = module._contexts()
    value, inverse, _g, _h = module.restricted_class(
        constituents[index], model.base_locus, vertex=2, generator_index=generator)
    assert module._qrecord(value) == execution["constituents"][index]["restricted_ext_class"]
    assert module._qrecord(inverse) == execution["constituents"][index]["restricted_ext_inverse"]


@pytest.mark.parametrize("index", range(8))
def test_fixed_point_ideals_have_independently_full_multiplication_span(execution, index):
    """An independent ideal-span rank test replaces the producer's gcd method."""

    modulus, coordinates = _algebra(execution)
    record = execution["deck_fixed_point_checks"][index]
    dx = tuple(_add(a, _neg(b)) for a, b in zip(
        _dense(record["image_x"], 9), coordinates[0], strict=True))
    dy = tuple(_add(a, _neg(b)) for a, b in zip(
        _dense(record["image_y"], 9), coordinates[1], strict=True))
    combined = tuple((*left, *right) for left, right in zip(
        _matrix(dx, modulus), _matrix(dy, modulus), strict=True))
    assert len(_eliminate(combined)[1]) == 9


def test_actual_embedding_equations_and_normal_jacobian_are_independent(execution):
    modulus, coordinates = _algebra(execution)
    f, g = (module.schoen_geometry().cover.cox.cubic_f,
            module.schoen_geometry().cover.cox.cubic_g)
    assert all(_evaluate_terms(((m, _pair(c)) for m, c in p.terms), coordinates, modulus)
               == (ZERO,)*9 for p in (f, g))

    def derivative(p, axis):
        return _evaluate_terms((
            (tuple(e-int(i == axis) for i, e in enumerate(m)),
             (m[axis]*_pair(c)[0], m[axis]*_pair(c)[1]))
            for m, c in p.terms if m[axis]), coordinates, modulus)

    fg = _product(derivative(f, 0), derivative(g, 1), modulus)
    gf = _product(derivative(f, 1), derivative(g, 0), modulus)
    j = tuple(_add(a, _neg(b)) for a, b in zip(fg, gf, strict=True))
    assert j == _dense(execution["jacobian"], 9)
    assert _product(j, _dense(execution["jacobian_inverse"], 9), modulus) == (
        ONE, *(ZERO for _ in range(8)))
    assert execution["normal_bundle_degrees"] == [-1, -1]


def test_actual_deck_groups_not_a_different_pair_of_generators(execution):
    modulus, coordinates = _algebra(execution)
    for action, saved in zip(module.schoen_sparse_deck_actions(),
                             execution["actual_schoen_deck_identification"], strict=True):
        assert action.name == saved["actual_generator"]
        for images, key in ((action.x_images, "first_factor"), (action.u_images, "second_factor")):
            values = tuple(_evaluate_terms(((m, _pair(c)),), coordinates, modulus)
                           for c, m in images)
            inverse = _unit_inverse(values[2], modulus)
            assert _product(values[0], inverse, modulus) == _dense(saved[key]["image_x"], 9)
            assert _product(values[1], inverse, modulus) == _dense(saved[key]["image_y"], 9)


def test_curve_family_keeps_all_pairs_and_outer_parameters_without_amplitudes(execution):
    assert execution["cover_curve_count"] == 81
    assert execution["quotient_curve_count"] == 9
    assert execution["two_basepoint_factors_are_independent"] is True
    assert execution["quotient_map_degree_on_each_cover_curve"] == 1
    assert execution["whole_frozen_outer_parameter_family"] is True
    assert execution["visible_restricted_splitting_degrees"] == [0]*4
    # H0(O(-1)) has no nonnegative homogeneous monomial; H1 has no monomial
    # with both powers negative and total degree -1. The Euler normal lines
    # have the same acyclicity, independently of finite point sampling.
    assert execution["visible_spin_twist_degree"] == -1
    assert execution["visible_spin_twisted_h0"] == execution["visible_spin_twisted_h1"] == 0
    for flag in ("outer_extension_point_selected", "missing_seed_conic_embeddings_supplied",
                 "physical_pfaffian_amplitude_available", "hidden_restrictions_available",
                 "instanton_sum_available", "quillen_normalization_available",
                 "torsion_or_b_field_cancellation_evaluated", "common_stabilized_vacuum_available",
                 "physical_yukawas_available", "genesis_to_uv_derivation_available",
                 "observations_used"):
        assert execution[flag] is False


@pytest.mark.parametrize("index", (0, 1))
def test_zero_serre_class_is_not_relabelled_as_a_trivial_restriction(index):
    model, constituents = module._contexts()
    original = constituents[index]
    zero = replace(original, full=replace(original.full, representative=ConstituentFullCochain()))
    with pytest.raises(ValueError, match="nonunit Ext class"):
        module.restricted_class(zero, model.base_locus, vertex=2, generator_index=0)


@pytest.mark.parametrize("vertex", (True, 2.0, -1, 3))
def test_chart_identity_rejects_aliases_or_an_undeclared_chart(vertex):
    model, constituents = module._contexts()
    with pytest.raises(ValueError, match="plane vertex"):
        module.restricted_class(constituents[0], model.base_locus, vertex=vertex, generator_index=0)


@pytest.mark.parametrize("index", (True, 0.0, -1, 4))
def test_quotient_split_requires_an_explicit_original_generator(index):
    model, constituents = module._contexts()
    with pytest.raises(ValueError, match="generator index"):
        module.restricted_class(constituents[0], model.base_locus, vertex=2, generator_index=index)


def test_missing_execution_cannot_create_a_restriction_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        module.read_restrictions(expected_digest=EXECUTION_DIGEST)
    assert not module.OUTPUT.exists()


@pytest.mark.parametrize("field", (
    "physical_pfaffian_amplitude_available", "instanton_sum_available",
    "missing_seed_conic_embeddings_supplied", "outer_extension_point_selected",
))
def test_rehashed_physical_or_geometric_scope_attacks_fail_closed(
    execution, field, tmp_path, monkeypatch,
):
    changed = copy.deepcopy(execution)
    changed[field] = True
    changed.pop("artifact_digest")
    changed["artifact_digest"] = module.sha256(module._canonical(changed)).hexdigest()
    path = tmp_path / "scope.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="trusted digest"):
        module.read_restrictions(expected_digest=EXECUTION_DIGEST)


def test_self_hash_cannot_change_the_exact_two_factor_geometry(execution, tmp_path, monkeypatch):
    changed = copy.deepcopy(execution)
    changed["two_basepoint_factors_are_independent"] = False
    changed["cover_curve_count"] = 9
    changed.pop("artifact_digest")
    digest = module.sha256(module._canonical(changed)).hexdigest()
    changed["artifact_digest"] = digest
    path = tmp_path / "diagonal-only.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="sources or scientific scope"):
        module.read_restrictions(expected_digest=digest)


def test_saved_restrictions_are_not_overwritten_by_different_bytes(tmp_path, monkeypatch):
    path = tmp_path / "foreign.json"
    path.write_text('{"original": "scientific bytes"}')
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="refusing to overwrite"):
        module.write_restrictions()
    assert json.loads(path.read_text()) == {"original": "scientific bytes"}
