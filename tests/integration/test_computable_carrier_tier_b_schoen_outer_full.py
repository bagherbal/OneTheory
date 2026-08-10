"""Test the declared full Tier B Schoen-cover pair category and artifact.

Owns:
    Deterministic pair enumeration, finalized sparse cover-Hom artifact
    integrity, checkpoint agreement, exact dimension regressions, and the
    memory-bounded invariant-screen task ledger.

Depends on:
    The research-only Tier B topology and Serre-eigenray enumerators.

Must not:
    Treat pair enumeration as an Ext calculation, infer quotient invariants,
    or promote the declared category into a physical carrier.

Phase 0:
    The exhaustive sparse cover evaluation is exact; one quotient cocycle
    prototype exists while the full invariant and rank-four gates remain open.
"""

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _pending_order,
    _validated_cover_dimensions,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    declared_schoen_outer_candidate_data,
    declared_schoen_outer_pairs,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_invariants import (
    declared_schoen_invariant_pair_tasks,
)

ARTIFACT_PATH = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_full.json"
)
CHECKPOINT_PATH = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_full.partial.json"
)
INVARIANT_CHECKPOINT_PATH = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_invariants.partial.json"
)
EXPECTED_EXT_DISTRIBUTION = {
    0: 360,
    36: 72,
    54: 36,
    72: 72,
    90: 108,
    162: 72,
    198: 36,
    216: 108,
    270: 36,
    324: 36,
    342: 36,
    360: 36,
    378: 36,
    432: 36,
    450: 36,
    468: 36,
    594: 72,
    918: 36,
    972: 36,
    990: 36,
    1044: 36,
    1134: 72,
}


def test_declared_outer_pair_category_has_1440_pairs() -> None:
    """Every candidate is paired with the six-by-six length-six rays."""

    pairs = declared_schoen_outer_pairs()

    assert len(pairs) == 1440
    counts = Counter(pair[0] for pair in pairs)
    assert len(counts) == 40
    assert set(counts.values()) == {36}


def test_candidate_tasks_are_memory_bounded_by_topology() -> None:
    """Each worker receives one candidate with six rays on each side."""

    tasks = declared_schoen_outer_candidate_data()

    assert len(tasks) == 40
    assert all(len(task[2]) == 6 and len(task[3]) == 6 for task in tasks)


def test_full_cover_artifact_is_content_addressed_and_checkpointed() -> None:
    """The final payload matches its digest and complete checkpoint ledger."""

    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    digest = artifact.pop("artifact_digest")

    assert artifact.pop("content_addressed") is True
    assert artifact.pop("digest_algorithm") == "sha256"
    canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":"))
    assert sha256(canonical.encode("utf-8")).hexdigest() == digest

    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    assert checkpoint["completed_candidate_count"] == 40
    checkpoint_audits = [
        audit
        for candidate_index in range(1, 41)
        for audit in checkpoint["completed_candidates"][str(candidate_index)]
    ]
    assert checkpoint_audits == artifact["audits"]


def test_full_cover_artifact_matches_every_declared_pair() -> None:
    """All 1,440 records retain their exact declared ray identities."""

    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    pairs = declared_schoen_outer_pairs()

    assert artifact["screened_count"] == len(pairs) == 1440
    assert artifact["declared_topology_count"] == 40
    assert artifact["declared_presentation_pair_count"] == 1440
    assert artifact["complete_for_declared_category"] is True
    assert artifact["cover_level_only"] is True
    assert artifact["quotient_invariant_ext_computed"] is False
    assert artifact["outer_extension_constructed"] is False
    assert artifact["promotion_ready"] is False
    for audit, pair in zip(artifact["audits"], pairs, strict=True):
        candidate_index, _, left_ray, right_ray = pair
        assert audit["candidate_index"] == candidate_index
        assert audit["left_scheme"] == left_ray.cokernel.scheme.name
        assert audit["left_character_pair"] == [
            str(value) for value in left_ray.character_pair
        ]
        assert audit["right_scheme"] == right_ray.cokernel.scheme.name
        assert audit["right_character_pair"] == [
            str(value) for value in right_ray.character_pair
        ]


def test_full_cover_artifact_records_exact_ext_distribution() -> None:
    """Every cover differential closes with the frozen Ext-one dimensions."""

    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    audits = artifact["audits"]

    assert artifact["exact"] is True
    assert artifact["all_zero"] is False
    assert all(audit["exact"] and audit["squared_zero"] for audit in audits)
    assert Counter(
        audit["cover_ext_one_dimension"] for audit in audits
    ) == EXPECTED_EXT_DISTRIBUTION


def test_invariant_screen_reuses_certified_cover_dimensions_serially() -> None:
    """Every quotient task binds one verified cover result by exact identity."""

    digest, dimensions = _validated_cover_dimensions(ARTIFACT_PATH)
    tasks = declared_schoen_invariant_pair_tasks(dimensions)
    first_pending = min(tasks, key=_pending_order)

    assert len(digest) == 64
    assert len(tasks) == 1440
    assert [task[0] for task in tasks] == list(range(1, 1441))
    assert all(task[1] == (task[0] - 1) % 36 + 1 for task in tasks)
    assert first_pending[0:3] == (73, 1, 3)
    assert first_pending[-1] == 36


def test_first_invariant_candidate_is_compact_and_content_addressed() -> None:
    """Candidate 3 persists all cocycles without recursive basis-label bloat."""

    checkpoint = json.loads(INVARIANT_CHECKPOINT_PATH.read_text(encoding="utf-8"))
    records = [
        checkpoint["completed_pairs"][str(index)]
        for index in range(73, 109)
    ]

    assert checkpoint["schema"] == "tier-b-schoen-invariant-outer-v2"
    assert checkpoint["declared_pair_count"] == 1440
    assert checkpoint["completed_pair_count"] == 36
    assert all(record["candidate_index"] == 3 for record in records)
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 36
        for record in records
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 4
        for record in records
    )
    assert all(record["cocycle_basis"]["dimension"] == 4 for record in records)
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 540
        for record in records
    )
    assert all(
        [
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        ]
        == [12, 12, 12, 12]
        for record in records
    )
    assert all(
        "basis_coordinate" in term and "basis_label" not in term
        for record in records
        for representative in record["cocycle_basis"]["representatives"]
        for term in representative["terms"]
    )
    for record in records:
        payload = dict(record)
        digest = payload.pop("certificate_digest")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        assert sha256(canonical.encode("utf-8")).hexdigest() == digest
        assert payload["exact"] is True
