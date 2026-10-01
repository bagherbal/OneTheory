"""Attack the independent raw operator certificate for metric-section lifting.

Owns:
    Complete support/parity replay, signed-incidence and homotopy mutation
    attacks, exact actual filtration premises, and fail-closed scope checks.

Depends on:
    The research operator verifier, observed raw Čech implementation, and
    content-addressed universal metric-lift prerequisites.

Must not:
    Infer complete outer composition certification, metrics, a selected
    extension point, or physical Yukawas from a raw homotopy identity.

Phase 0:
    Independent operator regression tests; numerical physics remains open.
"""

import hashlib
import json

import pytest

from research.experiments.scientific_genesis import (
    alternate_metric_lift_operator_certificate as certificate,
)


def test_complete_support_category_reproduces_the_independent_certificate() -> None:
    payload = json.loads(certificate.OUTPUT.read_text())
    digest = payload.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    assert payload["raw_contraction"] == certificate.support_certificate()
    assert payload["carrier_premises"] == certificate.carrier_premises()
    assert payload["raw_contraction"]["verified_basis_column_count"] == 10816
    assert payload["raw_contraction"]["support_pattern_count"] == 256
    assert payload["closed_degree_one_residual_primitive_rule_certified"] is True
    assert payload["outer_lift_artifact_digest"] == certificate._verified_payload(
        certificate.lifts.OUTPUT,
    )[0]
    assert payload["outer_composition"] == certificate.composition_certificate()
    assert payload["repaired_averaging"] == certificate.averaging_premises()
    assert all(payload[key] is True for key in (
        "all_outer_section_products_independently_certified",
        "full_universal_lift_formula_certified", "rank_four_section_basis_available",
    ))
    assert all(payload[key] is False for key in (
        "complete_expanded_coefficient_replay",
        "numerical_metrics_available", "physical_yukawas_available",
        "extension_point_selected", "observational_inputs_used",
    ))


@pytest.mark.parametrize("parity", (0, 1))
def test_contraction_identity_detects_a_reversed_homotopy_sign(monkeypatch, parity) -> None:
    """The independent incidence path cannot agree with the same sign defect."""

    actual = certificate._homotopy
    monkeypatch.setattr(certificate, "_homotopy", lambda c: actual(c).scale(-1))
    with pytest.raises(ValueError, match="raw contraction fails d h"):
        certificate.verify_support_block(((), (), ()), parity)


@pytest.mark.parametrize("parity", (0, 1))
def test_incidence_comparison_detects_a_reversed_raw_differential(monkeypatch, parity) -> None:
    actual = certificate._cech_differential
    monkeypatch.setattr(certificate, "_cech_differential", lambda c: actual(c).scale(-1))
    with pytest.raises(ValueError, match="independent face incidence"):
        certificate.verify_support_block(((), (), ()), parity)


def test_actual_mixed_wedge_filtration_and_obstruction_scope() -> None:
    premises = certificate.carrier_premises()
    assert premises["ambient_component_count"] == 24
    assert premises["Q_vanishes_on_total_degree_one"] is True
    assert premises["minimum_checked_arrow_gain"] == 1
    assert premises["closed_residual_iteration_bound"] == 5
    assert premises["filtration_range"] == [0, 4]


@pytest.mark.parametrize("parameter", (0, 1))
def test_module_certificate_detects_a_wrong_source_differential_product(monkeypatch, parameter):
    """A sign error on P1 overlaps cannot be concealed by rescaling E."""

    actual = certificate._module_product

    def broken(extension, section):
        result = actual(extension, section)
        return result.scale(-1) if any(b.cech_degree == 1 for b, _ in section.terms) else result

    monkeypatch.setattr(certificate, "_module_product", broken)
    with pytest.raises(ValueError, match="constructor cup differs|Leibniz defect"):
        certificate.verify_module_column(0, 0, parameter)
