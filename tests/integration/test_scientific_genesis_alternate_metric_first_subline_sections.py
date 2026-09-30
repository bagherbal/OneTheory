"""Verify the first actual subline section basis by independent modular rank.

Owns:
    Source-derived eliminant, monomial-character counts, and an independent
    finite-field check of the chosen exact quotient complement.

Depends on:
    The frozen Schoen cubics, published coordinate action, generated basis,
    and pytest.

Must not:
    Identify these subline sections with a complete carrier basis or
    interpret finite-field specialization as a physical approximation.

Phase 0:
    Independent algebraic regression for one research section component.
"""

import hashlib
import json
from pathlib import Path

from onetheory.math.numbers import Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.computable_carrier.schoen_sparse_actions import (
    _monomial_action,
    schoen_sparse_deck_actions,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "data/generated/scientific_genesis/alternate_metric_first_subline_sections.json"
GENERATION = ROOT / "data/generated/scientific_genesis/alternate_metric_quotient_generation.json"
CONE = ROOT / "data/generated/scientific_genesis/alternate_constituent_outer_universal_cone.json"
PRIME = 7
OMEGA_MOD_PRIME = 2


def _mod(value: Eisenstein) -> int:
    assert value.a.denominator == value.b.denominator == 1
    return (value.a.numerator + OMEGA_MOD_PRIME * value.b.numerator) % PRIME


def _monomials(x_degree: int, u_degree: int):
    return (
        (x0, x1, x_degree - x0 - x1, u0, u1, u_degree - u0 - u1)
        for x0 in range(x_degree + 1)
        for x1 in range(x_degree - x0 + 1)
        for u0 in range(u_degree + 1)
        for u1 in range(u_degree - u0 + 1)
    )


def _p_image(monomial, action):
    x_scalar, x_image = _monomial_action(monomial[:3], action.x_images)
    u_scalar, u_image = _monomial_action(monomial[3:], action.u_images)
    return _mod(x_scalar * u_scalar), x_image + u_image


def _canonical_t_fixed_orbits(x_degree: int, u_degree: int, action):
    seen = set()
    result = []
    for monomial in _monomials(x_degree, u_degree):
        if monomial in seen:
            continue
        orbit = [monomial]
        current = monomial
        for _ in range(2):
            _scalar, current = _p_image(current, action)
            orbit.append(current)
        assert len(set(orbit)) == 3
        seen.update(orbit)
        canonical = min(orbit)
        _x0, x1, x2, _u0, u1, u2 = canonical
        if (x1 + 2 * x2 + 2 * u1 + u2) % 3 == 1:
            result.append(canonical)
    return tuple(result)


def _eliminant_mod_prime():
    cox = schoen_geometry().cover.cox
    result = {}
    for multiplier, cubic in ((2, cox.cubic_f), (-1, cox.cubic_g)):
        for x_monomial, x_value in cubic.terms:
            for u_monomial, u_value in cubic.terms:
                monomial = x_monomial + u_monomial
                result[monomial] = (
                    result.get(monomial, 0)
                    + multiplier * _mod(x_value) * _mod(u_value)
                ) % PRIME
    return {monomial: value for monomial, value in result.items() if value}


def _rank_mod_prime(columns: list[dict[int, int]]) -> int:
    pivots: dict[int, dict[int, int]] = {}
    for raw in columns:
        column = dict(raw)
        while column:
            pivot = min(column)
            existing = pivots.get(pivot)
            if existing is None:
                inverse = pow(column[pivot], -1, PRIME)
                pivots[pivot] = {
                    row: value * inverse % PRIME for row, value in column.items()
                }
                break
            factor = column[pivot]
            for row, value in existing.items():
                updated = (column.get(row, 0) - factor * value) % PRIME
                if updated:
                    column[row] = updated
                else:
                    column.pop(row, None)
    return len(pivots)


def test_actual_subline_basis_is_a_full_invariant_quotient_complement() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    generation = json.loads(GENERATION.read_text(encoding="utf-8"))
    assert record["prerequisite_artifact_digests"]["generation"] == generation["artifact_digest"]
    cone = json.loads(CONE.read_text(encoding="utf-8"))
    assert record["prerequisite_artifact_digests"]["alternate_cone"] == cone["artifact_digest"]
    assert cone["common_flat_character_twist"] == [1, 2]
    assert record["schema"] == "alternate-metric-first-subline-sections-v1"
    assert record["twisted_subline_cover_degree"] == [13, 17, 0]
    assert record["metric_twist_linearization"] == "natural commuting ambient P/T coordinate lifts"
    assert record["actual_subline_frame_p_t"] == ["1", "-1-omega"]
    assert OMEGA_MOD_PRIME**2 + OMEGA_MOD_PRIME + 1 == PRIME
    p_action, t_action = schoen_sparse_deck_actions()
    target = _canonical_t_fixed_orbits(13, 17, p_action)
    source = _canonical_t_fixed_orbits(10, 14, p_action)
    assert len(target) == record["ambient_invariant_orbit_count"] == 1995
    assert len(source) == record["ideal_invariant_orbit_count"] == 880
    for monomial in target:
        x_scalar, x_image = _monomial_action(monomial[:3], t_action.x_images)
        u_scalar, u_image = _monomial_action(monomial[3:], t_action.u_images)
        assert x_image + u_image == monomial
        assert _mod(x_scalar * u_scalar) == OMEGA_MOD_PRIME
    basis = tuple(tuple(monomial) for monomial in record["quotient_basis_monomials_x_u"])
    assert len(basis) == record["quotient_subline_section_count"] == 1115
    assert len(set(basis)) == len(basis)
    assert set(basis) <= set(target)
    basis_set = set(basis)
    pivot_labels = tuple(monomial for monomial in target if monomial not in basis_set)
    assert len(pivot_labels) == 880
    pivot_index = {monomial: index for index, monomial in enumerate(pivot_labels)}

    eliminant = _eliminant_mod_prime()
    cox = schoen_geometry().cover.cox
    exact_eliminant: dict[tuple[int, ...], Eisenstein] = {}
    for multiplier, cubic in ((2, cox.cubic_f), (-1, cox.cubic_g)):
        for x_monomial, x_value in cubic.terms:
            for u_monomial, u_value in cubic.terms:
                monomial = x_monomial + u_monomial
                exact_eliminant[monomial] = exact_eliminant.get(
                    monomial, Eisenstein(0)
                ) + multiplier * x_value * u_value
    assert record["projected_eliminant_terms"] == [
        {"monomial": list(monomial), "coefficient": str(value)}
        for monomial, value in sorted(exact_eliminant.items()) if not value.is_zero()
    ]
    assert eliminant == {
        monomial: residue
        for monomial, value in exact_eliminant.items()
        if (residue := _mod(value))
    }
    columns = []
    for canonical in source:
        current = canonical
        coefficient = 1
        column: dict[int, int] = {}
        for _ in range(3):
            for relation, value in eliminant.items():
                target_monomial = tuple(a + b for a, b in zip(current, relation, strict=True))
                index = pivot_index.get(target_monomial)
                if index is not None:
                    column[index] = (column.get(index, 0) + coefficient * value) % PRIME
            factor, current = _p_image(current, p_action)
            coefficient = coefficient * factor % PRIME
        assert current == canonical and coefficient == 1
        columns.append({index: value for index, value in column.items() if value})
    assert _rank_mod_prime(columns) == 880
    assert record["ideal_inclusion_rank"] == 880
    assert record["projected_eliminant_deck_invariant"] is True
    assert all(record[key] is False for key in (
        "full_constituent_section_basis_available",
        "rank_four_section_basis_available", "numerical_metrics_available",
        "observational_inputs_used",
    ))
