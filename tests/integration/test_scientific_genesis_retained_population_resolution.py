"""Guard complete-population-only numerical resolution and retained failures.

Owns:
    Immutable workload declaration, shard boundaries, no-redraw failures and
    forbidden subset aggregation without expensive full-cloud execution.

Depends on:
    Original retained inputs and the numerical population-resolution consumer.

Must not:
    Replace actual scientific data with fixtures or infer global error control
    from scope-contract tests.

Phase 0:
    Research execution guards; physical convergence remains unresolved.
"""

import copy

import pytest

from research.experiments.scientific_genesis import retained_population_resolution as module


def test_declaration_preserves_the_entire_old_population_and_selected_h1(monkeypatch):
    monkeypatch.setattr("os.getrandom", lambda *_: pytest.fail("no fresh entropy is permitted"))
    result = module._declaration()
    assert result["sample_count"] == 2048
    assert result["training_count"] == 1536 and result["validation_count"] == 512
    assert result["original_section_count"] == 5345
    assert result["h1_factor_digest"] == module.nonunit.H1
    assert result["policy"]["input_prefix_bits"] == 128
    assert result["policy"]["newton_steps"] == 8
    assert result["old_validation_is_blind"] is False
    assert result["numerical_error_bound_certified"] is False
    assert result["new_entropy_obtained"] is False


@pytest.mark.parametrize("ordinal", (True, -1, 2048, 1.0, "1"))
def test_original_workload_boundaries_have_no_numeric_aliases(ordinal):
    with pytest.raises(ValueError, match="original retained-population"):
        module.sample_path(ordinal)


@pytest.mark.parametrize("worker,workers", ((True, 2), (0, 0), (-1, 2), (2, 2), (0, 1.0)))
def test_invalid_shards_do_not_start_geometry(worker, workers):
    with pytest.raises(ValueError, match="disjoint worker"):
        module.run_shard(expected_digest="unused", worker=worker, workers=workers)


def test_missing_population_cannot_produce_an_admitted_subset_mean(monkeypatch, tmp_path):
    request = module._declaration()
    monkeypatch.setattr(module, "read_request", lambda **_: request)
    monkeypatch.setattr(module, "sample_path", lambda ordinal: tmp_path / f"absent_{ordinal}.json")
    monkeypatch.setattr(module.full, "_install_json", lambda *_: pytest.fail("no partial manifest"))
    with pytest.raises(FileNotFoundError, match="complete original"):
        module.collect(expected_digest="unused")


def test_failed_numerical_geometry_keeps_the_original_input_identity(monkeypatch):
    original = module.full.read_request(expected_digest=module.curvature.PARENT_REQUEST)
    inputs = module.full.cloud.inputs.read_inputs(expected_digest=original["input_digest"],
                                                 path=module.full.INPUTS)
    manifest = module._parent_manifest()
    request = {**module._declaration(), "artifact_digest": "engineering-request-guard"}
    before = copy.deepcopy(module.full.cloud.inputs.sample_identity(inputs, 526))

    def fail(*_, **__):
        raise ArithmeticError("declared numerical geometry unresolved")

    monkeypatch.setattr(module.geometry, "evaluate_geometry", fail)
    monkeypatch.setattr("os.getrandom", lambda *_: pytest.fail("no redraw"))
    record = module.process_sample(request, inputs, manifest, 526, None, None, None,
                                   original_request=original)
    assert record["status"] == "unresolved"
    assert record["reason"] == "declared numerical geometry unresolved"
    assert all(record[key] == value for key, value in before.items())
    assert record["original_sample_digest"] == manifest["sample_archives"][526]["artifact_digest"]
    assert "h1" not in record


def test_missing_independent_comparison_prevents_whole_population_request(monkeypatch, tmp_path):
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "resolution.json")
    monkeypatch.setattr(module, "REQUEST", tmp_path / "request.json")
    monkeypatch.setattr(module.full, "_install_json", lambda *_: pytest.fail("no unchecked run"))
    with pytest.raises(FileNotFoundError):
        module.create_request()
    assert not module.REQUEST.exists()
