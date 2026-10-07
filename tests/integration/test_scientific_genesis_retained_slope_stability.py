"""Attack the actual retained-polarization stability refinement.

Owns:
    Independent matrix ranks, source-ordered degree bounds, proper-rank
    quantifiers, frozen-input preservation and evidence-mutation tests.

Depends on:
    The research refinement, ordinary Fraction arithmetic and pytest.

Must not:
    Treat finite examples as exhaustive subobjects, choose a vacuum, or
    promote slope stability into a computed HYM or matter metric.

Phase 0:
    Source-conditioned research theorem tests only.
"""

import hashlib
import json
from copy import deepcopy
from fractions import Fraction

import pytest

from research.experiments.scientific_genesis import retained_slope_stability as module

CERTIFICATE = "0017a8dc6c3a654ae6513d0cbc54a72c67c712c353162f9de32a8e3b1313cafd"


@pytest.fixture(scope="module")
def packet():
    return module.read_certificate(expected_digest=CERTIFICATE)


def _degree(line):
    """Independent linear functional from the explicit ambient Chow product."""

    return 2400 * line[0] + 2184 * line[1] + 4032 * line[2]


def test_actual_four_cover_line_Homs_vanish_with_independent_exact_ranks(packet):
    expected = {
        (0, (-1, -2, 2)): (43, 262, 252),
        (0, (-4, 1, 2)): (3, 28, 14),
        (1, (-2, -1, 2)): (93, 563, 566),
        (1, (1, -4, 2)): (3, 33, 14),
    }
    probes = packet["actual_cover_line_Hom_probes"]
    assert len(probes) == 4
    for probe in probes:
        key = (probe["constituent_index"], tuple(probe["candidate_line_class"]))
        n, m, count = expected[key]
        assert len(probe["domain"]["ordered_basis"]) == n
        assert len(probe["codomain"]["ordered_basis"]) == m
        assert len(probe["degree_zero_entries"]) == count
        assert probe["degree_zero_rank_over_Qomega"] == n
        assert module.rational_restriction_rank(probe["degree_zero_entries"], m, n) == 2*n
        assert probe["independent_rank_over_Q"] == 2*n
        assert probe["cover_line_hom_dimension"] == 0
        assert probe["every_flat_equivariant_character_excluded"] is True
        assert all(size == 0 for degree, size in probe["space_dimensions"] if degree < 0)
        assert Fraction(probe["cover_line_slope_exact"]) == _degree(key[1]) > 0


def test_proper_descendants_are_retained_with_quantified_strict_negative_bounds(packet):
    bounds = packet["source_order_refinement"]
    effective = bounds["minimal_proper_effective_divisors"]
    assert len(effective) == 5
    assert [Fraction(row["cover_degree_exact"]) for row in effective] == [
        4032, 3168, 6984, 6768, 2520,
    ]
    assert all(Fraction(row["cover_degree_exact"]) == _degree(row["class"])
               for row in effective)
    assert Fraction(bounds["minimum_proper_effective_cover_degree"]) == 2520
    assert [Fraction(row["all_line_degrees_upper_bound"]) for row in
            bounds["constituent_line_bounds"]] == [-1224, -792]
    for constituent in bounds["constituent_line_bounds"]:
        assert len(constituent["source_order_rows"]) == 6
        for row in constituent["source_order_rows"]:
            degree = Fraction(row["cover_slope_exact"])
            assert degree == _degree(row["line_class"])
            expected = degree - 2520 if degree >= 0 else degree
            assert Fraction(row["remaining_cover_degree_upper_bound"]) == expected < 0
    assert len(packet["source_order_premises"]) == 4


def test_all_proper_rank_pairs_include_the_codimension_two_nonsplitting_case(packet):
    bounds = packet["source_order_refinement"]
    assert list(map(Fraction, bounds["constituent_determinant_cover_degrees"])) == [-432, 432]
    expected = {(1, 0): -1224, (0, 1): -792, (2, 0): -432, (1, 1): -2016,
                (0, 2): -2088, (2, 1): -1224, (1, 2): -792}
    cases = bounds["proper_rank_extension_cases"]
    assert {(row["intersection_rank"], row["image_rank"]) for row in cases} == set(expected)
    for row in cases:
        pair = row["intersection_rank"], row["image_rank"]
        rank = sum(pair)
        determinant = Fraction(row["cover_determinant_degree_upper_bound"])
        assert determinant == expected[pair] < 0
        assert Fraction(row["cover_slope_upper_bound"]) == determinant/rank
        assert determinant/(9*rank) < 0
        if pair == (0, 2):
            assert "codimension two" in row["reason"]
            assert "split the nonzero outer extension" in row["reason"]


def test_slope_stability_does_not_promote_the_remaining_physical_inputs(packet):
    assert packet["status"] == "PROVED"
    assert packet["descended_slope_stability_established"] is True
    assert packet["polarization"] == [14, 16, 1]
    assert packet["original_section_count"] == 5345
    assert packet["parameter_quantifier"] == "every nonzero alternate P1 outer class"
    for flag in (
        "full_stability_chamber_computed", "non_equivariant_cover_stability_claimed",
        "original_sections_or_cloud_inputs_changed", "physical_kahler_class_selected",
        "observations_used", "compatible_background_algorithm_derived",
        "ricci_flat_or_hym_metric_available", "matter_and_higgs_metrics_available",
        "physical_yukawas_available", "common_stabilized_vacuum_available",
    ):
        assert packet[flag] is False


def test_live_dependency_graph_closes_only_the_actual_slope_hypothesis(packet):
    from research.experiments.scientific_genesis import audit

    nodes = audit._nodes()
    claims = {node["id"]: node for node in nodes}
    assert claims["retained_slope_stability"]["status"] == "PROVED"
    assert claims["retained_polarization_stability"]["status"] == "BLOCKED"
    assert claims["visible_metrics"]["status"] == "BLOCKED"
    assert claims["physical_yukawas"]["status"] == "BLOCKED"
    missing = claims["retained_polarization_stability"]["missing_prerequisites"]
    assert "controlled reference-background curvature and metric refinement" in missing
    assert all("actual stability" not in item for item in missing)
    edges = audit._edges()
    pairs = {(edge["source"], edge["target"]) for edge in edges}
    assert ("retained_slope_stability", "retained_polarization_stability") in pairs
    assert ("alternate_constituent_outer_stability_locus", "retained_slope_stability") in pairs
    assert ("alternate_constituent_carrier_state", "retained_slope_stability") in pairs
    assert len(nodes) == 230
    assert len(edges) == 414
    task = next(task for task in audit._scheduler()
                if task["task"] == "alternate_metric_convergence")
    assert "now establish descended slope stability" in task["rationale"]
    state = {"claims": nodes, "dependencies": edges, "fitted_inputs": []}
    state["artifact_digest"] = audit._canonical_digest(state)
    audit.validate_state(state)


def test_reader_is_read_only_and_preserves_every_frozen_request(packet, monkeypatch):
    paths = [module.DIRECTORY / name for name in (
        "full_trial_cloud_request.json", "full_trial_cloud_inputs.json",
        "expanded_trial_cloud_request.json", "expanded_trial_cloud_inputs.json",
    )]
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]

    def forbidden(*args, **kwargs):
        raise AssertionError("stability verification must not draw, write or redraw")

    monkeypatch.setattr("os.urandom", forbidden)
    monkeypatch.setattr(module.Path, "write_text", forbidden)
    monkeypatch.setattr(module.Path, "write_bytes", forbidden)
    assert module.read_certificate(expected_digest=packet["artifact_digest"]) == packet
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths] == before


def test_independent_rank_detects_removed_or_dependent_columns(packet):
    for probe in packet["actual_cover_line_Hom_probes"]:
        n = len(probe["domain"]["ordered_basis"])
        m = len(probe["codomain"]["ordered_basis"])
        entries = [entry for entry in probe["degree_zero_entries"] if entry[1] != n-1]
        assert module.rational_restriction_rank(entries, m, n) == 2*(n-1)
    assert module.rational_restriction_rank(
        [[0, 0, "0", "1"], [0, 1, "0", "1"]], 1, 2,
    ) == 2


@pytest.mark.parametrize("entries, rows, columns", (
    ([[0, 0, "1", "0"], [0, 0, "1", "0"]], 1, 1),
    ([[0, 1, "1", "0"]], 1, 1), ([[True, 0, "1", "0"]], 1, 1),
    ([[0, 0, 1.0, "0"]], 1, 1), ([[0, 0, "2/2", "0"]], 1, 1),
    ([[0, 0, "0", "0"]], 1, 1), ([], 1.0, 1), ([], -1, 0),
))
def test_independent_rank_rejects_ambiguous_or_inexact_matrix_data(entries, rows, columns):
    with pytest.raises(ValueError):
        module.rational_restriction_rank(entries, rows, columns)


@pytest.mark.parametrize("index, line", (
    (False, (-1, -2, 2)), (0.0, (-1, -2, 2)), (2, (-1, -2, 2)),
    (0, (-1.0, -2, 2)), (0, (-1, -2, 2.0)), (0, (-1, -2, True)),
    (0, (-1, -2)), (0, (0, 0, 0)), (1, (-4, 1, 2)),
))
def test_probe_rejects_aliases_even_after_valid_exact_inputs_are_cached(packet, index, line):
    with pytest.raises(ValueError, match="actual source candidate"):
        module.line_hom_probe(index, line)


def test_mutating_returned_probe_does_not_poison_cached_actual_evidence(packet):
    original = module.line_hom_probe(0, (-4, 1, 2))
    attacked = module.line_hom_probe(0, (-4, 1, 2))
    attacked["degree_zero_entries"].clear()
    attacked["cover_line_hom_dimension"] = 1
    assert module.line_hom_probe(0, (-4, 1, 2)) == original


@pytest.mark.parametrize("attack", ("matrix", "rank", "physical", "rank_two", "descendant"))
def test_rehashed_artifacts_cannot_replace_actual_maps_or_scope(packet, attack, tmp_path):
    changed = deepcopy(packet)
    changed.pop("artifact_digest")
    if attack == "matrix":
        changed["actual_cover_line_Hom_probes"][0]["degree_zero_entries"].pop()
    elif attack == "rank":
        changed["actual_cover_line_Hom_probes"][0]["independent_rank_over_Q"] -= 2
    elif attack == "physical":
        changed["ricci_flat_or_hym_metric_available"] = True
    elif attack == "rank_two":
        changed["source_order_refinement"]["proper_rank_extension_cases"].pop(4)
    else:
        changed["source_order_refinement"]["minimum_proper_effective_cover_degree"] = "0"
    changed["artifact_digest"] = module._digest(changed)
    path = tmp_path / "attacked-stability.json"
    path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match="actual line-Hom calculation or source-order"):
        module.read_certificate(expected_digest=changed["artifact_digest"], path=path)
