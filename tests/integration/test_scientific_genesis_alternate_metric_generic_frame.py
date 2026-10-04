"""Attack the full-measure named frame using original arrows and native failures.

Owns:
    Independent Fraction-pair minors, all-parameter block identities, projective
    homogeneity, actual excluded points and rejection of inflated numerical scope.

Depends on:
    Original resolution/Serre arrows, native complete-root membership certificates,
    exact polynomial algebra and the conditional geometric null-locus proof.

Must not:
    Infer solver termination from properness, label arithmetic witnesses as draws,
    drop finite-prefix failures or identify a failed frame with a singular bundle.

Phase 0:
    Research theorem tests only; controlled numerical integration remains open.
"""

import copy
import hashlib
import json
from fractions import Fraction
from itertools import permutations

import pytest

from onetheory.math.numbers import OMEGA, Eisenstein, Rational
from onetheory.math.polynomials import Polynomial, determinant
from research.experiments.scientific_genesis import alternate_metric_generic_frame as module
from tests.integration.test_scientific_genesis_alternate_metric_bounded_fibers import (
    _raw_presentation,
)
from tests.integration.test_scientific_genesis_uncertain_cover_frames import _functional

DIGEST = "4a3f35677039b12aa0239fbab79047b23b07d79ecd79288d7a9f0b0832c21b8f"


def _pair(value):
    return Fraction(str(value.a)), Fraction(str(value.b))


def _plus(left, right):
    return left[0]+right[0], left[1]+right[1]


def _times(left, right):
    a, b = left
    c, d = right
    return a*c-b*d, a*d+b*c-b*d


def _independent_det(rows):
    result = (Fraction(0), Fraction(0))
    for permutation in permutations(range(len(rows))):
        sign = (-1)**sum(permutation[i] > permutation[j] for i in range(len(rows))
                         for j in range(i+1, len(rows)))
        value = (Fraction(sign), Fraction(0))
        for i, j in enumerate(permutation):
            value = _times(value, _pair(rows[i][j]))
        result = _plus(result, value)
    return result


@pytest.mark.parametrize("offset", (0, 1, 2))
def test_polynomial_minors_match_independent_original_raw_arrow_fraction_determinants(offset):
    _, _, frame = module.symbolic.domains.declared_frames()[0]
    values = _functional(frame, offset)
    raw_first, raw_second, _ = _raw_presentation(values, frame.point)
    compiled_first, compiled_second, _ = module.local_relations()
    for compiled, raw, pivots, minor in zip(
        (compiled_first, compiled_second), (raw_first, raw_second),
        (module.FIRST_PIVOTS, module.SECOND_PIVOTS), module.frame_minors(), strict=True,
    ):
        for coefficients, direct in zip(compiled, raw, strict=True):
            assert tuple(p.substitute(values).coefficient(()) for p in coefficients) == direct
        expected = _independent_det(tuple(raw[i] for i in pivots))
        assert _pair(minor.substitute(values).coefficient(())) == expected


def test_actual_full_five_relation_minor_is_parameter_independent_without_splitting():
    b1, b2, extensions = module.local_relations()

    def extend(p):
        return Polynomial(tuple((m+(0, 0), c) for m, c in p.terms),
                          variable_count=10, scalar_type=Eisenstein)

    zero = Polynomial.zero(10, scalar_type=Eisenstein)
    a0, a1 = tuple(Polynomial.monomial(tuple(int(i == j) for i in range(10)),
                                      scalar_type=Eisenstein) for j in (8, 9))
    assert any(not p.is_zero() for matrix in extensions for row in matrix for p in row)
    upper = tuple(tuple(extend(p) for p in b1[i]) + tuple(
        a0*extend(x) + a1*extend(y) for x, y in zip(extensions[0][i], extensions[1][i],
                                                  strict=True)) for i in module.FIRST_PIVOTS)
    lower = tuple((zero, zero) + tuple(extend(p) for p in b2[i])
                  for i in module.SECOND_PIVOTS)
    first, second = module.frame_minors()
    assert determinant(upper+lower) == extend(first*second)


def test_actual_failure_numerator_has_explicit_homogeneity_and_normalized_chart():
    first, second = module.frame_minors()
    numerator, degrees = module.homogeneous_numerator(first*second)
    assert degrees == (4, 5, 0) and len(numerator.terms) == 12
    assert all((sum(m[:3]), sum(m[3:6]), sum(m[6:])) == degrees for m, _ in numerator.terms)
    _, _, frame = module.symbolic.domains.declared_frames()[0]
    values = _functional(frame)
    normalized = numerator.substitute(values).coefficient(())
    assert normalized == (first*second).substitute(values).coefficient(())
    scales = (Eisenstein(2), Eisenstein(3, 1), OMEGA)
    scaled = tuple(v*s for group, s in zip((values[:3], values[3:6], values[6:]), scales,
                                          strict=True) for v in group)
    assert numerator.substitute(scaled).coefficient(()) == (
        normalized * scales[0]**4 * scales[1]**5)


def test_genuine_cover_points_outside_the_chart_are_not_declared_absent():
    point = module.bounded.fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    assert point.p[0].is_zero()
    with pytest.raises(ValueError, match="absent from the chosen chart"):
        module.bounded.fiber.CoverPoint(point.x, point.u, point.p, module.CHART)


def test_actual_zero_minor_family_has_an_explicit_regular_alternative_frame():
    roots = module.bounded.bounds.roots
    configuration = roots.intersection_roots(
        roots.ProjectiveLine((1, 0, 0), (0, 0, 1)),
        roots.ProjectiveLine((1, 1, 0), (0, 0, 1)), (1, 1),
        parameter_pivots=(0, 0),
        policy=roots.RootPolicy(Rational(1, 2**30), 60, 100, 128),
    )
    point = module.bounded.bounds.BoundedCoverPoint(configuration, (0, 0), module.CHART, 100)
    assert point.x[1].center.is_zero() and point.x[1].radius == 0
    with pytest.raises(ZeroDivisionError):
        module.bounded.BoundedFiberFrame(point, module.FIRST_PIVOTS, module.SECOND_PIVOTS)
    # This different frame is declared only for an actual geometric attack.
    # It does not silently change the frame of the theorem or numerical archive.
    alternative = module.bounded.BoundedFiberFrame(point, (0, 1), module.SECOND_PIVOTS)
    assert alternative.relation_minor.center.norm() > alternative.relation_minor.radius**2


def test_null_limit_does_not_authorize_dropping_positive_mass_finite_cells():
    for bits in (1, 8, 40):
        mass = Fraction(1, 2**bits)
        assert mass > 0
        # The uniform-cell mean is nonzero although its limit singleton is zero.
        assert mass/2 != 0
    record = json.loads(module.OUTPUT.read_text())
    assert record["fixed_chart_and_frame_failure_is_auxiliary_null"] is True
    for flag in ("finite_prefix_failures_discardable",
                 "native_solver_almost_sure_termination_proved",
                 "single_named_frame_claimed_deck_invariant",
                 "global_numerical_input_coverage_certified", "independent_cover_cloud_available",
                 "controlled_integral_available", "physical_yukawas_available"):
        assert record[flag] is False


@pytest.mark.parametrize("field", (
    "first_relation_minor", "source_signature", "positive_auxiliary_law_digest",
    "native_solver_almost_sure_termination_proved", "finite_prefix_failures_discardable",
    "controlled_integral_available", "fixed_frame_failure_is_physical_bundle_singularity",
))
def test_rehashed_scope_or_source_inflation_cannot_pass_a_trusted_reader(field, tmp_path):
    original = json.loads(module.OUTPUT.read_text())
    changed = copy.deepcopy(original)
    changed[field] = not changed[field] if type(changed[field]) is bool else "changed"
    changed.pop("artifact_digest")
    changed["artifact_digest"] = hashlib.sha256(
        module.symbolic.archive._canonical(changed)).hexdigest()
    path = tmp_path / "inflated.json"
    path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="trusted digest"):
        module.read_generic_frame(expected_digest=DIGEST, path=path)


def test_complete_native_record_replays_every_source_minor_and_scope_field():
    stored = json.loads(module.OUTPUT.read_text())
    assert stored["artifact_digest"] == DIGEST
    assert module.read_generic_frame(expected_digest=DIGEST) == stored


def test_accepting_a_new_digest_does_not_disable_source_and_scope_reconstruction(tmp_path):
    changed = json.loads(module.OUTPUT.read_text())
    changed["native_solver_almost_sure_termination_proved"] = True
    changed.pop("artifact_digest")
    digest = hashlib.sha256(module.symbolic.archive._canonical(changed)).hexdigest()
    changed["artifact_digest"] = digest
    path = tmp_path / "untrusted-new-digest.json"
    path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="theorem changed"):
        module.read_generic_frame(expected_digest=digest, path=path)
