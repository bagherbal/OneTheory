"""Guard uniform arithmetic workloads and preservation of their failed parent.

Owns:
    Whole-population declarations, disjoint worker boundaries and missing-output
    rejection without inventing a physical numerical result.

Depends on:
    The actual failed binary64 result and the precise population producer.

Must not:
    Average a fixture or turn an execution guard into a global accuracy claim.

Phase 0:
    Research arithmetic workload governance only.
"""

import pytest

from research.experiments.scientific_genesis import retained_precise_population as module


def test_uniform_arithmetic_declaration_keeps_all_original_inputs_and_h1():
    r = module._declaration()
    assert r["sample_count"] == 2048
    assert r["failed_binary64_result_digest"] == module.RAW
    assert r["policy"]["geometry_working_precision_bits"] == 256
    assert r["policy"]["floating_mantissa_bits"] == 53
    assert r["policy"]["scaled_equation_residual_tolerance"] == 1e-12
    assert r["policy"]["newton_steps"] == 8
    assert r["h1_factor_digest"] == module.previous.nonunit.H1
    assert r["original_section_count"] == 5345
    assert r["hybrid_or_subset_mean_available"] is False


@pytest.mark.parametrize("ordinal", (-1, 2048, True, 1.0, "1"))
def test_new_workload_does_not_allow_replacement_ordinals(ordinal):
    with pytest.raises(ValueError, match="original retained"):
        module.sample_path(ordinal)


@pytest.mark.parametrize("worker,workers", ((True, 2), (0, 0), (-1, 2), (2, 2), (0, 1.0)))
def test_invalid_shards_do_not_evaluate_geometry(worker, workers):
    with pytest.raises(ValueError, match="disjoint worker"):
        module.run_shard(expected_digest="engineering-guard", worker=worker, workers=workers)


def test_missing_uniform_population_cannot_patch_the_old_mean(monkeypatch, tmp_path):
    request = module._declaration()
    monkeypatch.setattr(module, "read_request", lambda **_: request)
    monkeypatch.setattr(module, "sample_path", lambda ordinal: tmp_path / f"absent_{ordinal}.json")
    monkeypatch.setattr(module.full, "_install_json",
                        lambda *_: pytest.fail("no partial aggregate"))
    with pytest.raises(FileNotFoundError, match="complete uniform arithmetic"):
        module.collect(expected_digest="engineering-guard")
