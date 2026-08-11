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

    assert checkpoint["schema"] == "tier-b-schoen-invariant-outer-v2"
    assert checkpoint["declared_pair_count"] == 1440
    assert checkpoint["completed_pair_count"] == 756
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
