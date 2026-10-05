"""Attack the full original sparse discovery evaluator independently.

Owns:
    Complete execution checks, exact Fraction-pair arithmetic probes, existing
    interval comparisons, basis/source rejection, and nonphysical scope gates.

Depends on:
    The original polynomial archive, named quotient frames, and pytest.

Must not:
    Promote numerical centers or regression domains into physical or IID data.

Phase 0:
    Research numerical discovery tests; global integration remains unresolved.
"""

import gzip
import hashlib
import json
import math
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
from functools import cache

import pytest

from research.experiments.scientific_genesis import compiled_section_features as module

EXECUTION = "6d0cc28da2e9426cb7803cc096ca735dbed2a499acaecb3cd2a91067aa5d225a"


@cache
def _program():
    return module.compile_features()


@cache
def _records():
    # Held-out indices are not those used to construct the coefficient compiler.
    selected = {407, 3089, 5017}
    with gzip.open(module.exact.MATRIX, "rb") as stream:
        return {i: json.loads(line) for i, line in enumerate(stream) if i in selected}


def _add(a, b):
    return a[0]+b[0], a[1]+b[1]


def _multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]-a[1]*b[1]


def _pair(value):
    return Fraction(value.a), Fraction(value.b)


def _embedding(pair):
    return complex(float(pair[0]-pair[1]/2), float(pair[1]) * math.sqrt(3)/2)


def _independent_center_columns(record, frame):
    """Use stdlib rational-pair products, not the sparse or polynomial engine."""

    zero = Fraction(0), Fraction(0)
    one = Fraction(1), Fraction(0)
    coordinates = tuple(_pair(c.center) for group in (
        frame.point.x, frame.point.u, frame.point.p,
    ) for c in group)
    all_polynomials = [p for group in (record["constant_generators"],
                                       *record["first_parameter_generators"]) for p in group]
    maxima = [max((m[i] for p in all_polynomials for m, _ in p), default=0) for i in range(8)]
    powers = []
    for c, n in zip(coordinates, maxima, strict=True):
        values = [one]
        for _ in range(n):
            values.append(_multiply(values[-1], c))
        powers.append(values)
    evaluated = []
    for polynomial in all_polynomials:
        value = zero
        for monomial, coefficient in polynomial:
            term = tuple(map(Fraction, coefficient))
            for i, exponent in enumerate(monomial):
                term = _multiply(term, powers[i][exponent])
            value = _add(value, term)
        evaluated.append(value)
    projections = tuple(tuple(tuple(_pair(c.center) for c in row) for row in matrix)
                        for matrix in frame.projections)

    def dot(row, values):
        result = zero
        for a, b in zip(row, values, strict=True):
            result = _add(result, _multiply(a, b))
        return result

    result = [tuple(dot(row, evaluated[:9]) for row in projections[0])]
    for m in range(2):
        correction = evaluated[9+4*m:13+4*m] + [zero]*5
        result.append(tuple(_add(dot(row, correction), dot(other, evaluated[:9]))
                            for row, other in zip(projections[0], projections[m+1], strict=True)))
    return tuple(tuple(_embedding(c) for c in row) for row in result)


@pytest.mark.parametrize("domain_index", (0, 10, 14))
def test_discovery_matches_independent_exact_center_and_existing_bounds(domain_index):
    program = _program()
    _, _, frame = module.exact.domains.declared_frames()[domain_index]
    values = program.evaluate(frame, source_signature=program.source_signature)
    assert len(values.columns) == 5345
    assert values.basis_digest == module.BASIS
    assert values.fiber_labels == frame.basis_labels
    saved = json.loads(module.OUTPUT.read_bytes())["domains"][domain_index]
    assert saved["coefficient_stream_sha256"] == hashlib.sha256(
        module.exact.archive._canonical([
            [[[c.real.hex(), c.imag.hex()] for c in row] for row in column]
            for column in values.columns
        ]),
    ).hexdigest()
    for index, record in _records().items():
        witness = _independent_center_columns(record, frame)
        compiled = module.exact.parse_column(record, index=index, chart=(0, 0, 0),
                                            source_signature=program.source_signature)
        certified = compiled.evaluate(frame, source_signature=program.source_signature)
        scale = max(1, *(abs(c) for row in witness for c in row))
        for channel in range(3):
            for row in range(4):
                discovered = values.columns[index][channel][row]
                assert abs(discovered-witness[channel][row]) <= 1e-10 * scale
                enclosure = certified[channel][row][0]
                assert abs(discovered-module._complex(enclosure.center)) <= (
                    float(enclosure.radius) + 1e-10 * scale
                )


def test_program_is_complete_immutable_and_keeps_source_and_basis_identity():
    program = _program()
    assert len(memoryview(program.offsets).cast("I")) == 90866
    assert len(memoryview(program.feature_indices).cast("I")) == 3621141
    assert memoryview(program.coefficients).readonly
    assert all(m[0] == m[3] == m[6] == 0 for m in program.features)
    with pytest.raises(FrozenInstanceError):
        program.features = ()
    with pytest.raises(TypeError, match="immutable"):
        replace(program, coefficients=bytearray(program.coefficients))
    with pytest.raises(ValueError, match="original polynomial"):
        replace(program, offsets=program.offsets[:-4])
    with pytest.raises(ValueError, match="unique monomials"):
        replace(program, source_signature=())
    with pytest.raises(ValueError, match="original sparse"):
        replace(program, coefficients=program.coefficients[:-16])


def test_per_point_discovery_does_not_rebuild_exact_cochains(monkeypatch):
    program = _program()
    _, _, frame = module.exact.domains.declared_frames()[0]

    def reject(*args, **kwargs):
        raise AssertionError("per-point exact construction is forbidden in discovery mode")

    monkeypatch.setattr(module.exact.CompiledColumn, "evaluate", reject)
    monkeypatch.setattr(module.exact.SymbolicCompiler, "compile_basis", reject)
    actual = program.evaluate(frame, source_signature=program.source_signature)
    repeated = program.evaluate(frame, source_signature=program.source_signature)
    assert actual == repeated
    with pytest.raises(ValueError, match="source identity"):
        program.evaluate(frame, source_signature=())
    with pytest.raises(TypeError, match="admitted"):
        program.evaluate(object(), source_signature=program.source_signature)


def test_nonfinite_embedding_never_falls_back_to_zero():
    with pytest.raises((OverflowError, ValueError)):
        module._complex(module.exact.Eisenstein(10**1000))


@pytest.mark.parametrize("repetitions", (0, -1, True, 1.0))
def test_benchmark_requires_an_explicit_positive_workload(repetitions):
    with pytest.raises(ValueError, match="repetition"):
        module.benchmark(repetitions=repetitions)


def test_source_guard_rejects_rehashed_wrong_compilation(monkeypatch):
    original = module.exact.original.fiber._verified_payload

    def forged(path):
        digest, record = original(path)
        if path == module.exact.OUTPUT:
            record = {**record, "section_count": 5344}
        return digest, record

    monkeypatch.setattr(module.exact.original.fiber, "_verified_payload", forged)
    with pytest.raises(ValueError, match="trusted original"):
        module._sources()


def test_saved_complete_execution_preserves_all_domain_and_physics_boundaries():
    record = module.read_execution(expected_digest=EXECUTION)
    payload = {k: v for k, v in record.items() if k != "artifact_digest"}
    assert hashlib.sha256(module.exact.archive._canonical(payload)).hexdigest() == (
        record["artifact_digest"]
    )
    program = _program()
    assert record["source_sha256"] == hashlib.sha256(
        module.Path(module.__file__).read_bytes(),
    ).hexdigest()
    assert record["section_count"] == 5345
    assert record["exact_term_count"] == 3621141
    assert record["shared_monomial_count"] == len(program.features)
    assert record["instruction_sha256"] == hashlib.sha256(
        program.offsets+program.feature_indices+program.coefficients,
    ).hexdigest()
    assert [(d["component"], tuple(d["branch"])) for d in record["domains"]] == [
        (name, branch) for name, branch, _ in module.exact.domains.declared_frames()
    ]
    assert all(d["repetitions"] == 2 and d["elapsed_seconds"] > 0 for d in record["domains"])
    for flag in ("coordinate_centers_are_cover_points", "numerical_error_bound_certified",
                 "input_radii_propagated", "independent_cloud_available",
                 "controlled_integral_available", "nonunit_h_iteration_executed",
                 "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
                 "common_stabilized_vacuum_available", "extension_parameters_specialized",
                 "observations_used"):
        assert record[flag] is False


@pytest.mark.parametrize("change", (
    {"section_count": 5344}, {"numerical_error_bound_certified": True},
    {"input_radii_propagated": True}, {"independent_cloud_available": True},
    {"controlled_integral_available": True}, {"nonunit_h_iteration_executed": True},
    {"physical_yukawas_available": True}, {"original_section_basis_digest": "0"*64},
))
def test_rehashed_scope_changes_cannot_masquerade_as_a_trusted_execution(
    tmp_path, monkeypatch, change,
):
    original = json.loads(module.OUTPUT.read_bytes())
    payload = {k: v for k, v in original.items() if k != "artifact_digest"}
    payload.update(change)
    digest = hashlib.sha256(module.exact.archive._canonical(payload)).hexdigest()
    forged = tmp_path / "forged.json"
    forged.write_bytes(module.exact.archive._canonical({**payload, "artifact_digest": digest}))
    monkeypatch.setattr(module, "OUTPUT", forged)
    with pytest.raises(ValueError, match="trusted digest"):
        module.read_execution(expected_digest=EXECUTION)
    with pytest.raises(ValueError, match="scientific scope"):
        module.read_execution(expected_digest=digest)


def test_missing_measured_execution_does_not_return_a_synthetic_benchmark(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        module.read_execution(expected_digest=EXECUTION)
