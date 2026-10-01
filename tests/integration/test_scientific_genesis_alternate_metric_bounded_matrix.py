"""Test complete bounded-output encoding without confusing scope with physics.

Owns:
    Original index/parameter ordering, rational-radius validation, truncated
    archive rejection, actual completed execution checks, and preservation of
    different existing scientific files.

Depends on:
    Actual predecessor section probes, the independent streaming validator,
    and pytest temporary paths used only for encoding/error-path tests.

Must not:
    Present parser fixtures as computed sections, replace full-matrix execution
    by mocked counts, treat metadata-only scope contracts as actual completed
    artifacts, or infer sampling, metrics, or physical predictions.

Phase 0:
    Research archive tests; single-domain completion does not establish metrics.
"""

import copy
import gzip
import json

import pytest

from research.experiments.scientific_genesis import alternate_metric_bounded_matrix as matrix


def _probe(index=0):
    parent = json.loads(matrix.support.OUTPUT.read_text())
    return copy.deepcopy(next(p for p in parent["actual_frame_probes"][0][
        "actual_universal_section_probes"
    ] if p["basis_index"] == index))


def test_actual_probe_columns_have_explicit_identity_and_outward_precision():
    for index in (0, 1273, 2655):
        n, radius = matrix._validate_column(_probe(index), index, 80)
        assert n > 0 and radius > 0
    with pytest.raises(ValueError, match="ordering"):
        matrix._validate_column(_probe(), 1, 80)
    bad = _probe()
    bad["basis_index"] = False
    with pytest.raises(ValueError, match="integer"):
        matrix._validate_column(bad, 0, 80)


@pytest.mark.parametrize("kind,error", (
    ("parameter", "constant/a0/a1"), ("shape", "four named"),
    ("radius", "nonnegative"), ("mesh", "outward mesh"),
    ("coordinate", "center pairs"), ("false_extension", "injected V1"),
))
def test_malformed_or_misassigned_probe_columns_fail_closed(kind, error):
    bad = _probe()
    coefficients = bad["coefficient_columns_constant_a0_a1"]
    if kind == "parameter":
        coefficients.pop()
    elif kind == "shape":
        coefficients[0].pop()
    elif kind == "radius":
        coefficients[0][0][0]["radius"] = "-1"
    elif kind == "mesh":
        coefficients[0][0][0]["radius"] = "1/3"
    elif kind == "coordinate":
        coefficients[0][0][0]["center"] = [0, 0]
    else:
        coefficients[1][0][0]["center"] = ["1", "0"]
    with pytest.raises(ValueError, match=error):
        matrix._validate_column(bad, 0, 80)


def test_truncation_and_noncanonical_encoding_cannot_pass_archive_validation(tmp_path):
    path = tmp_path / "actual_probe_only.jsonl.gz"
    probe = _probe()
    with gzip.open(path, "wb") as stream:
        stream.write(matrix._canonical(probe) + b"\n")
    with pytest.raises(ValueError, match="all 5345"):
        matrix.verify_archive(path, bits=80)
    with gzip.open(path, "wb") as stream:
        stream.write(json.dumps(probe, indent=2).encode() + b"\n")
    # A malformed JSON-line record is rejected, never reconstructed by a fallback.
    with pytest.raises(ValueError):
        matrix.verify_archive(path, bits=80)


def test_installation_preserves_existing_different_scientific_output(tmp_path):
    original = tmp_path / "original"
    incoming = tmp_path / "incoming"
    original.write_bytes(b"original scientific bytes")
    incoming.write_bytes(b"different scientific bytes")
    with pytest.raises(ValueError, match="refusing to overwrite"):
        matrix._install_unchanged_or_new(incoming, original)
    assert original.read_bytes() == b"original scientific bytes"
    destination = tmp_path / "new_output"
    matrix._install_unchanged_or_new(incoming, destination)
    assert destination.read_bytes() == b"different scientific bytes"
    same = tmp_path / "identical"
    same.write_bytes(destination.read_bytes())
    matrix._install_unchanged_or_new(same, destination)
    assert same.exists()


def test_unknown_configuration_is_not_replaced_by_a_regression_domain():
    with pytest.raises(ValueError, match="explicitly named"):
        matrix.declared_frame("not a certified configuration")


def test_scratch_files_do_not_create_domains_or_leave_partial_output(tmp_path, monkeypatch):
    monkeypatch.setattr(matrix, "OUTPUT", tmp_path / "matrix.json")
    with matrix._scratch_files() as (temporary, metadata):
        assert temporary.parent == metadata.parent == tmp_path
        assert temporary.is_file() and not metadata.exists()
        metadata.write_bytes(b"unfinished metadata")
        assert not any(p.is_dir() for p in tmp_path.iterdir())
    assert not temporary.exists() and not metadata.exists()
    with pytest.raises(RuntimeError, match="execution failure"):
        with matrix._scratch_files() as (temporary, metadata):
            temporary.write_bytes(b"uncertified partial stream")
            raise RuntimeError("execution failure")
    assert not temporary.exists() and not metadata.exists()


def _scope_contract():
    digest, parent = matrix.fiber._verified_payload(matrix.support.OUTPUT)
    root_digest, _roots = matrix.fiber._verified_payload(matrix.bounds.roots.OUTPUT)
    return matrix._scope_fields(digest, parent, root_digest)


@pytest.mark.parametrize("field", (
    "independent_all_column_full_cochain_replay_performed",
    "practical_multi_point_integration_throughput_certified",
    "controlled_numerical_sampling_available", "numerical_metrics_available",
    "physical_yukawas_available", "centers_are_exact_cover_points",
    "extension_point_selected", "vacuum_selected", "observational_inputs_used",
))
def test_metadata_contract_cannot_inflate_single_domain_scientific_scope(field):
    required = _scope_contract()
    record = dict(required)
    record[field] = True
    # These are descriptive metadata contracts, not output packets or matrices.
    with pytest.raises(ValueError, match=f"scientific scope is incompatible: {field}"):
        matrix._require_scope(record, required)


@pytest.mark.parametrize("field,value", (
    ("root_pair", [0, 1]), ("chart_pivots", [False, 0, 0]),
    ("first_pivot_rows", [2, 0]), ("parameter_basis", ["a1", "a0"]),
    ("section_count", 5345.0), ("single_certified_local_domain_only", 1),
    ("numerical_metrics_available", 0),
))
def test_metadata_contract_rejects_changed_domain_and_numeric_type_aliases(field, value):
    required = _scope_contract()
    record = dict(required)
    record[field] = value
    with pytest.raises(ValueError, match=f"scientific scope is incompatible: {field}"):
        matrix._require_scope(record, required)


def test_consumer_requires_the_explicit_trusted_completed_execution_digest(tmp_path, monkeypatch):
    record = _scope_contract()
    digest = matrix.hashlib.sha256(matrix._canonical(record)).hexdigest()
    record["artifact_digest"] = digest
    meta = tmp_path / "metadata_only_not_a_completed_output.json"
    meta.write_text(json.dumps(record))
    monkeypatch.setattr(matrix, "OUTPUT", meta)
    with pytest.raises(ValueError, match="trusted execution digest"):
        matrix.verify_completed_output(expected_digest="0" * 64)


def test_metadata_hash_cannot_replace_missing_completed_archive(tmp_path, monkeypatch):
    monkeypatch.setattr(matrix, "MATRIX", tmp_path / "missing.columns.jsonl.gz")
    monkeypatch.setattr(matrix.fiber.lifts.first, "ROOT", tmp_path)
    record = _scope_contract()
    record["matrix_archive_sha256"] = "0" * 64
    record["matrix_archive_bytes"] = 0
    digest = matrix.hashlib.sha256(matrix._canonical(record)).hexdigest()
    record["artifact_digest"] = digest
    meta = tmp_path / "metadata_only_not_a_completed_output.json"
    meta.write_text(json.dumps(record))
    monkeypatch.setattr(matrix, "OUTPUT", meta)
    with pytest.raises(FileNotFoundError):
        matrix.verify_completed_output(expected_digest=digest)


def test_actual_completed_execution_has_all_original_columns_and_parent_probes():
    verified = matrix.verify_completed_output(
        expected_digest="88cc1d553baa2a00a8f9c105d1ecab52d18d9c9a3e73042b617161253e09688a",
    )
    assert verified["matrix_archive_sha256"] == (
        "3f0b600967c9b61d060c2c5d13f51d8b6e5e549bf50600ca6cd813d387e9afce"
    )
    assert verified["exact_column_stream_sha256"] == (
        "88bc48fda6bdaed2368ece1f8394920a68bed0e04d318a0a5cbd7e0a6d57b53d"
    )
    assert verified["section_count"] == 5345
    assert verified["coefficient_entry_count"] == 64140
    assert verified["uncertain_entry_count"] == 21430
    assert verified["original_probe_indices_checked"] == [0, 1273, 2655]
    assert verified["single_certified_local_domain_only"] is True
    assert verified["numerical_metrics_available"] is False
    assert verified["physical_yukawas_available"] is False
