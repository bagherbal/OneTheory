"""Specialize regular second-plane coefficients before universal fiber evaluation.

Owns:
    An exact point-functional evaluation of the certified lifting series using
    polynomial coefficient specialization, explicit deck channels, and safe
    zero-coordinate pruning; no full physical cochain is returned.

Depends on:
    Actual frozen outer coefficients, the original mixed perturbation and raw
    homotopy, repaired deck actions, and explicitly based local fiber quotients.

Must not:
    Replace the section basis, choose extension moduli, specialize Laurent poles,
    forget deck phases, infer metrics, or call an encoded cochain a physical section.

Phase 0:
    Research-only exact evaluation compression; numerical convergence is open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from functools import cache

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import _monomial_action

from . import alternate_metric_fiber_evaluation as fiber
from .mixed_schoen_common_dga import perturbed_homotopy

OUTPUT = fiber.lifts.first.ROOT / (
    "data/generated/scientific_genesis/alternate_metric_specialized_evaluation.json"
)
MATRIX = OUTPUT.with_suffix(".matrix.json.gz")


def _monomial(coordinates, exponents):
    return _cached_monomial(tuple(coordinates), tuple(exponents))


@cache
def _cached_monomial(coordinates, exponents):
    result = Eisenstein(1)
    for c, e in zip(coordinates, exponents, strict=True):
        if e < 0:
            raise ValueError("regular-plane specialization cannot evaluate a Laurent pole")
        result *= c ** e
    return result


def _encode(cochain, u):
    """Encode a regular cochain's u coefficients while retaining ambient degree."""

    return SparseOuterCechCochain(tuple((OuterCechBasis(
        b.component, b.x_monomial, (sum(b.u_monomial), 0, 0), b.p_monomial, b.cell,
    ), c * _monomial(u, b.u_monomial)) for b, c in cochain.terms))


def _pullback_point(coordinates, images):
    return tuple(c * _monomial(coordinates, m) for c, m in images)


@cache
def regularity_premises():
    """Check actual coefficients, not an assumed coefficient-ring presentation."""

    target = fiber.lifts.first._context()[0]
    if any(c.ambient_degree[1] < 0 for c in target.components.values()):
        raise ValueError("dummy homogeneous degree would introduce second-plane negative support")
    if any(e < 0 for t in target.left.extension_terms for e in t.x_monomial + t.u_monomial):
        raise ValueError("an actual mixed arrow is not polynomial in both planes")
    for arrow in target.left.resolution_arrows:
        if any(e < 0 for m, _c in arrow.polynomial.terms for e in m):
            raise ValueError("an actual resolution arrow is not polynomial")
    extensions = fiber.lifts._inputs()[2]
    if any(e < 0 for ext in extensions for b, _c in ext.terms for e in b.u_monomial):
        raise ValueError("an outer coefficient has second-plane Laurent support")
    return {
        "target_components_checked": len(target.components),
        "all_target_second_plane_ambient_degrees_nonnegative": True,
        "all_actual_object_arrows_polynomial_in_both_planes": True,
        "both_outer_coefficients_second_plane_regular": True,
        "Koszul_equations_polynomial_in_both_planes": True,
        "series_length_bound": fiber.lifts.structural_certificate()["h_delta_nilpotence_bound"],
    }


@dataclass(slots=True)
class _SpecializedPerturbation:
    """Internal degree-bookkeeping encoding of a specialized linear operator."""

    target: object
    u: tuple[Eisenstein, ...]
    zero_x: tuple[int, ...]

    def keep(self, basis):
        return not any(basis.x_monomial[i] > 0 for i in self.zero_x)

    def perturbation(self, cochain):
        groups = defaultdict(list)
        for b, c in cochain.terms:
            if b.u_monomial != (b.component.ambient_degree[1], 0, 0):
                raise ValueError("an encoded coefficient lost its explicit dummy grading")
            groups[b.component].append((b, c))
        result = []
        for component, terms in groups.items():
            source_degree = component.ambient_degree[1]
            image = self.target.perturbation(SparseOuterCechCochain(tuple(terms)))
            for b, c in image.terms:
                if not self.keep(b):
                    continue
                powers = (b.u_monomial[0] - source_degree, *b.u_monomial[1:])
                value = c * _monomial(self.u, powers)
                if not value.is_zero():
                    result.append((OuterCechBasis(
                        b.component, b.x_monomial, (sum(b.u_monomial), 0, 0),
                        b.p_monomial, b.cell,
                    ), value))
        return SparseOuterCechCochain(tuple(result))


class SpecializedEvaluator:
    """Evaluate the same universal section basis in a supplied exact fiber frame."""

    def __init__(self, frame):
        regularity_premises()
        self.frame = frame
        self.target, self.actions, self.frames = fiber.lifts.first._context()
        self.p = self.actions[0]
        self.projection = fiber._quotient(fiber.local_presentation(frame.point)[0],
                                         frame.first_pivots)[0]
        self.line_frames = tuple(frame.point.line_frame(o.line_degree)
                                 for o in self.target.left.objects[:4])
        self.numerators = {}
        self.u_channels = [frame.point.u]
        for _ in range(2):
            self.u_channels.append(_pullback_point(self.u_channels[-1], self.p.u_images))
        self.operators = []
        self.arrows = {}
        self.unit_values = {}
        for power, u in enumerate(self.u_channels):
            zero_x = []
            for i in range(3):
                m = tuple(int(j == i) for j in range(3))
                scalar = Eisenstein(1)
                for _ in range(power):
                    unit, m = _monomial_action(m, self.p.x_images)
                    scalar *= unit
                if (scalar * _monomial(frame.point.x, m)).is_zero():
                    zero_x.append(i)
            self.operators.append(_SpecializedPerturbation(self.target, u, tuple(zero_x)))
            for parameter, extension in enumerate(fiber.lifts._inputs()[2]):
                grouped = defaultdict(dict)
                for b, c in extension.terms:
                    key = b.component.right_index, b.cell[2][-1]
                    component = self.target.components[
                        b.component.left_index, 0, b.component.koszul_summand,
                    ]
                    label = component, b.x_monomial, b.p_monomial, b.cell
                    values = grouped[key]
                    values[label] = (values.get(label, Eisenstein(0))
                                     + c * _monomial(u, b.u_monomial))
                self.arrows[power, parameter] = {
                    key: tuple((label, c) for label, c in values.items() if not c.is_zero())
                    for key, values in grouped.items()
                }

    def _unit_correction(self, power, parameter, key):
        """Cache an evaluated linear operator column, not a replacement section."""

        cache_key = power, parameter, key
        if cache_key in self.unit_values:
            return self.unit_values[cache_key]
        index, x, p, chart = key
        operator = self.operators[power]
        residual = []
        for (component, ax, ap, cell), coefficient in self.arrows[power, parameter].get(
            (index, chart), (),
        ):
            basis = OuterCechBasis(
                component, tuple(a + b for a, b in zip(x, ax, strict=True)),
                (component.ambient_degree[1], 0, 0),
                tuple(a + b for a, b in zip(p, ap, strict=True)), cell,
            )
            if operator.keep(basis):
                residual.append((basis, coefficient))
        primitive, depth = perturbed_homotopy(SparseOuterCechCochain(tuple(residual)), operator)
        if depth > 5:
            raise ValueError("the specialized actual filtration exceeded its certified bound")
        # u coefficients have already been evaluated at P^power(u). Remove the
        # artificial dummy monomial's deck scalar before pulling back cells,
        # x/p monomials, object frames, and Koszul units by the ORIGINAL action.
        corrected = []
        for b, c in primitive.terms:
            m = b.u_monomial
            scalar = Eisenstein(1)
            for _ in range(power):
                unit, m = _monomial_action(m, self.p.u_images)
                scalar *= unit
            corrected.append((b, c / scalar))
        pulled = SparseOuterCechCochain(tuple(corrected))
        for _ in range(power):
            pulled = fiber.lifts.first._action(pulled, 0)
        coordinates = [Eisenstein(0)] * 4
        for b, c in pulled.terms:
            if (b.cell != self.frame.point.cell or b.component.koszul_summand != "k0"
                or self.target.left.objects[b.component.left_index].position != 0):
                continue
            obj = b.component.left_index
            # The dummy u numerator is one: real u values reside in c already.
            monomial = b.x_monomial + (0, 0, 0) + b.p_monomial
            if monomial not in self.numerators:
                self.numerators[monomial] = self.frame.point.monomial(monomial)
            coordinates[obj] += c * self.numerators[monomial] / self.line_frames[obj]
        value = self.projection.matmul(fiber._columns((tuple(coordinates),))).scale(
            Eisenstein(-1) / 3,
        )
        self.unit_values[cache_key] = value
        return value

    def evaluate_basis(self, index):
        """Return constant/a0/a1 columns, preserving the exact archived ordering."""

        if type(index) is not int or not 0 <= index < 5345:
            raise ValueError("a universal basis index must be an integer in range(5345)")
        streams = fiber.lifts._inputs()[1]
        first = index < 2655
        context = self.target if first else fiber.lifts.second._context()[0]
        record = streams[0 if first else 1][index if first else index - 2655]
        local = fiber.compact_coordinates(record, self.frame.point, context)
        ambient = local + (Eisenstein(0),) * 5 if first else (Eisenstein(0),) * 4 + local
        constant = self.frame.projections[0].matmul(fiber._columns((ambient,)))
        if first:
            zero = constant.scale(0)
            return constant, zero, zero
        corrections = []
        for parameter in range(2):
            value = Matrix(((0,), (0,)), scalar_type=Eisenstein)
            for power, u in enumerate(self.u_channels):
                sources = {}
                for obj, m, chart, pair in record["terms"]:
                    key = obj, tuple(m[:3]), tuple(m[6:]), chart
                    sources[key] = sources.get(key, Eisenstein(0)) + Eisenstein(*pair) * _monomial(
                        u, m[3:6],
                    )
                for key, scalar in sources.items():
                    if not scalar.is_zero():
                        value = value + self._unit_correction(power, parameter, key).scale(scalar)
            correction = Matrix((*value.rows, ((Eisenstein(0),)), ((Eisenstein(0),))),
                                scalar_type=Eisenstein)
            corrections.append(correction + self.frame.projections[parameter + 1].matmul(
                fiber._columns((ambient,)),
            ))
        return constant, *corrections


def write_evaluation():
    """Materialize all 5345 exact columns, never substituting a Hermitian metric."""

    parent_digest, parent = fiber._verified_payload(fiber.OUTPUT)
    point = fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    frame = fiber.fiber_frame(point, (0, 2), (0, 1, 2))
    engine = SpecializedEvaluator(frame)
    probes = {}
    selected = parent["actual_basis_indices"]
    expected = parent["actual_section_coefficients_constant_a0_a1"]
    stream = []
    for index in range(5345):
        column = engine.evaluate_basis(index)
        record = [fiber._matrix_record(m) for m in column]
        if index in selected:
            position = selected.index(index)
            if any(record[p] != [[expected[p][i][position]] for i in range(4)] for p in range(3)):
                raise ValueError("specialized evaluation differs from the full-cochain result")
            probes[str(index)] = record
        stream.append(record)
        if (index + 1) % 100 == 0 or index == 5344:
            print(f"exact_basis_columns_evaluated: {index + 1}/5345", flush=True)
    raw = json.dumps(stream, separators=(",", ":")).encode()
    archive = gzip.compress(raw, mtime=0)
    # The already independently reproduced nonzero probe minor certifies rank
    # four for the complete evaluation matrix; no guessed matrices enter here.
    if len(probes) != 4 or parent["actual_section_determinant_all_parameters"] != "1/81":
        raise ValueError("the complete evaluation lacks its actual all-parameter rank-four minor")
    payload = {
        "schema": "alternate-metric-specialized-evaluation-v1",
        "carrier_status": "conditional on the selected heterotic UV realization",
        "fiber_evaluation_artifact_digest": parent_digest,
        "prerequisite_artifact_digests": fiber.lifts._inputs()[0],
        "point": parent["point"], "parameter_basis": ["a0", "a1"],
        "fiber_basis_labels": list(frame.basis_labels),
        "first_pivot_rows": list(frame.first_pivots),
        "second_pivot_rows": list(frame.second_pivots),
        "regularity_premises": regularity_premises(),
        "section_count": len(stream), "fiber_dimension": 4,
        "matrix_archive": str(MATRIX.relative_to(fiber.lifts.first.ROOT)),
        "matrix_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "exact_column_stream_sha256": hashlib.sha256(raw).hexdigest(),
        "cached_operator_column_count": len(engine.unit_values),
        "independent_full_cochain_probe_indices": selected,
        "all_probe_coefficients_match_full_cochain_evaluation": True,
        "actual_spanning_minor_all_parameters": "1/81",
        "complete_5345_column_point_matrix_materialized": True,
        "controlled_numerical_sampling_available": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "observational_inputs_used": False,
    }
    payload["artifact_digest"] = hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    temporary = MATRIX.with_name(f".{MATRIX.name}.tmp")
    temporary.write_bytes(archive)
    temporary.replace(MATRIX)
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    temporary.replace(OUTPUT)
    return payload


if __name__ == "__main__":
    report = write_evaluation()
    print(f"artifact_digest: {report['artifact_digest']}")
