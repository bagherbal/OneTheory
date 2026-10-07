"""Check complete retained curvature sums and independent Chern-Weil targets.

Owns:
    Actual all-input profile inspection, independent intersection arithmetic,
    and mutation attacks on identities, scientific scope and complete means.

Depends on:
    The terminal H0 refinement and its raw parent, exact rational arithmetic,
    the research normalization reader and pytest.

Must not:
    Refit empirical weights, substitute fixtures for carrier data, or claim
    discovery offsets certify integration accuracy or a physical HYM metric.

Phase 0:
    Research scope and normalization checks only.
"""

import json
import math
from copy import deepcopy
from fractions import Fraction
from functools import cache

import pytest

from research.experiments.scientific_genesis import reference_curvature_checks as module


@cache
def _actual():
    return module.read_profile(expected_digest=module.PROFILE)


def test_completed_refinement_consumes_all_original_points_without_entropy_or_writes(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("a complete-profile reader must not draw or write")

    monkeypatch.setattr("os.urandom", forbidden)
    monkeypatch.setattr(module.Path, "write_text", forbidden)
    monkeypatch.setattr(module.Path, "write_bytes", forbidden)
    record = module.read_profile(expected_digest=module.PROFILE)
    assert len(record["points"]) == 2048
    assert sum(p["role"] == "training" for p in record["points"]) == 1536
    assert sum(p["role"] == "validation" for p in record["points"]) == 512
    assert all(record["points"][i]["status"] == "computed_discovery"
               for i in (632, 956, 1007, 1161, 1637, 1962))
    assert record["full_population_tau_discovery"] == 1.2445720689962494
    assert record["admitted_subset_mean_available"] is False


def test_chern_weil_targets_match_an_independent_exact_quotient_intersection():
    targets = module.normalization_targets()
    # Independent expansion of the published quotient tensor, not the producer's
    # ambient Polynomial multiplication. The actual divisor order is x,u,p.
    x, u, p = map(Fraction, (14, 16, 1))
    cubic = x * x * u + x * u * u + 6 * x * u * p
    assert cubic == 8064
    assert Fraction(targets["quotient_volume_exact"]) == cubic / 6 == 1344
    assert Fraction(targets["trace_integral_pi_coefficient_exact"]) == 4 * cubic == 32256
    assert Fraction(targets["volume_average_trace_pi_coefficient_exact"]) == 4 * 3 * 2 == 24
    assert targets["twisted_c1_coordinates"] == [56, 64, 4]


def test_empirical_trace_and_volume_remain_unadjusted_discovery_offsets():
    record = _actual()
    trace = math.fsum(p["reference_volume_weight"] * p["twisted_curvature_trace"]
                      for p in record["points"]) / 2048
    assert math.isclose(trace, 102896.70412172737, rel_tol=1e-14)
    assert math.isclose(trace / (32256 * math.pi) - 1, 0.0154091696947614,
                        rel_tol=1e-12)
    assert record["empirical_reference_volume_discovery"] != 1344
    assert record["numerical_and_sampling_error_certified"] is False
    assert record["reference_background_is_ricci_flat"] is False


@pytest.mark.parametrize("flag", (
    "hym_convergence_established", "physical_yukawas_available",
    "common_stabilized_vacuum_available", "numerical_and_sampling_error_certified",
    "reference_background_is_ricci_flat", "admitted_subset_mean_available",
    "old_validation_is_blind", "observations_used",
))
def test_complete_discovery_profile_cannot_inflate_its_scientific_scope(flag):
    record = deepcopy(_actual())
    record[flag] = True
    with pytest.raises(ValueError, match="scientific scope"):
        module.validate_profile(record)


@pytest.mark.parametrize("change", ("remove", "role", "root", "source", "mean", "weight"))
def test_complete_profile_rejects_identity_source_or_aggregate_mutations(change):
    record = deepcopy(_actual())
    if change == "remove":
        record["points"].pop(632)
    elif change == "role":
        record["points"][632]["role"] = "validation"
    elif change == "root":
        record["points"][632]["selected_branch"] = [0, 0]
    elif change == "source":
        source = next(iter(record["source_files_sha256"]))
        record["source_files_sha256"][source] = "0" * 64
    elif change == "weight":
        record["points"][632]["reference_volume_weight"] *= 2
    else:
        record["full_population_tau_discovery"] *= 2
    with pytest.raises(ValueError):
        module.validate_profile(record)


def test_profile_requires_the_terminal_digest_not_its_own_edited_checksum(tmp_path):
    record = deepcopy(_actual())
    record["points"].pop(632)
    record["artifact_digest"] = module.refinement.curvature.full.cloud.inputs._digest({
        key: value for key, value in record.items() if key != "artifact_digest"
    })
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="completed reference"):
        module.read_profile(expected_digest=record["artifact_digest"], path=path)
