"""Check the leverage identity and the recorded H1 sampling diagnosis.

Owns:
    A numerical check of the exact leverage identity on random rank-four
    samples, and regression of the content-addressed diagnosis artifact.

Depends on:
    The research leverage module, numpy, and pytest.

Must not:
    Rebuild H factors, alter samples, or use observations.

Phase 0:
    Regression checks for a research-only diagnosis.
"""

import hashlib
import json
from fractions import Fraction

import numpy as np
import pytest

from research.experiments.metric_sampling.leverage import (
    OUTPUT,
    diagnose,
    mean_leverage_fraction,
)


def test_leverage_identity_holds_on_random_rank_four_samples() -> None:
    rng = np.random.default_rng(7)
    sections, rank, samples = 30, 4, 9
    blocks = [rng.normal(size=(rank, sections)) + 1j * rng.normal(size=(rank, sections))
              for _ in range(samples)]
    weights = rng.lognormal(size=samples)
    t = sum(w / samples * m.conj().T @ m for w, m in zip(weights, blocks, strict=True))
    inverse = np.linalg.inv(t)
    leverages = [w / samples * m @ inverse @ m.conj().T
                 for w, m in zip(weights, blocks, strict=True)]
    assert np.isclose(sum(np.trace(b).real for b in leverages), sections)
    for block in leverages:
        eigenvalues = np.linalg.eigvalsh((block + block.conj().T) / 2)
        assert eigenvalues.min() > -1e-9 and eigenvalues.max() < 1 + 1e-9


def test_mean_leverage_fraction_is_exact_and_guards_invertibility() -> None:
    assert mean_leverage_fraction(5345, 4, 1536) == Fraction(5345, 6144)
    assert mean_leverage_fraction(5345, 4, 8192) == Fraction(5345, 32768)
    with pytest.raises(ValueError, match="cannot be invertible"):
        mean_leverage_fraction(5345, 4, 1336)


def test_recorded_split_is_in_sample_and_artifact_is_current() -> None:
    result = diagnose()
    assert result.effective_size_below_threshold
    assert result.h1_in_sample_ratio > 100
    assert abs(result.h0_in_sample_ratio - 1) < 0.1
    assert result.h1_validation_tau < result.h0_validation_tau
    record = json.loads(OUTPUT.read_text())
    unsigned = {key: value for key, value in record.items() if key != "artifact_digest"}
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    assert record["artifact_digest"] == hashlib.sha256(payload).hexdigest()
    assert record["registered_prediction"] == result.registered_prediction
