"""Enclose dyadic input cells for the auxiliary uniform projective law.

Owns:
    Explicit simplex-spacing and phase inputs, rational transcendental bounds,
    coupled homogeneous-coordinate disks, and projective input error bounds.

Depends on:
    Exact Rational and Eisenstein arithmetic, established circular enclosures,
    and the declared positive auxiliary projective-intersection law.

Must not:
    Treat disk centers as uniform samples or exact cover points, generate
    physical coefficients, reject tied bins, select moduli, or assert metrics.

Phase 0:
    Research input precision only; controlled cover sampling remains absent.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from math import factorial, isqrt
from pathlib import Path

from onetheory.math.numbers import Eisenstein, Rational

from .alternate_metric_enclosures import Ball, Interval

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/projective_uniform_input_cells.json"
PROOF = Path(__file__).with_name("PROJECTIVE_UNIFORM_INPUT_CELLS_NOTE.md")


@dataclass(frozen=True, slots=True)
class InputPolicy:
    """Caller-declared dyadic input resolution and finite analytic work limits."""

    cell_bits: int
    bound_bits: int
    atan_terms: int
    taylor_terms: int

    def __post_init__(self):
        for value in (self.cell_bits, self.bound_bits, self.atan_terms, self.taylor_terms):
            if type(value) is not int or value < 1:
                raise ValueError("all input precision and work limits must be positive integers")


def _sqrt_endpoints(value, bits):
    """Enclose one nonnegative rational square root by integer arithmetic."""

    if value < 0:
        raise ValueError("a square-root endpoint cannot be negative")
    scale = 1 << bits
    square = value.numerator * value.denominator * scale**2
    floor = isqrt(square)
    lower = Rational(floor, value.denominator * scale)
    return lower, (lower if floor**2 == square else
                   Rational(floor + 1, value.denominator * scale))


def sqrt_interval(value):
    """Retain exact singleton roots when rational; otherwise round outward."""

    lo = _sqrt_endpoints(value.lower, value.bits)[0]
    hi = _sqrt_endpoints(value.upper, value.bits)[1]
    return Interval(lo, hi, value.bits)


def pi_interval(policy):
    """Apply the alternating atan remainder to the exact Machin identity."""

    def atan_inverse(inverse):
        x = Rational(1, inverse)
        value = sum(((-1)**k * x**(2 * k + 1) / (2 * k + 1)
                     for k in range(policy.atan_terms)), Rational(0))
        next_term = (-1)**policy.atan_terms * x**(2 * policy.atan_terms + 1) / (
            2 * policy.atan_terms + 1
        )
        return Interval(min(value, value + next_term), max(value, value + next_term),
                        policy.bound_bits)

    return atan_inverse(5) * 16 - atan_inverse(239) * 4


def phase_rectangles(cell, policy):
    """Bound cos/sin on a full phase cell with Taylor and derivative remainders."""

    if cell.bits != policy.bound_bits or not 0 <= cell.lower <= cell.upper <= 1:
        raise ValueError("phase bounds require a compatible interval inside the unit cell")
    pi = pi_interval(policy)
    midpoint = (cell.lower + cell.upper) / 2
    pi_midpoint = (pi.lower + pi.upper) / 2
    angle = 2 * pi_midpoint * midpoint
    angle_error = pi.upper * cell.width + midpoint * pi.width
    order = 2 * policy.taylor_terms
    remainder = abs(angle)**order / factorial(order) + angle_error
    cosine = sum(((-1)**k * angle**(2 * k) / factorial(2 * k)
                  for k in range(policy.taylor_terms)), Rational(0))
    sine = sum(((-1)**k * angle**(2 * k + 1) / factorial(2 * k + 1)
                for k in range(policy.taylor_terms)), Rational(0))

    def enclose(value):
        return Interval(max(Rational(-1), value - remainder),
                        min(Rational(1), value + remainder), policy.bound_bits)

    return enclose(cosine), enclose(sine)


def _cell(index, policy):
    if type(index) is not int or not 0 <= index < 1 << policy.cell_bits:
        raise ValueError("a supplied input index must lie in its declared dyadic range")
    return Interval(Rational(index, 1 << policy.cell_bits),
                    Rational(index + 1, 1 << policy.cell_bits), policy.bound_bits)


def spacing_intervals(indices, policy):
    """Enclose sorted-uniform spacings without rejecting overlapping or tied bins."""

    ordered = tuple(sorted((_cell(index, policy) for index in indices),
                           key=lambda value: value.lower))
    if len(ordered) not in (1, 2):
        raise ValueError("the current projective law requires one or two ordered uniforms")
    endpoints = (Interval(Rational(0), Rational(0), policy.bound_bits), *ordered,
                 Interval(Rational(1), Rational(1), policy.bound_bits))
    differences = tuple(right - left for left, right in zip(endpoints[:-1], endpoints[1:],
                                                            strict=True))
    return tuple(Interval(max(Rational(0), value.lower), min(Rational(1), value.upper),
                          policy.bound_bits) for value in differences)


def _rectangle_disk(real, imaginary):
    """Convert a complex rectangle without pretending that i lies in Q(omega)."""

    real_mid = (real.lower + real.upper) / 2
    imaginary_mid = (imaginary.lower + imaginary.upper) / 2
    inv_sqrt_three = sqrt_interval(Interval(Rational(3), Rational(3), real.bits)).inverse()
    inverse_mid = (inv_sqrt_three.lower + inv_sqrt_three.upper) / 2
    center = Eisenstein(real_mid + imaginary_mid * inverse_mid,
                        2 * imaginary_mid * inverse_mid)
    # The chosen imaginary center equals sqrt(3)*inverse_mid*imaginary_mid.
    # sqrt(3)<2 gives a rational bound for its displacement from imaginary_mid.
    radius = (real.width + imaginary.width) / 2 + abs(imaginary_mid) * (
        inv_sqrt_three.width
    )
    return Ball(center, radius, real.bits)


@dataclass(frozen=True, slots=True)
class ProjectiveInputCell:
    """Disks enclosing one coupled unit representative, not independent coordinates."""

    spacing_indices: tuple[int, ...]
    phase_indices: tuple[int, ...]
    policy: InputPolicy
    spacings: tuple[Interval, ...]
    coordinates: tuple[Ball, ...]

    @property
    def center_distance_bound(self):
        """Bound the Euclidean distance of the ideal representative from the center."""

        return sum((value.radius for value in self.coordinates), Rational(0))

    @property
    def projective_chordal_diameter_bound(self):
        """Bound projective distance between any two ideal points in this cell."""

        return 2 * self.center_distance_bound


def projective_input_cell(spacing_indices, phase_indices, *, policy):
    """Convert declared bit cells; the caller must justify independent uniform inputs.

    The first homogeneous phase is fixed to zero only to remove common phase.
    The same construction applies to hyperplane covectors in the dual space.
    No RNG, cover equation, chosen physical basis, or moduli enters this map.
    """

    spacing_indices, phase_indices = tuple(spacing_indices), tuple(phase_indices)
    if len(phase_indices) != len(spacing_indices):
        raise ValueError("one independent phase is required per projective dimension")
    spacings = spacing_intervals(spacing_indices, policy)
    phases = tuple(_cell(index, policy) for index in phase_indices)
    amplitudes = tuple(sqrt_interval(value) for value in spacings)
    zero = Interval(Rational(0), Rational(0), policy.bound_bits)
    coordinates = [_rectangle_disk(amplitudes[0], zero)]
    for amplitude, phase in zip(amplitudes[1:], phases, strict=True):
        cosine, sine = phase_rectangles(phase, policy)
        coordinates.append(_rectangle_disk(amplitude * cosine, amplitude * sine))
    return ProjectiveInputCell(spacing_indices, phase_indices, policy, spacings,
                               tuple(coordinates))


def input_cell_record():
    """Record deterministic boundary probes, not an independent sampling cloud."""

    policy = InputPolicy(8, 60, 30, 40)
    probes = (((0,), (255,)), ((255,), (0,)),
              ((127, 127), (0, 255)), ((240, 16), (17, 201)))
    records = []
    for spacing, phases in probes:
        cell = projective_input_cell(spacing, phases, policy=policy)
        records.append({
            "spacing_indices": list(spacing), "phase_indices": list(phases),
            "spacing_intervals": [[str(v.lower), str(v.upper)] for v in cell.spacings],
            "coordinate_disks": [{"center": [str(v.center.a), str(v.center.b)],
                                  "radius": str(v.radius)} for v in cell.coordinates],
            "center_distance_bound": str(cell.center_distance_bound),
            "projective_chordal_diameter_bound": str(cell.projective_chordal_diameter_bound),
        })
    return {
        "schema": "projective-uniform-input-cells-v1",
        "law": "normalized FS on CP^1 or CP^2; dual hyperplane covectors use the same law",
        "probability_assumption": "all spacing and phase cell indices independent uniform",
        "input_cell_bits": policy.cell_bits, "bound_bits": policy.bound_bits,
        "atan_terms": policy.atan_terms, "taylor_terms": policy.taylor_terms,
        "proof_sha256": hashlib.sha256(PROOF.read_bytes()).hexdigest(),
        "declared_boundary_probes": records,
        "coupled_projective_input_cell_enclosures_available": True,
        "ideal_uniform_input_law_derived": True,
        "random_generator_implemented": False,
        "independent_cover_sampling_cloud_available": False,
        "uncertain_input_intersection_roots_certified": False,
        "centers_are_exact_cover_points": False,
        "total_variation_convergence_claimed": False,
        "numerical_metrics_available": False, "physical_yukawas_available": False,
        "extension_point_selected": False, "vacuum_selected": False,
        "observational_inputs_used": False,
    }


def _digest(record):
    serialized = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(serialized).hexdigest()


def write_input_cells(path=OUTPUT):
    """Serialize the executed finite probes with their exact proof provenance."""

    record = input_cell_record()
    record["artifact_digest"] = _digest(record)
    path.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return record


def read_input_cells(path=OUTPUT):
    """Recompute every cell disk and scope flag; never treat presence as a sampler."""

    record = json.loads(path.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest", None)
    if digest != _digest(record) or record != input_cell_record():
        raise ValueError("the projective input cells changed their bounds, inputs, proof, or scope")
    return record


if __name__ == "__main__":
    print(write_input_cells()["artifact_digest"])
