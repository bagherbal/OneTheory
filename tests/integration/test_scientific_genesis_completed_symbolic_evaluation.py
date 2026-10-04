"""Check the actual complete numerical stream against exact polynomial witnesses.

Owns:
    Independent rational parsing of every saved fiber coefficient, consistency
    with the previous original-domain stream, and exact Gaussian probe checks.

Depends on:
    Completed original polynomial and numerical archives, explicit uncertain
    cover frames, exact scalar arithmetic and independent raw-arrow quotients.

Must not:
    Treat overlap as equality, probes as all-column cochain replay, runtime as
    practical sampling throughput, or a single domain as a physical metric.

Phase 0:
    Research execution verification; controlled integration remains unresolved.
"""

import copy
import gzip
import hashlib
import json
from fractions import Fraction
from functools import cache
from math import prod

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.scientific_genesis import alternate_metric_fiber_functionals as previous
from research.experiments.scientific_genesis import alternate_metric_symbolic_evaluation as module
from tests.integration.test_scientific_genesis_completed_symbolic_columns import (
    DIGEST as COMPILATION_DIGEST,
)
from tests.integration.test_scientific_genesis_completed_symbolic_columns import (
    PROBES,
)
from tests.integration.test_scientific_genesis_completed_symbolic_columns import (
    _inspection as _polynomial_records,
)
from tests.integration.test_scientific_genesis_uncertain_cover_frames import (
    _full_boundary,
    _functional,
)

DIGEST = "b439fab56d1095001f6f7ec5bb795d2606c55f4e51beb8b8e66959023c4318d9"
ARCHIVE_SHA = "794217a2df51b0eca496d9396d5d8cae470079fbbaa43631e3c69183cb78f322"
STREAM_SHA = "a7f48c7da40064c11548bd6956301e03dd28b47f82d5dc16fe9dd958d06665a3"


def _scalar(record):
    assert set(record) == {"center", "radius"}
    assert len(record["center"]) == 2
    raw = (*record["center"], record["radius"])
    assert all(type(value) is str for value in raw)
    a, b, radius = tuple(Fraction(value) for value in raw)
    assert tuple(str(value) for value in (a, b, radius)) == raw
    assert radius >= 0 and (radius * 2**100).denominator == 1
    return Eisenstein(a, b), radius


@cache
def _inspection():
    """Read both actual streams; no producer parser or new evaluation is used."""

    selected, count, uncertain, largest = {}, 0, 0, Fraction(0)
    digest = hashlib.sha256()
    with gzip.open(module.MATRIX, "rb") as stream, gzip.open(previous.MATRIX, "rb") as old:
        for index, (line, earlier) in enumerate(zip(stream, old, strict=True)):
            record, reference = json.loads(line), json.loads(earlier)
            assert set(record) == {"basis_index", "coefficient_columns_constant_a0_a1"}
            assert type(record["basis_index"]) is int and record["basis_index"] == index
            assert reference["basis_index"] == index
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
            assert line == canonical + b"\n"
            matrices = record["coefficient_columns_constant_a0_a1"]
            assert len(matrices) == 3
            for parameter, (matrix, other) in enumerate(zip(
                matrices, reference["coefficient_columns_constant_a0_a1"], strict=True,
            )):
                assert len(matrix) == 4
                for row, old_row in zip(matrix, other, strict=True):
                    assert len(row) == 1
                    center, radius = _scalar(row[0])
                    old_center, old_radius = _scalar(old_row[0])
                    # Different outward evaluation orders need not be equal.
                    # Overlap is necessary consistency, not proof of equality.
                    assert (center - old_center).norm() <= (radius + old_radius)**2
                    if index < 2655 and parameter > 0:
                        assert center.is_zero() and radius == 0
                    uncertain += int(radius > 0)
                    largest = max(largest, radius)
            if index in PROBES:
                selected[index] = matrices
            digest.update(line)
            count += 1
    assert count == 5345 and uncertain == 21430
    assert largest == Fraction(
        "136745486219359945981577150497088181/1267650600228229401496703205376")
    assert digest.hexdigest() == STREAM_SHA
    return selected


def test_completed_numerical_archive_has_every_original_coefficient_and_trusted_provenance():
    assert hashlib.sha256(module.MATRIX.read_bytes()).hexdigest() == ARCHIVE_SHA
    assert module.MATRIX.stat().st_size == 1216047
    assert set(_inspection()) == set(PROBES)
    record = module.verify_completed_domain(
        expected_digest=DIGEST, expected_compilation_digest=COMPILATION_DIGEST,
    )
    assert record["section_count"] == 5345
    assert record["coefficient_entry_count"] == 64140
    assert record["complete_original_basis_evaluated"] is True
    assert record["bound_bits"] == record["uncertain_center_bits"] == 100


def _exact_polynomial(polynomial, values):
    """Evaluate saved rational pairs directly, without SymbolicColumn or Ball."""

    return sum((Eisenstein(*(Fraction(c) for c in coefficient))
                * prod((value**exponent for value, exponent in zip(values, monomial, strict=True)),
                       start=Eisenstein(1))
                for monomial, coefficient in polynomial), start=Eisenstein(0))


@pytest.mark.parametrize("index", PROBES)
def test_saved_numerical_columns_contain_independent_exact_polynomial_gaussian_probes(index):
    raw = _polynomial_records()[index]
    saved = tuple(tuple(_scalar(row[0]) for row in matrix) for matrix in _inspection()[index])
    _, _, frame = module.domains.declared_frames()[0]
    for offset in (0, 1):
        values = _functional(frame, offset)
        constant = tuple(_exact_polynomial(p, values) for p in raw["constant_generators"])
        parameters = tuple(tuple(_exact_polynomial(p, values) for p in group)
                           + (Eisenstein(0),) * 5 for group in raw["first_parameter_generators"])
        for a0, a1, radius_factors in ((Eisenstein(1), OMEGA, (1, 1)),
                                     (OMEGA, Eisenstein(2, -1), (1, 3))):
            # The factors are exact upper bounds: |omega|=1, |2-omega|^2=7<9.
            # These arithmetic witnesses are neither selected moduli nor draws.
            _, quotient = _full_boundary(values, frame, a0, a1)
            column = Matrix(tuple((c + a0*x + a1*y,) for c, x, y in zip(
                constant, *parameters, strict=True)), scalar_type=Eisenstein)
            expected = quotient.matmul(column)
            for row, value in enumerate(expected):
                center = saved[0][row][0] + a0*saved[1][row][0] + a1*saved[2][row][0]
                radius = (saved[0][row][1] + radius_factors[0]*saved[1][row][1]
                          + radius_factors[1]*saved[2][row][1])
                assert (value[0] - center).norm() <= radius**2


@pytest.mark.parametrize("field", (
    "original_section_basis_digest", "normalized_cover_bounds", "complete_compilation_digest",
    "all_15_domains_executed", "controlled_integral_available", "physical_yukawas_available",
))
def test_rehashed_numerical_output_cannot_change_execution_or_scientific_scope(
    field, tmp_path, monkeypatch,
):
    changed = copy.deepcopy(json.loads(module.OUTPUT.read_text()))
    changed[field] = not changed[field] if type(changed[field]) is bool else "changed"
    changed.pop("artifact_digest")
    changed["artifact_digest"] = hashlib.sha256(module.archive._canonical(changed)).hexdigest()
    path = tmp_path / "inflated.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="trusted digest"):
        module.verify_completed_domain(
            expected_digest=DIGEST, expected_compilation_digest=COMPILATION_DIGEST,
        )


def test_missing_numerical_output_is_not_replaced_with_a_partial_stream(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "missing-complete.json")
    with pytest.raises(FileNotFoundError):
        module.verify_completed_domain(
            expected_digest=DIGEST, expected_compilation_digest=COMPILATION_DIGEST,
        )
    assert not module.OUTPUT.exists()


def test_numerical_stream_identity_cannot_claim_point_independent_or_physical_results():
    record = json.loads(module.OUTPUT.read_text())
    assert record["original_section_basis_digest"] not in (
        record["artifact_digest"], record["exact_column_stream_sha256"], COMPILATION_DIGEST,
    )
    for flag in ("point_dependent_stream_is_global_section_identity", "all_15_domains_executed",
                 "independent_all_column_cochain_replay",
                 "practical_multi_point_throughput_certified",
                 "independent_cloud_available", "controlled_integral_available",
                 "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
                 "common_stabilized_vacuum_available", "extension_point_selected",
                 "centers_are_exact_cover_points", "observations_used"):
        assert record[flag] is False
