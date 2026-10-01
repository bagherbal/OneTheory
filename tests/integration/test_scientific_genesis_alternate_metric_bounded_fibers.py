"""Independently attack actual universal quotient and section enclosures.

Owns:
    Raw-arrow coefficient checks, full five-relation symbolic elimination,
    independent exact Gaussian solves, frame transitions, and actual lift probes.

Depends on:
    Exact field/polynomial engines, original relation and section archives,
    certified geometric points, and research bounded-fiber construction.

Must not:
    Regard zero-containing residuals as identity proofs, choose physical
    extension points, replace outer lifts by constituent sections, or infer metrics.

Phase 0:
    Research quotient tests; full bounded-matrix throughput remains open.
"""

import gzip
import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, PolynomialMatrix, determinant
from research.experiments.scientific_genesis import alternate_metric_bounded_fibers as bounded

bounds, fiber = bounded.bounds, bounded.fiber
roots = bounds.roots


def _configuration(bits=30, infinity=False):
    return roots.intersection_roots(
        roots.ProjectiveLine((1, 0, 0), (0, 1, -1 if infinity else 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (0, 1) if infinity else (1, 1),
        parameter_pivots=(0, 0),
        policy=roots.RootPolicy(Rational(1, 2**bits), 2 * bits, 2 * bits + 20, 128),
    )


def _frame(bits=30, infinity=False):
    intersection = _configuration(bits, infinity)
    pair = ("infinity", 0) if infinity else (0, 0)
    chart = (1, 0, 1) if infinity else (0, 0, 0)
    point = bounds.BoundedCoverPoint(intersection, pair, chart, 120)
    return bounded.BoundedFiberFrame(point, (0, 2), (0, 1, 2))


@pytest.fixture(scope="module")
def exact_point():
    intersection = roots.intersection_roots(
        roots.ProjectiveLine((1, -1, 0), (0, 0, 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (0, 1), parameter_pivots=(0, 0),
        policy=roots.RootPolicy(Rational(1, 2**30), 60, 80, 128),
    )
    indices = []
    for name, value in (("first", Eisenstein(0)), ("second", Eisenstein(1))):
        side = getattr(intersection, name)
        matches = tuple(i for i, disk in enumerate(side.finite.disks)
                        if (disk.center - value).norm() <= disk.radius**2)
        assert len(matches) == 1
        index = matches[0]
        disks = list(side.finite.disks)
        disks[index] = roots.certify_disk(side.finite.polynomial, value, Rational(0), 80)
        intersection = replace(intersection, **{
            name: replace(side, finite=replace(side.finite, disks=tuple(disks))),
        })
        indices.append(index)
    return bounds.BoundedCoverPoint(intersection, tuple(indices), (0, 0, 1), 80)


def _centers(matrix):
    return Matrix(tuple(tuple(c.center for c in row) for row in matrix), scalar_type=Eisenstein)


def _contains(matrix, exact):
    assert bounded._shape(matrix) == (exact.row_count, exact.column_count)
    assert all(ball.contains(value) for row, erow in zip(matrix, exact.rows, strict=True)
               for ball, value in zip(row, erow, strict=True))


def _as_polynomials(coefficients):
    return PolynomialMatrix(tuple(tuple(sum((
        Polynomial.monomial(powers, matrix[i][j].center, scalar_type=Eisenstein)
        for powers, matrix in zip(((0, 0), (1, 0), (0, 1)), coefficients, strict=True)
    ), Polynomial.zero(2, scalar_type=Eisenstein)) for j in range(len(coefficients[0][0])))
        for i in range(len(coefficients[0]))))


def _raw_presentation(values, point):
    """Evaluate ORIGINAL raw arrows, not compiled differential/cup columns."""

    def monomial(exponents):
        result = Eisenstein(1)
        for value, exponent in zip(values, exponents, strict=True):
            result *= value**exponent
        return result

    matrices = []
    for context in (fiber.lifts.first._context()[0], fiber.lifts.second._context()[0]):
        objects = context.left.objects
        count = sum(o.position == 0 for o in objects)
        rows = [[Eisenstein(0) for o in objects if o.position == -1] for _ in range(count)]
        for arrow in context.left.resolution_arrows:
            coordinates = values[:3] if arrow.factor == 1 else values[3:6]
            c = Eisenstein.coerce(arrow.polynomial.substitute(coordinates).coefficient(()))
            rows[arrow.target][arrow.source - count] += c
        for term in context.left.extension_terms:
            if term.cell == point.cell and term.koszul_degree == 0 and term.cech_degree == 0:
                rows[term.target][term.source - count] += term.coefficient * monomial(
                    term.x_monomial + term.u_monomial + term.p_monomial,
                )
        matrices.append(Matrix(rows, scalar_type=Eisenstein))
    extensions = []
    for extension in fiber.lifts._inputs()[2]:
        rows = [[Eisenstein(0) for _ in range(3)] for _ in range(4)]
        for basis, c in extension.terms:
            component = basis.component
            if (basis.cell == point.cell and component.koszul_summand == "k0"
                and component.object_degree == 1):
                rows[component.left_index][component.right_index - 5] += c * monomial(
                    basis.x_monomial + basis.u_monomial + basis.p_monomial,
                )
        extensions.append(Matrix(rows, scalar_type=Eisenstein))
    return *matrices, tuple(extensions)


def _dehomogenized_coefficients(cochain, values, point, context):
    """Evaluate a separate sparse polynomial representation in five affine variables."""

    pivots = (point.chart[0], 3 + point.chart[1], 6 + point.chart[2])
    affine = tuple(value for i, value in enumerate(values) if i not in pivots)
    polynomials = [Polynomial.zero(5, scalar_type=Eisenstein)
                   for obj in context.left.objects if obj.position == 0]
    for basis, c in cochain.terms:
        component = basis.component
        if (basis.cell != point.cell or component.koszul_summand != "k0"
            or context.left.objects[component.left_index].position != 0):
            continue
        powers = basis.x_monomial + basis.u_monomial + basis.p_monomial
        exponents = tuple(e for i, e in enumerate(powers) if i not in pivots)
        assert all(e >= 0 for e in exponents)
        polynomials[component.left_index] += Polynomial.monomial(exponents, c,
                                                               scalar_type=Eisenstein)
    return tuple(Eisenstein.coerce(p.substitute(affine).coefficient(())) for p in polynomials)


def test_exact_frames_recover_the_original_nonsplit_presentation(exact_point):
    frame = bounded.BoundedFiberFrame(exact_point, (0, 2), (0, 1, 2))
    exact = fiber.fiber_frame(fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1)),
                              (0, 2), (0, 1, 2))
    assert frame.basis_labels == exact.basis_labels
    assert frame.relation_minor.radius == 0
    assert frame.relation_minor.center == exact.relation_minor
    for name in ("relations", "projections"):
        matrices = getattr(frame, name)
        assert tuple(_centers(m) for m in matrices) == getattr(exact, name)
        assert all(c.radius == 0 for m in matrices for row in m for c in row)
    assert _centers(frame.inclusion) == exact.inclusion
    assert all(not _centers(m).is_zero() for m in frame.relations[1:])


def test_full_five_relation_symbolic_elimination_matches_block_quotient(exact_point):
    frame = bounded.BoundedFiberFrame(exact_point, (0, 2), (0, 1, 2))
    b, q = _as_polynomials(frame.relations), _as_polynomials(frame.projections)
    pivots = (0, 2, 4, 5, 6)
    free = tuple(i for i in range(9) if i not in pivots)
    minor = tuple(b.rows[i] for i in pivots)
    det = determinant(minor)
    assert det.degree == 0
    value = Eisenstein.coerce(det.coefficient((0, 0)))
    assert value == frame.relation_minor.center
    # Eliminate the entire five-by-five parameter matrix at once. This is
    # independent of the implementation's separate two/three-row inverses.
    inverse = PolynomialMatrix(tuple(tuple(determinant(
        tuple(tuple(minor[r][c] for c in range(5) if c != i)
              for r in range(5) if r != j),
    ).scale(Eisenstein((-1)**(i + j)) / value) for j in range(5)) for i in range(5)))
    def constant(c):
        return Polynomial.monomial((0, 0), c, scalar_type=Eisenstein)

    selector = PolynomialMatrix(tuple(tuple(constant(int(i == j)) for j in range(9))
                                      for i in pivots))
    eliminated = PolynomialMatrix(tuple(b.rows[i] for i in free)).compose(inverse).compose(selector)
    independently_solved = tuple(tuple(constant(int(i == j)) - eliminated.rows[k][j]
                                       for j in range(9)) for k, i in enumerate(free))
    assert independently_solved == q.rows
    assert q.compose(b).is_zero()


@pytest.mark.parametrize("infinity", (False, True))
def test_unknown_root_frames_contain_independent_raw_full_matrix_solves(infinity):
    frame = _frame(infinity=infinity)
    point = frame.point
    assert frame.relation_minor.center.norm() > frame.relation_minor.radius**2
    for offset in range(3):
        directions = (Eisenstein(0), Eisenstein(1), OMEGA)
        values = tuple(c.center + Eisenstein(c.radius) * directions[(i + offset) % 3]
                       for i, c in enumerate((*point.x, *point.u, *point.p)))
        b1, b2, outer = _raw_presentation(values, point)
        constant = Matrix(tuple((*b1[i], 0, 0, 0) for i in range(4))
                          + tuple((0, 0, *b2[i]) for i in range(5)), scalar_type=Eisenstein)
        coefficients = tuple(Matrix(tuple((0, 0, *e[i]) for i in range(4))
                                    + ((0,) * 5,) * 5, scalar_type=Eisenstein) for e in outer)
        _contains(frame.relations[0], constant)
        for matrix, exact in zip(frame.relations[1:], coefficients, strict=True):
            _contains(matrix, exact)
        for a0, a1 in ((Eisenstein(0), Eisenstein(0)), (Eisenstein(1), OMEGA),
                        (OMEGA, Eisenstein(2, -1))):
            # Exact functionals of symbolic parameters, not selected physical
            # extension points. The entire five-row inverse uses Gaussian
            # elimination in the independent exact Matrix implementation.
            b = constant + coefficients[0].scale(a0) + coefficients[1].scale(a1)
            exact_q = fiber._quotient(b, (0, 2, 4, 5, 6))[0]
            enclosure_q = bounded._add(frame.projections[0], bounded._add(
                tuple(tuple(c * a0 for c in row) for row in frame.projections[1]),
                tuple(tuple(c * a1 for c in row) for row in frame.projections[2]),
            ))
            _contains(enclosure_q, exact_q)


def test_frame_transitions_and_explicit_pivot_order_preserve_the_same_quotient(exact_point):
    exact = fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    choices = fiber.admissible_pivots(exact)
    frames = tuple(bounded.BoundedFiberFrame(exact_point, choices[0][i], choices[1][i])
                   for i in range(3))
    for i, first in enumerate(frames):
        for j, second in enumerate(frames):
            transition = _as_polynomials(first.transition_to(second))
            assert transition.compose(_as_polynomials(first.projections)).rows == (
                _as_polynomials(second.projections).rows
            )
            for third in frames:
                assert _as_polynomials(second.transition_to(third)).compose(transition).rows == (
                    _as_polynomials(first.transition_to(third)).rows
                )
            if i == j:
                assert transition.rows == tuple(tuple(Polynomial.monomial(
                    (0, 0), int(r == c), scalar_type=Eisenstein,
                ) for c in range(4)) for r in range(4))
    original = bounded.BoundedFiberFrame(exact_point, (0, 2), (0, 1, 2))
    reordered = bounded.BoundedFiberFrame(exact_point, (2, 0), (0, 1, 2))
    assert reordered.projections == original.projections
    assert reordered.relation_minor.center == -original.relation_minor.center


def test_root_refinement_contracts_actual_quotient_bounds():
    coarse, fine = _frame(25), _frame(50)
    checked = 0
    for cm, fm in zip(coarse.projections, fine.projections, strict=True):
        for cr, fr in zip(cm, fm, strict=True):
            for c, f in zip(cr, fr, strict=True):
                if c.radius == 0:
                    assert f.radius == 0 and f.center == c.center
                else:
                    assert f.radius < c.radius / 1000
                    assert (c.center - f.center).norm() < (c.radius - f.radius)**2
                    checked += 1
    assert checked > 10


def test_pivot_inverse_and_basis_failures_do_not_trigger_fallback(exact_point):
    with pytest.raises(ValueError, match="explicit distinct"):
        bounded.BoundedFiberFrame(exact_point, (0, 0), (0, 1, 2))
    with pytest.raises(ValueError, match="explicit distinct"):
        bounded.BoundedFiberFrame(exact_point, (False, 2), (0, 1, 2))
    first, _second, _outer = fiber.local_presentation(
        fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1)),
    )
    bad = next(rows for rows in ((0, 1), (1, 2), (1, 3), (2, 3)) if Matrix(
        tuple(first[i] for i in rows), scalar_type=Eisenstein,
    ).determinant().is_zero())
    with pytest.raises(ZeroDivisionError):
        bounded.BoundedFiberFrame(exact_point, bad, (0, 1, 2))
    frame = bounded.BoundedFiberFrame(exact_point, (0, 2), (0, 1, 2))
    with pytest.raises(ValueError, match="identical certified point"):
        frame.transition_to(_frame())
    with pytest.raises(TypeError, match="original universal section"):
        frame._evaluate_section(object())
    with pytest.raises(FrozenInstanceError):
        frame.projections = ()


def test_small_inverse_bounds_cover_exact_gaussian_inverses_and_reject_possible_zero():
    # Arithmetic fixtures only, not invented physical matrices.
    for values in (((2, 1), (3, 4)), ((2, 1, 0), (0, 3, 1), (1, 0, 4))):
        matrix = tuple(tuple(bounds.Ball(Eisenstein(v), Rational(1, 4096), 80) for v in row)
                       for row in values)
        inverse = bounded._inverse(matrix)
        for direction in (Eisenstein(1), OMEGA, OMEGA**2):
            exact = Matrix(tuple(tuple(c.center + Eisenstein(c.radius) * direction for c in row)
                                 for row in matrix), scalar_type=Eisenstein).inverse()
            _contains(inverse, exact)
    z = bounds.Ball(Eisenstein(0), Rational(0), 80)
    with pytest.raises(ZeroDivisionError):
        bounded._inverse(((z, z), (z, z)))
    with pytest.raises(ValueError, match="rectangular"):
        bounded._multiply(((z,), (z, z)), ((z,),))
    with pytest.raises(ValueError, match="dimensions"):
        bounded._multiply(((z, z),), ((z, z),))


@pytest.fixture(scope="module")
def outer_section():
    return fiber.lifts.universal_section(2655)


def test_outer_corrected_section_matches_independent_complete_point_archive(
    exact_point, outer_section,
):
    frame = bounded.BoundedFiberFrame(exact_point, (0, 2), (0, 1, 2))
    archive = json.loads(gzip.decompress(bounded.fiber.lifts.first.ROOT.joinpath(
        "data/generated/scientific_genesis/alternate_metric_specialized_evaluation.matrix.json.gz",
    ).read_bytes()))
    for index, coefficients in ((0, frame.evaluate_basis(0)),
                                 (2655, frame._evaluate_section(outer_section))):
        assert [[str(c.center) for row in m for c in row] for m in coefficients] == (
            [[row[0] for row in m] for m in archive[index]]
        )
        assert all(c.radius == 0 for m in coefficients for row in m for c in row)
    assert all(len(c.terms) > 0 for c in outer_section.first_coefficients)


def test_actual_outer_section_has_coefficientwise_unknown_root_bounds(outer_section):
    for infinity in (False, True):
        frame = _frame(infinity=infinity)
        coefficients = frame._evaluate_section(outer_section)
        assert all(bounded._shape(m) == (4, 1) for m in coefficients)
        assert any(c.radius > 0 for m in coefficients for row in m for c in row)
        assert any(not c.center.is_zero() for m in coefficients[1:] for row in m for c in row)
        assert all(c.center.is_zero() and c.radius == 0 for m in coefficients[1:]
                   for row in m[2:] for c in row)
        values = tuple(c.center + Eisenstein(c.radius) * OMEGA
                       for c in (*frame.point.x, *frame.point.u, *frame.point.p))
        first, second = fiber.lifts.first._context()[0], fiber.lifts.second._context()[0]
        constants = (_dehomogenized_coefficients(outer_section.first_constant, values,
                                                 frame.point, first)
                     + _dehomogenized_coefficients(outer_section.second_constant, values,
                                                   frame.point, second))
        corrections = tuple(_dehomogenized_coefficients(c, values, frame.point, first)
                            + (Eisenstein(0),) * 5 for c in outer_section.first_coefficients)
        b1, b2, outer = _raw_presentation(values, frame.point)
        for a0, a1 in ((Eisenstein(1), OMEGA), (OMEGA, Eisenstein(2, 1))):
            # Arithmetic functionals only, not chosen extension moduli. Use
            # a full Gaussian solve and independent affine polynomial section
            # values instead of the producer's block formula and Laurent loop.
            e = outer[0].scale(a0) + outer[1].scale(a1)
            b = Matrix(tuple((*b1[i], *e[i]) for i in range(4))
                       + tuple((0, 0, *b2[i]) for i in range(5)), scalar_type=Eisenstein)
            q = fiber._quotient(b, (0, 2, 4, 5, 6))[0]
            v = Matrix(tuple((c + a0 * x + a1 * y,) for c, x, y in zip(
                constants, *corrections, strict=True,
            )), scalar_type=Eisenstein)
            enclosure = bounded._add(coefficients[0], bounded._add(
                tuple(tuple(c * a0 for c in row) for row in coefficients[1]),
                tuple(tuple(c * a1 for c in row) for row in coefficients[2]),
            ))
            _contains(enclosure, q.matmul(v))


def test_saved_frames_and_corrected_section_probes_rebuild_with_scope_intact():
    saved = json.loads(bounded.OUTPUT.read_text())
    assert saved == bounded.fiber_artifact()
    digest = saved.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(saved, sort_keys=True, separators=(",", ":"))
                                    .encode()).hexdigest()
    for probe in saved["actual_frame_probes"]:
        assert [p["basis_index"] for p in probe["actual_universal_section_probes"]] == [0, 2655]
        minor = probe["relation_minor"]
        center = Eisenstein(*(Fraction(c) for c in minor["center"]))
        assert center.norm() > Fraction(minor["radius"])**2
    assert saved["bounded_universal_fiber_frame_available"] is True
    for flag in ("complete_bounded_5345_column_matrix_materialized",
                 "compressed_complete_section_enclosure_engine_available",
                 "bounded_section_and_density_evaluation_available",
                 "controlled_numerical_sampling_available", "numerical_metrics_available",
                 "physical_yukawas_available", "extension_point_selected", "vacuum_selected",
                 "observational_inputs_used"):
        assert saved[flag] is False
