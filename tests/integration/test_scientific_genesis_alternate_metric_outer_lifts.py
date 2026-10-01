"""Verify the finite universal metric-section lifting formula.

Owns:
    Independent ambient degree counts, filtration checks, direct suffix-cell
    outer composition, actual parameter-coefficient replay, and scope tests.

Depends on:
    Certified source complexes, exact scalar arithmetic, both constituent
    section streams, and the research universal section constructor.

Must not:
    Treat probe agreement as full basis replay or infer numerical metrics,
    a chosen extension point, a vacuum, or physical Yukawa predictions.

Phase 0:
    Exact structural and coefficient tests for a research lifting formula.
"""

import hashlib
import json
from functools import cache
from math import comb

import pytest

from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    OuterCechBasis,
    SparseOuterCechCochain,
)
from research.experiments.scientific_genesis import alternate_metric_outer_lifts as lifts


def _projective_cohomology(dimension, degree):
    if degree >= 0:
        return 0, comb(degree + dimension, dimension)
    if degree <= -dimension - 1:
        return dimension, comb(-degree - 1, dimension)
    return 0, 0


def test_every_ambient_component_has_no_positive_reduced_degree() -> None:
    """Recompute each Künneth count without the producer's line-bundle engine."""

    record = lifts.structural_certificate()
    totals = {}
    for profile in record["component_profiles"]:
        factors = [_projective_cohomology(n, d)
                   for n, d in zip((2, 2, 1), profile["ambient_degree"], strict=True)]
        degree = sum(q for q, _h in factors)
        count = factors[0][1] * factors[1][1] * factors[2][1]
        expected = [0] * 6
        expected[degree] = count
        assert profile["ambient_h0_to_h5"] == expected
        if count:
            total = degree + profile["structural_degree"]
            totals[total] = totals.get(total, 0) + count
    assert record["raw_reduced_dimensions"] == [[d, h] for d, h in sorted(totals.items())]
    assert totals == {-3: 8640, -2: 72504, -1: 177966, 0: 137997}
    assert record["raw_reduced_degree_one_dimension"] == 0
    assert all(d <= 0 for d in totals)


def test_all_mixed_arrows_raise_the_combined_filtration_even_with_wedges() -> None:
    """Object gains must also dominate a mixed arrow's Koszul-degree loss."""

    target = lifts.first._context()[0]
    weights = (2, 1, 1, 1, 0, 0)
    for arrow in target.left.resolution_arrows:
        assert weights[arrow.target] > weights[arrow.source]
    for term in target.left.extension_terms:
        assert weights[term.target] - weights[term.source] - term.koszul_degree > 0
    for component in target.components.values():
        weight = weights[component.left_index] + 2 + {
            "k0": 0, "k1_x": -1, "k1_u": -1, "k2": -2,
        }[component.koszul_summand]
        assert 0 <= weight <= 4
    assert lifts.structural_certificate()["h_delta_nilpotence_bound"] == 5


@cache
def _probe(index):
    return lifts.universal_section(2655 + index)


def _direct_composition(extension, section):
    """Use suffix vertices directly; no common cup or cell-product helper."""

    by_suffix = {}
    for basis, coefficient in section.terms:
        assert basis.component.object_degree == 0
        assert basis.component.koszul_summand == "k0" and basis.cech_degree == 0
        key = basis.component.left_index, tuple(s[0] for s in basis.cell)
        by_suffix.setdefault(key, []).append((basis, coefficient))
    targets = lifts.first._context()[0].components
    values = {}
    for arrow, scalar in extension.terms:
        key = arrow.component.right_index, tuple(s[-1] for s in arrow.cell)
        for basis, coefficient in by_suffix.get(key, ()):
            image = OuterCechBasis(
                targets[arrow.component.left_index, 0, arrow.component.koszul_summand],
                tuple(a + b for a, b in zip(arrow.x_monomial, basis.x_monomial, strict=True)),
                tuple(a + b for a, b in zip(arrow.u_monomial, basis.u_monomial, strict=True)),
                tuple(a + b for a, b in zip(arrow.p_monomial, basis.p_monomial, strict=True)),
                arrow.cell,
            )
            values[image] = values.get(image, Eisenstein(0)) + scalar * coefficient
    return SparseOuterCechCochain(tuple(values.items()))


@pytest.mark.parametrize("index", (0, 1135))
def test_actual_universal_coefficients_close_against_independent_composition(index) -> None:
    section = _probe(index)
    target = lifts.first._context()[0]
    for parameter, extension in enumerate(lifts._inputs()[2]):
        residual = _direct_composition(extension, section.second_constant)
        coefficient = section.first_coefficients[parameter]
        assert not residual.is_zero() and not coefficient.is_zero()
        assert target.differential(residual).is_zero()
        assert (target.differential(coefficient) + residual).is_zero()
        assert all(lifts.first._action(coefficient, g) == coefficient for g in (0, 1))
        assert section.homotopy_depths[parameter] <= 5
    assert section.first_constant.is_zero()


def test_probe_artifact_reproduces_without_claiming_full_replay_or_physics() -> None:
    payload = json.loads(lifts.OUTPUT.read_text())
    digest = payload.pop("artifact_digest")
    assert hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
    )).hexdigest() == digest
    assert payload["structural_certificate"] == lifts.structural_certificate()
    assert payload["prerequisite_artifact_digests"] == lifts._inputs()[0]
    for probe in payload["actual_coefficient_probes"]:
        section = _probe(probe["second_basis_index"])
        assert probe["coefficient_term_counts"] == [len(c.terms)
                                                   for c in section.first_coefficients]
        assert probe["coefficient_digests"] == [lifts._cochain_digest((c,))
                                               for c in section.first_coefficients]
        assert probe["homotopy_depths"] == list(section.homotopy_depths)
    assert payload["universal_section_constructor_available"] is True
    assert all(payload[key] is False for key in (
        "complete_independent_rank_four_basis_replay", "rank_four_section_basis_available",
        "numerical_metrics_available", "physical_yukawas_available",
        "extension_point_selected", "observational_inputs_used",
    ))


@pytest.mark.parametrize("index", (-1, 5345, True, 0.0, "0"))
def test_universal_basis_indices_are_explicit_and_bounded(index) -> None:
    with pytest.raises(ValueError, match="basis index"):
        lifts.universal_section(index)


def test_injected_first_sections_retain_the_actual_basis_and_no_outer_correction() -> None:
    section = lifts.universal_section(0)
    assert not section.first_constant.is_zero()
    assert lifts.first._context()[0].differential(section.first_constant).is_zero()
    assert section.second_constant.is_zero()
    assert all(c.is_zero() for c in section.first_coefficients)
    assert section.homotopy_depths == (0, 0)
