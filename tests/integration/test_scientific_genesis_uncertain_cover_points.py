"""Verify native uncertain families use the original bounded cover representation.

Owns:
    Complete branch selection, explicit chart normalization, original Laurent
    rules, immutable bounds, and fail-closed membership and precision checks.

Depends on:
    Actual uniform root families and the existing bounded geometric point.

Must not:
    Invent cover points, select extension parameters, infer sampling or metrics,
    or treat an admitted point type as a verified complete section matrix.

Phase 0:
    Research input-domain tests; physical integration remains unavailable.
"""

from dataclasses import FrozenInstanceError
from functools import cache

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.scientific_genesis import alternate_metric_enclosures as old
from research.experiments.scientific_genesis import projective_uncertain_intersections as roots
from research.experiments.scientific_genesis.uncertain_cover_weights import declared_configurations


@cache
def configurations():
    return declared_configurations()


@pytest.mark.parametrize("component", range(3))
def test_every_actual_coupled_branch_uses_the_same_normalized_coordinate_arithmetic(component):
    configuration = configurations()[component]
    for branch, groups in zip(configuration.root_pairs, configuration.points, strict=True):
        point = roots.UncertainCoverPoint(configuration, branch, (0, 0, 0), 100)
        assert isinstance(point, old.BoundedCoverPoint)
        assert point.cell == ((0,), (0,), (0,))
        for values, original in zip((point.x, point.u, point.p), groups, strict=True):
            assert values[0].center == Eisenstein(1) and values[0].radius == 0
            inverse = original[0].inverse()
            assert values[1:] == tuple(c * inverse for c in original[1:])
        powers = (0, 2, 1, 0, 1, 2, 0, 1)
        manual = point.x[1]**2 * point.x[2] * point.u[1] * point.u[2]**2 * point.p[1]
        assert point.monomial(powers) == manual
        assert any(c.radius > 0 for group in (point.x, point.u, point.p) for c in group)


def test_native_point_has_no_mutable_instance_dictionary_or_implicit_chart_change():
    point = roots.UncertainCoverPoint(configurations()[0], (0, 0), (0, 0, 0), 100)
    with pytest.raises(FrozenInstanceError):
        point.chart = (1, 1, 1)
    with pytest.raises(TypeError, match="__dict__"):
        vars(point)
    with pytest.raises(ValueError, match="pole escaped"):
        point.monomial((0, -1, 0, 0, 0, 0, 0, 0))


@pytest.mark.parametrize("branch", ((True, 0), (0, False), (3, 0), ("infinity", 0), (0,), [0, 0]))
def test_invalid_or_retyped_branches_cannot_acquire_membership(branch):
    with pytest.raises(ValueError, match="complete-family root pair"):
        roots.UncertainCoverPoint(configurations()[0], branch, (0, 0, 0), 100)


@pytest.mark.parametrize("chart", ((True, 0, 0), (3, 0, 0), (0, 0), [0, 0, 0]))
def test_charts_remain_explicit_and_correctly_typed(chart):
    with pytest.raises(ValueError, match="chart pivots"):
        roots.UncertainCoverPoint(configurations()[0], (0, 0), chart, 100)


@pytest.mark.parametrize("bits", (99, 101, True, 100.0))
def test_precision_is_not_changed_or_retyped(bits):
    with pytest.raises(ValueError, match="original input/root"):
        roots.UncertainCoverPoint(configurations()[0], (0, 0), (0, 0, 0), bits)


def test_raw_coordinate_bounds_are_not_a_native_membership_certificate():
    with pytest.raises(TypeError, match="actual coupled"):
        roots.UncertainCoverPoint(configurations()[0].points[0], (0, 0), (0, 0, 0), 100)


def test_a_pivot_that_may_vanish_does_not_trigger_automatic_fallback():
    def ball(c):
        return roots.Ball(Eisenstein(c), Rational(1, 2**30), 100)
    line = roots.BoundedLine(tuple(ball(c) for c in (0, 1, 1)), 2, (0, 1))
    base = tuple(ball(c) for c in (0, 1))
    policy = roots.roots.RootPolicy(Rational(1, 4096), 64, 100, 128)
    _, complete = roots.line_base_line(line, line, base, parameter_pivots=(0, 0), policy=policy)
    configuration = roots.LineBaseLineConfiguration(line, line, base, *complete)
    # The original reciprocal first-plane branch has x0 close to zero;
    # keeping pivot x0 is an explicit unresolved normalization, not a no-go.
    index = next(i for i, d in enumerate(complete[0].disks) if d.parameter_pivot == 1)
    with pytest.raises(ZeroDivisionError):
        roots.UncertainCoverPoint(configuration, (index, 0), (0, 0, 1), 100)
