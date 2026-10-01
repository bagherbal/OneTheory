"""Verify coefficient specialization of the actual universal section evaluator.

Owns:
    Exact homotopy/perturbation naturality attacks, independent full-cochain
    probe comparison, deck-phase rejection, and complete column-stream integrity.

Depends on:
    Frozen outer source data, the original full-cover operators, the specialized
    research evaluator, and independent previously archived fiber evaluations.

Must not:
    Treat algebraic operator units as physical states, infer numerical sampling
    convergence, or select a vacuum or extension coordinate.

Phase 0:
    Research evaluation tests only; controlled metrics remain unresolved.
"""

import gzip
import hashlib
import json
from dataclasses import replace

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
    _homotopy,
)
from research.experiments.scientific_genesis import alternate_metric_specialized_evaluation as spec


@pytest.fixture(scope="module")
def engine():
    p = spec.fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    return spec.SpecializedEvaluator(spec.fiber.fiber_frame(p, (0, 2), (0, 1, 2)))


def _actual_units():
    """Use actual arrow/source columns, not invented bundle coefficients."""

    source = spec.fiber.lifts.second._context()[0]
    target = spec.fiber.lifts.first._context()[0]
    selected = {}
    for extension in spec.fiber.lifts._inputs()[2]:
        for b, c in extension.terms:
            right = b.component.right_index
            if right >= 5:
                continue
            key = b.component.left_index, b.component.koszul_summand, tuple(map(len, b.cell))
            if key in selected:
                continue
            dx, du, dp = source.left.objects[right].line_degree
            component = target.components[b.component.left_index, 0, b.component.koszul_summand]
            selected[key] = SparseOuterCechCochain(((OuterCechBasis(
                component,
                tuple(x + y for x, y in zip(b.x_monomial, (0, dx - 2, 2), strict=True)),
                tuple(x + y for x, y in zip(b.u_monomial, (du - 1, 1, 0), strict=True)),
                tuple(x + y for x, y in zip(b.p_monomial, (dp, 0), strict=True)), b.cell,
            ), c),))
    return tuple(selected.values())


def test_specialization_commutes_with_actual_homotopy_and_perturbation(engine):
    target = engine.target
    units = _actual_units()
    assert len(units) > 10
    for u in engine.u_channels:
        operator = spec._SpecializedPerturbation(target, u, ())
        for unit in units:
            encoded = spec._encode(unit, u)
            assert spec._encode(_homotopy(unit), u) == _homotopy(encoded)
            assert spec._encode(target.perturbation(unit), u) == operator.perturbation(encoded)


def test_all_four_full_cochain_fiber_probes_are_reproduced_coefficientwise(engine):
    parent = json.loads(spec.fiber.OUTPUT.read_text())
    expected = parent["actual_section_coefficients_constant_a0_a1"]
    for col, index in enumerate(parent["actual_basis_indices"]):
        result = engine.evaluate_basis(index)
        assert [spec.fiber._matrix_record(m) for m in result] == [
            [[expected[p][row][col]] for row in range(4)] for p in range(3)
        ]


def test_omitting_dummy_deck_phase_cannot_pass_the_full_cochain_gate(monkeypatch):
    p = spec.fiber.CoverPoint((1, -1, 0), (1, 1, 1), (0, 1), (0, 0, 1))
    broken = spec.SpecializedEvaluator(spec.fiber.fiber_frame(p, (0, 2), (0, 1, 2)))
    actual = spec._monomial_action

    def without_u_phase(monomial, images):
        scalar, image = actual(monomial, images)
        return (Eisenstein(1), image) if images == broken.p.u_images else (scalar, image)

    monkeypatch.setattr(spec, "_monomial_action", without_u_phase)
    parent = json.loads(spec.fiber.OUTPUT.read_text())
    position = parent["actual_basis_indices"].index(2670)
    expected = [[[parent["actual_section_coefficients_constant_a0_a1"][p][row][position]]
                 for row in range(4)] for p in range(3)]
    assert [spec.fiber._matrix_record(m) for m in broken.evaluate_basis(2670)] != expected


def test_specialized_evaluation_retains_explicit_projective_normalization(engine):
    point = engine.frame.point
    rescaled = spec.fiber.CoverPoint(tuple(2 * c for c in point.x), tuple(3 * c for c in point.u),
                                   tuple(5 * c for c in point.p), point.chart)
    other = spec.SpecializedEvaluator(spec.fiber.fiber_frame(rescaled, (0, 2), (0, 1, 2)))
    assert other.evaluate_basis(2670) == engine.evaluate_basis(2670)


def test_complementary_chart_matches_the_original_full_cochain_evaluator():
    """Swap the zero-coordinate factor and P1 chart without choosing moduli."""

    point = spec.fiber.CoverPoint((1, 1, 1), (1, -1, 0), (1, 0), (0, 0, 0))
    frame = spec.fiber.fiber_frame(point, (0, 2), (0, 1, 2))
    engine = spec.SpecializedEvaluator(frame)
    assert all(operator.zero_x == () for operator in engine.operators)
    # This actual injected V2 section is nonzero on this distinct exact point.
    source = spec.fiber.compact_coordinates(
        spec.fiber.lifts._inputs()[1][1][2670 - 2655], point,
        spec.fiber.lifts.second._context()[0],
    )
    assert any(not coordinate.is_zero() for coordinate in source)
    assert engine.evaluate_basis(2670) == frame.evaluate_basis(2670)


def test_second_plane_laurent_poles_are_not_silently_specialized(engine):
    b, c = _actual_units()[0].terms[0]
    degree = sum(b.u_monomial)
    b = replace(b, u_monomial=(-1, degree + 1, 0), cell=(b.cell[0], (0, 1), b.cell[2]))
    with pytest.raises(ValueError, match="Laurent pole"):
        spec._encode(SparseOuterCechCochain(((b, c),)), engine.frame.point.u)
    for invalid in (-1, 5345, True, 1.0):
        with pytest.raises(ValueError, match="basis index"):
            engine.evaluate_basis(invalid)


def test_complete_exact_column_stream_and_scientific_scope():
    digest, payload = spec.fiber._verified_payload(spec.OUTPUT)
    archive = spec.MATRIX.read_bytes()
    raw = gzip.decompress(archive)
    assert hashlib.sha256(archive).hexdigest() == payload["matrix_archive_sha256"]
    assert hashlib.sha256(raw).hexdigest() == payload["exact_column_stream_sha256"]
    columns = json.loads(raw)
    assert payload["section_count"] == len(columns) == 5345
    assert all(len(column) == 3 and all(len(m) == 4 and all(len(row) == 1 for row in m)
                                       for m in column) for column in columns)
    assert payload["fiber_evaluation_artifact_digest"] == spec.fiber._verified_payload(
        spec.fiber.OUTPUT,
    )[0]
    assert payload["regularity_premises"] == spec.regularity_premises()
    assert payload["actual_spanning_minor_all_parameters"] == "1/81"
    assert payload["complete_5345_column_point_matrix_materialized"] is True
    assert payload["all_probe_coefficients_match_full_cochain_evaluation"] is True
    assert digest
    for flag in ("controlled_numerical_sampling_available", "numerical_metrics_available",
                 "physical_yukawas_available", "extension_point_selected",
                 "observational_inputs_used"):
        assert payload[flag] is False
