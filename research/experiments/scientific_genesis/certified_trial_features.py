"""Bound original full trial kernels using exact Gaussian dyadic disks.

Owns:
    Integer-only outward disk arithmetic, shared exact polynomial instructions,
    preconditioned full-section perturbations, and certified projector errors.

Depends on:
    The unchanged original polynomial archive, certified native quotient frames,
    and retained discovery rows as explicitly approximate reference values.

Must not:
    Trust floating roundoff, redraw samples, change the section basis, infer
    statistical independence, or promote a finite-cloud error bound to HYM.

Phase 0:
    Research numerical certification only; physical normalization remains open.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from array import array
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from onetheory.math.numbers import Eisenstein

from . import independent_trial_cloud as cloud

features = cloud.features
CLOUD_DIGEST = "706b323d3d1860767e916755d7b982ec2bd9cc4e6a884d064e67d29b8094b10c"
OUTPUT = cloud.OUTPUT.with_name("certified_trial_cloud.json")
PROOF = Path(__file__).with_name("CERTIFIED_TRIAL_FEATURES_NOTE.md")


def _ceil_div(a, b):
    return -((-a) // b)


def _sqrt_ceil(n):
    root = math.isqrt(n)
    return root + (root * root != n)


@dataclass(frozen=True, slots=True)
class Disk:
    """Complex center and circular radius in explicitly declared mesh units.

    The stored center is (real + i imaginary)/2**bits; the radius is
    radius/2**bits. Integers and integer square roots are the entire arithmetic.
    ``upper`` is a checked upper bound on the center modulus, not its norm square.
    """

    real: int
    imaginary: int
    radius: int
    bits: int
    upper: int

    def __post_init__(self):
        if (
            any(
                type(n) is not int
                for n in (self.real, self.imaginary, self.radius, self.bits, self.upper)
            )
            or self.bits < 1
            or self.radius < 0
            or self.upper != _sqrt_ceil(self.real**2 + self.imaginary**2)
        ):
            raise ValueError(
                "exact integer center, radius, modulus bound and positive mesh required"
            )

    @classmethod
    def make(cls, real, imaginary, radius, bits):
        return cls(real, imaginary, radius, bits, _sqrt_ceil(real * real + imaginary * imaginary))

    def _same(self, other):
        if not isinstance(other, Disk) or self.bits != other.bits:
            raise ValueError("disk operations require the same explicit arithmetic mesh")

    def __add__(self, other):
        self._same(other)
        return Disk.make(
            self.real + other.real,
            self.imaginary + other.imaginary,
            self.radius + other.radius,
            self.bits,
        )

    def __neg__(self):
        return Disk(-self.real, -self.imaginary, self.radius, self.bits, self.upper)

    def __sub__(self, other):
        return self + -other

    def __mul__(self, other):
        self._same(other)
        bits, mesh = self.bits, 1 << self.bits
        real = self.real * other.real - self.imaginary * other.imaginary
        imaginary = self.real * other.imaginary + self.imaginary * other.real
        r, i = real >> bits, imaginary >> bits
        # Floor each Gaussian coordinate. Exact products add no rounding radius;
        # otherwise the displacement is less than sqrt(2) mesh units, hence <=2.
        displacement = 2 if real != r * mesh or imaginary != i * mesh else 0
        radius = (
            _ceil_div(
                self.upper * other.radius + other.upper * self.radius + self.radius * other.radius,
                mesh,
            )
            + displacement
        )
        return Disk.make(r, i, radius, bits)

    def conjugate(self):
        return Disk(self.real, -self.imaginary, self.radius, self.bits, self.upper)

    @property
    def absolute_upper(self):
        return self.upper + self.radius


@dataclass(frozen=True, slots=True)
class Arithmetic:
    """Explicit uniform mesh and exact square-root-three embedding bounds."""

    bits: int

    def __post_init__(self):
        if type(self.bits) is not int or self.bits < 1:
            raise ValueError("an explicit positive integer arithmetic mesh is required")

    @property
    def mesh(self):
        return 1 << self.bits

    def gaussian(self, real, imaginary=0, radius=0):
        if any(isinstance(c, (float, complex, bool)) for c in (real, imaginary, radius)):
            raise TypeError("exact rational Gaussian coordinates required")
        real, imaginary, radius = map(Fraction, (real, imaginary, radius))
        if radius < 0:
            raise ValueError("a nonnegative source radius is required")
        r, i = (c * self.mesh for c in (real, imaginary))
        rc, ic = r.numerator // r.denominator, i.numerator // i.denominator
        displacement = abs(r - rc) + abs(i - ic)
        return Disk.make(
            rc,
            ic,
            _ceil_div(
                (radius * self.mesh + displacement).numerator,
                (radius * self.mesh + displacement).denominator,
            ),
            self.bits,
        )

    def eisenstein(self, value, radius=0):
        value = Eisenstein.coerce(value)
        if isinstance(radius, (float, bool)):
            raise TypeError("an exact rational source radius is required")
        radius = Fraction(radius)
        if radius < 0:
            raise ValueError("a nonnegative source radius is required")
        # Extra precision tightens the embedding, but no implicit arithmetic
        # policy changes: every resulting disk still uses the caller's mesh.
        sqrt_mesh = 1 << (self.bits + 16)
        lo = Fraction(math.isqrt(3 * sqrt_mesh * sqrt_mesh), sqrt_mesh)
        hi = lo + Fraction(1, sqrt_mesh)
        a, b = Fraction(value.a), Fraction(value.b)
        endpoints = sorted((b * lo / 2, b * hi / 2))
        middle = sum(endpoints) / 2
        return self.gaussian(a - b / 2, middle, radius + (endpoints[1] - endpoints[0]) / 2)

    def reference(self, value):
        """Treat finite saved binary64 coordinates as exact dyadic references."""

        if (
            not isinstance(value, complex)
            or not math.isfinite(value.real)
            or not math.isfinite(value.imag)
        ):
            raise ValueError("an explicit finite saved complex reference is required")
        return self.gaussian(Fraction.from_float(value.real), Fraction.from_float(value.imag))

    def bounded(self, value):
        return self.eisenstein(value.center, value.radius)

    def zero(self):
        return Disk(0, 0, 0, self.bits, 0)

    def one(self):
        return Disk(self.mesh, 0, 0, self.bits, self.mesh)


def _sum(values, arithmetic):
    # Addition on one fixed mesh is exact; avoid one square root per summand.
    real = imaginary = radius = 0
    for value in values:
        if value.bits != arithmetic.bits:
            raise ValueError("explicit equal arithmetic meshes required")
        real += value.real
        imaginary += value.imaginary
        radius += value.radius
    return Disk.make(real, imaginary, radius, arithmetic.bits)


@dataclass(frozen=True, slots=True)
class CompiledDisks:
    """Complete original exact coefficients and shared monomial instructions."""

    arithmetic: Arithmetic
    signature: tuple
    monomials: tuple
    offsets: bytes
    indices: bytes
    coefficient_indices: bytes
    coefficients: tuple

    def __post_init__(self):
        if (
            not isinstance(self.arithmetic, Arithmetic)
            or type(self.signature) is not tuple
            or type(self.monomials) is not tuple
            or len(self.monomials) != 83523
            or any(
                type(v) is not bytes for v in (self.offsets, self.indices, self.coefficient_indices)
            )
            or len(self.offsets) != 4 * 90866
            or len(self.indices) != 4 * 3621141
            or len(self.coefficient_indices) != len(self.indices)
            or type(self.coefficients) is not tuple
            or any(
                not isinstance(c, Disk) or c.bits != self.arithmetic.bits for c in self.coefficients
            )
        ):
            raise ValueError("immutable full original instructions on one explicit mesh required")
        offsets = memoryview(self.offsets).cast("I")
        if (
            offsets[0] != 0
            or offsets[-1] != 3621141
            or any(x > y for x, y in zip(offsets, offsets[1:], strict=False))
            or any(i >= len(self.monomials) for i in memoryview(self.indices).cast("I"))
            or any(
                i >= len(self.coefficients) for i in memoryview(self.coefficient_indices).cast("I")
            )
        ):
            raise ValueError("the exact original sparse instructions are invalid")

    def evaluate(self, frame, parameters, *, progress=None):
        if (
            not isinstance(frame, features.exact.original.bounded.BoundedFiberFrame)
            or frame.point.chart != (0, 0, 0)
            or len(parameters) != 2
        ):
            raise ValueError("the original admitted chart and explicit parameter pair required")
        a = self.arithmetic
        coordinates = tuple(
            a.bounded(c)
            for group in (
                frame.point.x,
                frame.point.u,
                frame.point.p,
            )
            for c in group
        )
        maxima = tuple(max(m[i] for m in self.monomials) for i in range(8))
        powers = []
        for c, limit in zip(coordinates, maxima, strict=True):
            values = [a.one()]
            for _ in range(limit):
                values.append(values[-1] * c)
            powers.append(values)
        monomials = []
        for m in self.monomials:
            value = a.one()
            for i, exponent in enumerate(m):
                if exponent:
                    value = value * powers[i][exponent]
            monomials.append(value)
        offsets = memoryview(self.offsets).cast("I")
        indices = memoryview(self.indices).cast("I")
        coefficients = memoryview(self.coefficient_indices).cast("I")
        values = []
        for k, (start, end) in enumerate(zip(offsets, offsets[1:], strict=False)):
            values.append(
                _sum(
                    (
                        self.coefficients[coefficients[i]] * monomials[indices[i]]
                        for i in range(start, end)
                    ),
                    a,
                )
            )
            if progress is not None and k % 17000 == 0:
                progress({"bounded_original_polynomials": k})
        projections = tuple(
            tuple(tuple(a.bounded(c) for c in row) for row in matrix)
            for matrix in frame.projections
        )
        eta = tuple(a.eisenstein(p) for p in parameters)
        columns = []
        for index in range(5345):
            constant = values[17 * index : 17 * index + 9]
            correction = (
                values[17 * index + 9 : 17 * index + 13],
                values[17 * index + 13 : 17 * index + 17],
            )
            columns.append(
                tuple(
                    _sum(
                        (
                            _sum((projections[0][i][j] * constant[j] for j in range(9)), a),
                            *(
                                _sum((projections[0][i][j] * correction[m][j] for j in range(4)), a)
                                * eta[m]
                                + _sum(
                                    (projections[m + 1][i][j] * constant[j] for j in range(9)), a
                                )
                                * eta[m]
                                for m in range(2)
                            ),
                        ),
                        a,
                    )
                    for i in range(4)
                )
            )
        return tuple(columns)


def compile_disks(*, bits, progress=None):
    """Compile the trusted original exact stream without cochain reconstruction."""

    before = features._sources()
    a = Arithmetic(bits)
    monomials, lookup = [], {}
    coefficients, coefficient_lookup = [], {}
    offsets, indices, coefficient_indices = array("I", [0]), array("I"), array("I")
    stream_hash = hashlib.sha256()
    count = 0
    with gzip.open(features.exact.MATRIX, "rb") as stream:
        for index, line in enumerate(stream):
            stream_hash.update(line)
            record = json.loads(line)
            if record["basis_index"] != index or index >= 5345:
                raise ValueError("the complete original section order changed")
            groups = (record["constant_generators"], *record["first_parameter_generators"])
            if tuple(map(len, groups)) != (9, 4, 4):
                raise ValueError("the original exact polynomial channels changed")
            for group in groups:
                for polynomial in group:
                    for m, pair in polynomial:
                        m, pair = tuple(m), tuple(pair)
                        if m not in lookup:
                            lookup[m] = len(monomials)
                            monomials.append(m)
                        if pair not in coefficient_lookup:
                            coefficient_lookup[pair] = len(coefficients)
                            coefficients.append(a.eisenstein(Eisenstein(*map(Fraction, pair))))
                        indices.append(lookup[m])
                        coefficient_indices.append(coefficient_lookup[pair])
                    offsets.append(len(indices))
            count += 1
            if progress is not None and index % 1000 == 0:
                progress({"exact_disk_compilation_index": index})
    if (
        count != 5345
        or stream_hash.hexdigest() != before[1]
        or features._sources() != before
        or len(indices) != 3621141
        or len(monomials) != 83523
        or len(offsets) != 90866
    ):
        raise ValueError("the trusted full original coefficient stream changed")
    return CompiledDisks(
        a,
        before[0],
        tuple(monomials),
        offsets.tobytes(),
        indices.tobytes(),
        coefficient_indices.tobytes(),
        tuple(coefficients),
    )


def certify_projector(columns, q, transition, *, arithmetic, weight_interval, reference_weight):
    """Prove a full section-space error bound, or retain unresolved rank admission."""

    if (
        len(q) != 4
        or len(transition) != 4
        or len(columns) != len(q[0])
        or any(len(row) != len(q[0]) for row in q)
        or any(len(row) != 4 for row in transition)
        or any(len(column) != 4 for column in columns)
    ):
        raise ValueError("all four original rows and their explicit fiber transition required")
    # Saved modified Gram--Schmidt transitions are exactly lower triangular
    # as dyadic reference matrices. Their nonzero diagonal proves invertibility.
    if any(transition[i][j] != 0 for i in range(4) for j in range(i + 1, 4)) or any(
        transition[i][i] == 0 for i in range(4)
    ):
        raise ValueError("a nonsingular explicit lower-triangular row preconditioner required")
    a = arithmetic
    change = tuple(tuple(a.reference(c) for c in row) for row in transition)
    reference = tuple(tuple(a.reference(c) for c in row) for row in q)
    gram = tuple(
        tuple(
            _sum((reference[i][k] * reference[j][k].conjugate() for k in range(len(q[0]))), a)
            - a.eisenstein(int(i == j))
            for j in range(4)
        )
        for i in range(4)
    )
    rho_units = _sqrt_ceil(sum(c.absolute_upper**2 for row in gram for c in row))
    errors_squared = 0
    for k, column in enumerate(columns):
        for i in range(4):
            error = _sum((change[i][j] * column[j] for j in range(4)), a) - reference[i][k]
            errors_squared += error.absolute_upper**2
    epsilon_units = _sqrt_ceil(errors_squared)
    rho, epsilon = Fraction(rho_units, a.mesh), Fraction(epsilon_units, a.mesh)
    result = {
        "gram_frobenius_error_upper": str(rho),
        "preconditioned_full_section_error_upper": str(epsilon),
        "section_count": len(columns),
        "arithmetic_mesh_bits": a.bits,
        "row_preconditioner_is_physical_normalization": False,
    }
    if rho >= 1:
        return {**result, "status": "unresolved", "reason": "reference row rank is unresolved"}
    # Exact dyadic floor of sqrt(1-rho), with no floating square root.
    x = (1 - rho) * a.mesh * a.mesh
    sigma = Fraction(math.isqrt(x.numerator // x.denominator), a.mesh)
    result["reference_smallest_singular_value_lower"] = str(sigma)
    if epsilon >= sigma:
        return {
            **result,
            "status": "unresolved",
            "reason": "full-section perturbation does not resolve rank four",
        }
    sqrt_two = Fraction(_sqrt_ceil(2 * a.mesh * a.mesh), a.mesh)
    projector_error = sqrt_two * epsilon / (sigma - epsilon) + rho
    lower, upper = map(Fraction, weight_interval)
    if (
        lower <= 0
        or upper < lower
        or not isinstance(reference_weight, Fraction)
        or reference_weight <= 0
    ):
        raise ValueError("exact positive quotient weight bounds and explicit reference required")
    weight_error = max(abs(reference_weight - lower), abs(reference_weight - upper))
    weighted_error = reference_weight * projector_error + 2 * weight_error
    return {
        **result,
        "status": "certified",
        "ideal_fiber_rank": 4,
        "projector_frobenius_error_upper": str(projector_error),
        "weighted_kernel_frobenius_error_upper_without_pi_cubed": str(weighted_error),
        "weight_absolute_error_upper_without_pi_cubed": str(weight_error),
        "covers_input_and_arithmetic_error": True,
        "sampling_error_included": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
    }


def replay_sample(ordinal, *, levels=(12, 16), max_cells=65536):
    """Reproduce the original native ancestry from retained inputs, never new entropy."""

    record = cloud.inputs.read_inputs(expected_digest=cloud.INPUT_DIGEST)
    available = cloud.inputs.address(record, ordinal)
    geometric = cloud.draws.declared_policy()
    previous = None
    for level in levels:
        address = cloud.roots.refinement_address(available, level)
        policy, work = cloud.roots.refinement_policy(
            level, first_frame=geometric.first, second_frame=geometric.second
        )
        frame_policy = cloud.continuation.FramePolicy(
            (0, 0, 0), (0, 2), (0, 1, 2), 8 * level, Eisenstein(1), 9
        )
        work["max_cells"] = max_cells
        if previous is None:
            previous = cloud.continuation.admit_frame(
                cloud.roots.attempt_subdivision_draw(address, policy, **work),
                frame_policy,
            )
        else:
            previous = cloud.continuation.refine_frame(
                previous, address, policy, frame_policy, **work
            )
    return previous


def certify_saved_sample(program, ordinal, *, refinement_level, max_cells=65536, progress=None):
    """Bound the unchanged saved full discovery kernel on its original native cell."""

    if type(ordinal) is not int or not 0 <= ordinal < 16:
        raise ValueError("an original captured sample ordinal required")
    if type(refinement_level) is not int or not 16 <= refinement_level <= 32:
        raise ValueError("explicit refinement within the retained 128-bit stream required")
    digest, record = features.exact.original.fiber._verified_payload(cloud.OUTPUT)
    if digest != CLOUD_DIGEST:
        raise ValueError("the original trusted cloud changed")
    reference = record["sample_archives"][ordinal]
    path = cloud._checkpoint_path(ordinal)
    if features.exact.archive._file_digest(path) != reference["sha256"]:
        raise ValueError("the trusted original sample bytes changed")
    sample = json.loads(gzip.decompress(path.read_bytes()))
    unsigned = {k: v for k, v in sample.items() if k != "artifact_digest"}
    original_inputs = cloud.inputs.read_inputs(expected_digest=cloud.INPUT_DIGEST)
    if (
        cloud.inputs._digest(unsigned) != sample["artifact_digest"]
        or sample["artifact_digest"] != reference["artifact_digest"]
        or {k: sample[k] for k in ("sample_id", "ordinal", "streams")}
        != (cloud.inputs.sample_identity(original_inputs, ordinal))
    ):
        raise ValueError("the original sample checkpoint changed")
    admission = replay_sample(ordinal)
    if not isinstance(admission, cloud.continuation.AdmittedFrame):
        return {
            "ordinal": ordinal,
            "status": "unresolved",
            "stage": admission.stage,
            "reason": admission.reason,
            "sample_id": sample["sample_id"],
        }
    final = sample["history"][-1]
    expected = cloud._history(admission, 16)
    if any(final[k] != v for k, v in expected.items()):
        raise ValueError("the saved original frame or retained ancestry changed")
    if refinement_level > 16:
        geometric = cloud.draws.declared_policy()
        policy, work = cloud.roots.refinement_policy(
            refinement_level, first_frame=geometric.first, second_frame=geometric.second
        )
        work["max_cells"] = max_cells
        address = cloud.roots.refinement_address(
            cloud.inputs.address(original_inputs, ordinal), refinement_level
        )
        frame_policy = cloud.continuation.FramePolicy(
            (0, 0, 0), (0, 2), (0, 1, 2), 8 * refinement_level, Eisenstein(1), 9
        )
        admission = cloud.continuation.refine_frame(
            admission, address, policy, frame_policy, **work
        )
        if not isinstance(admission, cloud.continuation.AdmittedFrame):
            return {
                "ordinal": ordinal,
                "sample_id": sample["sample_id"],
                "status": "unresolved",
                "stage": admission.stage,
                "reason": admission.reason,
                "refinement_history": cloud._history(admission, refinement_level),
            }
    columns = program.evaluate(admission.frame, (Eisenstein(1), cloud.OMEGA), progress=progress)
    q = cloud._decode_rows(final["kernel_rows"])
    transition = tuple(
        tuple(complex(float.fromhex(c[0]), float.fromhex(c[1])) for c in row)
        for row in final["kernel_diagnostics"]["row_change_of_basis"]
    )
    result = certify_projector(
        columns,
        q,
        transition,
        arithmetic=program.arithmetic,
        weight_interval=cloud.continuation.bounded.bounds._interval_record(
            admission.weight.quotient_weight_without_pi_cubed
        ),
        reference_weight=Fraction.from_float(
            float.fromhex(
                final["weight_midpoint_without_pi_cubed"],
            )
        ),
    )
    return {
        "ordinal": ordinal,
        "sample_id": sample["sample_id"],
        "original_checkpoint_digest": sample["artifact_digest"],
        "refinement_history": cloud._history(admission, refinement_level),
        **result,
    }


def _sources():
    result = cloud._sources()
    for path in (Path(__file__), PROOF):
        result[str(path.relative_to(features.exact.domains.ROOT))] = hashlib.sha256(
            path.read_bytes(),
        ).hexdigest()
    digest, original = features.exact.original.fiber._verified_payload(cloud.OUTPUT)
    if digest != CLOUD_DIGEST:
        raise ValueError("the original independent cloud changed")
    for reference in original["sample_archives"]:
        path = features.exact.domains.ROOT / reference["path"]
        if features.exact.archive._file_digest(path) != reference["sha256"]:
            raise ValueError("an original retained cloud archive changed")
    return result


def _checkpoint_path(ordinal):
    return OUTPUT.with_name(f"certified_trial_cloud.sample_{ordinal:04d}.json.gz")


def write_certificates(*, bits, refinement_level, max_cells, progress=None):
    """Bound every original sample; any unresolved member prevents a mean bound."""

    Arithmetic(bits)
    if (
        type(refinement_level) is not int
        or not 16 <= refinement_level <= 32
        or type(max_cells) is not int
        or max_cells < 1
    ):
        raise ValueError("explicit retained-stream refinement and positive work cap required")
    before = _sources()
    policy = {
        "arithmetic_mesh_bits": bits,
        "original_levels": [12, 16],
        "refinement_level": refinement_level,
        "max_cells": max_cells,
    }
    signature = cloud.inputs._digest(
        {"original_cloud_digest": CLOUD_DIGEST, "source_files_sha256": before, "policy": policy}
    )
    program = compile_disks(bits=bits, progress=progress)
    samples, references = [], []
    for ordinal in range(16):
        path = _checkpoint_path(ordinal)
        if path.exists():
            sample = json.loads(gzip.decompress(path.read_bytes()))
            unsigned = {k: v for k, v in sample.items() if k != "artifact_digest"}
            if (
                cloud.inputs._digest(unsigned) != sample["artifact_digest"]
                or sample["execution_signature"] != signature
            ):
                raise ValueError("retain the certificate checkpoint belonging to its original run")
        else:
            sample = certify_saved_sample(
                program,
                ordinal,
                refinement_level=refinement_level,
                max_cells=max_cells,
                progress=progress,
            )
            sample["execution_signature"] = signature
            sample["artifact_digest"] = cloud.inputs._digest(sample)
            cloud._install_sample(path, sample)
        samples.append(sample)
        references.append(
            {
                "ordinal": ordinal,
                "path": str(path.relative_to(features.exact.domains.ROOT)),
                "sha256": features.exact.archive._file_digest(path),
                "artifact_digest": sample["artifact_digest"],
            }
        )
        if progress is not None:
            progress(
                {
                    "certified_sample_ordinal": ordinal,
                    "status": sample["status"],
                    "perturbation_upper": sample.get("preconditioned_full_section_error_upper"),
                }
            )
    unresolved = [s["ordinal"] for s in samples if s["status"] != "certified"]
    result = {
        "schema": "certified-retained-trial-cloud-v1",
        "original_cloud_digest": CLOUD_DIGEST,
        "input_digest": cloud.INPUT_DIGEST,
        "original_section_basis_digest": features.BASIS,
        "compilation_parent_digest": features.COMPILATION,
        "source_files_sha256": before,
        "policy": policy,
        "execution_signature": signature,
        "sample_count": 16,
        "sample_certificates": references,
        "unresolved_sample_ordinals": unresolved,
        "finite_cloud_numerical_error_bound_available": not unresolved,
        "arithmetic": "exact integer Gaussian disk centers, radii and square-root bounds",
        "roundoff_assumptions_used": False,
        "original_discovery_references_overwritten": False,
        "sample_operator_rank_upper_bound": 64,
        "minimum_samples_necessary_for_invertibility": 1337,
        "entropy_assumption_status": "ASSUMED",
        "sampling_error_included": False,
        "failed_samples_dropped": False,
        "controlled_integral_available": False,
        "nonunit_h_iteration_executed": False,
        "ricci_flat_or_hym_metric_available": False,
        "physical_yukawas_available": False,
        "common_stabilized_vacuum_available": False,
        "observations_used": False,
    }
    if not unresolved:
        mean_bound = (
            sum(
                Fraction(s["weighted_kernel_frobenius_error_upper_without_pi_cubed"])
                for s in samples
            )
            / 16
        )
        # Outward dyadic rounding keeps the certificate compact without hiding
        # uncertainty or requiring a gigantic product-denominator serialization.
        bound = Fraction(
            _ceil_div(mean_bound.numerator * (1 << bits), mean_bound.denominator), 1 << bits
        )
        result["finite_cloud_mean_operator_frobenius_error_upper_without_pi_cubed"] = str(bound)
    if _sources() != before:
        raise ValueError("original inputs or certificate sources changed during execution")
    result["artifact_digest"] = cloud.inputs._digest(result)
    encoded = cloud.inputs._canonical(result) + b"\n"
    if OUTPUT.exists() and OUTPUT.read_bytes() != encoded:
        raise FileExistsError("preserve existing finite-cloud certificates; no silent replacement")
    if not OUTPUT.exists():
        with OUTPUT.open("xb") as stream:
            stream.write(encoded)
    return result


def read_certificates(*, expected_digest, path=OUTPUT):
    """Verify retained certificate identities and algebraic bounds without resampling."""

    result = json.loads(path.read_bytes())
    unsigned = {k: v for k, v in result.items() if k != "artifact_digest"}
    if result.get("artifact_digest") != expected_digest or cloud.inputs._digest(unsigned) != (
        expected_digest
    ):
        raise ValueError("the trusted finite-cloud certificate changed")
    if (
        result["schema"] != "certified-retained-trial-cloud-v1"
        or result["original_cloud_digest"] != CLOUD_DIGEST
        or result["input_digest"] != cloud.INPUT_DIGEST
        or result["original_section_basis_digest"] != features.BASIS
        or result["compilation_parent_digest"] != features.COMPILATION
        or result["source_files_sha256"] != _sources()
        or result["sample_count"] != 16
        or len(result["sample_certificates"]) != 16
        or result["entropy_assumption_status"] != "ASSUMED"
        or result["sample_operator_rank_upper_bound"] != 64
        or result["minimum_samples_necessary_for_invertibility"] != 1337
    ):
        raise ValueError("the original sources, basis or certificate scope changed")
    for key in (
        "roundoff_assumptions_used",
        "original_discovery_references_overwritten",
        "sampling_error_included",
        "failed_samples_dropped",
        "controlled_integral_available",
        "nonunit_h_iteration_executed",
        "ricci_flat_or_hym_metric_available",
        "physical_yukawas_available",
        "common_stabilized_vacuum_available",
        "observations_used",
    ):
        if result[key] is not False:
            raise ValueError("finite-cloud numerical control cannot be promoted to physical output")
    signature = cloud.inputs._digest(
        {
            "original_cloud_digest": CLOUD_DIGEST,
            "source_files_sha256": _sources(),
            "policy": result["policy"],
        }
    )
    if result["execution_signature"] != signature:
        raise ValueError("the explicit certificate request changed")
    originals = cloud.inputs.read_inputs(expected_digest=cloud.INPUT_DIGEST)
    samples = []
    for ordinal, reference in enumerate(result["sample_certificates"]):
        archive_path = _checkpoint_path(ordinal)
        if (
            reference["ordinal"] != ordinal
            or reference["path"] != str(archive_path.relative_to(features.exact.domains.ROOT))
            or features.exact.archive._file_digest(archive_path) != reference["sha256"]
        ):
            raise ValueError("a retained original sample certificate changed")
        sample = json.loads(gzip.decompress(archive_path.read_bytes()))
        signed = {k: v for k, v in sample.items() if k != "artifact_digest"}
        if (
            sample["artifact_digest"] != reference["artifact_digest"]
            or cloud.inputs._digest(signed) != reference["artifact_digest"]
            or sample["execution_signature"] != signature
            or sample["ordinal"] != ordinal
            or sample["sample_id"] != cloud.inputs.sample_identity(originals, ordinal)["sample_id"]
        ):
            raise ValueError("a sample lost its original identity")
        if sample["status"] == "certified":
            _check_bound(sample, result["policy"], ordinal, originals)
        elif sample["status"] != "unresolved" or not sample["reason"]:
            raise ValueError("an unavailable sample must retain its explicit reason")
        samples.append(sample)
    unresolved = [s["ordinal"] for s in samples if s["status"] != "certified"]
    if result["unresolved_sample_ordinals"] != unresolved or result[
        "finite_cloud_numerical_error_bound_available"
    ] is not (not unresolved):
        raise ValueError("failed samples cannot become an admitted-subset mean")
    if not unresolved:
        value = (
            sum(
                Fraction(s["weighted_kernel_frobenius_error_upper_without_pi_cubed"])
                for s in samples
            )
            / 16
        )
        bits = result["policy"]["arithmetic_mesh_bits"]
        bound = Fraction(_ceil_div(value.numerator * (1 << bits), value.denominator), 1 << bits)
        if result["finite_cloud_mean_operator_frobenius_error_upper_without_pi_cubed"] != str(
            bound
        ):
            raise ValueError("the full sixteen-sample operator error bound changed")
    return result


def _check_bound(sample, policy, ordinal, originals):
    """Independently reconstruct the scalar perturbation inequality from its witnesses."""

    bits = policy["arithmetic_mesh_bits"]
    a = Arithmetic(bits)
    rho = Fraction(sample["gram_frobenius_error_upper"])
    epsilon = Fraction(sample["preconditioned_full_section_error_upper"])
    x = (1 - rho) * a.mesh * a.mesh
    if not 0 <= rho < 1 or epsilon < 0:
        raise ValueError("a positive rank margin is required")
    sigma = Fraction(math.isqrt(x.numerator // x.denominator), a.mesh)
    if epsilon >= sigma or str(sigma) != sample["reference_smallest_singular_value_lower"]:
        raise ValueError("the full ideal rank gate is unresolved")
    bound = Fraction(_sqrt_ceil(2 * a.mesh * a.mesh), a.mesh) * epsilon / (sigma - epsilon) + rho
    original = json.loads(gzip.decompress(cloud._checkpoint_path(ordinal).read_bytes()))
    reference_weight = Fraction.from_float(
        float.fromhex(
            original["history"][-1]["weight_midpoint_without_pi_cubed"],
        )
    )
    history = sample["refinement_history"]
    level = policy["refinement_level"]
    if (
        history["address"]
        != cloud.draws._address_record(
            cloud.roots.refinement_address(cloud.inputs.address(originals, ordinal), level)
        )
        or history["level"] != level
        or history["status"] != "admitted"
        or history["root_parent_retained"] is not True
        or history["frame_parent_retained"] is not True
        or sample["original_checkpoint_digest"] != original["artifact_digest"]
        or sample["section_count"] != 5345
        or sample["ideal_fiber_rank"] != 4
        or sample["arithmetic_mesh_bits"] != bits
        or sample["covers_input_and_arithmetic_error"] is not True
        or sample["sampling_error_included"] is not False
        or sample["row_preconditioner_is_physical_normalization"] is not False
        or sample["ricci_flat_or_hym_metric_available"] is not False
        or sample["physical_yukawas_available"] is not False
    ):
        raise ValueError("a certificate changed its original scientific identity or scope")
    lower, upper = map(Fraction, history["quotient_weight_without_pi_cubed"])
    weight_error = max(abs(reference_weight - lower), abs(reference_weight - upper))
    if (
        lower <= 0
        or upper < lower
        or sample["projector_frobenius_error_upper"] != str(bound)
        or sample["weight_absolute_error_upper_without_pi_cubed"] != str(weight_error)
        or sample["weighted_kernel_frobenius_error_upper_without_pi_cubed"]
        != str(reference_weight * bound + 2 * weight_error)
    ):
        raise ValueError("the certified full-kernel error inequality changed")


if __name__ == "__main__":
    result = write_certificates(
        bits=160,
        refinement_level=24,
        max_cells=65536,
        progress=lambda r: print(json.dumps(r), flush=True),
    )
    print(result["artifact_digest"], flush=True)
