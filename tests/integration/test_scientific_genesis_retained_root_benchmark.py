"""Guard the actual retained-input root benchmark's immutable predecessors.

Owns:
    Trusted native packet checks, declared case boundaries and forbidden
    sampling/physical claims for the certification-cost experiment.

Depends on:
    The research benchmark and independently completed native resolution data.

Must not:
    Replace physical data with fixtures, run costly benchmark geometry during
    collection, or infer global convergence from two selected cases.

Phase 0:
    Provenance and scope tests for an unresolved global metric calculation.
"""

import pytest

from research.experiments.scientific_genesis import retained_root_benchmark as module


@pytest.mark.parametrize("ordinal", (526, 1360))
def test_benchmark_requires_the_executed_native_packet(ordinal):
    record = module.read_native(ordinal)
    assert record["artifact_digest"] == module.NATIVE[ordinal]
    assert record["original_sample_digest"] == module.prior.SAMPLES[ordinal]
    assert record["observations_used"] is False
    assert record["h2_executed"] is False
    assert record["local_resolution_error_bound_certified"] is False
    assert record["history"][-1]["level"] == module.LEVEL == 32


@pytest.mark.parametrize("ordinal", (True, 0, 526.0, "526"))
def test_no_implicit_extra_cases_or_numeric_aliases(ordinal):
    with pytest.raises(ValueError, match="diagnostic cases"):
        module.output_path(ordinal)
