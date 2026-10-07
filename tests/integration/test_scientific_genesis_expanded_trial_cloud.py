"""Test fresh-population retention without manufacturing geometric evidence.

Owns:
    Predeclaration, immutable receipts, disjoint scheduling, old-data retention,
    native checkpoint contracts and explicit unresolved-population boundaries.

Depends on:
    The research expanded-cloud controller, original retained checkpoints and
    pytest for nonphysical scheduler fixtures and real archive regressions.

Must not:
    Substitute test streams or synthetic rows for the actual independent cloud,
    claim IID from receipts or turn a larger sample count into a metric theorem.

Phase 0:
    Research controller tests only; no physical metric is supplied.
"""

import gzip
import json
from copy import deepcopy

import pytest

from research.experiments.scientific_genesis import expanded_trial_cloud as module


def _unavailable(*args, **kwargs):
    raise AssertionError("this operation must not obtain entropy or perform geometry")


def _parent():
    return module.frozen.read_request(expected_digest=module.PARENT_REQUEST)


REQUEST_DIGEST = "65d7683b549605256f95b23bccf1f97e6f5c4ffc07ae7cac68fdfa778b6e55b8"


def test_actual_fresh_receipt_is_complete_and_its_reader_is_read_only(monkeypatch):
    monkeypatch.setattr(module.frozen.cloud.inputs, "create_inputs", _unavailable)
    monkeypatch.setattr(module.frozen, "process_sample", _unavailable)
    request = module.read_request(expected_digest=REQUEST_DIGEST)
    assert request["input_digest"] == (
        "c4858eb82f7152c9332130b80a4af047fcc2c571dfc628f08f9a4a2cd21ad958"
    )
    inputs = module.frozen.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=module.INPUTS,
    )
    assert inputs["sample_count"] == 16384
    assert inputs["bytes_per_stream"] == 32
    assert all(len(sample["streams"]) == 13 for sample in inputs["samples"])
    assert (request["training_count"], request["validation_count"]) == (8192, 8192)
    assert module.INPUTS != module.frozen.INPUTS
    assert module._sample_path(0) != module.frozen._sample_path(0)
    assert module.frozen._role(request, 8191) == "training"
    assert module.frozen._role(request, 8192) == "validation"


@pytest.mark.parametrize("key,value", (
    ("older_populations_retained_unchanged", False),
    ("older_validation_is_blind_for_this_experiment", True),
    ("old_and_new_populations_combined_in_an_estimator", True),
    ("sample_budget_proves_balance", True),
    ("new_validation_used_to_select_request", True),
    ("observations_used", True),
    ("entropy_assumption_status", "PROVED"),
    ("parameter_point_status", "DERIVED"),
    ("auxiliary_law", "clipped empirical weights"),
    ("original_section_basis_digest", "0" * 64),
))
def test_rehashed_fresh_request_cannot_promote_or_change_scientific_scope(key, value, tmp_path):
    record = json.loads(module.REQUEST.read_bytes())
    record[key] = value
    record.pop("artifact_digest")
    record["artifact_digest"] = module.frozen.cloud.inputs._digest(record)
    path = tmp_path / "attacked-request.json"
    module.frozen._install_json(path, record)
    with pytest.raises(ValueError, match="scientific scope"):
        module.read_request(expected_digest=record["artifact_digest"], path=path)


@pytest.mark.parametrize("change", (
    {"count": True}, {"count": 0}, {"training_count": True}, {"training_count": 1536},
    {"training_count": 16384}, {"training_count": 16000}, {"levels": ()},
    {"levels": (True,)}, {"levels": (1,)}, {"levels": (20, 16)},
    {"levels": (16, 16)}, {"max_cells": False}, {"max_cells": 0},
))
def test_invalid_declaration_fails_before_entropy(change, monkeypatch, tmp_path):
    monkeypatch.setattr(module, "REQUEST", tmp_path / "request.json")
    monkeypatch.setattr(module, "INPUTS", tmp_path / "inputs.json")
    monkeypatch.setattr(module, "_parent", _parent)
    monkeypatch.setattr(module.frozen.cloud.inputs, "create_inputs", _unavailable)
    values = dict(count=16384, training_count=8192, bytes_per_stream=32,
                  levels=(16, 20, 24), max_cells=65536)
    values.update(change)
    with pytest.raises(ValueError):
        module.create_request(**values)


@pytest.mark.parametrize("change", ({"bytes_per_stream": 31}, {"levels": (65,)}))
def test_stream_policy_cannot_exceed_captured_bits(change, monkeypatch, tmp_path):
    monkeypatch.setattr(module, "REQUEST", tmp_path / "request.json")
    monkeypatch.setattr(module, "INPUTS", tmp_path / "inputs.json")
    monkeypatch.setattr(module.frozen.cloud.inputs, "create_inputs", _unavailable)
    values = dict(count=16384, training_count=8192, bytes_per_stream=32,
                  levels=(16, 20, 24), max_cells=65536)
    values.update(change)
    with pytest.raises(ValueError):
        module.create_request(**values)


@pytest.mark.parametrize("existing", ("REQUEST", "INPUTS"))
def test_partial_or_complete_capture_never_triggers_replacement(existing, monkeypatch, tmp_path):
    monkeypatch.setattr(module, "REQUEST", tmp_path / "request.json")
    monkeypatch.setattr(module, "INPUTS", tmp_path / "inputs.json")
    getattr(module, existing).write_bytes(b"retained nonphysical scheduler receipt")
    monkeypatch.setattr(module.frozen.cloud.inputs, "create_inputs", _unavailable)
    with pytest.raises(FileExistsError, match="replacement entropy"):
        module.create_request(count=16384, training_count=8192, bytes_per_stream=32,
                              levels=(16, 20, 24), max_cells=65536)


def test_declaration_keeps_all_sections_and_does_not_recycle_old_validation():
    parent = _parent()
    record = module._declaration(parent, count=16384, training_count=8192,
                                 levels=(16, 20, 24), max_cells=65536)
    assert (record["training_count"], record["validation_count"]) == (8192, 8192)
    assert record["policy"] == parent["policy"]
    assert record["section_form"] == parent["section_form"]
    assert record["original_section_basis_digest"] == parent["original_section_basis_digest"]
    assert record["older_populations_retained_unchanged"] is True
    assert record["split_fixed_before_geometry"] is True
    for flag in ("older_validation_is_blind_for_this_experiment",
                 "old_and_new_populations_combined_in_an_estimator", "sample_budget_proves_balance",
                 "new_validation_used_to_select_request", "observations_used"):
        assert record[flag] is False


def test_parent_obstruction_reader_is_read_only(monkeypatch):
    monkeypatch.setattr(module.frozen.cloud.inputs, "create_inputs", _unavailable)
    monkeypatch.setattr(module.frozen, "process_sample", _unavailable)
    assert module._parent()["artifact_digest"] == module.PARENT_REQUEST


@pytest.mark.parametrize("ordinal", (0, 78, 1535, 1536, 2047))
def test_parameterized_reader_matches_real_frozen_native_history(ordinal, monkeypatch):
    """Real old archives check the reader contract, not a new sample result."""

    request = _parent()
    inputs = module.frozen.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=module.frozen.INPUTS,
    )
    before = module.frozen._sample_path(ordinal).read_bytes()
    expected = module.frozen._read_sample(request, inputs, ordinal)
    monkeypatch.setattr(module.frozen, "process_sample", _unavailable)
    actual = module.read_sample(request, inputs, ordinal, path=module.frozen._sample_path(ordinal))
    assert actual == expected
    assert module.frozen._sample_path(ordinal).read_bytes() == before
    assert all(len(row) == 5345 for row in actual["history"][-1]["kernel_rows"])


@pytest.mark.parametrize("attack", ("role", "identity", "basis", "columns", "address", "precision",
                                   "component", "frame", "history", "weight"))
def test_rehashed_checkpoint_cannot_change_original_identity_or_scope(attack, tmp_path):
    request = _parent()
    inputs = module.frozen.cloud.inputs.read_inputs(
        expected_digest=request["input_digest"], path=module.frozen.INPUTS,
    )
    record = module.frozen._read_sample(request, inputs, 78)
    record = deepcopy(record)
    final = record["history"][-1]
    if attack == "role":
        record["role"] = "validation"
    elif attack == "identity":
        record["sample_id"] = "another sample"
    elif attack == "basis":
        record["original_section_basis_digest"] = "0" * 64
    elif attack == "columns":
        final["kernel_rows"][0].pop()
    elif attack == "address":
        final["address"] = {}
    elif attack == "precision":
        final["floating_mantissa_bits"] = 24
    elif attack == "component":
        final["component"] = "replacement"
    elif attack == "frame":
        final["frame_policy"]["covering_degree"] = 1
    elif attack == "history":
        record["history"] = []
    else:
        final["weight_midpoint_without_pi_cubed"] = float("nan").hex()
    record.pop("artifact_digest")
    record["artifact_digest"] = module.frozen.cloud.inputs._digest(record)
    path = tmp_path / "attacked.json.gz"
    module.frozen.cloud._install_sample(path, record)
    with pytest.raises(ValueError):
        module.read_sample(request, inputs, 78, path=path)


def test_terminal_shards_keep_failed_inputs_without_geometric_replay(monkeypatch, tmp_path):
    # Scheduler-only fixture; contains no physical coefficients or sample rows.
    request = {"sample_count": 11, "input_digest": "scheduler-only"}
    monkeypatch.setattr(module, "read_request", lambda **kw: request)
    monkeypatch.setattr(module, "_sources", lambda: {"scheduler": "only"})
    monkeypatch.setattr(module.frozen.cloud.inputs, "read_inputs", lambda **kw: {})
    monkeypatch.setattr(module, "_sample_path", lambda ordinal: tmp_path / f"{ordinal}.json.gz")
    for ordinal in (2, 5, 8):
        module._sample_path(ordinal).write_bytes(gzip.compress(b"scheduler-only"))
    seen = []

    def read(req, inputs, ordinal):
        seen.append(ordinal)
        return {"history": [{"kernel_status": "unresolved"}]}

    monkeypatch.setattr(module, "read_sample", read)
    monkeypatch.setattr(module.frozen.cloud.features, "compile_features", _unavailable)
    monkeypatch.setattr(module.frozen, "process_sample", _unavailable)
    monkeypatch.setattr(module.frozen.cloud.inputs, "create_inputs", _unavailable)
    result = module.run_shard(expected_request_digest="scheduler-only", worker=2, workers=3)
    assert seen == [2, 5, 8]
    assert result["owned_request_count"] == 3
    assert result["unresolved_ordinals"] == [2, 5, 8]


def test_incomplete_population_has_no_integral_or_manifest(monkeypatch, tmp_path):
    # No simulated universe: test only a missing filesystem workload.
    request = {"sample_count": 4, "training_count": 2, "validation_count": 2,
               "input_digest": "scheduler-only", "artifact_digest": "scheduler-only"}
    monkeypatch.setattr(module, "read_request", lambda **kw: request)
    monkeypatch.setattr(module, "_sources", lambda: {"scheduler": "only"})
    monkeypatch.setattr(module.frozen.cloud.inputs, "read_inputs", lambda **kw: {})
    monkeypatch.setattr(module, "_sample_path", lambda ordinal: tmp_path / f"{ordinal}.json.gz")
    monkeypatch.setattr(module.frozen.cloud.inputs, "create_inputs", _unavailable)
    monkeypatch.setattr(module.frozen, "process_sample", _unavailable)
    record = module.inspect_progress(expected_request_digest="scheduler-only")
    assert record["missing_sample_ordinals"] == [0, 1, 2, 3]
    assert record["completed_checkpoint_count"] == 0
    for flag in ("complete_original_workload_available", "admitted_subset_mean_available",
                 "controlled_integral_available", "atomic_condition_tested",
                 "nonunit_h_iteration_executed", "physical_yukawas_available"):
        assert record[flag] is False
    with pytest.raises(FileNotFoundError, match="incomplete"):
        module.collect(expected_request_digest="scheduler-only")
