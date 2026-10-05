"""Attack original-basis workload retention and held-out sample scheduling.

Owns:
    Input-policy rejection, immutable checkpoints, disjoint scheduling, absence
    of admitted-subset means, and genuine full-section pilot regression.

Depends on:
    The research full-cloud controller, frozen original pilot inputs, and pytest.

Must not:
    Present scheduler fixtures as physical inputs, invent section matrices, or
    claim that numerical row admission establishes an invertible global metric.

Phase 0:
    Research execution tests only; HYM and physical flavor remain unavailable.
"""

import gzip
import json
from copy import deepcopy

import pytest

from research.experiments.scientific_genesis import full_trial_cloud as module


def _unavailable(*args, **kwargs):
    raise AssertionError("read-only verification must not discover or redraw")


REQUEST_DIGEST = "9e13a565bc13a2bd27320e5746d3fbf2104c3290f8792efc97d8d3316bc8a5b5"


def test_captured_whole_request_is_read_only_and_keeps_the_original_population(monkeypatch):
    monkeypatch.setattr(module.cloud.inputs, "create_inputs", _unavailable)
    monkeypatch.setattr(module, "process_sample", _unavailable)
    record = module.read_request(expected_digest=REQUEST_DIGEST)
    assert (record["sample_count"], record["training_count"], record["validation_count"]) == (
        2048,
        1536,
        512,
    )
    assert record["input_digest"] == (
        "cfaac611b57142a0c291a3c3336c6bf34c61c64aecfd3370af50aa0474380d6e"
    )
    assert record["split_fixed_before_geometry"] is True
    assert record["observations_used"] is False
    assert record["entropy_assumption_status"] == "ASSUMED"


@pytest.mark.parametrize(
    "key,value",
    (
        ("training_count", 1400),
        ("parameter_point_status", "DERIVED"),
        ("entropy_assumption_status", "PROVED"),
        ("observations_used", True),
        ("original_section_basis_digest", "0" * 64),
        ("section_form", "reduced empirical metric"),
        ("source_files_sha256", {}),
    ),
)
def test_rehashed_real_request_cannot_change_selection_or_scope(key, value, tmp_path):
    record = json.loads(module.REQUEST.read_bytes())
    record[key] = value
    record.pop("artifact_digest")
    record["artifact_digest"] = module.cloud.inputs._digest(record)
    path = tmp_path / "attacked-request.json"
    module._install_json(path, record)
    with pytest.raises(ValueError, match="split, policy or scientific scope"):
        module.read_request(expected_digest=record["artifact_digest"], path=path)


def test_existing_request_cannot_be_replaced_with_new_entropy(monkeypatch):
    monkeypatch.setattr(module.cloud.inputs, "create_inputs", _unavailable)
    with pytest.raises(FileExistsError, match="replacement entropy"):
        module.create_request(
            count=2048,
            training_count=1536,
            bytes_per_stream=32,
            levels=(16, 20, 24),
            max_cells=65536,
        )


@pytest.mark.parametrize(
    "change",
    (
        {"count": 0},
        {"count": True},
        {"training_count": 1336},
        {"training_count": 2048},
        {"training_count": True},
        {"bytes_per_stream": 15},
        {"levels": (16, 16)},
        {"levels": (16, 20, 65)},
        {"levels": (16, 12)},
        {"max_cells": 0},
    ),
)
def test_insufficient_or_ambiguous_request_fails_before_entropy(change, monkeypatch):
    monkeypatch.setattr(module.cloud.inputs, "create_inputs", _unavailable)
    values = dict(
        count=2048, training_count=1536, bytes_per_stream=32, levels=(16, 20, 24), max_cells=65536
    )
    values.update(change)
    with pytest.raises(ValueError):
        module.create_request(**values)


def test_missing_reader_never_obtains_entropy_or_runs_geometry(tmp_path, monkeypatch):
    monkeypatch.setattr(module.cloud.inputs, "create_inputs", _unavailable)
    monkeypatch.setattr(module, "process_sample", _unavailable)
    with pytest.raises(FileNotFoundError):
        module.read_request(expected_digest="0" * 64, path=tmp_path / "missing.json")


def test_json_checkpoint_installation_is_immutable(tmp_path):
    path = tmp_path / "scheduler.json"
    module._install_json(path, {"scheduler_test": True})
    module._install_json(path, {"scheduler_test": True})
    with pytest.raises(FileExistsError):
        module._install_json(path, {"scheduler_test": False})
    assert json.loads(path.read_bytes()) == {"scheduler_test": True}


def test_terminal_shard_reuses_failed_checkpoints_without_entropy_or_replay(tmp_path, monkeypatch):
    # Nonphysical scheduler fixture. No section values or geometry are supplied.
    request = {"sample_count": 11, "input_digest": "scheduler-only"}
    monkeypatch.setattr(module, "read_request", lambda **kw: request)
    monkeypatch.setattr(module.cloud.inputs, "read_inputs", lambda **kw: {})
    monkeypatch.setattr(module, "_sources", lambda: {"scheduler": "only"})
    monkeypatch.setattr(module, "_sample_path", lambda i: tmp_path / f"{i}.json")
    for ordinal in (2, 5, 8):
        module._install_json(module._sample_path(ordinal), {"scheduler_test": True})
    seen = []

    def saved(req, inputs, ordinal):
        seen.append(ordinal)
        return {"history": [{"kernel_status": "unresolved"}]}

    monkeypatch.setattr(module, "_read_sample", saved)
    monkeypatch.setattr(module, "process_sample", _unavailable)
    monkeypatch.setattr(module.cloud.features, "compile_features", _unavailable)
    monkeypatch.setattr(module.cloud.inputs, "create_inputs", _unavailable)
    result = module.run_shard(expected_request_digest="scheduler-only", worker=2, workers=3)
    assert seen == [2, 5, 8]
    assert result["owned_request_count"] == 3
    assert result["unresolved_ordinals"] == [2, 5, 8]


def test_pending_workload_never_becomes_an_admitted_subset_integral(tmp_path, monkeypatch):
    # Scheduler fixture has no geometric or numerical payload.
    request = {
        "sample_count": 4,
        "training_count": 3,
        "validation_count": 1,
        "input_digest": "scheduler-only",
        "artifact_digest": "scheduler-only",
    }
    monkeypatch.setattr(module, "read_request", lambda **kw: request)
    monkeypatch.setattr(module.cloud.inputs, "read_inputs", lambda **kw: {})
    monkeypatch.setattr(module, "_sources", lambda: {"scheduler": "only"})
    monkeypatch.setattr(module, "_sample_path", lambda i: tmp_path / f"{i}.json")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    for ordinal in (0, 1, 3):
        module._install_json(module._sample_path(ordinal), {"scheduler_test": True})

    def saved(req, inputs, ordinal):
        return {
            "artifact_digest": "scheduler-only",
            "history": [
                {
                    "kernel_status": "unresolved" if ordinal == 1 else "computed_discovery",
                    "component": "scheduler-only",
                }
            ],
        }

    monkeypatch.setattr(module, "_read_sample", saved)
    result = module.inspect_progress(expected_request_digest="scheduler-only")
    assert result["missing_sample_ordinals"] == [2]
    assert result["unresolved_sample_ordinals"] == [1]
    assert result["completed_checkpoint_count"] == 3
    for flag in (
        "complete_original_workload_available",
        "failed_samples_dropped",
        "admitted_subset_mean_available",
        "global_trial_operator_estimate_available",
        "nonunit_h_iteration_executed",
        "ricci_flat_or_hym_metric_available",
    ):
        assert result[flag] is False
    with pytest.raises(FileNotFoundError):
        module.collect(expected_request_digest="scheduler-only")


def _pilot_regression():
    """Use actual original sections, never generic physical matrices."""

    inputs = module.cloud.inputs.read_inputs(expected_digest=module.cloud.INPUT_DIGEST)
    original = json.loads(gzip.decompress(module.cloud._checkpoint_path(0).read_bytes()))
    request = {
        "sample_count": 16,
        "training_count": 16,
        "artifact_digest": "regression-on-original-pilot-not-a-new-cloud",
        "policy": {"levels": [16], "max_cells": 65536},
    }
    sample = {
        **{k: original[k] for k in ("sample_id", "ordinal", "streams")},
        "history": [original["history"][-1]],
        "role": "training",
        "request_digest": request["artifact_digest"],
        "original_section_basis_digest": module.cloud.features.BASIS,
    }
    sample["artifact_digest"] = module.cloud.inputs._digest(sample)
    return request, inputs, sample


def test_checkpoint_reader_checks_actual_full_pilot_rows(tmp_path, monkeypatch):
    request, inputs, sample = _pilot_regression()
    monkeypatch.setattr(module, "_sample_path", lambda i: tmp_path / f"{i}.json.gz")
    module.cloud._install_sample(module._sample_path(0), sample)
    assert module._read_sample(request, inputs, 0) == sample
    assert len(module.cloud._decode_rows(sample["history"][-1]["kernel_rows"])[0]) == 5345


@pytest.mark.parametrize(
    "key,value",
    (
        ("role", "validation"),
        ("original_section_basis_digest", "0" * 64),
        ("request_digest", "reselected"),
        ("ordinal", 1),
    ),
)
def test_rehashed_checkpoint_cannot_change_original_identity(key, value, tmp_path, monkeypatch):
    request, inputs, sample = _pilot_regression()
    sample[key] = value
    sample.pop("artifact_digest")
    sample["artifact_digest"] = module.cloud.inputs._digest(sample)
    monkeypatch.setattr(module, "_sample_path", lambda i: tmp_path / f"{i}.json.gz")
    module.cloud._install_sample(module._sample_path(0), sample)
    with pytest.raises(ValueError):
        module._read_sample(request, inputs, 0)


def test_rehashed_checkpoint_cannot_omit_a_section(tmp_path, monkeypatch):
    request, inputs, sample = _pilot_regression()
    sample = deepcopy(sample)
    for row in sample["history"][-1]["kernel_rows"]:
        row.pop()
    sample.pop("artifact_digest")
    sample["artifact_digest"] = module.cloud.inputs._digest(sample)
    monkeypatch.setattr(module, "_sample_path", lambda i: tmp_path / f"{i}.json.gz")
    module.cloud._install_sample(module._sample_path(0), sample)
    with pytest.raises(ValueError, match="all four full original"):
        module._read_sample(request, inputs, 0)


def test_fresh_single_request_consumes_all_original_sections_without_redraw():
    request, inputs, _ = _pilot_regression()
    program = module.cloud.features.compile_features()
    result = module.process_sample(request, inputs, 0, program)
    assert result["sample_id"] == module.cloud.inputs.sample_identity(inputs, 0)["sample_id"]
    assert len(result["history"]) == 1
    final = result["history"][-1]
    assert final["status"] == "admitted"
    assert final["kernel_status"] == "computed_discovery"
    assert final["complete_original_sections_consumed"] is True
    assert len(module.cloud._decode_rows(final["kernel_rows"])[0]) == 5345
    assert final["frame_policy"]["covering_degree"] == 9


def test_selected_pilot_point_passes_the_established_exact_common_rank_gate():
    from onetheory.math.numbers import OMEGA, Eisenstein, Rational
    from research.experiments.scientific_genesis.mixed_schoen_chain_actions import (
        _parse_eisenstein_text,
    )

    state = json.loads(
        (
            module.ROOT / "data/generated/scientific_genesis/scientific_genesis_state.json"
        ).read_bytes()
    )
    terms = state["completed_down_lepton_holomorphic_matrices"][
        "four_sector_common_rank_three_locus_polynomial"
    ]
    value = sum(
        (_parse_eisenstein_text(t["coefficient"]) * OMEGA ** t["powers"][1] for t in terms),
        Eisenstein(0),
    )
    assert value == Eisenstein(Rational(-9, 87808), Rational(81, 43904))
    assert value != Eisenstein(0)
