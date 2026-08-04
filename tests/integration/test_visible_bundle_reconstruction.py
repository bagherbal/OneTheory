"""Verify the deterministic visible-carrier reconstruction artifact.

Owns:
    Content-address validation, exact point-scheme resolution fields, and the
    fail-closed outcome recorded after primary-source inspection.

Depends on:
    The research reconstruction reproducer, JSON, SHA-256, and repository data.

Must not:
    Treat unresolved cocycles, section matrices, or conic maps as physical
    fixtures, or promote research output into production imports.

Phase 0:
    The test verifies the source-backed boundary artifact only.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from research.experiments.visible_bundle_reconstruction.reconstruct import write_artifact


def test_visible_carrier_artifact_is_content_addressed() -> None:
    """The checked-in JSON must reproduce its declared canonical digest."""

    root = Path(__file__).resolve().parents[2]
    path = root / "data/generated/visible_carrier/visible_carrier_artifact.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    digest = artifact.pop("artifact_digest")
    canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    assert sha256(canonical.encode("utf-8")).hexdigest() == digest
    assert write_artifact(root) == {**artifact, "artifact_digest": digest}


def test_visible_carrier_artifact_preserves_the_unresolved_boundary() -> None:
    """Published dimensions do not unlock absent chain representatives."""

    root = Path(__file__).resolve().parents[2]
    artifact = write_artifact(root)

    assert artifact["schema"]["name"] == "VisibleCarrierArtifact"
    assert artifact["outcome"]["code"] == 3
    assert artifact["outer_extension"]["invariant_ext1_dimension"] == 4
    assert artifact["outer_extension"]["representatives"] == []
    assert artifact["positive_twist"]["certified"] is False
    assert artifact["conic_seeds"]["pfaffian_representatives"] == []
