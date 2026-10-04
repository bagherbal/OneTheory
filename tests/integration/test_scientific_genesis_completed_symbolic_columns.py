"""Verify the completed original polynomial archive without replaying the compiler.

Owns:
    Independent full-stream shape, coefficient and original-order inspection,
    full-cochain probes from actual archive columns, and scope-inflation attacks.

Depends on:
    Trusted complete polynomial execution, original corrected section cochains,
    the independent raw-arrow quotient check, and exact Fraction arithmetic.

Must not:
    Call partial output complete, substitute numerical stream hashes for section
    identity, or infer all-column cochain replay, an integral, or a physical metric.

Phase 0:
    Research execution verification only; normalization and convergence are open.
"""

import copy
import gzip
import hashlib
import json
from fractions import Fraction
from functools import cache

import pytest

from onetheory.math.linear import Matrix
from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.scientific_genesis import alternate_metric_symbolic_columns as module
from tests.integration.test_scientific_genesis_uncertain_cover_frames import (
    _contains,
    _dehomogenized_coefficients,
    _full_boundary,
    _functional,
    _specialize,
)

DIGEST = "63dcc3ff50a8cf3aadbd896dd20a732774efbc460d714daeb2ee8ce41c44a488"
ARCHIVE_SHA = "2f587826ae4cfee863e8016149d1ef827b538c91df6560876cabb557a4be3815"
STREAM_SHA = "35471fcc01237efca2d83f09128d0a1e70242716d6612a97951e5a7eec58567e"
PROBES = (0, 1273, 2655, 3790, 5344)


@cache
def _inspection():
    """Inspect EVERY actual record independently of the production stream parser."""

    selected, digest, terms, count = {}, hashlib.sha256(), 0, 0
    with gzip.open(module.MATRIX, "rb") as stream:
        for index, line in enumerate(stream):
            record = json.loads(line)
            assert set(record) == {
                "basis_index", "constant_generators", "first_parameter_generators",
            }
            assert type(record["basis_index"]) is int and record["basis_index"] == index
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
            assert line == canonical + b"\n"
            constant = record["constant_generators"]
            parameters = record["first_parameter_generators"]
            assert len(constant) == 9 and len(parameters) == 2
            assert all(len(group) == 4 for group in parameters)
            if index < 2655:
                assert all(not p for p in constant[4:])
                assert all(not p for group in parameters for p in group)
            for polynomial in (*constant, *parameters[0], *parameters[1]):
                previous = None
                for monomial, coefficient in polynomial:
                    assert len(monomial) == 8
                    assert all(type(e) is int and e >= 0 for e in monomial)
                    assert all(monomial[i] == 0 for i in (0, 3, 6))
                    current = tuple(monomial)
                    assert previous is None or previous > current
                    previous = current
                    assert len(coefficient) == 2 and all(type(c) is str for c in coefficient)
                    pair = tuple(Fraction(c) for c in coefficient)
                    assert tuple(str(c) for c in pair) == tuple(coefficient)
                    assert pair != (0, 0)
                    terms += 1
            if index in PROBES:
                selected[index] = record
            digest.update(line)
            count += 1
    assert count == 5345
    assert terms == 3621141
    assert digest.hexdigest() == STREAM_SHA
    return selected


def test_complete_archive_is_independently_ordered_exact_and_content_addressed():
    assert hashlib.sha256(module.MATRIX.read_bytes()).hexdigest() == ARCHIVE_SHA
    assert set(_inspection()) == set(PROBES)
    record = module.verify_completed_chart(expected_digest=DIGEST)
    assert record["section_count"] == 5345
    assert record["polynomial_count"] == 90865
    assert record["exact_polynomial_term_count"] == 3621141
    assert record["complete_original_basis_compiled"] is True


@pytest.mark.parametrize("index", PROBES)
def test_actual_completed_columns_match_independent_full_cochain_quotients(index):
    """Use the saved column, not a second invocation of SymbolicCompiler."""

    _, _, frame = module.domains.declared_frames()[0]
    column = module.parse_column(_inspection()[index], index=index, chart=(0, 0, 0),
                                 source_signature=module._source_signature())
    bounded = column.evaluate(frame, source_signature=module._source_signature())
    # The old domain wrapper deliberately permits only its two declared probes.
    # Reuse the underlying FULL constructor for all five original indices.
    section = module.original.fiber.lifts.universal_section(index)
    contexts = (module.original.fiber.lifts.first._context()[0],
                module.original.fiber.lifts.second._context()[0])
    for offset in (0, 1):
        values = _functional(frame, offset)
        constant = (_dehomogenized_coefficients(section.first_constant, values,
                                                frame.point, contexts[0])
                    + _dehomogenized_coefficients(section.second_constant, values,
                                                  frame.point, contexts[1]))
        corrections = tuple(_dehomogenized_coefficients(c, values, frame.point, contexts[0])
                            + (Eisenstein(0),) * 5 for c in section.first_coefficients)
        for a0, a1 in ((Eisenstein(1), OMEGA), (OMEGA, Eisenstein(2, -1))):
            _, quotient = _full_boundary(values, frame, a0, a1)
            full = Matrix(tuple((c + a0*x + a1*y,) for c, x, y in zip(
                constant, *corrections, strict=True)), scalar_type=Eisenstein)
            _contains(_specialize(bounded, a0, a1), quotient.matmul(full))


@pytest.mark.parametrize("flag", (
    "every_chart_compiled", "independent_all_column_cochain_replay",
    "practical_multi_point_throughput_certified", "controlled_integral_available",
    "physical_yukawas_available", "independent_cloud_available",
))
def test_rehashed_completion_cannot_claim_an_unperformed_physical_calculation(
    flag, tmp_path, monkeypatch,
):
    changed = copy.deepcopy(json.loads(module.OUTPUT.read_text()))
    changed[flag] = True
    changed.pop("artifact_digest")
    digest = hashlib.sha256(module.archive._canonical(changed)).hexdigest()
    changed["artifact_digest"] = digest
    path = tmp_path / "inflated.json"
    path.write_text(json.dumps(changed))
    monkeypatch.setattr(module, "OUTPUT", path)
    with pytest.raises(ValueError, match="trusted digest"):
        module.verify_completed_chart(expected_digest=DIGEST)


def test_missing_complete_archive_has_no_partial_prefix_fallback(tmp_path, monkeypatch):
    missing = module.MATRIX.with_name(f".missing-complete-{tmp_path.name}.gz")
    assert not missing.exists()
    # Retain the reader's repository-root path contract; no file is created.
    monkeypatch.setattr(module, "MATRIX", missing)
    with pytest.raises(FileNotFoundError):
        module.verify_completed_chart(expected_digest=DIGEST)


def test_original_section_identity_remains_separate_from_the_completed_point_chart():
    identity = module.section_basis_identity()
    assert identity["artifact_digest"] == (
        "71f9c2f46c1f7a69087e8f3aab1ed98f4474cf76cf66db5bf2c902f4f372621c"
    )
    assert identity["numeric_point_or_chart_input"] is False
    assert "chart_pivots" not in identity
    assert "exact_polynomial_stream_sha256" not in identity
