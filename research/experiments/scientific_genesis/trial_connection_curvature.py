"""Differentiate the original full-section trial connection on a declared background.

Owns:
    Analytic first derivatives of all 5345 original section columns, the actual
    quotient projection, and trace-free Chern curvature in a reference FS metric.

Depends on:
    The frozen exact polynomial stream, original local relation cochains,
    retained coordinate receipts, and explicit discovery linear algebra.

Must not:
    Redraw roots, reduce sections, regularize, treat centers as exact points,
    export a physical metric, or mistake a reference residual for convergence.

Phase 0:
    Research discovery calculation only; physical normalization remains open.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from functools import cache
from pathlib import Path

import numpy as np
from scipy.linalg import solve_triangular
from scipy.sparse import csr_matrix

from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial

from . import alternate_metric_bounded_fibers as frames
from . import alternate_metric_measure as measure
from . import compiled_section_features as features
from . import full_trial_cloud as full
from .metric_polarization_scope import ambient_cover_triple

CHART = measure.ProjectionChart(0, 2, 0, 2, 0)
PIVOTS = (0, 2, 4, 5, 6)
FREE = (1, 3, 7, 8)
POLARIZATION = (14, 16, 1)
PARENT_REQUEST = "9e13a565bc13a2bd27320e5746d3fbf2104c3290f8792efc97d8d3316bc8a5b5"
PARENT_CLOUD = "3138e6d6eb4c17fb977714f78069cc704e09f3eab45fb73e1b8d16d540cd29cc"
OUTPUT = full.OUTPUT.with_name("trial_connection_curvature.json")
NOTE = Path(__file__).with_name("TRIAL_CONNECTION_CURVATURE_NOTE.md")


def monomial_jets(exponents, coordinates, tangent):
    """Evaluate values and analytic directional derivatives without dividing by z."""

    exponents = np.asarray(exponents)
    coordinates = np.asarray(coordinates, dtype=np.complex128)
    tangent = np.asarray(tangent, dtype=np.complex128)
    if (exponents.ndim != 2 or exponents.shape[1] != 8
            or exponents.dtype.kind not in "iu" or np.any(exponents < 0)
            or coordinates.shape != (8,) or tangent.shape != (8, 3)
            or not np.all(np.isfinite(coordinates)) or not np.all(np.isfinite(tangent))):
        raise ValueError("eight regular coordinates and three explicit tangent directions required")
    result = np.zeros((len(exponents), 4), dtype=np.complex128)
    result[:, 0] = np.prod(coordinates[None, :] ** exponents, axis=1)
    for axis in range(8):
        selected = exponents[:, axis] > 0
        reduced = exponents[selected].copy()
        reduced[:, axis] -= 1
        derivative = exponents[selected, axis] * np.prod(
            coordinates[None, :] ** reduced, axis=1,
        )
        result[selected, 1:] += derivative[:, None] * tangent[axis]
    if not np.all(np.isfinite(result)):
        raise ArithmeticError("analytic monomial discovery arithmetic overflowed")
    return result


def polynomial_jets(polynomial, coordinates, tangent):
    """Differentiate a small original exact polynomial, including at zero coordinates."""

    if not polynomial.terms:
        return np.zeros(4, dtype=np.complex128)
    monomials, coefficients = zip(*polynomial.terms, strict=True)
    values = monomial_jets(monomials, coordinates, tangent)
    return np.asarray([features._complex(c) for c in coefficients]) @ values


@cache
def relation_polynomials():
    """Extract the unchanged original nine-generator/five-relation presentation."""

    first, second, relations, outer = frames._relation_cochains((0, 0, 0))

    def coefficients(cochain, context):
        values = [Polynomial.zero(8, scalar_type=Eisenstein)
                  for obj in context.left.objects if obj.position == 0]
        for basis, coefficient in cochain.terms:
            component = basis.component
            key = component.left_index, component.right_index, component.koszul_summand
            if context.components.get(key) != component:
                raise ValueError("an original relation cochain lost its typed component")
            if (basis.cell != ((0,), (0,), (0,)) or component.koszul_summand != "k0"
                    or context.left.objects[component.left_index].position != 0):
                continue
            powers = list(basis.x_monomial + basis.u_monomial + basis.p_monomial)
            for pivot in (0, 3, 6):
                powers[pivot] = 0
            values[component.left_index] += Polynomial.monomial(
                tuple(powers), coefficient, scalar_type=Eisenstein,
            )
        return tuple(values)

    return (tuple(coefficients(c, first) for c in relations[0]),
            tuple(coefficients(c, second) for c in relations[1]),
            tuple(tuple(coefficients(c, first) for c in channel) for channel in outer))


def projection_jets(coordinates, tangent, parameters):
    """Differentiate pivot elimination, rather than freezing a pointwise projection."""

    first, second, outer = relation_polynomials()
    relation = np.zeros((9, 5, 4), dtype=np.complex128)
    for column, polynomials in enumerate(first):
        for row, polynomial in enumerate(polynomials):
            relation[row, column] = polynomial_jets(polynomial, coordinates, tangent)
    for column, polynomials in enumerate(second):
        for row, polynomial in enumerate(polynomials):
            relation[row + 4, column + 2] = polynomial_jets(polynomial, coordinates, tangent)
    for parameter, channel in zip(parameters, outer, strict=True):
        for column, polynomials in enumerate(channel):
            for row, polynomial in enumerate(polynomials):
                relation[row, column + 2] += parameter * polynomial_jets(
                    polynomial, coordinates, tangent,
                )
    pivot = relation[list(PIVOTS), :, 0]
    free = relation[list(FREE), :, 0]
    eliminated = np.linalg.solve(pivot.T, free.T).T
    selector = np.eye(9, dtype=np.complex128)[list(PIVOTS)]
    result = np.zeros((4, 9, 4), dtype=np.complex128)
    result[:, :, 0] = np.eye(9)[list(FREE)] - eliminated @ selector
    for direction in range(3):
        derivative = (relation[list(FREE), :, direction + 1]
                      - eliminated @ relation[list(PIVOTS), :, direction + 1])
        result[:, :, direction + 1] = -np.linalg.solve(pivot.T, derivative.T).T @ selector
    if not np.all(np.isfinite(result)):
        raise ArithmeticError("original pivot differentiation is numerically unresolved")
    return result


@cache
def equation_derivatives():
    equations = measure.projection_polynomials(CHART)
    return tuple(tuple(equation.derivative(i) for i in range(5)) for equation in equations)


def tangent_background(coordinates):
    """Pull back 14 FS_x + 16 FS_u + FS_p with integral_CP1 FS = 1.

    Arrays use the Hermitian convention v^dagger g v. The Kähler form is
    i g_(i,bar j) dz_i wedge dbar z_j, so the FS coefficient is 1/(2*pi).
    Centers are arithmetic approximations; the implicit tangent is not certified.
    """

    coordinates = np.asarray(coordinates, dtype=np.complex128)
    if (coordinates.shape != (8,) or not np.all(np.isfinite(coordinates))
            or np.any(coordinates[[0, 3, 6]] != 1)):
        raise ValueError("the original normalized chart (0,0,0) is required")
    affine = coordinates[[1, 2, 4, 5, 7]]

    def value(polynomial):
        return sum(features._complex(c) * np.prod(affine ** np.asarray(m))
                   for m, c in polynomial.terms)

    df, dg = tuple(tuple(value(p) for p in derivatives) for derivatives in equation_derivatives())
    if not df[1] or not dg[3]:
        raise ArithmeticError("the declared projection tangent is ramified at this center")
    tangent = np.zeros((8, 3), dtype=np.complex128)
    tangent[1, 0], tangent[4, 1], tangent[7, 2] = 1, 1, 1
    tangent[2] = (-df[0] / df[1], 0, -df[4] / df[1])
    tangent[5] = (0, -dg[2] / dg[3], -dg[4] / dg[3])
    metric = np.zeros((3, 3), dtype=np.complex128)
    for indices, coefficient in zip(((1, 2), (4, 5), (7,)), POLARIZATION, strict=True):
        z = coordinates[list(indices)]
        potential = 1 + np.vdot(z, z).real
        block = np.eye(len(indices)) / potential - np.outer(z, z.conj()) / potential**2
        directions = tangent[list(indices)]
        metric += coefficient / (2 * math.pi) * directions.conj().T @ block @ directions
    np.linalg.cholesky(metric)
    if not np.all(np.isfinite(tangent)) or not np.all(np.isfinite(metric)):
        raise ArithmeticError("reference background arithmetic is unresolved")
    return tangent, metric, 1 / abs(df[1] * dg[3])**2


class FullSectionJets:
    """A derivative consumer of the frozen CSR instructions, not a new section basis."""

    def __init__(self, program):
        if not isinstance(program, features.CompiledFeatures):
            raise TypeError("the original complete compiled program is required")
        self.program = program
        self.exponents = np.asarray(program.features, dtype=np.int64)
        self.coefficients = csr_matrix((
            np.frombuffer(program.coefficients, dtype=np.complex128),
            np.frombuffer(program.feature_indices, dtype=np.uint32),
            np.frombuffer(program.offsets, dtype=np.uint32),
        ), shape=(90865, len(program.features)))

    def evaluate(self, coordinates, parameters, *, source_signature):
        """Consume every original channel at fixed extension parameters (not their jets)."""

        if source_signature != self.program.source_signature:
            raise ValueError("the original full section source identity changed")
        parameters = np.asarray(parameters, dtype=np.complex128)
        if parameters.shape != (2,) or not np.all(np.isfinite(parameters)):
            raise ValueError("two explicit finite fixed extension parameters required")
        tangent, metric, residue_squared = tangent_background(coordinates)
        raw = np.asarray(self.coefficients @ monomial_jets(
            self.exponents, coordinates, tangent,
        )).reshape(5345, 17, 4)
        ambient = raw[:, :9, :].copy()
        ambient[:, :4, :] += parameters[0] * raw[:, 9:13, :] + parameters[1] * raw[:, 13:17, :]
        projection = projection_jets(coordinates, tangent, parameters)
        values = projection[:, :, 0] @ ambient[:, :, 0].T
        derivatives = np.asarray([
            projection[:, :, direction + 1] @ ambient[:, :, 0].T
            + projection[:, :, 0] @ ambient[:, :, direction + 1].T
            for direction in range(3)
        ])
        if values.shape != (4, 5345) or not np.all(np.isfinite(derivatives)):
            raise ArithmeticError("the complete original section jets are unresolved")
        return values, derivatives, metric, residue_squared


def trace_free_curvature(values, derivatives, metric):
    """Contract Chern curvature of h=(S S^dagger)^-1, then remove its trace.

    F = bar-partial(h^-1 partial h); components use dz_i wedge dbar z_j.
    At a constant numerically whitened fiber frame P=I, F_(i,bar j) is
    R_i R_j^dagger, R_i = partial_i S (I - S^dagger S). No second jets occur.
    The final trace subtraction removes the line-twist curvature without
    selecting a determinant-volume trivialization or exporting an SU(4) metric.
    """

    values = np.asarray(values, dtype=np.complex128)
    derivatives = np.asarray(derivatives, dtype=np.complex128)
    metric = np.asarray(metric, dtype=np.complex128)
    if (values.shape != (4, 5345) or derivatives.shape != (3, 4, 5345)
            or metric.shape != (3, 3) or any(not np.all(np.isfinite(a))
                                           for a in (values, derivatives, metric))):
        raise ValueError("all original finite section values, jets and background required")
    orthogonal, upper = np.linalg.qr(values.conj().T, mode="reduced")
    if np.linalg.cond(upper) > 1e12:
        raise ArithmeticError("the full fiber whitening is numerically unresolved")
    rows = orthogonal.conj().T
    jets = np.asarray([solve_triangular(upper.conj().T, d, lower=True) for d in derivatives])
    remainder = jets - np.asarray([(d @ rows.conj().T) @ rows for d in jets])
    inverse = np.linalg.solve(metric, np.eye(3))
    contracted = sum(inverse[i, j] * (remainder[i] @ remainder[j].conj().T)
                     for i in range(3) for j in range(3))
    antihermitian = float(np.linalg.norm(contracted - contracted.conj().T, "fro"))
    if antihermitian > 1e-10 * max(1, float(np.linalg.norm(contracted, "fro"))):
        raise ArithmeticError("contracted curvature fails the declared Hermiticity check")
    # This symmetrization only removes checked arithmetic skew, not eigenvalues.
    contracted = (contracted + contracted.conj().T) / 2
    trace_free = contracted - np.trace(contracted) / 4 * np.eye(4)
    eigenvalues = np.linalg.eigvalsh(trace_free)
    if not np.all(np.isfinite(eigenvalues)):
        raise ArithmeticError("curvature eigenvalues are numerically unresolved")
    return {"trace_free_eigenvalues": [float(x) for x in eigenvalues],
            "trace_free_l1": float(np.sum(np.abs(eigenvalues))),
            "trace_free_frobenius": float(np.linalg.norm(trace_free, "fro")),
            "twisted_curvature_trace": float(np.trace(contracted).real),
            "hermiticity_residual": antihermitian,
            "fiber_condition_number_discovery": float(np.linalg.cond(upper))}


def _sources():
    paths = (Path(__file__), NOTE, Path(features.__file__), Path(frames.__file__),
             Path(measure.__file__),
             full.ROOT / "tests/integration/test_scientific_genesis_trial_connection_curvature.py")
    return {str(path.relative_to(full.ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def run(*, progress=None):
    """Evaluate every old retained sample; no aggregate exists if one is unresolved.

    This is an empirical discovery error in a reference Kähler background.
    It is not an error-controlled continuum integral or a new blind experiment.
    The old hold-out points are explicitly marked as previously inspected.
    """

    if OUTPUT.exists():
        raise FileExistsError("preserve the original full-population curvature calculation")
    sources = _sources()
    request = full.read_request(expected_digest=PARENT_REQUEST)
    manifest = full.read_cloud(expected_request_digest=PARENT_REQUEST, expected_digest=PARENT_CLOUD)
    inputs = full.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=full.INPUTS,
    )
    program = features.compile_features()
    consumer = FullSectionJets(program)
    parameters = tuple(features._complex(Eisenstein(Fraction(a), Fraction(b)))
                       for a, b in request["policy"]["parameters"])
    volume = float(ambient_cover_triple(POLARIZATION, POLARIZATION, POLARIZATION)) / (6 * 9)
    points = []
    for ordinal in range(request["sample_count"]):
        saved = full._read_sample(request, inputs, ordinal)
        reference = manifest["sample_archives"][ordinal]
        if (reference["ordinal"] != ordinal
                or reference["artifact_digest"] != saved["artifact_digest"]):
            raise ValueError("an original checkpoint changed after the manifest check")
        final = saved["history"][-1]
        item = {"ordinal": ordinal, "role": saved["role"],
                "sample_artifact_digest": saved["artifact_digest"],
                "address": final["address"], "selected_branch": final["selected_branch"],
                "frame_policy": final["frame_policy"],
                "fiber_basis_labels": final["fiber_basis_labels"],
                "status": "unresolved"}
        try:
            if final["kernel_status"] != "computed_discovery":
                raise ArithmeticError("the original retained sample is unresolved")
            coordinates = np.asarray([
                features._complex(Eisenstein(Fraction(c["center"][0]), Fraction(c["center"][1])))
                for group in final["coordinate_bounds"] for c in group
            ])
            values, jets, metric, residue_squared = consumer.evaluate(
                coordinates, parameters, source_signature=program.source_signature,
            )
            diagnostic = trace_free_curvature(values, jets, metric)
            # dVol_FS = 8 det(g) d^6x, dVol_Omega = |residue|^2 d^6x.
            # The inherited quotient weight omits pi^3; restore it explicitly.
            omega_weight = math.pi**3 * float.fromhex(final["weight_midpoint_without_pi_cubed"])
            background_weight = omega_weight * 8 * np.linalg.det(metric).real / residue_squared
            weighted_l1 = background_weight * diagnostic["trace_free_l1"]
            if (not math.isfinite(background_weight) or background_weight <= 0
                    or not math.isfinite(weighted_l1) or weighted_l1 < 0):
                raise ArithmeticError("the retained reference-volume weighting is unresolved")
            item.update({"status": "computed_discovery", **diagnostic,
                         "reference_volume_weight": float(background_weight),
                         "weighted_trace_free_l1": float(weighted_l1)})
        except (ArithmeticError, ValueError, np.linalg.LinAlgError) as error:
            item["reason"] = str(error)
        points.append(item)
        if progress and (ordinal % 128 == 0 or ordinal + 1 == request["sample_count"]):
            progress({"samples_consumed": ordinal + 1, "sample_count": request["sample_count"],
                      "unresolved_count": sum(p["status"] == "unresolved" for p in points)})
    unresolved = [point["ordinal"] for point in points if point["status"] == "unresolved"]
    complete = not unresolved
    record = {"schema": "full-original-trial-curvature-v1", "source_files_sha256": sources,
              "cloud_request_digest": PARENT_REQUEST, "cloud_manifest_digest": PARENT_CLOUD,
              "input_digest": inputs["artifact_digest"],
              "original_section_basis_digest": features.BASIS,
              "original_section_count": 5345, "section_form": request["section_form"],
              "parameter_point": request["policy"]["parameters"],
              "parameter_point_status": "SELECTED", "entropy_assumption_status": "ASSUMED",
              "reference_polarization": list(POLARIZATION), "reference_quotient_volume": volume,
              "reference_background": "pullback 14 FS_x + 16 FS_u + FS_p; integral_CP1 FS=1",
              "fiber_metric_convention": "h=(S H0 S^dagger)^-1; H0=I in original sections",
              "curvature_convention": "bar-partial(h^-1 partial h), dz_i wedge dbar z_j",
              "untwisting": "pointwise F - trace(F)/4 I; no determinant-volume frame selected",
              "numerical_policy": {"maximum_fiber_condition": 1e12,
                                   "relative_hermiticity_tolerance": 1e-10},
              "points": points, "sample_count": len(points), "unresolved_ordinals": unresolved,
              "complete_original_workload_available": complete,
              "admitted_subset_mean_available": False,
              "old_validation_is_blind": False, "all_old_samples_retained": True,
              "numerical_and_sampling_error_certified": False,
              "reference_background_is_ricci_flat": False, "hym_convergence_established": False,
              "determinant_normalized_su4_metric_exported": False,
              "matter_or_higgs_metrics_available": False, "physical_yukawas_available": False,
              "common_stabilized_vacuum_available": False, "observations_used": False}
    if complete:
        record["full_population_tau_discovery"] = math.fsum(
            point["weighted_trace_free_l1"] for point in points
        ) / (len(points) * 2 * math.pi * volume * 4)
        record["empirical_reference_volume_discovery"] = math.fsum(
            point["reference_volume_weight"] for point in points
        ) / len(points)
        record["role_tau_discovery"] = {
            role: math.fsum(p["weighted_trace_free_l1"] for p in points if p["role"] == role)
            / (sum(p["role"] == role for p in points) * 2 * math.pi * volume * 4)
            for role in ("training", "validation")
        }
    if _sources() != sources:
        raise ValueError("the declared derivative experiment changed during execution")
    record["artifact_digest"] = full.cloud.inputs._digest(record)
    full._install_json(OUTPUT, record)
    return record


if __name__ == "__main__":
    result = run(progress=lambda item: print(json.dumps(item), flush=True))
    print(json.dumps({key: result[key] for key in (
        "artifact_digest", "sample_count", "unresolved_ordinals",
        "complete_original_workload_available",
    )}), flush=True)
