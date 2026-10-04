"""Enclose the complete actual section basis through its original finite support.

Owns:
    Bounded coefficient containers, original unit-column reuse, finite-pole
    functional evaluation, and constant/a0/a1 fiber enclosures in archived order.

Depends on:
    The certified original support encoding, original raw homotopy, original
    mixed arrow and deck operators, and determinant-certified bounded frames.

Must not:
    Discard uncertain zeros, substitute root centers as cover points, replace
    universal lifts by direct sums, choose parameters, or infer sampling or metrics.

Phase 0:
    Research bounded section evaluation; complete packet certification is separate.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from functools import cache

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
    _homotopy,
)
from research.experiments.computable_carrier.schoen_sparse_actions import _monomial_action

from . import alternate_metric_bounded_fibers as bounded
from . import alternate_metric_support_evaluation as support
from .mixed_schoen_common_dga import perturbed_homotopy

bounds, fiber = bounded.bounds, bounded.fiber
OUTPUT = bounded.OUTPUT.with_name("alternate_metric_bounded_support.json")


def _exact_zero(coefficient):
    return coefficient.radius == 0 and coefficient.center.is_zero()


@dataclass(frozen=True, slots=True, init=False)
class BoundedCoefficients:
    """Enclosures on ORIGINAL cochain basis labels, not new physical cochains.

    Zero-center positive-radius entries remain present. Exact zeros alone
    are removed. No observation, replacement basis, or tolerance is accepted.
    """

    terms: tuple
    bits: int

    def __init__(self, terms=(), *, bits):
        bounds._bits(bits)
        values = {}
        for basis, coefficient in terms:
            if not isinstance(basis, OuterCechBasis) or not isinstance(coefficient, bounds.Ball):
                raise TypeError(
                    "original cochain labels and explicit coefficient balls are required",
                )
            if coefficient.bits != bits:
                raise ValueError("incompatible declared bound precisions")
            values[basis] = (values[basis] + coefficient if basis in values else coefficient)
        object.__setattr__(self, "bits", bits)
        object.__setattr__(self, "terms", tuple((basis, c) for basis, c in sorted(values.items())
                                               if not _exact_zero(c)))

    def __add__(self, other):
        if not isinstance(other, BoundedCoefficients) or self.bits != other.bits:
            raise ValueError("bounded cochain addition has incompatible precision or type")
        return BoundedCoefficients(self.terms + other.terms, bits=self.bits)

    def scale(self, scalar):
        return BoundedCoefficients(tuple((b, c * scalar) for b, c in self.terms), bits=self.bits)

    def is_zero(self):
        return not self.terms


@cache
def _homotopy_column(basis):
    return _homotopy(SparseOuterCechCochain(((basis, Eisenstein(1)),))).terms


@cache
def _deck_column(basis):
    return fiber.lifts.first._action(SparseOuterCechCochain(((basis, Eisenstein(1)),)), 0).terms


def _linear_columns(cochain, columns):
    return BoundedCoefficients(tuple((target, c * scalar) for b, c in cochain.terms
                                      for target, scalar in columns(b)), bits=cochain.bits)


def bounded_homotopy(cochain):
    return _linear_columns(cochain, _homotopy_column)


def _artificial_deck_phase(basis, power, action):
    """Return the original phase of the dummy homogeneous degree, not its poles."""

    dummy_x, dummy_u = support._positive(basis.x_monomial), basis.u_monomial
    scalar = Eisenstein(1)
    for _ in range(power):
        unit, dummy_x = _monomial_action(dummy_x, action.x_images)
        scalar *= unit
        unit, dummy_u = _monomial_action(dummy_u, action.u_images)
        scalar *= unit
    return scalar


@cache
def _monomial(coordinates, powers):
    result = coordinates[0]._coerce(1)
    for coordinate, exponent in zip(coordinates, powers, strict=True):
        if type(exponent) is not int or exponent < 0:
            raise ValueError("regular coefficient specialization cannot evaluate a pole")
        result = result * coordinate**exponent
    return result


def _pullback(coordinates, images):
    return tuple(_monomial(tuple(coordinates), m) * c for c, m in images)


def _encode_x_term(basis, coefficient, x, powers=None):
    encoded, positive = support._x_pole_encoding(basis, powers)
    value = coefficient * _monomial(tuple(x), positive)
    return () if _exact_zero(value) else ((encoded, value),)


def encode_x(cochain, x):
    return BoundedCoefficients(tuple(term for b, c in cochain.terms
                                     for term in _encode_x_term(b, c, x)), bits=cochain.bits)


@dataclass(slots=True)
class _BoundedPerturbation:
    """Evaluate the ORIGINAL support operator columns with bounded coefficients."""

    target: object
    x: tuple
    u: tuple
    column_images: dict = field(default_factory=dict)

    def _column(self, source):
        result = []
        columns = support._original_column_terms(self.target, source)
        for basis, residual_x, arrow_u, scalar in columns:
            coefficient = _monomial(self.u, arrow_u) * scalar
            result.extend(_encode_x_term(basis, coefficient, self.x, residual_x))
        return BoundedCoefficients(tuple(result), bits=self.x[0].bits)

    def perturbation(self, cochain):
        result = []
        for basis, coefficient in cochain.terms:
            if basis.u_monomial != (basis.component.ambient_degree[1], 0, 0):
                raise ValueError("an encoded coefficient lost its original u grading")
            if basis not in self.column_images:
                self.column_images[basis] = self._column(basis)
            result.extend((target, coefficient * c)
                          for target, c in self.column_images[basis].terms)
        return BoundedCoefficients(tuple(result), bits=cochain.bits)


class BoundedSupportEvaluator:
    """The certified finite-pole representation with actual coefficient error bounds.

    Caches belong to this declared point/frame. No tiny or zero center is
    pruned unless its radius is also zero. The original finite lifting series
    is reused with original homotopy and deck columns extended by linearity.
    """

    def __init__(self, frame):
        if not isinstance(frame, bounded.BoundedFiberFrame):
            raise TypeError("a determinant-certified actual bounded fiber frame is required")
        support.regular.regularity_premises()
        self.frame = frame
        self.target, actions, _frames = fiber.lifts.first._context()
        if any(c.ambient_degree[0] < 0 for c in self.target.components.values()):
            raise ValueError("positive first-plane ambient grading is required")
        self.p = actions[0]
        self.scalar = frame.point.x[0]._coerce
        self.projection = tuple(tuple(row[:4]) for row in frame.projections[0][:2])
        self.x_channels, self.u_channels = [frame.point.x], [frame.point.u]
        for _ in range(2):
            self.x_channels.append(_pullback(self.x_channels[-1], self.p.x_images))
            self.u_channels.append(_pullback(self.u_channels[-1], self.p.u_images))
        self.operators = [_BoundedPerturbation(self.target, x, u)
                          for x, u in zip(self.x_channels, self.u_channels, strict=True)]
        self.arrows, self.unit_values, self.residual_values, self.numerators = {}, {}, {}, {}
        self.series_depths = set()
        for power, u in enumerate(self.u_channels):
            for parameter, extension in enumerate(fiber.lifts._inputs()[2]):
                grouped = defaultdict(dict)
                for b, c in extension.terms:
                    key = b.component.right_index, b.cell[2][-1]
                    component = self.target.components[
                        b.component.left_index, 0, b.component.koszul_summand,
                    ]
                    label = component, b.x_monomial, b.p_monomial, b.cell
                    value = _monomial(tuple(u), b.u_monomial) * c
                    grouped[key][label] = (grouped[key][label] + value
                                           if label in grouped[key] else value)
                self.arrows[power, parameter] = {
                    key: tuple((label, c) for label, c in values.items() if not _exact_zero(c))
                    for key, values in grouped.items()
                }

    def _encoded_residual(self, power, parameter, key):
        """Retain the original residual construction for either evaluation order."""

        index, x, p, chart = key
        residual = []
        for (component, ax, ap, cell), c in self.arrows[power, parameter].get((index, chart), ()):
            basis = OuterCechBasis(
                component, tuple(a + b for a, b in zip(x, ax, strict=True)),
                (component.ambient_degree[1], 0, 0),
                tuple(a + b for a, b in zip(p, ap, strict=True)), cell,
            )
            residual.extend(_encode_x_term(basis, c, self.x_channels[power]))
        return BoundedCoefficients(tuple(residual), bits=self.frame.point.bits)

    def _residual_functional(self, power, encoded):
        """Apply the existing finite series, deck pullback and fiber projection.

        This is a linear functional on encoded degree-one inputs. It is not
        a claim that an individual unit input is closed or has a primitive.
        """

        primitive, depth = perturbed_homotopy(encoded, self.operators[power],
                                              homotopy=bounded_homotopy)
        if depth > 5:
            raise ValueError("the original finite-support filtration exceeded its bound")
        self.series_depths.add(depth)
        corrected = []
        for basis, c in primitive.terms:
            scalar = _artificial_deck_phase(basis, power, self.p)
            corrected.append((basis, c / scalar))
        pulled = BoundedCoefficients(tuple(corrected), bits=self.frame.point.bits)
        for _ in range(power):
            pulled = _linear_columns(pulled, _deck_column)
        coordinates = [self.scalar(0)] * 4
        for basis, c in pulled.terms:
            if (basis.cell != self.frame.point.cell or basis.component.koszul_summand != "k0"
                or self.target.left.objects[basis.component.left_index].position != 0):
                continue
            monomial = tuple(min(e, 0) for e in basis.x_monomial) + (0, 0, 0) + basis.p_monomial
            if monomial not in self.numerators:
                self.numerators[monomial] = self.frame.point.monomial(monomial)
            obj = basis.component.left_index
            coordinates[obj] = coordinates[obj] + c * self.numerators[monomial]
        value = bounded._multiply(self.projection, bounded._columns((tuple(coordinates),)))
        return tuple(tuple(c * (Eisenstein(-1) / 3) for c in row) for row in value)

    def _unit_correction(self, power, parameter, key):
        cache_key = power, parameter, key
        if cache_key in self.unit_values:
            return self.unit_values[cache_key]
        encoded = self._encoded_residual(power, parameter, key)
        residual_key = power, parameter, encoded
        if residual_key in self.residual_values:
            value = self.residual_values[residual_key]
        else:
            value = self._residual_functional(power, encoded)
            self.residual_values[residual_key] = value
        self.unit_values[cache_key] = value
        return value

    def evaluate_basis(self, index):
        """Enclose every ORIGINAL basis index; retain constant,a0,a1 ordering."""

        if type(index) is not int or not 0 <= index < 5345:
            raise ValueError("a universal basis index must be an integer in range(5345)")
        streams = fiber.lifts._inputs()[1]
        first = index < 2655
        record = streams[0 if first else 1][index if first else index - 2655]
        local = [self.scalar(0)] * (4 if first else 5)
        for obj, monomial, chart, pair in record["terms"]:
            if chart == self.frame.point.chart[2]:
                local[obj] = local[obj] + self.frame.point.monomial(monomial) * Eisenstein(*pair)
        ambient = tuple(local) + (self.scalar(0),) * 5 if first else (
            (self.scalar(0),) * 4 + tuple(local)
        )
        ambient = bounded._columns((ambient,))
        constant = bounded._multiply(self.frame.projections[0], ambient)
        if first:
            zero = tuple((self.scalar(0),) for _ in range(4))
            return constant, zero, zero
        corrections = []
        for parameter in range(2):
            value = ((self.scalar(0),), (self.scalar(0),))
            for power, u in enumerate(self.u_channels):
                sources = {}
                for obj, m, chart, pair in record["terms"]:
                    key = obj, tuple(m[:3]), tuple(m[6:]), chart
                    scalar = _monomial(tuple(u), tuple(m[3:6])) * Eisenstein(*pair)
                    sources[key] = sources[key] + scalar if key in sources else scalar
                for key, scalar in sources.items():
                    if not _exact_zero(scalar):
                        unit = self._unit_correction(power, parameter, key)
                        value = bounded._add(value, tuple(tuple(c * scalar for c in row)
                                                           for row in unit))
            correction = (*value, (self.scalar(0),), (self.scalar(0),))
            corrections.append(bounded._add(correction, bounded._multiply(
                self.frame.projections[parameter + 1], ambient,
            )))
        return constant, *corrections


def support_artifact():
    """Reproduce bounded actual section probes, not a complete matrix or metric.

    The algorithm accepts every archived index. This packet deliberately
    distinguishes that engine from materialized all-column output and
    practical metric-integration throughput, neither of which it certifies.
    """

    frame_digest, _parent = fiber._verified_payload(bounded.OUTPUT)
    root_digest, root_parent = fiber._verified_payload(bounds.roots.OUTPUT)
    exact_digest, exact = fiber._verified_payload(support.regular.OUTPUT)
    archive = support.regular.MATRIX.read_bytes()
    if hashlib.sha256(archive).hexdigest() != exact["matrix_archive_sha256"]:
        raise ValueError("the independent exact matrix archive changed")
    records = []
    for raw in root_parent["actual_configurations"]:
        def scalar(pair):
            return Eisenstein(Fraction(pair[0]), Fraction(pair[1]))

        lines = tuple(bounds.roots.ProjectiveLine(*(tuple(scalar(c) for c in v) for v in raw[key]))
                      for key in ("first_line", "second_line"))
        intersection = bounds.roots.intersection_roots(
            *lines, tuple(scalar(c) for c in raw["P1_point"]),
            parameter_pivots=(raw["first"]["parameter_pivot"], raw["second"]["parameter_pivot"]),
            policy=bounds.roots.RootPolicy(Rational(1, 2**30), 60, 80, 128),
        )
        pair = (0, 0) if raw["name"] == "finite_chart" else ("infinity", 0)
        chart = (0, 0, 0) if raw["name"] == "finite_chart" else (1, 0, 1)
        point = bounds.BoundedCoverPoint(intersection, pair, chart, 80)
        engine = BoundedSupportEvaluator(bounded.BoundedFiberFrame(point, (0, 2), (0, 1, 2)))
        probes = [{
            "basis_index": i,
            "coefficient_columns_constant_a0_a1": [
                bounded._matrix_record(m) for m in engine.evaluate_basis(i)
            ],
        } for i in (0, 1273, 2655)]
        records.append({
            "name": raw["name"], "root_pair": list(pair), "chart_pivots": list(chart),
            "first_pivot_rows": [0, 2], "second_pivot_rows": [0, 1, 2],
            "fiber_basis_labels": list(engine.frame.basis_labels),
            "actual_universal_section_probes": probes,
            "original_operator_columns_compiled": sum(
                len(o.column_images) for o in engine.operators
            ),
            "unit_correction_count": len(engine.unit_values),
            "distinct_bounded_residual_count": len(engine.residual_values),
            "observed_series_depths": sorted(engine.series_depths),
        })
    payload = {
        "schema": "alternate-metric-bounded-support-v1",
        "bounded_fiber_artifact_digest": frame_digest,
        "root_artifact_digest": root_digest,
        "independent_exact_matrix_artifact_digest": exact_digest,
        "independent_exact_matrix_archive_sha256": exact["matrix_archive_sha256"],
        "parameter_basis": ["a0", "a1"], "bound_bits": 80,
        "original_basis_count": 5345, "original_constituent_counts": [2655, 2690],
        "construction": "same finite-pole encoding and lifting series; original exact unit columns",
        "zero_policy": "discard only exact center-zero radius-zero coefficients",
        "filtration_length_bound": support.regular.regularity_premises()["series_length_bound"],
        "actual_frame_probes": records,
        "compressed_complete_section_enclosure_engine_available": True,
        "complete_bounded_5345_column_matrix_materialized": False,
        "practical_multi_point_integration_throughput_certified": False,
        "bounded_section_and_density_evaluation_available": False,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "vacuum_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "certify complete bounded matrix output and practical multi-point throughput; "
            "control SU-uniform proposal precision and integration error, then metric convergence"
        ),
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    return payload


def write_artifact():
    payload = support_artifact()
    OUTPUT.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return payload
