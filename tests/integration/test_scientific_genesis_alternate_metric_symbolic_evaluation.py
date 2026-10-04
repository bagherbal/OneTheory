"""Verify complete original polynomial consumption and fixed-domain provenance.

Owns:
    Explicit domain identity, unavailable-input rejection and preservation of
    the distinction between original section identity and numerical output.

Depends on:
    Trusted complete polynomial execution, original actual cover frames,
    existing bounded arithmetic and independently verified output streams.

Must not:
    Infer complete execution from declared scope metadata, import observations,
    treat arithmetic probes as an IID cloud or claim converged physical metrics.

Phase 0:
    Research execution verification; physical normalization remains unresolved.
"""

import pytest

from research.experiments.scientific_genesis import alternate_metric_symbolic_evaluation as module


def test_declared_scope_is_not_proof_of_execution_or_a_physical_metric():
    name, branch, frame = module.domains.declared_frames()[0]
    assert name == "A" and branch == (0, 0)
    scope = module._scope("explicit provenance argument; not an execution digest", frame)
    assert scope["fiber_basis_labels"] == list(frame.basis_labels)
    assert scope["parameter_order"] == ["constant", "a0", "a1"]
    assert scope["domain_role"] == "predeclared coupled-input regression; not an independent draw"
    # A scope declaration supplies no content digest or actual output count.
    assert "artifact_digest" not in scope
    assert "section_count" not in scope
    assert "complete_original_basis_evaluated" not in scope
    assert scope["original_section_basis_digest"] == (
        module.symbolic.section_basis_identity()["artifact_digest"])
    for flag in ("point_dependent_stream_is_global_section_identity", "all_15_domains_executed",
                 "independent_all_column_cochain_replay",
                 "practical_multi_point_throughput_certified",
                 "independent_cloud_available", "controlled_integral_available",
                 "ricci_flat_or_hym_metric_available", "physical_yukawas_available",
                 "common_stabilized_vacuum_available", "extension_point_selected",
                 "centers_are_exact_cover_points", "observations_used"):
        assert scope[flag] is False


def test_other_actual_domains_cannot_be_silently_mislabeled():
    for _, _, frame in (module.domains.declared_frames()[1], module.domains.declared_frames()[9]):
        with pytest.raises(ValueError, match="predeclared A"):
            module._scope("nonpublication scope probe", frame)
    with pytest.raises(TypeError, match="actual original"):
        module._scope("nonpublication scope probe", object())


def test_unavailable_compilation_never_installs_a_numerical_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(module.symbolic, "OUTPUT", tmp_path / "unavailable-compilation.json")
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "unavailable-evaluation.json")
    monkeypatch.setattr(module, "MATRIX", tmp_path / "unavailable-evaluation.columns.gz")
    with pytest.raises(FileNotFoundError):
        module.write_complete_domain(expected_compilation_digest="0" * 64)
    assert not module.OUTPUT.exists()
    assert not module.MATRIX.exists()
