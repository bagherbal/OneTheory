"""Evaluate the frozen original section polynomials through shared numeric features.

Owns:
    A source-bound sparse binary64 discovery representation of all original
    section coefficients and the existing rank-four quotient projections.

Depends on:
    The certified complete exact polynomial archive and original named frames.

Must not:
    Replace the exact verifier, call centers geometric points, infer numerical
    error bounds, select physical moduli, or report integration or HYM metrics.

Phase 0:
    Research discovery arithmetic only; physical normalization remains unresolved.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from array import array
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from time import perf_counter

from . import alternate_metric_symbolic_columns as exact

COMPILATION = "63dcc3ff50a8cf3aadbd896dd20a732774efbc460d714daeb2ee8ce41c44a488"
ARCHIVE_SHA = "2f587826ae4cfee863e8016149d1ef827b538c91df6560876cabb557a4be3815"
STREAM_SHA = "35471fcc01237efca2d83f09128d0a1e70242716d6612a97951e5a7eec58567e"
BASIS = "71f9c2f46c1f7a69087e8f3aab1ed98f4474cf76cf66db5bf2c902f4f372621c"
OUTPUT = exact.OUTPUT.with_name("compiled_section_features.json")
PROOF = Path(__file__).with_name("COMPILED_SECTION_FEATURES_NOTE.md")


def _sources():
    digest, metadata = exact.original.fiber._verified_payload(exact.OUTPUT)
    signature = exact._source_signature()
    if (digest != COMPILATION or metadata["matrix_archive_sha256"] != ARCHIVE_SHA
        or metadata["exact_polynomial_stream_sha256"] != STREAM_SHA
        or exact.archive._file_digest(exact.MATRIX) != ARCHIVE_SHA
        or metadata["original_source_signature"] != json.loads(json.dumps(signature))
        or metadata["proof_sha256"] != hashlib.sha256(exact.PROOF.read_bytes()).hexdigest()
        or metadata["section_count"] != 5345 or metadata["polynomial_count"] != 90865
        or metadata["exact_polynomial_term_count"] != 3621141
        or exact.section_basis_identity()["artifact_digest"] != BASIS):
        raise ValueError("the trusted original compilation or section identity changed")
    return signature, metadata["exact_polynomial_stream_sha256"]


def _complex(value):
    """Explicit binary64 embedding of Q(omega), not exact arithmetic."""

    a, b = float(value.a), float(value.b)
    result = complex(a - b / 2, b * (math.sqrt(3) / 2))
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ValueError("binary64 discovery arithmetic overflowed; use the exact verifier")
    return result


@dataclass(frozen=True, slots=True)
class DiscoveryValues:
    """Full original coefficient columns with explicit noncertified arithmetic."""

    basis_digest: str
    fiber_labels: tuple
    chart: tuple
    source_signature: tuple
    columns: tuple
    center_bits: int
    bound_bits: int


@dataclass(frozen=True, slots=True)
class CompiledFeatures:
    """Immutable CSR polynomial instructions sharing the original monomials.

    Byte buffers use native uint32 and binary64; their layout is declared in
    execution metadata. They are not a portable physical-input archive.
    """

    source_signature: tuple
    features: tuple
    offsets: bytes
    feature_indices: bytes
    coefficients: bytes

    def __post_init__(self):
        if array("I").itemsize != 4 or array("d").itemsize != 8:
            raise ValueError("uint32 and binary64 discovery buffers required")
        if any(type(b) is not bytes for b in (
            self.offsets, self.feature_indices, self.coefficients,
        )):
            raise TypeError("immutable instruction bytes required")
        if (type(self.source_signature) is not tuple or type(self.features) is not tuple
            or len(self.source_signature) != 2
            or any(type(part) is not tuple or not part or any(type(pair) is not tuple
                or len(pair) != 2 or any(type(s) is not str for s in pair) for pair in part)
                for part in self.source_signature)
            or not self.features or len(set(self.features)) != len(self.features)
            or any(type(m) is not tuple or len(m) != 8 or any(type(e) is not int or e < 0
                for e in m) or any(m[i] for i in (0, 3, 6)) for m in self.features)):
            raise ValueError("unique monomials in the original normalized chart required")
        if len(self.offsets) != 4 * (90865 + 1) or len(self.feature_indices) % 4:
            raise ValueError("complete original polynomial instruction shapes required")
        offsets = memoryview(self.offsets).cast("I")
        indices = memoryview(self.feature_indices).cast("I")
        if (offsets[0] != 0 or offsets[-1] != 3621141 or len(indices) != offsets[-1]
            or any(a > b for a, b in zip(offsets, offsets[1:], strict=False))
            or len(self.coefficients) != 16 * len(indices)
            or any(i >= len(self.features) for i in indices)
            or any(not math.isfinite(c) for c in memoryview(self.coefficients).cast("d"))):
            raise ValueError("complete finite original sparse instructions required")

    def evaluate(self, frame, *, source_signature):
        """Evaluate all sections at explicit arithmetic centers, not cover points.

        Precision and input radii remain those of the caller's certified frame.
        This mode does not propagate these radii or certify binary64 roundoff.
        """

        if not isinstance(frame, exact.original.bounded.BoundedFiberFrame):
            raise TypeError("an original admitted bounded quotient frame required")
        if frame.point.chart != (0, 0, 0) or source_signature != self.source_signature:
            raise ValueError("the frozen chart and original source identity must match")
        coordinates = tuple(_complex(c.center) for group in (
            frame.point.x, frame.point.u, frame.point.p,
        ) for c in group)
        maximum = tuple(max(m[i] for m in self.features) for i in range(8))
        powers = tuple(tuple(c ** n for n in range(limit + 1))
                       for c, limit in zip(coordinates, maximum, strict=True))
        features = []
        for monomial in self.features:
            value = complex(1)
            for i, exponent in enumerate(monomial):
                if exponent:
                    value *= powers[i][exponent]
            features.append(value)
        offsets = memoryview(self.offsets).cast("I")
        indices = memoryview(self.feature_indices).cast("I")
        coefficients = memoryview(self.coefficients).cast("d")
        polynomials = []
        for start, end in zip(offsets, offsets[1:], strict=False):
            total = complex(0)
            for i in range(start, end):
                total += complex(coefficients[2*i], coefficients[2*i+1]) * features[indices[i]]
            polynomials.append(total)
        projections = tuple(tuple(tuple(_complex(c.center) for c in row) for row in matrix)
                            for matrix in frame.projections)
        columns = []
        for index in range(5345):
            constant = polynomials[17*index:17*index+9]
            result = [tuple(sum(a*b for a, b in zip(row, constant, strict=True))
                            for row in projections[0])]
            for parameter in range(2):
                correction = polynomials[17*index+9+4*parameter:17*index+13+4*parameter]
                result.append(tuple(
                    sum(row[j] * correction[j] for j in range(4))
                    + sum(a*b for a, b in zip(other, constant, strict=True))
                    for row, other in zip(projections[0], projections[parameter+1], strict=True)
                ))
            if any(not math.isfinite(c.real) or not math.isfinite(c.imag)
                   for values in result for c in values):
                raise ValueError(
                    "discovery values overflowed; refine or change arithmetic explicitly",
                )
            columns.append(tuple(result))
        return DiscoveryValues(BASIS, frame.basis_labels, frame.point.chart,
                               self.source_signature, tuple(columns), frame.point.center_bits,
                               frame.point.bits)


def compile_features(*, progress=None):
    """Compile verified exact bytes once without rerunning cochain construction."""

    before = _sources()
    features, lookup = [], {}
    offsets, indices, coefficients = array("I", [0]), array("I"), array("d")
    coefficient_cache = {}
    stream_hash = hashlib.sha256()
    count = 0
    with gzip.open(exact.MATRIX, "rb") as stream:
        for index, line in enumerate(stream):
            stream_hash.update(line)
            record = json.loads(line)
            if record["basis_index"] != index or index >= 5345:
                raise ValueError("the complete original section order changed")
            groups = (record["constant_generators"], *record["first_parameter_generators"])
            if tuple(map(len, groups)) != (9, 4, 4):
                raise ValueError("the original polynomial channels changed")
            for group in groups:
                for polynomial in group:
                    for monomial, pair in polynomial:
                        monomial = tuple(monomial)
                        feature = lookup.get(monomial)
                        if feature is None:
                            feature = len(features)
                            features.append(monomial)
                            lookup[monomial] = feature
                        pair = tuple(pair)
                        if pair not in coefficient_cache:
                            a, b = map(Fraction, pair)
                            coefficient_cache[pair] = complex(float(a - b/2),
                                                             float(b) * (math.sqrt(3)/2))
                        value = coefficient_cache[pair]
                        indices.append(feature)
                        coefficients.extend((value.real, value.imag))
                    offsets.append(len(indices))
            count += 1
            if progress is not None and (index % 500 == 0 or index == 5344):
                progress({"last_original_index": index, "feature_count": len(features)})
    if count != 5345 or stream_hash.hexdigest() != before[1] or _sources() != before:
        raise ValueError("trusted original polynomial bytes changed during compilation")
    return CompiledFeatures(before[0], tuple(features), offsets.tobytes(),
                            indices.tobytes(), coefficients.tobytes())


def benchmark(*, repetitions, progress=None):
    """Measure repeated complete discovery evaluation on all 15 fixed domains."""

    if type(repetitions) is not int or repetitions < 1:
        raise ValueError("a positive explicit repetition count required")
    before = _sources()
    implementation = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    proof = hashlib.sha256(PROOF.read_bytes()).hexdigest()
    started = perf_counter()
    program = compile_features(progress=progress)
    compile_seconds = perf_counter() - started
    domains = exact.domains.declared_frames()
    records = []
    for name, branch, frame in domains:
        started = perf_counter()
        results = [program.evaluate(frame, source_signature=before[0])
                   for _ in range(repetitions)]
        elapsed = perf_counter() - started
        if any(r != results[0] for r in results[1:]):
            raise ValueError("repeated discovery evaluation changed its scientific identity")
        values = results[0]
        checksum = hashlib.sha256(exact.archive._canonical([
            [[[c.real.hex(), c.imag.hex()] for c in row] for row in column]
            for column in values.columns
        ])).hexdigest()
        records.append({"component": name, "branch": list(branch),
                        "repetitions": repetitions, "elapsed_seconds": elapsed,
                        "coefficient_stream_sha256": checksum,
                        "fiber_basis_labels": list(frame.basis_labels),
                        "center_bits": values.center_bits, "bound_bits": values.bound_bits})
        if progress is not None:
            progress(records[-1])
    if (_sources() != before or implementation != hashlib.sha256(
        Path(__file__).read_bytes()).hexdigest()
        or proof != hashlib.sha256(PROOF.read_bytes()).hexdigest()):
        raise ValueError("original sources changed during repeated discovery execution")
    result = {"schema": "compiled-section-features-v1", "compilation_digest": COMPILATION,
        "source_archive_sha256": ARCHIVE_SHA, "original_section_basis_digest": BASIS,
        "original_source_signature": before[0], "section_count": 5345,
        "polynomial_count": 90865, "exact_term_count": 3621141,
        "shared_monomial_count": len(program.features),
        "instruction_bytes": sum(map(len, (program.offsets, program.feature_indices,
                                            program.coefficients))),
        "instruction_sha256": hashlib.sha256(program.offsets + program.feature_indices
                                               + program.coefficients).hexdigest(),
        "arithmetic": "native uint32 indices; binary64 complex discovery centers",
        "byte_order": sys.byteorder, "compile_seconds": compile_seconds,
        "source_sha256": implementation,
        "proof_sha256": proof,
        "domains": records, "domain_role": "15 fixed regression domains, not IID samples",
        "complete_original_sections_evaluated": True,
        "coordinate_centers_are_cover_points": False,
        "numerical_error_bound_certified": False, "input_radii_propagated": False,
        "independent_cloud_available": False, "controlled_integral_available": False,
        "nonunit_h_iteration_executed": False, "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False, "common_stabilized_vacuum_available": False,
        "extension_parameters_specialized": False, "observations_used": False}
    result["artifact_digest"] = hashlib.sha256(exact.archive._canonical(result)).hexdigest()
    return result


def read_execution(*, expected_digest):
    """Validate a trusted measured workload without treating timing as a proof."""

    before = _sources()
    digest, record = exact.original.fiber._verified_payload(OUTPUT)
    if digest != expected_digest:
        raise ValueError("the frozen discovery execution changed its trusted digest")
    required = {"schema": "compiled-section-features-v1", "compilation_digest": COMPILATION,
        "source_archive_sha256": ARCHIVE_SHA, "original_section_basis_digest": BASIS,
        "original_source_signature": before[0], "section_count": 5345,
        "polynomial_count": 90865, "exact_term_count": 3621141,
        "arithmetic": "native uint32 indices; binary64 complex discovery centers",
        "byte_order": sys.byteorder,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "domain_role": "15 fixed regression domains, not IID samples",
        "complete_original_sections_evaluated": True}
    for flag in ("coordinate_centers_are_cover_points", "numerical_error_bound_certified",
                 "input_radii_propagated", "independent_cloud_available",
                 "controlled_integral_available", "nonunit_h_iteration_executed",
                 "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
                 "common_stabilized_vacuum_available", "extension_parameters_specialized",
                 "observations_used"):
        required[flag] = False
    exact.archive._require_scope(record, required)
    domains = exact.domains.declared_frames()
    if (len(record["domains"]) != len(domains)
        or type(record["shared_monomial_count"]) is not int
        or not 0 < record["shared_monomial_count"] <= 3621141
        or record["instruction_bytes"] != 4*(90865+1) + 20*3621141
        or len(record["instruction_sha256"]) != 64
        or not math.isfinite(record["compile_seconds"]) or record["compile_seconds"] <= 0):
        raise ValueError("complete measured discovery workload required")
    for actual, (name, branch, frame) in zip(record["domains"], domains, strict=True):
        if (actual["component"] != name or actual["branch"] != list(branch)
            or actual["fiber_basis_labels"] != list(frame.basis_labels)
            or actual["center_bits"] != frame.point.center_bits
            or actual["bound_bits"] != frame.point.bits
            or type(actual["repetitions"]) is not int or actual["repetitions"] < 1
            or len(actual["coefficient_stream_sha256"]) != 64
            or not math.isfinite(actual["elapsed_seconds"]) or actual["elapsed_seconds"] <= 0):
            raise ValueError("every original regression identity and finite timing required")
    if _sources() != before:
        raise ValueError("the original discovery sources changed during inspection")
    return {"artifact_digest": digest, **record}


if __name__ == "__main__":
    record = benchmark(repetitions=2, progress=lambda r: print(json.dumps(r), flush=True))
    # Timings are a new measured run, not an immutable mathematical input.
    if OUTPUT.exists():
        raise FileExistsError("retain existing benchmark; declare a new output for a new run")
    with OUTPUT.open("xb") as stream:
        stream.write(exact.archive._canonical(record) + b"\n")
    print(record["artifact_digest"], flush=True)
