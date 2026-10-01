"""Test complete bounded-output encoding without confusing scope with physics.

Owns:
    Original index/parameter ordering, rational-radius validation, truncated
    archive rejection, and preservation of different existing scientific files.

Depends on:
    Actual predecessor section probes, the independent streaming validator,
    and pytest temporary paths used only for encoding/error-path tests.

Must not:
    Present parser fixtures as computed sections, replace full-matrix execution
    by mocked counts, or infer sampling, metrics, or physical predictions.

Phase 0:
    Research archive tests; completed scientific output needs separate evidence.
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
