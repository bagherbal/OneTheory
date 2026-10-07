"""Attack the retained polarization's stability-theorem applicability.

Owns:
    Independent exact intersection, normalization, strict-interval, scaling
    and scope-mutation tests for the original metric section system.

Depends on:
    The research scope certificate, exact Rational arithmetic, published
    stability rows and pytest; no cloud geometry or new entropy is needed.

Must not:
    Treat mathematical test divisors as physical data, sufficient-bound failure
    as instability, or an interval witness as a selected vacuum.

Phase 0:
    Exact research theorem-scope tests only; HYM remains unresolved.
"""

import hashlib
import json
from copy import deepcopy
from fractions import Fraction

import pytest

from onetheory.math.numbers import Rational
from onetheory.models.heterotic_schoen.visible import STABILITY_ROWS
from research.experiments.scientific_genesis import metric_polarization_scope as module

CERTIFICATE = "4b05abef53e7814af7b5faca2511e35944dc1df603a78bfe02b6809e100bb9e8"


def _line_slope(line, polarization):
    """An independent exact Chow coefficient, not a call to either tensor."""

    a, b, c = map(Fraction, polarization)
    x, u, p = map(Fraction, line)
    return x * (6 * a * b + 3 * b * b + 18 * b * c) + u * (
        3 * a * a + 6 * a * b + 18 * a * c
    ) + p * 18 * a * b


def test_actual_scope_packet_preserves_physical_unavailability(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("a scope reader must not draw inputs or write artifacts")

    monkeypatch.setattr("os.urandom", forbidden)
    monkeypatch.setattr(module.Path, "write_text", forbidden)
    monkeypatch.setattr(module.Path, "write_bytes", forbidden)
    record = module.read_certificate(expected_digest=CERTIFICATE)
    assert record["status"] == "PROVED"
    assert record["retained_twist"] == [14, 16, 1]
    assert record["original_section_count"] == 5345
    assert record["sufficient_chamber_test_passed"] is False
    assert record["every_positive_rescaling_has_the_same_slope_signs"] is True
    for flag in (
        "scope_failure_is_a_bundle_instability_proof", "actual_destabilizing_subsheaf_constructed",
        "stability_at_retained_polarization_established",
        "original_sections_or_cloud_inputs_changed",
        "finite_cloud_should_stop_because_of_this_sufficient_test",
        "physical_kahler_class_selected",
        "observations_used", "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
        "common_stabilized_vacuum_available",
    ):
        assert record[flag] is False


def test_all_nine_slopes_have_independent_cover_and_quotient_normalizations():
    record = module.read_certificate(expected_digest=CERTIFICATE)
    expected = (1296, -3600, -2088, 648, -4248, -432, 1080, 1728, -3816)
    for row, cover in zip(record["rows"], expected, strict=True):
        assert Fraction(row["cover_line_slope_exact"]) == cover
        assert Fraction(row["quotient_line_slope_exact"]) == Fraction(cover, 9)
        assert _line_slope(row["line_class"], (14, 16, 1)) == cover
    assert sum(not row["strictly_negative_at_retained_twist"] for row in record["rows"]) == 4
    # A determinant-line value is not the slope of its rank-two constituent.
    assert Fraction(record["rows"][5]["cover_line_slope_exact"]) / 2 == -216


@pytest.mark.parametrize("y, admitted", (
    (Fraction(1), False), (Fraction(17, 5), False), (Fraction(4), True),
    (Fraction(50), True), (Fraction(51), False), (Fraction(52), False),
    (Fraction(17, 5) + Fraction(1, 10**400), True),
    (Fraction(51) - Fraction(1, 10**400), True),
))
def test_strict_restricted_interval_is_exact_even_near_endpoints(y, admitted):
    lower, upper, rows = module.restricted_sufficient_interval(14, 16)
    assert lower == Rational(17, 5)
    assert upper == Rational(51)
    exact_y = Rational(y.numerator, y.denominator)
    assert (lower < exact_y < upper) is admitted
    assert all(constant + linear * exact_y < 0 for _, constant, linear in rows) is admitted
    assert all(_line_slope(line, (14, 16, y)) < 0 for line, *_ in STABILITY_ROWS) is admitted


@pytest.mark.parametrize("scale", (Fraction(1, 9), Fraction(2), Fraction(9),
                                    Fraction(1, 10**400)))
def test_positive_rescaling_cannot_repair_the_missing_chamber_hypothesis(scale):
    scaled = tuple(Rational(scale.numerator * coordinate, scale.denominator)
                   for coordinate in (14, 16, 1))
    for line, *_ in STABILITY_ROWS:
        original = _line_slope(line, (14, 16, 1))
        result = module.ambient_cover_triple(line, scaled, scaled)
        expected = original * scale * scale
        assert result == Rational(expected.numerator, expected.denominator)
        assert (result < 0) == (original < 0)


@pytest.mark.parametrize("coordinates", ((0, 16), (-1, 16), (14, 0), (14, -1),
                                            (14.0, 16), (14, True)))
def test_invalid_slice_coordinates_are_not_coerced_to_a_physical_choice(coordinates):
    with pytest.raises((TypeError, ValueError)):
        module.restricted_sufficient_interval(*coordinates)


@pytest.mark.parametrize("key", (
    "scope_failure_is_a_bundle_instability_proof", "stability_at_retained_polarization_established",
    "original_sections_or_cloud_inputs_changed", "physical_kahler_class_selected",
    "finite_cloud_should_stop_because_of_this_sufficient_test",
    "ricci_flat_or_hym_metric_available",
    "physical_yukawas_available", "common_stabilized_vacuum_available",
))
def test_rehashed_scope_packet_cannot_promote_physics(key, tmp_path):
    record = deepcopy(json.loads(module.OUTPUT.read_bytes()))
    record.pop("artifact_digest")
    record[key] = True
    digest = module._digest(record)
    record["artifact_digest"] = digest
    path = tmp_path / "attacked-scope.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="scope or independent arithmetic"):
        module.read_certificate(expected_digest=digest, path=path)


def test_scope_reader_keeps_retained_request_receipts_unchanged():
    paths = tuple(module.DIRECTORY / name for name in (
        "full_trial_cloud_request.json", "full_trial_cloud_inputs.json",
        "expanded_trial_cloud_request.json", "expanded_trial_cloud_inputs.json",
    ))
    before = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)
    module.read_certificate(expected_digest=CERTIFICATE)
    assert before == tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in paths)


def test_metric_graph_separates_scope_proof_from_open_stability_hypothesis():
    from research.experiments.scientific_genesis import audit

    nodes = audit._nodes()
    claims = {node["id"]: node for node in nodes}
    assert claims["metric_polarization_scope"]["status"] == "PROVED"
    assert claims["retained_polarization_stability"]["status"] == "BLOCKED"
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert claims["physical_yukawas"]["status"] == "BLOCKED"
    edges = audit._edges()
    endpoints = {(edge["source"], edge["target"]) for edge in edges}
    assert ("metric_polarization_scope", "retained_polarization_stability") in endpoints
    assert ("retained_polarization_stability", "visible_metrics") in endpoints
    task = next(task for task in audit._scheduler()
                if task["task"] == "alternate_metric_convergence")
    assert "does not prove instability" in task["rationale"]
    assert "compatible background/line-untwisting algorithm" in task["rationale"]
    payload = {"claims": nodes, "dependencies": edges, "fitted_inputs": []}
    payload["artifact_digest"] = audit._canonical_digest(payload)
    audit.validate_state(payload)
