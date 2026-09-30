"""Independently check the alternate carrier's quotient-generation theorem.

Owns:
    Exact ambient support counts, source degree checks, deck commutators,
    and the fail-closed distinction between generation and metrics.

Depends on:
    The generated research certificate, frozen carrier, and pytest.

Must not:
    Treat the enlarged mathematical twist as a physical modulus or
    mistake generation for a numerical metric or physical Yukawa.

Phase 0:
    Independent mathematical regression for one carrier prerequisite.
"""

import hashlib
import json
from math import comb
from pathlib import Path

from onetheory.math.numbers import OMEGA, Eisenstein
from onetheory.models.heterotic_schoen.geometry import schoen_geometry
from research.experiments.scientific_genesis.distinct_constituent_ray_screen import (
    lift_joint_character_ray,
)
from research.experiments.scientific_genesis.mixed_constituent_schoen_arrows import (
    _constituent,
)
from research.experiments.scientific_genesis.published_constituent_deck_actions import (
    published_constituent_deck_actions,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "data/generated/scientific_genesis/alternate_metric_quotient_generation.json"
FIRST = ROOT / "data/generated/scientific_genesis/alternate_metric_subbundle_vanishing.json"


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


def _ambient(degree: tuple[int, int, int]) -> list[int]:
    result = [0] * 6
    for i, ni in _p2(degree[0]).items():
        for j, nj in _p2(degree[1]).items():
            for k, nk in _p1(degree[2]).items():
                result[i + j + k] += ni * nj * nk
    return result


def _h0(profile: dict[str, object], key: str) -> int:
    return profile[key]["ambient_h0_to_h5"][0]


def test_second_constituent_cover_generation_uses_actual_ray() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    digest = record.pop("artifact_digest")
    assert digest == hashlib.sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    assert record["schema"] == "alternate-metric-quotient-generation-v2"
    action = published_constituent_deck_actions()[1]
    ray = lift_joint_character_ray(action, Eisenstein(1), OMEGA)
    second = _constituent(ray, "I6-ray-0-1", 2, (1, -1, 0))
    assert [item.line_degree for item in second.objects] == [
        (1, -1, -1), *((1, -4, 1),) * 4, *((1, -5, 1),) * 3,
    ]
    assert record["right_serre_subline_base_degree"] == [6, 6, 0]
    assert record["right_hilbert_burch_source_base_degrees"] == [[6, 3, 2]] * 4
    profile = record["right_serre_subline_base_ambient_koszul_profile"]
    assert {name: item["ambient_h0_to_h5"] for name, item in profile.items()} == {
        "k0": [784, 0, 0, 0, 0, 0],
        "k1_x": [0, 0, 0, 0, 0, 0],
        "k1_u": [0, 0, 0, 0, 0, 0],
        "k2": [0, 100, 0, 0, 0, 0],
    }
    assert record["right_serre_subline_base_h0"] == 784 - 100 == 684
    for item in profile.values():
        assert item["ambient_h0_to_h5"] == _ambient(tuple(item["degree"]))
    assert record["right_constituent_cover_generated_at_base_twist"] is True


def test_large_twist_closes_invariant_evaluation_and_outer_h1() -> None:
    record = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    first = json.loads(FIRST.read_text(encoding="utf-8"))
    assert record["prerequisite_artifact_digests"]["first_constituent"] == first["artifact_digest"]
    assert record["base_twist_cover_degree"] == [5, 7, 1]
    assert record["orbit_separator_cover_degree"] == [9, 9, 0]
    assert record["generating_twist_cover_degree"] == [14, 16, 1]
    assert record["free_deck_orbit_size"] == 9
    assert record["projected_orbit_action_free"] is True
    assert record["projected_fiber_type"] == "empty, point, or the full projective line"
    assert record["ambient_multihomogeneous_separation_bound_per_p2_factor"] == 8
    geometry = schoen_geometry()
    assert geometry.quotient.acts_freely and geometry.quotient.order == 9
    assert geometry.cover.cox.equations == (
        "p1 = mu F(x) + nu G(x)", "p2 = 2 nu F(u) + mu G(u)",
    )
    assert (OMEGA**2) ** 9 * (OMEGA**2) ** 9 == Eisenstein(1)
    assert (OMEGA**2) ** 14 * (OMEGA**2) ** 16 == Eisenstein(1)
    assert record["orbit_separator_descends"] is True
    assert record["first_constituent_cover_generated_at_base_twist"] is True
    dimensions = []
    for source, item in zip(
        first["line_objects"], record["first_large_twist_line_profiles"], strict=True,
    ):
        assert item["name"] == source["name"]
        assert item["twisted_degree"] == [
            a + b for a, b in zip(source["source_degree"], (14, 16, 1), strict=True)
        ]
        for piece, subtraction in (
            ("k0", (0, 0, 0)), ("k1_x", (3, 0, 1)),
            ("k1_u", (0, 3, 1)), ("k2", (3, 3, 2)),
        ):
            expected_degree = tuple(
                a - b for a, b in zip(item["twisted_degree"], subtraction, strict=True)
            )
            profile = item["ambient_koszul_profile"][piece]
            assert profile["degree"] == list(expected_degree)
            assert profile["ambient_h0_to_h5"] == _ambient(expected_degree)
        profile = item["ambient_koszul_profile"]
        if item["role"] == "A":
            assert profile["k1_x"]["ambient_h0_to_h5"] == [0] * 6
            assert profile["k1_u"]["ambient_h0_to_h5"] == [0] * 6
            dimension = _h0(profile, "k0") - profile["k2"]["ambient_h0_to_h5"][1]
        else:
            assert all(value["ambient_h0_to_h5"][1:] == [0] * 5 for value in profile.values())
            dimension = (
                _h0(profile, "k0") - _h0(profile, "k1_x")
                - _h0(profile, "k1_u") + _h0(profile, "k2")
            )
        assert item["cover_h0"] == dimension
        assert item["cover_higher_cohomology_vanishes"] is True
        dimensions.append(dimension if item["role"] != "F1" else -dimension)
    assert sum(dimensions) == 23895
    second = _constituent(
        lift_joint_character_ray(
            published_constituent_deck_actions()[1], Eisenstein(1), OMEGA,
        ),
        "I6-ray-0-1", 2, (1, -1, 0),
    )
    right_dimensions = []
    for source, item in zip(
        second.objects, record["second_large_twist_line_profiles"], strict=True,
    ):
        assert item["twisted_degree"] == [
            a + b for a, b in zip(source.line_degree, (14, 16, 1), strict=True)
        ]
        profile = item["ambient_koszul_profile"]
        for piece in profile.values():
            assert piece["ambient_h0_to_h5"] == _ambient(tuple(piece["degree"]))
        if item["role"] == "A":
            assert profile["k1_x"]["ambient_h0_to_h5"] == [0] * 6
            assert profile["k1_u"]["ambient_h0_to_h5"] == [0] * 6
            dimension = _h0(profile, "k0") - profile["k2"]["ambient_h0_to_h5"][1]
        else:
            assert all(value["ambient_h0_to_h5"][1:] == [0] * 5 for value in profile.values())
            dimension = (
                _h0(profile, "k0") - _h0(profile, "k1_x")
                - _h0(profile, "k1_u") + _h0(profile, "k2")
            )
        assert item["cover_h0"] == dimension
        right_dimensions.append(dimension if item["role"] != "F1" else -dimension)
    assert sum(right_dimensions) == 24210
    assert record["cover_h0_constituents_at_generating_twist"] == [23895, 24210]
    assert record["quotient_h0_constituents_at_generating_twist"] == [2655, 2690]
    assert record["quotient_h0_rank_four_at_generating_twist"] == 5345
    assert record["first_constituent_h1_vanishes_at_generating_twist"] is True
    assert record["both_constituents_quotient_generated_at_generating_twist"] is True
    assert record["rank_four_quotient_generated_for_all_alternate_p1"] is True
    assert record["generation_at_base_twist_certified"] is False
    assert record["explicit_invariant_section_basis_constructed"] is False
    assert all(record[key] is False for key in (
        "numerical_metrics_available", "physical_yukawas_available", "observational_inputs_used",
    ))
