"""Test the frozen contract and finite search boundary for the new carrier.

Owns:
    Identity separation, target constraints, ordered tier locks, determinant
    cancellation, and content-addressed frontier-artifact integrity.

Depends on:
    The research computable-carrier specification, search, artifact, JSON, and
    exact production Schoen/Serre checks.

Must not:
    Treat a descriptor as a selected bundle, import observations, or validate
    the published reference carrier as the new candidate.

Phase 0:
    Contract and finite-category tests only; downstream construction remains
    unpromoted until its explicit gates pass.
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from research.experiments.computable_carrier.artifact import write_artifact
from research.experiments.computable_carrier.search import finite_tier_search
from research.experiments.computable_carrier.specification import (
    computable_carrier_specification,
)


def test_computable_carrier_contract_is_distinct_and_selection_safe() -> None:
    """The new target remains separate from the published benchmark."""

    specification = computable_carrier_specification()

    assert specification.identifier != specification.reference_carrier_identifier
    assert specification.geometry_identifier == "Schoen quotient"
    assert specification.rank == 4
    assert specification.first_chern_class == (0, 0, 0)
    assert specification.structure_group == "SU(4)"
    assert specification.selection_constraints_are_not_predictions
    assert "measured masses" in specification.forbidden_inputs
    assert tuple(tier.name for tier in specification.tiers) == (
        "Tier A",
        "Tier B",
        "Tier C",
    )


def test_finite_search_keeps_later_tiers_locked() -> None:
    """Tier B and Tier C descriptors cannot silently become active."""

    report = finite_tier_search()

    assert len(report.tier_a) == 1
    assert report.tier_a[0].left_scheme == "I3"
    assert report.tier_a[0].right_scheme == "I6"
    assert not report.tier_a[0].is_constructed
    assert report.tier_b
    assert all(candidate.status == "locked" for candidate in report.tier_b)
    assert report.tier_c == ()
    assert report.tier_b_locked
    assert report.tier_c_locked


def test_computable_carrier_artifact_digest_and_promotion_gate() -> None:
    """The generated frontier artifact is reproducible and unpromoted."""

    root = Path(__file__).resolve().parents[2]
    path = root / "data/generated/computable_carrier/computable_carrier_artifact.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    digest = artifact.pop("artifact_digest")
    canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    assert sha256(canonical.encode("utf-8")).hexdigest() == digest
    assert artifact["identity"]["identity_or_isomorphism_proved"] is False
    assert artifact["construction"]["selected_candidate"] is None
    assert artifact["promotion"]["production_import_allowed"] is False
    assert write_artifact(root) == {**artifact, "artifact_digest": digest}
