"""Independently check the conditional hidden chamber and its exclusions.

Owns:
    Cover-ring integration, Fraction-based affine inequalities, open-box
    verification, parent pinning, and attacks on rehashed scientific claims.

Depends on:
    The thin research certificate, actual parent metadata, and exact geometry.

Must not:
    Treat necessary positivity as a hidden construction or select a vacuum.

Phase 0:
    Conditional research regressions, not physical hidden-bundle evidence.
"""

import json
from fractions import Fraction
from itertools import product
from pathlib import Path

import pytest

from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.scientific_genesis import alternate_necessary_hidden_chamber as wall
from research.experiments.scientific_genesis import audit


def test_literal_artifact_matches_fresh_conditional_derivation() -> None:
    """A complete artifact remains no more than its scoped derivation."""

    record = wall.read_hidden_chamber()
    assert record == wall.necessary_hidden_chamber()
    assert record["divisor_basis"] == ["tau1", "tau2", "phi"]
    assert record["required_rational_hidden_c2"] == ["4/3", "7/3", "-4"]
    assert record["source"]["equations"] == [39, 40, 41, 42, 43, 44]
    assert record["covering_degree"] == 9


def test_necessary_wall_has_direct_dependencies_without_physical_promotion() -> None:
    """The declared graph records a constraint, not an invented hidden object."""

    claims = {claim["id"]: claim for claim in audit._nodes()}
    assert claims["alternate_necessary_hidden_chamber"]["status"] == "DERIVED"
    assert claims["hidden_bundle"]["status"] == "BLOCKED"
    assert claims["controlled_vacuum"]["status"] == "BLOCKED"
    edges = {(edge["source"], edge["target"]) for edge in audit._edges()}
    assert {
        ("alternate_constituent_outer_universal_cone", "alternate_necessary_hidden_chamber"),
        ("alternate_constituent_outer_stability_locus", "alternate_necessary_hidden_chamber"),
        ("alternate_necessary_hidden_chamber", "hidden_bundle"),
        ("alternate_necessary_hidden_chamber", "controlled_vacuum"),
    } <= edges


def test_independent_published_cover_ring_recovers_both_chern_classes() -> None:
    """Integrate cover products rather than reuse the producer's c2 subtraction."""

    record = wall.read_hidden_chamber()
    tensor = schoen_geometry().cover_intersections
    # Published hidden 11*tau1^2+8*tau2^2-4*tau1*tau2,
    # visible tau1^2+4*tau2^2+4*tau1*tau2, tangent 12*(tau1^2+tau2^2).
    polynomials = ((11, 8, -4), (1, 4, 4), (12, 12, 0))
    keys = ("required_rational_hidden_c2", "c2_visible", "c2_tangent")
    for (a, b, c), key in zip(polynomials, keys, strict=True):
        cover_coefficients = tuple(
            a * Fraction(tensor.coefficient(0, 0, k))
            + b * Fraction(tensor.coefficient(1, 1, k))
            + c * Fraction(tensor.coefficient(0, 1, k))
            for k in range(3)
        )
        assert tuple(value / 9 for value in cover_coefficients) == tuple(
            Fraction(value) for value in record[key]
        )
    assert tuple(3 * Fraction(value) for value in record[keys[0]]) == (4, 7, -12)


def test_entire_common_open_box_not_an_isolated_polarization() -> None:
    """Affine extrema and all eight closed-box corners verify the strict bound."""

    record = wall.read_hidden_chamber()
    box = record["common_open_box"]
    center = tuple(Fraction(value) for value in box["center"])
    radius = Fraction(box["coordinate_radius"])
    target = tuple(Fraction(value) for value in record["required_rational_hidden_c2"])
    slopes = json.loads(wall.STABILITY.read_text())["kahler_chamber"]["inequalities"]
    corners = tuple(
        tuple(x + sign * radius for x, sign in zip(center, signs, strict=True))
        for signs in product((-1, 1), repeat=3)
    )
    pairings = [sum(c * x for c, x in zip(target, corner, strict=True)) for corner in corners]
    assert min(pairings) == Fraction(1609, 96)
    assert min(pairings) == Fraction(box["hidden_quotient_pairing_lower_bound"]) > 0
    assert Fraction(box["hidden_quotient_pairing_at_center"]) == 17
    for row in slopes:
        a, b, c, d, e = map(Fraction, row["coefficients"])
        x, z, y = center
        value = a*x*x + b*x*z + c*x*y + d*z*z + e*z*y
        gradient = (2*a*x+b*z+c*y, b*x+2*d*z+e*y, c*x+e*z)
        bound = value + radius*sum(map(abs, gradient)) + radius**2*sum(map(abs, (a,b,c,d,e)))
        assert bound < 0
        for x, z, y in corners:
            assert x > 0 and z > 0 and y > 0
            assert a*x*x + b*x*z + c*x*y + d*z*z + e*z*y <= bound
    assert box["all_nonzero_outer_parameters"] is True
    assert box["physical_polarization_selected"] is False


def test_independent_affine_bounds_exclude_a_whole_visible_stable_family() -> None:
    """All nine affine inequalities, not example points, determine the interval."""

    record = wall.read_hidden_chamber()
    rows = json.loads(wall.STABILITY.read_text())["kahler_chamber"]["inequalities"]
    affine = []
    for row in rows:
        a, b, c, d, e = map(Fraction, row["coefficients"])
        affine.append((9*a+12*b+16*d, 3*c+4*e))
    assert affine == [(114,-180),(-174,36),(-39,-126),(51,-234),(-237,-18),
                      (-42,-36),(93,-198),(156,-144),(-195,18)]
    lower = max([Fraction(0), *(-a/b for a,b in affine if b < 0)])
    upper = min(-a/b for a,b in affine if b > 0)
    assert (lower, upper) == (Fraction(13,12), Fraction(29,6))
    assert all(a+b*lower <= 0 and a+b*upper <= 0 for a,b in affine)
    slice_record = record["symbolic_slice"]
    assert slice_record["visible_affine_coefficients_constant_linear"] == [
        [str(a), str(b)] for a,b in affine]
    assert slice_record["visible_sufficient_interval_open"] == [str(lower), str(upper)]
    hidden_a = Fraction(4,3)*3 + Fraction(7,3)*4
    hidden_b = Fraction(-4)
    face = -hidden_a/hidden_b
    assert face == Fraction(10,3)
    assert lower < face < upper
    assert hidden_a + hidden_b*face == 0  # Saturation cannot support nonzero real c2.
    assert slice_record["necessary_common_interval_open"] == [str(lower), str(face)]
    assert slice_record["excluded_visible_stable_interval"] == {
        "lower_inclusive": str(face), "upper_exclusive": str(upper)}


@pytest.mark.parametrize("parent", ("CONE", "STABILITY"))
def test_rehashed_parent_changes_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, parent: str,
) -> None:
    """An attacker cannot change actual sources while keeping their self hash valid."""

    record = json.loads(getattr(wall, parent).read_text())
    record.pop("artifact_digest")
    record["arbitrary_extension_point_selected"] = True
    record["artifact_digest"] = _canonical_digest(record)
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(record))
    monkeypatch.setattr(wall, parent, path)
    with pytest.raises(ValueError, match="trusted parents"):
        wall.necessary_hidden_chamber()


@pytest.mark.parametrize("field", (
    "hidden_bundle_constructed", "hidden_stability_proved",
    "integral_or_torsion_anomaly_cancelled", "full_common_stability_chamber_computed",
    "numerical_metrics_available", "vacuum_selected", "extension_point_selected",
    "physical_yukawas_available", "observational_inputs_used",
))
def test_rehashed_output_cannot_invent_physical_inputs(tmp_path: Path, field: str) -> None:
    """Necessary positivity must never silently become physical closure."""

    record = wall.read_hidden_chamber()
    assert record[field] is False
    record[field] = True
    record["artifact_digest"] = _canonical_digest(record)
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="exact derivation"):
        wall.read_hidden_chamber(path)


@pytest.mark.parametrize("field", (
    "hidden_bundle_constructed", "hidden_stability_proved",
    "integral_or_torsion_anomaly_cancelled", "full_common_stability_chamber_computed",
    "numerical_metrics_available", "vacuum_selected", "extension_point_selected",
    "physical_yukawas_available", "observational_inputs_used",
))
def test_governance_rejects_rehashed_hidden_scope(
    monkeypatch: pytest.MonkeyPatch, field: str,
) -> None:
    """The governing audit must fail before admitting inflated physical claims."""

    original = json.loads

    def inflated_loads(text: str) -> object:
        record = original(text)
        if isinstance(record, dict) and record.get("schema") == (
            "alternate-necessary-hidden-chamber-v1"
        ):
            record.pop("artifact_digest")
            record[field] = True
            record["artifact_digest"] = _canonical_digest(record)
        return record

    monkeypatch.setattr(audit.json, "loads", inflated_loads)
    with pytest.raises(ValueError, match="exact derivation"):
        audit.build_state()


@pytest.mark.parametrize("field,value", (
    ("covering_degree", 1), ("quotient_pairing_coefficients", ["4", "7", "-12"]),
    ("necessary_wall", "4*x1+7*x2-12*y >= 0"),
))
def test_rehashed_output_cannot_change_normalization_or_wall(
    tmp_path: Path, field: str, value: object,
) -> None:
    """Correct signs without the explicit integration factor are not the certificate."""

    record = wall.read_hidden_chamber()
    record[field] = value
    record["artifact_digest"] = _canonical_digest(record)
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="exact derivation"):
        wall.read_hidden_chamber(path)
