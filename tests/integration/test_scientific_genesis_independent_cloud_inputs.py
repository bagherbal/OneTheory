"""Test computational entropy receipts without treating mocks as physical randomness.

Owns:
    Short-read preservation, exact stream decoding, immutable replay identities,
    and rejection of scope inflation or outcome-dependent regeneration.

Depends on:
    The research input receipt module and pytest temporary files.

Must not:
    Claim finite fixtures prove IID or use them as the executed integration cloud.

Phase 0:
    IO and address regressions only; the entropy law remains an assumption.
"""

import hashlib
import json

import pytest

from research.experiments.scientific_genesis import independent_cloud_inputs as module


def test_partial_reads_are_retained_and_receipts_replay_without_entropy(tmp_path, monkeypatch):
    calls = []

    def entropy(n):
        calls.append(n)
        return bytes([len(calls) % 256]) * min(n, 3)

    monkeypatch.setattr(module.os, "getrandom", entropy)
    path = tmp_path / "receipt.json"
    record = module.create_inputs(count=2, bytes_per_stream=16, path=path)
    assert len(calls) == 2*len(module.CHANNELS)*6
    assert record["samples"][0]["streams"][0]["hex"] == (
        b"\x01"*3 + b"\x02"*3 + b"\x03"*3 + b"\x04"*3 + b"\x05"*3 + b"\x06"
    ).hex()
    old_calls = len(calls)
    assert module.read_inputs(expected_digest=record["artifact_digest"], path=path) == record
    with pytest.raises(FileExistsError):
        module.create_inputs(count=2, bytes_per_stream=16, path=path)
    assert len(calls) == old_calls
    assert record["finite_bytes_prove_independence"] is False
    assert record["geometry_outcomes_used_to_select_inputs"] is False
    assert record["entropy_assumption_status"] == "ASSUMED"
    assert module.address(record, 0).component.bits[:8] == (0, 0, 0, 0, 0, 0, 0, 1)
    identity = module.sample_identity(record, 0)
    assert len({s["stream_id"] for s in identity["streams"]}) == len(module.CHANNELS)
    assert module.sample_identity(record, 0) != module.sample_identity(record, 1)


def test_duplicate_values_do_not_condition_the_random_law(tmp_path, monkeypatch):
    monkeypatch.setattr(module.os, "getrandom", lambda n: b"\x00"*n)
    record = module.create_inputs(count=2, bytes_per_stream=1, path=tmp_path / "receipt.json")
    assert module.address(record, 0) == module.address(record, 1)
    assert module.sample_identity(record, 0)["sample_id"] != (
        module.sample_identity(record, 1)["sample_id"]
    )


@pytest.mark.parametrize("count,size", ((0, 16), (-1, 16), (True, 16), (1, 0), (1, 1.0)))
def test_invalid_workloads_do_not_request_any_entropy(count, size, tmp_path, monkeypatch):
    def reject(n):
        raise AssertionError("no random source may be invoked for invalid requests")
    monkeypatch.setattr(module.os, "getrandom", reject)
    with pytest.raises(ValueError):
        module.create_inputs(count=count, bytes_per_stream=size, path=tmp_path / "unused.json")


@pytest.mark.parametrize("change", (
    {"finite_bytes_prove_independence": True},
    {"geometry_outcomes_used_to_select_inputs": True},
    {"entropy_assumption_status": "PROVED"},
    {"sample_count": True},
))
def test_rehashed_scope_changes_do_not_promote_independence(tmp_path, monkeypatch, change):
    monkeypatch.setattr(module.os, "getrandom", lambda n: b"\x00"*n)
    path = tmp_path / "receipt.json"
    record = module.create_inputs(count=1, bytes_per_stream=1, path=path)
    unsigned = {k: v for k, v in record.items() if k != "artifact_digest"}
    unsigned.update(change)
    digest = hashlib.sha256(module._canonical(unsigned)).hexdigest()
    path.write_bytes(module._canonical({**unsigned, "artifact_digest": digest}))
    with pytest.raises(ValueError, match="trusted identity"):
        module.read_inputs(expected_digest=record["artifact_digest"], path=path)
    with pytest.raises(ValueError, match="entropy scope"):
        module.read_inputs(expected_digest=digest, path=path)


@pytest.mark.parametrize("ordinal", (-1, 1, True, 0.0))
def test_sample_lookups_reject_aliases(ordinal, tmp_path, monkeypatch):
    monkeypatch.setattr(module.os, "getrandom", lambda n: b"\x00"*n)
    record = module.create_inputs(count=1, bytes_per_stream=1, path=tmp_path / "receipt.json")
    for lookup in (module.address, module.sample_identity):
        with pytest.raises(ValueError):
            lookup(record, ordinal)


def test_missing_receipt_is_not_regenerated(tmp_path, monkeypatch):
    monkeypatch.setattr(module.os, "getrandom", lambda n: pytest.fail("unexpected new bits"))
    with pytest.raises(FileNotFoundError):
        module.read_inputs(expected_digest="0"*64, path=tmp_path / "missing.json")


def test_saved_receipt_is_canonical_json(tmp_path, monkeypatch):
    monkeypatch.setattr(module.os, "getrandom", lambda n: b"\xab"*n)
    path = tmp_path / "receipt.json"
    record = module.create_inputs(count=1, bytes_per_stream=1, path=path)
    assert json.loads(path.read_bytes()) == record
    assert path.read_bytes() == module._canonical(record) + b"\n"
