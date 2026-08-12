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
    The exhaustive sparse cover and invariant cocycle evaluations are exact;
    automorphism-orbit and rank-four construction gates remain open.
"""

import gc
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path

from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _pending_order,
    _validated_cover_dimensions,
    _write_atomic,
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
INVARIANT_ARTIFACT_PATH = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_invariants.json"
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


def test_invariant_checkpoint_streaming_preserves_exact_json(tmp_path: Path) -> None:
    """Streaming writes retain the canonical pretty-printed checkpoint bytes."""

    path = tmp_path / "checkpoint.json"
    payload = {"zeta": ["ω", 3], "alpha": {"exact": True}}

    _write_atomic(path, payload)

    assert path.read_text(encoding="utf-8") == (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    assert not path.with_name(f".{path.name}.tmp").exists()


def test_full_invariant_artifact_is_content_addressed_and_checkpointed() -> None:
    """The final invariant payload agrees with every checkpoint certificate."""

    checkpoint = json.loads(INVARIANT_CHECKPOINT_PATH.read_text(encoding="utf-8"))
    checkpoint_digests = [
        checkpoint["completed_pairs"][str(index)]["certificate_digest"]
        for index in range(1, 1441)
    ]
    assert checkpoint["completed_pair_count"] == 1440
    del checkpoint
    gc.collect()

    artifact = json.loads(INVARIANT_ARTIFACT_PATH.read_text(encoding="utf-8"))
    digest = artifact.pop("artifact_digest")

    assert artifact.pop("content_addressed") is True
    assert artifact.pop("digest_algorithm") == "sha256"
    canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":"))
    assert sha256(canonical.encode("utf-8")).hexdigest() == digest

    audits = artifact["audits"]
    assert [record["certificate_digest"] for record in audits] == checkpoint_digests
    assert artifact["schema"] == "tier-b-schoen-invariant-outer-v2"
    assert artifact["screened_count"] == artifact["declared_pair_count"] == 1440
    assert artifact["complete_for_declared_category"] is True
    assert artifact["exact"] is True
    assert artifact["automorphism_actions_computed"] is False
    assert artifact["canonical_orbits_computed"] is False
    assert artifact["outer_extensions_constructed"] is False
    assert artifact["promotion_ready"] is False
    assert Counter(record["candidate_index"] for record in audits) == {
        index: 36 for index in range(1, 41)
    }
    assert Counter(
        record["invariant_subcomplex"]["cover_ext_one_dimension"]
        for record in audits
    ) == EXPECTED_EXT_DISTRIBUTION


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


def test_computed_invariant_frontiers_are_compact_and_content_addressed() -> None:
    """Completed low-dimensional cover frontiers persist compact exact cocycles."""

    checkpoint = json.loads(INVARIANT_CHECKPOINT_PATH.read_text(encoding="utf-8"))
    records = [
        checkpoint["completed_pairs"][str(index)]
        for indices in (range(73, 109), range(793, 829))
        for index in indices
    ]
    completed_records = list(checkpoint["completed_pairs"].values())
    dimension_54 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 54
    ]
    dimension_72 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 72
    ]
    dimension_90 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 90
    ]
    dimension_162 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 162
    ]
    dimension_198 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 198
    ]
    dimension_216 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 216
    ]
    dimension_270 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 270
    ]
    dimension_324 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 324
    ]
    dimension_342 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 342
    ]
    dimension_360 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 360
    ]
    dimension_378 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 378
    ]
    dimension_432 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 432
    ]
    dimension_450 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 450
    ]
    dimension_468 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 468
    ]
    dimension_594 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 594
    ]
    dimension_918 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 918
    ]
    dimension_972 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 972
    ]
    dimension_990 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 990
    ]
    dimension_1044 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 1044
    ]
    dimension_1134 = [
        record
        for record in completed_records
        if record["invariant_subcomplex"]["cover_ext_one_dimension"] == 1134
    ]
    zero_candidate_1 = [
        checkpoint["completed_pairs"][str(index)] for index in range(1, 37)
    ]
    zero_candidate_2 = [
        checkpoint["completed_pairs"][str(index)] for index in range(37, 73)
    ]
    zero_candidate_11 = [
        checkpoint["completed_pairs"][str(index)] for index in range(361, 397)
    ]
    zero_candidate_12 = [
        checkpoint["completed_pairs"][str(index)] for index in range(397, 433)
    ]
    zero_candidate_13 = [
        checkpoint["completed_pairs"][str(index)] for index in range(433, 469)
    ]
    zero_candidate_21 = [
        checkpoint["completed_pairs"][str(index)] for index in range(721, 757)
    ]
    zero_candidate_22 = [
        checkpoint["completed_pairs"][str(index)] for index in range(757, 793)
    ]
    zero_candidate_31 = [
        checkpoint["completed_pairs"][str(index)] for index in range(1081, 1117)
    ]
    zero_candidate_32 = [
        checkpoint["completed_pairs"][str(index)] for index in range(1117, 1153)
    ]
    zero_candidate_33 = [
        checkpoint["completed_pairs"][str(index)] for index in range(1153, 1189)
    ]

    assert checkpoint["schema"] == "tier-b-schoen-invariant-outer-v2"
    assert checkpoint["declared_pair_count"] == 1440
    assert checkpoint["completed_pair_count"] == 1440
    assert all(record["candidate_index"] == 1 for record in zero_candidate_1)
    assert [record["candidate_pair_index"] for record in zero_candidate_1] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_1
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_1
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 300], [2, 1266], [3, 922], [4, 40]]
        for record in zero_candidate_1
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 2700
        for record in zero_candidate_1
    )
    assert all(record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_1)
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_1
    )
    assert all(record["candidate_index"] == 2 for record in zero_candidate_2)
    assert [record["candidate_pair_index"] for record in zero_candidate_2] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_2
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_2
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 180], [2, 706], [3, 506], [4, 24]]
        for record in zero_candidate_2
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 1620
        for record in zero_candidate_2
    )
    assert all(record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_2)
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_2
    )
    assert all(record["candidate_index"] == 11 for record in zero_candidate_11)
    assert [record["candidate_pair_index"] for record in zero_candidate_11] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_11
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_11
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 0], [2, 1094], [3, 1362], [4, 40]]
        for record in zero_candidate_11
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 0
        for record in zero_candidate_11
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_11
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_11
    )
    assert all(record["candidate_index"] == 12 for record in zero_candidate_12)
    assert [record["candidate_pair_index"] for record in zero_candidate_12] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_12
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_12
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 0], [2, 650], [3, 806], [4, 24]]
        for record in zero_candidate_12
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 0
        for record in zero_candidate_12
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_12
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_12
    )
    assert all(record["candidate_index"] == 13 for record in zero_candidate_13)
    assert [record["candidate_pair_index"] for record in zero_candidate_13] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_13
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_13
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 0], [2, 206], [3, 250], [4, 8]]
        for record in zero_candidate_13
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 0
        for record in zero_candidate_13
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_13
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_13
    )
    assert all(record["candidate_index"] == 21 for record in zero_candidate_21)
    assert [record["candidate_pair_index"] for record in zero_candidate_21] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_21
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_21
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 300], [2, 1266], [3, 922], [4, 40]]
        for record in zero_candidate_21
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 2700
        for record in zero_candidate_21
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_21
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_21
    )
    assert all(record["candidate_index"] == 22 for record in zero_candidate_22)
    assert [record["candidate_pair_index"] for record in zero_candidate_22] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_22
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_22
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 180], [2, 706], [3, 506], [4, 24]]
        for record in zero_candidate_22
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 1620
        for record in zero_candidate_22
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_22
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_22
    )
    assert all(record["candidate_index"] == 31 for record in zero_candidate_31)
    assert [record["candidate_pair_index"] for record in zero_candidate_31] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_31
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_31
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 0], [2, 1094], [3, 1362], [4, 40]]
        for record in zero_candidate_31
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 0
        for record in zero_candidate_31
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_31
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_31
    )
    assert all(record["candidate_index"] == 32 for record in zero_candidate_32)
    assert [record["candidate_pair_index"] for record in zero_candidate_32] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_32
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_32
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 0], [2, 650], [3, 806], [4, 24]]
        for record in zero_candidate_32
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 0
        for record in zero_candidate_32
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_32
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_32
    )
    assert all(record["candidate_index"] == 33 for record in zero_candidate_33)
    assert [record["candidate_pair_index"] for record in zero_candidate_33] == list(
        range(1, 37),
    )
    assert all(
        record["invariant_subcomplex"]["cover_ext_one_dimension"] == 0
        for record in zero_candidate_33
    )
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
        for record in zero_candidate_33
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 0], [1, 0], [2, 206], [3, 250], [4, 8]]
        for record in zero_candidate_33
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 0
        for record in zero_candidate_33
    )
    assert all(
        record["cocycle_basis"]["dimension"] == 0 for record in zero_candidate_33
    )
    assert all(
        record["cocycle_basis"]["representatives"] == []
        for record in zero_candidate_33
    )
    assert Counter(record["candidate_index"] for record in records) == {
        3: 36,
        23: 36,
    }
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
    for record in completed_records:
        payload = dict(record)
        digest = payload.pop("certificate_digest")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        assert sha256(canonical.encode("utf-8")).hexdigest() == digest
        assert payload["exact"] is True
    assert len(dimension_54) == 36
    assert Counter(record["candidate_index"] for record in dimension_54) == {
        14: 18,
        34: 18,
    }
    assert {
        record["candidate_pair_index"]
        for record in dimension_54
        if record["candidate_index"] == 14
    } == {4, 5, 6, 10, 11, 12, 16, 17, 18, 19, 20, 21, 25, 26, 27, 31, 32, 33}
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 6
        for record in dimension_54
    )
    assert len(dimension_72) == 72
    assert Counter(record["candidate_index"] for record in dimension_72) == {
        8: 18,
        14: 18,
        28: 18,
        34: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 8
        for record in dimension_72
    )
    assert Counter(
        record["cocycle_basis"]["ambient_basis"]["dimension"]
        for record in dimension_72
    ) == {1854: 36, 2142: 36}
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_72
    ) == {
        (3, 3, 3, 3, 3, 3, 3, 3): 36,
        (3, 3, 3, 3, 6, 6, 9, 9): 36,
    }
    assert len(dimension_90) == 108
    assert Counter(record["candidate_index"] for record in dimension_90) == {
        8: 18,
        18: 36,
        28: 18,
        38: 36,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 10
        for record in dimension_90
    )
    assert Counter(
        record["cocycle_basis"]["ambient_basis"]["dimension"]
        for record in dimension_90
    ) == {1314: 72, 1854: 36}
    assert all(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        == (3, 3, 3, 3, 3, 3, 3, 3, 3, 3)
        for record in dimension_90
    )
    assert len(dimension_162) == 72
    assert Counter(record["candidate_index"] for record in dimension_162) == {
        9: 18,
        15: 18,
        29: 18,
        35: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 18
        for record in dimension_162
    )
    assert Counter(
        tuple(
            tuple(item)
            for item in record["invariant_subcomplex"][
                "invariant_cochain_dimensions"
            ]
        )
        for record in dimension_162
    ) == {
        ((-1, 24), (0, 806), (1, 650), (2, 0), (3, 0), (4, 0)): 36,
        ((-1, 0), (0, 0), (1, 682), (2, 1222), (3, 448), (4, 0)): 36,
    }
    assert Counter(
        record["cocycle_basis"]["ambient_basis"]["dimension"]
        for record in dimension_162
    ) == {5850: 36, 6138: 36}
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_162
    ) == {
        (3,) * 18: 36,
        (3,) * 12 + (6,) * 6: 36,
    }
    assert len(dimension_198) == 36
    assert Counter(record["candidate_index"] for record in dimension_198) == {
        17: 18,
        37: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 22
        for record in dimension_198
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 24], [1, 350], [2, 414], [3, 60], [4, 0]]
        for record in dimension_198
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 3150
        for record in dimension_198
    )
    assert all(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        == (3,) * 16 + (12,) * 2 + (21,) * 4
        for record in dimension_198
    )
    assert len(dimension_216) == 108
    assert Counter(record["candidate_index"] for record in dimension_216) == {
        9: 18,
        15: 18,
        17: 18,
        29: 18,
        35: 18,
        37: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 24
        for record in dimension_216
    )
    assert Counter(
        tuple(
            tuple(item)
            for item in record["invariant_subcomplex"][
                "invariant_cochain_dimensions"
            ]
        )
        for record in dimension_216
    ) == {
        ((-1, 24), (0, 806), (1, 650), (2, 0), (3, 0), (4, 0)): 36,
        ((-1, 0), (0, 0), (1, 682), (2, 1222), (3, 448), (4, 0)): 36,
        ((-1, 0), (0, 24), (1, 350), (2, 414), (3, 60), (4, 0)): 36,
    }
    assert Counter(
        record["cocycle_basis"]["ambient_basis"]["dimension"]
        for record in dimension_216
    ) == {3150: 36, 5850: 36, 6138: 36}
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_216
    ) == {
        (3,) * 24: 36,
        (3,) * 12 + (6,) * 6 + (9,) * 6: 36,
        (3,) * 16 + (12,) * 2 + (48, 54, 21, 21, 48, 57): 9,
        (3,) * 16 + (12,) * 2 + (48, 54, 21, 21, 51, 57): 9,
        (3,) * 16 + (12,) * 2 + (48, 48, 21, 21, 51, 51): 9,
        (3,) * 16 + (12,) * 2 + (54, 54, 21, 21, 57, 57): 9,
    }
    assert len(dimension_270) == 36
    assert Counter(record["candidate_index"] for record in dimension_270) == {
        10: 18,
        30: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 30
        for record in dimension_270
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 40], [0, 1362], [1, 1094], [2, 0], [3, 0], [4, 0]]
        for record in dimension_270
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 9846
        for record in dimension_270
    )
    assert all(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        == (3,) * 30
        for record in dimension_270
    )
    assert len(dimension_324) == 36
    assert Counter(record["candidate_index"] for record in dimension_324) == {
        7: 18,
        27: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 36
        for record in dimension_324
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 220], [1, 486], [2, 238], [3, 0], [4, 0]]
        for record in dimension_324
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 4374
        for record in dimension_324
    )
    support_prefix_324 = (3,) * 16 + (6,) * 2 + (9,) * 4 + (12,) * 6
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_324
    ) == {
        support_prefix_324 + (18,) * 8: 18,
        support_prefix_324 + (18,) * 5 + (12, 12, 18): 9,
        support_prefix_324 + (18, 18, 12, 18, 18, 12, 12, 18): 9,
    }
    assert len(dimension_342) == 36
    assert Counter(record["candidate_index"] for record in dimension_342) == {
        7: 18,
        27: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 38
        for record in dimension_342
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 220], [1, 486], [2, 238], [3, 0], [4, 0]]
        for record in dimension_342
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 4374
        for record in dimension_342
    )
    support_prefix_342 = (3,) * 16 + (6,) * 2 + (9,) * 4 + (12,) * 6
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_342
    ) == {
        support_prefix_342 + (18,) * 8 + (42,) * 2: 18,
        support_prefix_342
        + (18, 12, 12, 18, 18, 18, 18, 18, 42, 42): 9,
        support_prefix_342
        + (18, 18, 12, 18, 18, 18, 18, 18, 42, 42): 9,
    }
    assert len(dimension_360) == 36
    assert Counter(record["candidate_index"] for record in dimension_360) == {
        10: 18,
        30: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 40
        for record in dimension_360
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 40], [0, 1362], [1, 1094], [2, 0], [3, 0], [4, 0]]
        for record in dimension_360
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 9846
        for record in dimension_360
    )
    assert all(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        == (3,) * 40
        for record in dimension_360
    )
    assert len(dimension_378) == 36
    assert Counter(record["candidate_index"] for record in dimension_378) == {
        16: 18,
        36: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 42
        for record in dimension_378
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 56], [1, 790], [2, 974], [3, 180], [4, 0]]
        for record in dimension_378
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 7110
        for record in dimension_378
    )
    assert all(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        == (3,) * 32 + (12,) * 6 + (57,) * 4
        for record in dimension_378
    )
    assert len(dimension_432) == 36
    assert Counter(record["candidate_index"] for record in dimension_432) == {
        16: 18,
        36: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 48
        for record in dimension_432
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 56], [1, 790], [2, 974], [3, 180], [4, 0]]
        for record in dimension_432
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 7110
        for record in dimension_432
    )
    support_prefix_432 = (3,) * 32 + (12,) * 6
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_432
    ) == {
        support_prefix_432
        + (48, 54, 51, 60, 57, 57, 99, 114, 114, 129): 9,
        support_prefix_432
        + (48, 54, 51, 60, 57, 57, 96, 114, 114, 129): 9,
        support_prefix_432
        + (48, 48, 51, 51, 57, 57, 96, 114, 96, 114): 9,
        support_prefix_432
        + (54, 54, 60, 60, 57, 57, 111, 129, 111, 129): 9,
    }
    assert len(dimension_450) == 36
    assert Counter(record["candidate_index"] for record in dimension_450) == {
        4: 18,
        24: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 50
        for record in dimension_450
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 60], [1, 414], [2, 350], [3, 24], [4, 0]]
        for record in dimension_450
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 3726
        for record in dimension_450
    )
    support_prefix_450 = (3,) * 4 + (6,) * 2 + (12,) * 24
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_450
    ) == {
        support_prefix_450 + (18,) * 12 + (12,) * 8: 18,
        support_prefix_450
        + (
            18,
            18,
            12,
            12,
            12,
            12,
            18,
            18,
            18,
            18,
            18,
            18,
            12,
            12,
            18,
            18,
            12,
            12,
            18,
            18,
        ): 9,
        support_prefix_450
        + (
            18,
            18,
            12,
            12,
            12,
            12,
            18,
            18,
            18,
            18,
            18,
            18,
            12,
            12,
            18,
            18,
            18,
            18,
            12,
            12,
        ): 9,
    }
    assert len(dimension_468) == 36
    assert Counter(record["candidate_index"] for record in dimension_468) == {
        4: 18,
        24: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 52
        for record in dimension_468
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 60], [1, 414], [2, 350], [3, 24], [4, 0]]
        for record in dimension_468
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 3726
        for record in dimension_468
    )
    support_prefix_468 = (3,) * 4 + (6,) * 2 + (9,) * 2 + (12,) * 24
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_468
    ) == {
        support_prefix_468 + (18,) * 12 + (12,) * 8: 18,
        support_prefix_468
        + (
            18,
            18,
            12,
            12,
            18,
            18,
            18,
            18,
            12,
            12,
            18,
            18,
            18,
            18,
            12,
            12,
            12,
            12,
            18,
            18,
        ): 9,
        support_prefix_468
        + (
            18,
            18,
            12,
            12,
            18,
            18,
            18,
            18,
            12,
            12,
            18,
            18,
            12,
            12,
            12,
            12,
            18,
            18,
            18,
            18,
        ): 9,
    }
    assert len(dimension_594) == 72
    assert Counter(record["candidate_index"] for record in dimension_594) == {
        19: 36,
        39: 36,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 66
        for record in dimension_594
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 24], [0, 506], [1, 706], [2, 180], [3, 0], [4, 0]]
        for record in dimension_594
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 6354
        for record in dimension_594
    )
    support_prefix_594 = (3,) * 30 + (9,) * 4
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_594
    ) == {
        support_prefix_594
        + (
            9,
            9,
            9,
            9,
            15,
            15,
            15,
            15,
            15,
            15,
            15,
            15,
            21,
            27,
            21,
            27,
            48,
            48,
            42,
            42,
            45,
            45,
            45,
            45,
            33,
            36,
            33,
            36,
            57,
            60,
            57,
            60,
        ): 18,
        support_prefix_594
        + (
            15,
            15,
            15,
            15,
            9,
            9,
            9,
            9,
            15,
            15,
            15,
            15,
            21,
            27,
            21,
            27,
            48,
            48,
            42,
            42,
            45,
            45,
            45,
            45,
            33,
            36,
            33,
            36,
            54,
            57,
            54,
            57,
        ): 18,
        support_prefix_594
        + (
            9,
            9,
            15,
            15,
            15,
            15,
            21,
            21,
            15,
            15,
            18,
            15,
            24,
            27,
            24,
            27,
            48,
            45,
            39,
            42,
            42,
            54,
            54,
            54,
            54,
            42,
            33,
            36,
            63,
            69,
            45,
            51,
        ): 9,
        support_prefix_594
        + (
            15,
            15,
            18,
            15,
            9,
            9,
            15,
            15,
            21,
            21,
            15,
            15,
            24,
            27,
            24,
            27,
            42,
            33,
            36,
            48,
            45,
            39,
            42,
            42,
            45,
            51,
            54,
            54,
            54,
            54,
            63,
            69,
        ): 9,
        support_prefix_594
        + (
            15,
            15,
            18,
            15,
            15,
            15,
            21,
            21,
            9,
            9,
            15,
            15,
            24,
            27,
            24,
            27,
            42,
            33,
            36,
            39,
            42,
            42,
            48,
            54,
            60,
            63,
            60,
            63,
            63,
            63,
            45,
            51,
        ): 9,
        support_prefix_594
        + (
            15,
            15,
            21,
            21,
            15,
            15,
            9,
            9,
            18,
            15,
            15,
            15,
            24,
            27,
            24,
            27,
            39,
            42,
            42,
            48,
            45,
            42,
            33,
            36,
            54,
            54,
            54,
            54,
            45,
            51,
            60,
            66,
        ): 9,
    }
    assert len(dimension_918) == 36
    assert Counter(record["candidate_index"] for record in dimension_918) == {
        5: 18,
        25: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 102
        for record in dimension_918
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 180], [1, 974], [2, 790], [3, 56], [4, 0]]
        for record in dimension_918
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 8766
        for record in dimension_918
    )
    support_prefix_918 = (3,) * 12 + (6,) * 6 + (12,) * 44 + (18,) * 4
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_918
    ) == {
        support_prefix_918 + (18,) * 20 + (12,) * 16: 18,
        support_prefix_918
        + (12,) * 8
        + (18,) * 12
        + (12,) * 4
        + (18,) * 4
        + (12,) * 4
        + (18,) * 4: 9,
        support_prefix_918
        + (12,) * 8
        + (18,) * 12
        + (12,) * 4
        + (18,) * 8
        + (12,) * 4: 9,
    }
    assert len(dimension_972) == 36
    assert Counter(record["candidate_index"] for record in dimension_972) == {
        5: 18,
        25: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 108
        for record in dimension_972
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 180], [1, 974], [2, 790], [3, 56], [4, 0]]
        for record in dimension_972
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 8766
        for record in dimension_972
    )
    support_prefix_972 = (
        (3,) * 12 + (6,) * 6 + (9,) * 6 + (12,) * 44 + (18,) * 4
    )
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_972
    ) == {
        support_prefix_972 + (18,) * 20 + (12,) * 16: 18,
        support_prefix_972
        + (12,) * 4
        + (18,) * 8
        + (12,) * 4
        + (18,) * 4
        + (12,) * 8
        + (18,) * 8: 9,
        support_prefix_972
        + (12,) * 4
        + (18,) * 8
        + (12,) * 4
        + (18,) * 8
        + (12,) * 8
        + (18,) * 4: 9,
    }
    assert len(dimension_990) == 36
    assert Counter(record["candidate_index"] for record in dimension_990) == {
        6: 18,
        26: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 110
        for record in dimension_990
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 448], [1, 1222], [2, 682], [3, 0], [4, 0]]
        for record in dimension_990
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 10998
        for record in dimension_990
    )
    support_prefix_990 = (3,) * 32
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_990
    ) == {
        support_prefix_990
        + (9,) * 4
        + (12,) * 3
        + (15, 12, 15)
        + (12,) * 32
        + (18,) * 30
        + (12,) * 6: 9,
        support_prefix_990
        + (9,) * 2
        + (12,)
        + (9,) * 2
        + (12,) * 2
        + (15, 12, 15)
        + (12,) * 32
        + (18,) * 6
        + (12,) * 2
        + (18,) * 3
        + (12,) * 4
        + (18,) * 6
        + (12,) * 8
        + (18,) * 5
        + (12,) * 2: 9,
        support_prefix_990
        + (12,)
        + (9,) * 2
        + (12,)
        + (9,) * 2
        + (12, 15, 12, 15)
        + (12,) * 32
        + (18,) * 6
        + (12,) * 7
        + (18,) * 8
        + (12,) * 6
        + (18,) * 3
        + (12,) * 4
        + (18,) * 2: 9,
        support_prefix_990
        + (12,) * 2
        + (9,) * 4
        + (12, 15, 12, 15)
        + (12,) * 32
        + (18,) * 30
        + (12,) * 6: 9,
    }
    assert len(dimension_1044) == 36
    assert Counter(record["candidate_index"] for record in dimension_1044) == {
        6: 18,
        26: 18,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 116
        for record in dimension_1044
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 0], [0, 448], [1, 1222], [2, 682], [3, 0], [4, 0]]
        for record in dimension_1044
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 10998
        for record in dimension_1044
    )
    support_prefix_1044 = (3,) * 32
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_1044
    ) == {
        support_prefix_1044
        + (9,) * 4
        + (12,) * 3
        + (15, 12, 15)
        + (12,) * 32
        + (18,) * 30
        + (12,) * 6
        + (42,) * 6: 9,
        support_prefix_1044
        + (9,) * 2
        + (12,)
        + (9,) * 2
        + (12,) * 2
        + (15, 12, 15)
        + (12,) * 32
        + (18,) * 3
        + (12,) * 6
        + (18,) * 3
        + (12,) * 4
        + (18,) * 11
        + (12,) * 6
        + (18,) * 3
        + (42,) * 6: 9,
        support_prefix_1044
        + (12,)
        + (9,) * 2
        + (12,)
        + (9,) * 2
        + (12, 15, 12, 15)
        + (12,) * 32
        + (18,) * 6
        + (12,) * 5
        + (18,) * 2
        + (12,) * 2
        + (18,) * 9
        + (12,) * 2
        + (18,) * 3
        + (12,) * 4
        + (18,) * 3
        + (42,) * 6: 9,
        support_prefix_1044
        + (12,) * 2
        + (9,) * 4
        + (12, 15, 12, 15)
        + (12,) * 32
        + (18,) * 30
        + (12,) * 6
        + (42,) * 6: 9,
    }
    assert len(dimension_1134) == 72
    assert Counter(record["candidate_index"] for record in dimension_1134) == {
        20: 36,
        40: 36,
    }
    assert all(
        record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 126
        for record in dimension_1134
    )
    assert all(
        record["invariant_subcomplex"]["invariant_cochain_dimensions"]
        == [[-1, 40], [0, 922], [1, 1266], [2, 300], [3, 0], [4, 0]]
        for record in dimension_1134
    )
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 11394
        for record in dimension_1134
    )
    support_prefix_1134 = (3,) * 50 + (9,) * 8
    candidate_20_middle_1134 = (
        (21, 24, 27, 33) * 2
        + (48, 57, 60) * 2
        + (42, 51, 54) * 2
        + (45, 45, 51, 54) * 2
        + (33, 36, 51, 54) * 2
    )
    assert Counter(
        tuple(
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        )
        for record in dimension_1134
    ) == {
        support_prefix_1134
        + (9,) * 8
        + (15,) * 16
        + candidate_20_middle_1134
        + (57, 60, 81, 87) * 2: 18,
        support_prefix_1134
        + (15,) * 8
        + (9,) * 8
        + (15,) * 8
        + candidate_20_middle_1134
        + (54, 57, 75, 81) * 2: 18,
        support_prefix_1134
        + (9,) * 4
        + (15,) * 8
        + (21,) * 4
        + (15,) * 4
        + (18,)
        + (15,) * 3
        + (
            24,
            27,
            30,
            33,
            24,
            27,
            30,
            33,
            48,
            57,
            60,
            45,
            57,
            51,
            39,
            48,
            51,
            42,
            42,
            51,
            54,
            54,
            54,
            57,
            60,
            54,
            54,
            57,
            60,
            42,
            51,
            54,
            33,
            36,
            51,
            54,
            63,
            69,
            78,
            84,
            45,
            51,
            54,
            57,
        ): 9,
        support_prefix_1134
        + (15,) * 4
        + (18,)
        + (15,) * 3
        + (9,) * 4
        + (15,) * 4
        + (21,) * 4
        + (15,) * 4
        + (
            24,
            27,
            30,
            33,
            24,
            27,
            30,
            33,
            42,
            51,
            54,
            33,
            36,
            51,
            54,
            48,
            57,
            60,
            45,
            57,
            51,
            39,
            48,
            51,
            42,
            42,
            51,
            54,
            45,
            51,
            54,
            57,
            54,
            54,
            57,
            60,
            54,
            54,
            57,
            60,
            63,
            69,
            78,
            84,
        ): 9,
        support_prefix_1134
        + (15,) * 4
        + (18,)
        + (15,) * 7
        + (21,) * 4
        + (9,) * 4
        + (15,) * 4
        + (
            24,
            27,
            30,
            33,
            24,
            27,
            30,
            33,
            42,
            51,
            54,
            33,
            36,
            51,
            54,
            39,
            48,
            51,
            42,
            42,
            51,
            54,
            48,
            57,
            60,
            54,
            60,
            78,
            84,
            63,
            75,
            63,
            60,
            63,
            69,
            72,
            63,
            63,
            69,
            72,
            45,
            51,
            54,
            57,
        ): 9,
        support_prefix_1134
        + (15,) * 4
        + (21,) * 4
        + (15,) * 4
        + (9,) * 4
        + (18,)
        + (15,) * 7
        + (
            24,
            27,
            30,
            33,
            24,
            27,
            30,
            33,
            39,
            48,
            51,
            42,
            42,
            51,
            54,
            48,
            57,
            60,
            45,
            57,
            51,
            42,
            51,
            54,
            33,
            36,
            51,
            54,
            54,
            54,
            57,
            60,
            54,
            54,
            57,
            60,
            45,
            51,
            54,
            57,
            60,
            66,
            75,
            81,
        ): 9,
    }
    assert all(
        record["cocycle_basis"]["ambient_basis"]["dimension"] == 2142
        for record in dimension_54
    )
    assert all(
        [
            len(item["terms"])
            for item in record["cocycle_basis"]["representatives"]
        ]
        == [3, 3, 3, 3, 6, 6]
        for record in dimension_54
    )
