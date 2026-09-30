"""Independently check the first alternate metric-twist cohomology premise.

Owns:
    Combinatorial ambient cohomology counts, exact sequence dimensions,
    descent character, and fail-closed scope of the archived H1 result.

Depends on:
    The generated research certificate, frozen Schoen deck action, and pytest.

Must not:
    Treat section dimensions as global generation, reuse the reference
    carrier's metric ledger as an input, or claim numerical metrics.

Phase 0:
    Independent exact regression for a research-only metric prerequisite.
"""

import hashlib
import json
from math import comb
from pathlib import Path

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.schoen_sparse_actions import (
    _compose_images,
    schoen_sparse_deck_actions,
)
from research.experiments.computable_carrier.schoen_sparse_outer import sparse_line_bundle

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "data/generated/scientific_genesis/alternate_metric_subbundle_vanishing.json"


def _p2(degree: int) -> dict[int, int]:
    if degree >= 0:
        return {0: comb(degree + 2, 2)}
    if degree <= -3:
        return {2: comb(-degree - 1, 2)}
    return {}


def _p1(degree: int) -> dict[int, int]:
    if degree >= 0:
        return {0: degree + 1}
    if degree <= -2:
        return {1: -degree - 1}
    return {}


def _ambient(degrees: tuple[int, int, int]) -> list[int]:
    result = [0] * 6
    for x_degree, x_dimension in _p2(degrees[0]).items():
        for u_degree, u_dimension in _p2(degrees[1]).items():
            for p_degree, p_dimension in _p1(degrees[2]).items():
                result[x_degree + u_degree + p_degree] += (
                    x_dimension * u_dimension * p_dimension
                )
    return result


def test_subbundle_vanishing_uses_actual_exact_line_objects() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    assert record["schema"] == "alternate-metric-subbundle-vanishing-v1"
    assert record["twist_cover_degree"] == [5, 7, 1]
    assert record["equation_degrees_x_u_base"] == [[3, 0, 1], [0, 3, 1]]
    assert record["deck_coordinate_commutators"] == [str(OMEGA**2), str(OMEGA**2), "1"]
    assert record["twist_descends_by_commuting_lifts"] is True
    assert [item["role"] for item in record["line_objects"]] == [
        "A", "F0", "F0", "F0", "F1", "F1",
    ]
    assert [item["source_degree"] for item in record["line_objects"]] == [
        [-1, 1, -1], [-3, 1, 1], [-3, 1, 1], [-3, 1, 1],
        [-4, 1, 1], [-4, 1, 1],
    ]
    for item in record["line_objects"]:
        twisted = tuple(item["twisted_degree"])
        assert twisted == tuple(
            source + shift for source, shift in zip(
                item["source_degree"], (5, 7, 1), strict=True,
            )
        )
        for subset, subtraction in (
            ("k0", (0, 0, 0)), ("k1_x", (3, 0, 1)),
            ("k1_u", (0, 3, 1)), ("k2", (3, 3, 2)),
        ):
            degrees = tuple(a - b for a, b in zip(twisted, subtraction, strict=True))
            piece = item["ambient_koszul_profile"][subset]
            assert piece["degree"] == list(degrees)
            assert piece["ambient_h0_to_h5"] == _ambient(degrees)
        assert item["cover_h1_to_h3"] == [0, 0, 0]

    first, second, third = (record["line_objects"][index] for index in (0, 1, 4))
    assert first["ambient_koszul_profile"]["k0"]["ambient_h0_to_h5"][0] == 675
    assert first["ambient_koszul_profile"]["k2"]["ambient_h0_to_h5"][1] == 63
    assert first["cover_h0"] == 675 - 63 == 612
    assert record["subline_koszul_higher_transgression_rank"] == 63
    assert record["ambient_first_page_alone_incomplete_for_subline"] is True
    assert second["cover_h0"] == 810 - 252 == 558
    assert third["cover_h0"] == 405 - 126 == 279
    assert record["cover_h0_first_constituent"] == 612 + 3 * 558 - 2 * 279 == 1728
    assert record["cover_h1_to_h3_first_constituent"] == [0, 0, 0]
    assert record["quotient_h0_first_constituent"] == 1728 // 9 == 192
    assert record["quotient_h1_first_constituent"] == 0
    assert record["cover_global_generation_first_constituent"] is True
    assert record["quotient_global_generation_first_constituent_certified"] is False
    assert record["individual_f0_ambient_lifts_commute"] is False
    assert [item["ambient_line_deck_commutator"] for item in record["line_objects"]] == [
        "1", *(str(OMEGA**2) for _ in range(3)), "1", "1",
    ]
    assert [item["ambient_line_lift_commutes"] for item in record["line_objects"]] == [
        True, False, False, False, True, True,
    ]
    assert all(
        item["ambient_nonnegative_and_cover_generated"]
        for item in record["line_objects"][:4]
    )


def test_first_page_sparse_koszul_rank_is_not_final_subline_cohomology() -> None:
    """The missing higher transgression must not be silently set to zero."""

    first_page = sparse_line_bundle(4, 8, 0)
    assert first_page.space(-1).dimension == 63
    assert first_page.space(0).dimension == 675
    assert first_page.differential(-1).rank() == 0
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert record["line_objects"][0]["cover_h0"] == 612
    assert record["subline_koszul_higher_transgression_rank"] == 63


def test_twist_character_and_physical_scope_are_separate() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    first, second = schoen_sparse_deck_actions()
    central_factors = []
    for factor in ("x_images", "u_images", "p_images"):
        pt = _compose_images(getattr(first, factor), getattr(second, factor))
        tp = _compose_images(getattr(second, factor), getattr(first, factor))
        ratios = {a[0] / b[0] for a, b in zip(pt, tp, strict=True)}
        assert len(ratios) == 1
        central_factors.append(ratios.pop())
    assert central_factors == [OMEGA**2, OMEGA**2, Eisenstein(1)]
    assert central_factors[0] ** 5 * central_factors[1] ** 7 == Eisenstein(1)
    for item in record["line_objects"]:
        degree = item["twisted_degree"]
        commutator = (
            central_factors[0] ** degree[0]
            * central_factors[1] ** degree[1]
            * central_factors[2] ** degree[2]
        )
        assert item["ambient_line_deck_commutator"] == str(commutator)
        assert item["ambient_line_lift_commutes"] is (commutator == Eisenstein(1))
    assert record["result_independent_of_outer_extension_parameter"] is True
    assert all(record[key] is False for key in (
        "global_generation_of_constituents_certified",
        "rank_four_global_generation_certified", "numerical_metrics_available",
        "physical_yukawas_available", "observational_inputs_used",
    ))
