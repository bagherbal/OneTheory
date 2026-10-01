"""Attack bounded finite-pole evaluation with original uncompressed data.

Owns:
    Exact and uncertain coefficient naturality, finite filtration, archived
    basis ordering, full-cochain functionals, and finite/infinity chart probes.

Depends on:
    Original raw operators and section constructor, independently produced
    exact point columns, certified roots, and determinant-certified frames.

Must not:
    Treat arithmetic functionals as cover points, prune uncertain zeros,
    choose physical moduli, or infer sampling, metric convergence, or predictions.

Phase 0:
    Research evaluation tests; no physical metric is established here.
"""

import gzip
import hashlib
import json
from dataclasses import FrozenInstanceError, replace

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
    _homotopy,
)
from research.experiments.scientific_genesis import alternate_metric_bounded_support as module

bounded, bounds, fiber = module.bounded, module.bounds, module.fiber
roots = bounds.roots


def _configuration(bits=30, infinity=False):
    return roots.intersection_roots(
        roots.ProjectiveLine((1, 0, 0), (0, 1, -1 if infinity else 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (0, 1) if infinity else (1, 1),
        parameter_pivots=(0, 0),
        policy=roots.RootPolicy(Rational(1, 2**bits), 2 * bits, 2 * bits + 20, 128),
    )


def _frame(bits=30, infinity=False):
    point = bounds.BoundedCoverPoint(
        _configuration(bits, infinity), ("infinity", 0) if infinity else (0, 0),
        (1, 0, 1) if infinity else (0, 0, 0), 80,
    )
    return bounded.BoundedFiberFrame(point, (0, 2), (0, 1, 2))


@pytest.fixture(scope="module")
def exact_engine():
    intersection = roots.intersection_roots(
        roots.ProjectiveLine((1, -1, 0), (0, 0, 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (0, 1), parameter_pivots=(0, 0),
        policy=roots.RootPolicy(Rational(1, 2**30), 60, 80, 128),
    )
    indices = []
    for name, value in (("first", Eisenstein(0)), ("second", Eisenstein(1))):
        side = getattr(intersection, name)
        matches = tuple(i for i, d in enumerate(side.finite.disks)
                        if (d.center - value).norm() <= d.radius**2)
        assert len(matches) == 1
        index = matches[0]
        disks = list(side.finite.disks)
        disks[index] = roots.certify_disk(side.finite.polynomial, value, Rational(0), 80)
        intersection = replace(intersection, **{
            name: replace(side, finite=replace(side.finite, disks=tuple(disks))),
        })
        indices.append(index)
    point = bounds.BoundedCoverPoint(intersection, tuple(indices), (0, 0, 1), 80)
    return module.BoundedSupportEvaluator(bounded.BoundedFiberFrame(point, (0, 2), (0, 1, 2)))


@pytest.fixture(scope="module")
def actual_units():
    source = fiber.lifts.second._context()[0]
    target = fiber.lifts.first._context()[0]
    selected = {}
    for extension in fiber.lifts._inputs()[2]:
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


def _bounded(cochain, bits=80, radius=0):
    return module.BoundedCoefficients(tuple((b, bounds.Ball(c, radius, bits))
                                            for b, c in cochain.terms), bits=bits)


def _contains_coefficients(enclosure, exact):
    values = dict(enclosure.terms)
    for b, c in exact.terms:
        assert b in values and values[b].contains(c)
    exact_values = dict(exact.terms)
    assert all(c.contains(exact_values.get(b, Eisenstein(0))) for b, c in enclosure.terms)


def test_uncertain_zero_coefficients_remain_immutable_and_explicit(actual_units):
    b = actual_units[0].terms[0][0]
    zero_center = bounds.Ball(Eisenstein(0), Rational(1, 4096), 80)
    c = module.BoundedCoefficients(((b, zero_center),), bits=80)
    assert not c.is_zero()
    assert c.terms == ((b, zero_center),)
    assert (c + c.scale(-1)).terms[0][1].radius > 0
    assert c.scale(0).is_zero()
    with pytest.raises(FrozenInstanceError):
        c.terms = ()
    with pytest.raises(ValueError, match="precision"):
        module.BoundedCoefficients(((b, zero_center),), bits=40)
    with pytest.raises(ValueError, match="precision"):
        c + module.BoundedCoefficients(bits=40)
    with pytest.raises(TypeError, match="original cochain"):
        module.BoundedCoefficients(((b, Eisenstein(1)),), bits=80)
    with pytest.raises(ValueError, match="pole"):
        module._monomial((zero_center,), (-1,))


def test_original_homotopy_and_deck_columns_extend_by_bounded_linearity(actual_units):
    for unit in actual_units:
        exact = _bounded(unit)
        for operator, columns in ((_homotopy, module._homotopy_column),
                                  (lambda c: fiber.lifts.first._action(c, 0), module._deck_column)):
            result = module._linear_columns(exact, columns)
            assert result == _bounded(operator(unit))
            uncertain = _bounded(unit, radius=Rational(1, 2**30))
            for direction in (Eisenstein(1), OMEGA):
                functional = SparseOuterCechCochain(tuple((b, c.center + Eisenstein(c.radius)
                                                          * direction) for b, c in uncertain.terms))
                _contains_coefficients(module._linear_columns(uncertain, columns),
                                       operator(functional))


def test_partial_encoding_matches_original_exact_operator_on_all_actual_pole_units(actual_units):
    assert len(actual_units) > 10
    x, u = tuple(map(Eisenstein, (2, 3, 5))), tuple(map(Eisenstein, (7, 11, 13)))
    xb = tuple(bounds.Ball(c, Rational(0), 80) for c in x)
    ub = tuple(bounds.Ball(c, Rational(0), 80) for c in u)
    target = fiber.lifts.first._context()[0]
    operator = module._BoundedPerturbation(target, xb, ub)

    def original_encoding(cochain):
        return module.support.encode_x(module.support.regular._encode(cochain, u), x)

    for unit in actual_units:
        original = original_encoding(unit)
        encoded = module.encode_x(_bounded(module.support.regular._encode(unit, u)), xb)
        assert encoded == _bounded(original)
        assert module.bounded_homotopy(encoded) == _bounded(original_encoding(_homotopy(unit)))
        assert operator.perturbation(encoded) == _bounded(
            original_encoding(target.perturbation(unit)),
        )
        assert operator.perturbation(encoded.scale(Eisenstein(2, 3))) == (
            operator.perturbation(encoded).scale(Eisenstein(2, 3))
        )


def test_uncertain_coefficients_do_not_break_the_actual_finite_filtration(actual_units):
    x = tuple(bounds.Ball(Eisenstein(c), Rational(1, 2**30), 80) for c in (2, 3, 5))
    u = tuple(bounds.Ball(Eisenstein(c), Rational(1, 2**30), 80) for c in (7, 11, 13))
    target = fiber.lifts.first._context()[0]
    operator = module._BoundedPerturbation(target, x, u)
    reached = []
    for unit in actual_units:
        # Encode original regular-u factors; coefficients with center zero
        # remain nonzero enclosures throughout the actual lifting series.
        terms = tuple((OuterCechBasis(b.component, b.x_monomial,
                                     (sum(b.u_monomial), 0, 0), b.p_monomial, b.cell),
                       module._monomial(u, b.u_monomial)
                       * bounds.Ball(Eisenstein(0), Rational(1, 2**30), 80))
                      for b, _c in unit.terms)
        encoded = module.encode_x(module.BoundedCoefficients(terms, bits=80), x)
        primitive, depth = module.perturbed_homotopy(encoded, operator,
                                                    homotopy=module.bounded_homotopy)
        assert depth <= 5
        if depth:
            assert not primitive.is_zero()
            assert any(c.center.is_zero() and c.radius > 0 for _b, c in primitive.terms)
        reached.append(depth)
    assert max(reached) == 1  # These object-zero units require only the raw primitive.


def test_uncertain_encoded_arrows_contain_original_off_center_operator_values(actual_units):
    x = tuple(bounds.Ball(Eisenstein(c), Rational(1, 2**30), 80) for c in (2, 3, 5))
    u = tuple(bounds.Ball(Eisenstein(c), Rational(1, 2**30), 80) for c in (7, 11, 13))
    target = fiber.lifts.first._context()[0]
    operator = module._BoundedPerturbation(target, x, u)
    for unit in actual_units:
        terms = tuple((OuterCechBasis(b.component, b.x_monomial,
                                     (sum(b.u_monomial), 0, 0), b.p_monomial, b.cell),
                       module._monomial(u, b.u_monomial) * c) for b, c in unit.terms)
        encoded = module.encode_x(module.BoundedCoefficients(terms, bits=80), x)
        image = operator.perturbation(encoded)
        for direction in (Eisenstein(1), OMEGA):
            xv, uv = (tuple(c.center + Eisenstein(c.radius) * direction for c in coordinates)
                      for coordinates in (x, u))
            original = module.support.encode_x(
                module.support.regular._encode(target.perturbation(unit), uv), xv,
            )
            _contains_coefficients(image, original)


def test_archived_basis_columns_retain_exact_zero_error_at_the_certified_point(exact_engine):
    archive = json.loads(gzip.decompress(module.support.regular.MATRIX.read_bytes()))
    for index in (0, 1273, 2655):
        coefficients = exact_engine.evaluate_basis(index)
        assert [[str(c.center) for row in m for c in row] for m in coefficients] == (
            [[row[0] for row in m] for m in archive[index]]
        )
        assert all(c.radius == 0 for m in coefficients for row in m for c in row)
    assert exact_engine.unit_values and exact_engine.residual_values
    assert exact_engine.series_depths and max(exact_engine.series_depths) <= 5
    assert len(exact_engine.residual_values) < len(exact_engine.unit_values)
    for index in (-1, 5345, True, 0.0):
        with pytest.raises(ValueError, match="basis index"):
            exact_engine.evaluate_basis(index)
    with pytest.raises(TypeError, match="bounded fiber frame"):
        module.BoundedSupportEvaluator(object())


@pytest.fixture(scope="module")
def actual_section():
    return fiber.lifts.universal_section(2655)


def _raw_section_values(cochain, values, point, context):
    result = [Eisenstein(0) for obj in context.left.objects if obj.position == 0]
    for b, c in cochain.terms:
        if (b.cell != point.cell or b.component.koszul_summand != "k0"
            or context.left.objects[b.component.left_index].position != 0):
            continue
        for v, e in zip(values, b.x_monomial + b.u_monomial + b.p_monomial, strict=True):
            c *= v**e
        result[b.component.left_index] += c
    return tuple(result)


@pytest.mark.parametrize("infinity", (False, True))
def test_bounded_support_contains_the_original_full_section_functionals(actual_section, infinity):
    frame = _frame(infinity=infinity)
    engine = module.BoundedSupportEvaluator(frame)
    coefficients = engine.evaluate_basis(2655)
    original_bounds = frame._evaluate_section(actual_section)
    # Center equality attacks the finite-pole representation, not enclosure
    # tightness; both circular enclosures must contain the same exact value.
    for m, original in zip(coefficients, original_bounds, strict=True):
        assert tuple(c.center for row in m for c in row) == (
            tuple(c.center for row in original for c in row)
        )
    assert any(c.radius > 0 for m in coefficients for row in m for c in row)
    for direction in (Eisenstein(1), OMEGA):
        # Off-center coordinates are independent arithmetic functionals on
        # full original Laurent cochains, never fabricated cover points.
        values = tuple(c.center + Eisenstein(c.radius) * direction
                       for c in (*frame.point.x, *frame.point.u, *frame.point.p))
        contexts = (fiber.lifts.first._context()[0], fiber.lifts.second._context()[0])
        constants = (_raw_section_values(actual_section.first_constant, values, frame.point,
                                         contexts[0])
                     + _raw_section_values(actual_section.second_constant, values, frame.point,
                                           contexts[1]))
        corrections = tuple(_raw_section_values(c, values, frame.point, contexts[0])
                            + (Eisenstein(0),) * 5 for c in actual_section.first_coefficients)
        # Exact Gaussian elimination on the entire five-relation matrix
        # is independent of the bounded producer's separate adjugate blocks.
        # Evaluate the original relation cochains, not support-operator units.
        _first, _second, relations, outer_columns = bounded._relation_cochains(frame.point.chart)
        matrices = []
        for context, columns in zip(contexts, relations, strict=True):
            matrices.append(Matrix(tuple(zip(*(_raw_section_values(c, values, frame.point, context)
                                               for c in columns), strict=True)),
                                   scalar_type=Eisenstein))
        b1, b2 = matrices
        outer = tuple(Matrix(tuple(zip(*(_raw_section_values(c, values, frame.point, contexts[0])
                                        for c in columns), strict=True)), scalar_type=Eisenstein)
                      for columns in outer_columns)
        for a0, a1 in ((Eisenstein(1), OMEGA), (OMEGA, Eisenstein(2, 1))):
            e = outer[0].scale(a0) + outer[1].scale(a1)
            b = Matrix(tuple((*b1[i], *e[i]) for i in range(4))
                       + tuple((0, 0, *b2[i]) for i in range(5)), scalar_type=Eisenstein)
            q = fiber._quotient(b, (0, 2, 4, 5, 6))[0]
            column = Matrix(tuple((c + a0 * x + a1 * y,) for c, x, y in zip(
                constants, *corrections, strict=True,
            )), scalar_type=Eisenstein)
            exact = q.matmul(column)
            enclosed = bounded._add(coefficients[0], bounded._add(
                tuple(tuple(c * a0 for c in row) for row in coefficients[1]),
                tuple(tuple(c * a1 for c in row) for row in coefficients[2]),
            ))
            assert all(ball.contains(value) for row, erow in zip(enclosed, exact.rows, strict=True)
                       for ball, value in zip(row, erow, strict=True))


def test_refinement_contracts_compressed_actual_section_error():
    coarse = module.BoundedSupportEvaluator(_frame(25)).evaluate_basis(2655)
    fine = module.BoundedSupportEvaluator(_frame(40)).evaluate_basis(2655)
    checked = 0
    for cm, fm in zip(coarse, fine, strict=True):
        for cr, fr in zip(cm, fm, strict=True):
            for c, f in zip(cr, fr, strict=True):
                if c.radius == 0:
                    assert f.radius == 0 and f.center == c.center
                else:
                    assert f.radius < c.radius / 100
                    checked += 1
    assert checked > 2


def test_saved_support_probes_rebuild_without_promoting_a_complete_matrix_or_metrics():
    saved = json.loads(module.OUTPUT.read_text())
    assert saved == module.support_artifact()
    digest = saved.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(saved, sort_keys=True, separators=(",", ":"))
                                    .encode()).hexdigest()
    parent = json.loads(bounded.OUTPUT.read_text())
    assert saved["bounded_fiber_artifact_digest"] == parent["artifact_digest"]
    for probe, original in zip(saved["actual_frame_probes"], parent["actual_frame_probes"],
                               strict=True):
        assert probe["name"] == original["name"]
        assert [p["basis_index"] for p in probe["actual_universal_section_probes"]] == (
            [0, 1273, 2655]
        )
        originals = {p["basis_index"]: p for p in original["actual_universal_section_probes"]}
        for section in probe["actual_universal_section_probes"]:
            matrices = section["coefficient_columns_constant_a0_a1"]
            assert len(matrices) == 3
            assert all(len(m) == 4 and all(len(row) == 1 for row in m) for m in matrices)
            if section["basis_index"] in originals:
                original_matrices = originals[section["basis_index"]][
                    "coefficient_columns_constant_a0_a1"
                ]
                assert [c["center"] for m in matrices for row in m for c in row] == (
                    [c["center"] for m in original_matrices for row in m for c in row]
                )
        assert probe["original_operator_columns_compiled"] > 0
        assert probe["observed_series_depths"] and max(probe["observed_series_depths"]) <= 5
    assert saved["compressed_complete_section_enclosure_engine_available"] is True
    for flag in ("complete_bounded_5345_column_matrix_materialized",
                 "practical_multi_point_integration_throughput_certified",
                 "bounded_section_and_density_evaluation_available",
                 "controlled_numerical_sampling_available", "numerical_metrics_available",
                 "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
                 "observational_inputs_used"):
        assert saved[flag] is False
