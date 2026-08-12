"""Test exhaustive Tier B outer-automorphism artifact contracts.

Owns:
    Strict frozen-scalar decoding, invariant artifact validation, stored cocycle
    reconstruction, zero-space orbit closure, and resumable checkpoint shape.

Depends on:
    The exact generated invariant screen and research-only action generator.

Must not:
    Infer positive actions from dimensions, select an extension class, construct
    a rank-four bundle, or promote a partial action screen.

Phase 0:
    Pair-level action generation contracts are executable; the exhaustive action
    artifact and all rank-four gates remain unresolved until generation closes.
"""

import json
from collections import Counter
from pathlib import Path

import pytest

from onetheory.math.numbers import Eisenstein, Rational
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    DEFAULT_COVER_ARTIFACT,
    DEFAULT_INVARIANT_ARTIFACT,
    SCHEMA,
    _read_partial,
    _validated_invariant_records,
    generate,
)
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_invariants import (
    _validated_cover_dimensions,
)
from research.experiments.computable_carrier.schoen_sparse_outer import (
    sparse_outer_hom,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_automorphisms import (
    _eisenstein_text,
    _stored_cover_representatives,
    audit_schoen_outer_automorphism_pair,
    constituent_presentation_identity,
    constituent_presentation_key,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_full import (
    _clear_worker_caches,
)
from research.experiments.computable_carrier.tier_b_schoen_outer_invariants import (
    declared_schoen_invariant_pair_tasks,
)

ACTION_CHECKPOINT = Path(
    "data/generated/computable_carrier/"
    "tier_b_schoen_outer_automorphisms.partial.json"
)


def _tasks_and_records():
    """Return verified frozen tasks and invariant pair records."""

    _, dimensions = _validated_cover_dimensions(DEFAULT_COVER_ARTIFACT)
    digest, records = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    return digest, declared_schoen_invariant_pair_tasks(dimensions), records


def test_exact_eisenstein_artifact_text_is_strictly_decoded() -> None:
    """Only canonical rational and two-coordinate Eisenstein text is accepted."""

    assert _eisenstein_text("-73/4+73/4*omega") == Eisenstein(
        Rational(-73, 4),
        Rational(73, 4),
    )
    assert _eisenstein_text("omega") == Eisenstein(0, 1)
    assert _eisenstein_text("-omega") == Eisenstein(0, -1)
    assert _eisenstein_text("8/27") == Eisenstein(Rational(8, 27))
    with pytest.raises(ValueError):
        _eisenstein_text("1 + omega")
    with pytest.raises(ValueError):
        _eisenstein_text("__import__('os')")


def test_stored_positive_cocycles_reconstruct_in_the_exact_outer_basis() -> None:
    """Frozen pair 73 coordinates reconstruct as four exact cover cocycles."""

    _, tasks, records = _tasks_and_records()
    task = tasks[72]
    _, _, _, candidate, left_ray, right_ray, _ = task
    try:
        outer = sparse_outer_hom(
            left_ray,
            right_ray,
            candidate.left_factor,
            candidate.left_twist,
            candidate.right_factor,
            candidate.right_twist,
        )
        representatives = _stored_cover_representatives(outer, records[72])
        assert representatives.domain.dimension == 4
        assert not representatives.is_zero()
        assert dict(outer.total_differentials)[1].compose(representatives).is_zero()
    finally:
        _clear_worker_caches()


def test_zero_invariant_ext_has_the_unique_split_orbit() -> None:
    """A zero Ext space closes without fabricating constituent actions."""

    digest, tasks, records = _tasks_and_records()
    result = audit_schoen_outer_automorphism_pair(tasks[0], records[0])
    record = result.as_record()

    assert record["invariant_certificate_digest"] == records[0][
        "certificate_digest"
    ]
    assert record["invariant_ext_one_dimension"] == 0
    assert record["automorphism_action"] == {
        "extension_dimension": 0,
        "unique_action": True,
        "orbit_count": 1,
        "zero_orbit": {"representative": [], "split_extension": True},
        "canonical_orbits_computed": True,
        "outer_extension_constructed": False,
        "exact": True,
        "status": "zero Ext space has the unique trivial action and split orbit",
    }
    assert result.left_constituent is None
    assert result.right_constituent is None
    assert result.exact
    assert len(digest) == 64


def test_generator_checkpoints_one_exact_zero_pair(tmp_path: Path) -> None:
    """A bounded resume writes one verifiable pair without a final artifact."""

    partial = tmp_path / "actions.partial.json"
    artifact = tmp_path / "actions.json"

    assert generate(max_pairs=1, partial_path=partial, artifact_path=artifact) is None
    payload = json.loads(partial.read_text(encoding="utf-8"))
    digest, pairs = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    completed, constituents = _read_partial(partial, digest)

    assert payload["schema"] == SCHEMA
    assert payload["completed_pair_count"] == len(completed) == 1
    assert payload["constituent_count"] == len(constituents) == 0
    assert completed[1]["invariant_certificate_digest"] == pairs[0][
        "certificate_digest"
    ]
    assert not artifact.exists()


def test_checked_action_frontier_closes_every_zero_ext_pair() -> None:
    """The growing checkpoint retains the complete 360-pair zero frontier."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    zero_indices = {
        record["global_pair_index"]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 0
    }

    assert zero_indices <= set(pairs)
    assert len(zero_indices) == 360
    assert all(record["exact"] is True for record in pairs.values())
    assert all(
        pairs[index]["automorphism_action"]["unique_action"] is True
        for index in zero_indices
    )
    assert Counter(pairs[index]["candidate_index"] for index in zero_indices) == {
        index: 36 for index in (1, 2, 11, 12, 13, 21, 22, 31, 32, 33)
    }
    assert all(record["exact"] is True for record in constituents.values())


def test_checked_action_frontier_contains_the_positive_prototype() -> None:
    """Pair 73 persists its exact scalar action and constituent references."""

    digest, _ = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    record = pairs[73]
    action = record["automorphism_action"]

    assert record["invariant_ext_one_dimension"] == 4
    assert action["left_scalar_character"] == ["0", "0", "0", "1"]
    assert action["right_scalar_character"] == ["1"]
    assert action["left_cover_equalities"] is True
    assert action["right_cover_equalities"] is True
    assert action["unit_characters_exact"] is True
    assert action["nonzero_orbit_space"] == "P^3(Q(omega))"
    assert record["left_constituent_key"] in constituents
    assert record["right_constituent_key"] in constituents
    assert record["canonical_orbits_computed"] is True
    assert record["outer_extension_constructed"] is False
    assert record["exact"] is True


def test_checked_action_frontier_closes_candidate_three() -> None:
    """All 36 candidate-three ray pairs have exact projective orbit charts."""

    digest, _ = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    records = [
        pairs[index]
        for index in range(73, 109)
    ]

    assert all(record["candidate_index"] == 3 for record in records)
    assert all(record["invariant_ext_one_dimension"] == 4 for record in records)
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^3(Q(omega))"
        for record in records
    )
    assert all(
        record["automorphism_action"]["unit_characters_exact"] is True
        for record in records
    )
    candidate_keys = {
        record[key]
        for record in records
        for key in ("left_constituent_key", "right_constituent_key")
    }
    assert candidate_keys <= set(constituents)
    assert len(candidate_keys) == 12


def test_checked_action_frontier_closes_factor_exchanged_candidate() -> None:
    """Candidate 23 independently reproduces 36 projective three-spaces."""

    digest, _ = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    records = [pairs[index] for index in range(793, 829)]

    assert all(record["candidate_index"] == 23 for record in records)
    assert all(record["invariant_ext_one_dimension"] == 4 for record in records)
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^3(Q(omega))"
        for record in records
    )
    candidate_keys = {
        record[key]
        for record in records
        for key in ("left_constituent_key", "right_constituent_key")
    }
    assert candidate_keys <= set(constituents)
    assert len(candidate_keys) == 12
    assert candidate_keys.isdisjoint(
        {
            pairs[index][key]
            for index in range(73, 109)
            for key in ("left_constituent_key", "right_constituent_key")
        }
    )


def test_checked_action_frontier_closes_dimension_six() -> None:
    """Every frozen six-dimensional Ext space has an exact projective quotient."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    indices = [
        record["global_pair_index"]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 6
    ]
    records = [pairs[index] for index in indices]

    assert len(records) == 36
    assert Counter(record["candidate_index"] for record in records) == {14: 18, 34: 18}
    assert all(record["invariant_ext_one_dimension"] == 6 for record in records)
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^5(Q(omega))"
        for record in records
    )
    assert all(
        record["automorphism_action"]["left_cover_equalities"] is True
        and record["automorphism_action"]["right_cover_equalities"] is True
        and record["automorphism_action"]["unit_characters_exact"] is True
        for record in records
    )
    assert all(
        record[key] in constituents
        for record in records
        for key in ("left_constituent_key", "right_constituent_key")
    )


def test_constituent_keys_bind_serre_shift_and_extension_map() -> None:
    """Presentation addresses distinguish rays omitted by the legacy key."""

    _, tasks, _ = _tasks_and_records()
    _, _, _, candidate, left_ray, right_ray, _ = tasks[255]
    left_identity = constituent_presentation_identity(
        left_ray,
        candidate.left_factor,
        candidate.left_twist,
    )
    right_identity = constituent_presentation_identity(
        right_ray,
        candidate.right_factor,
        candidate.right_twist,
    )

    assert left_identity["target_line_shift"] == -6
    assert right_identity["target_line_shift"] == 0
    assert left_identity["extension_map"]
    assert right_identity["extension_map"]
    assert constituent_presentation_key(left_identity) != constituent_presentation_key(
        right_identity
    )


def test_checked_action_frontier_records_exact_quotient_fallback() -> None:
    """Pair 256 reduces nonscalar cover products to a scalar Ext action."""

    digest, _ = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    record = pairs[256]
    action = record["automorphism_action"]

    assert record["invariant_ext_one_dimension"] == 8
    assert action["action_proof"] == "exact quotient reduction modulo coboundaries"
    assert action["left_cover_equalities"] is False
    assert action["right_cover_equalities"] is False
    assert action["quotient_action_exact"] is True
    assert action["module_laws_exact"] is True
    assert action["actions_commute"] is True
    assert action["nonzero_orbit_space"] == "P^7(Q(omega))"
    assert action["canonical_normal_form"]["chart_count"] == 8
    assert record["left_constituent_key"] in constituents
    assert record["right_constituent_key"] in constituents
    assert record["exact"] is True


def test_checked_action_frontier_closes_dimension_eight() -> None:
    """All 72 eight-dimensional spaces close by direct or quotient proof."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, _ = _read_partial(ACTION_CHECKPOINT, digest)
    indices = [
        record["global_pair_index"]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 8
    ]
    records = [pairs[index] for index in indices]

    assert len(records) == 72
    assert Counter(record["candidate_index"] for record in records) == {
        8: 18,
        14: 18,
        28: 18,
        34: 18,
    }
    assert Counter(
        record["automorphism_action"]["action_proof"] for record in records
    ) == {
        "exact equality on cover cocycles": 36,
        "exact quotient reduction modulo coboundaries": 36,
    }
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^7(Q(omega))"
        for record in records
    )
    assert all(record["exact"] is True for record in records)


def test_checked_action_frontier_closes_dimension_ten() -> None:
    """All 108 ten-dimensional spaces have exact projective-nine quotients."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, _ = _read_partial(ACTION_CHECKPOINT, digest)
    records = [
        pairs[record["global_pair_index"]]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 10
    ]

    assert len(records) == 108
    assert Counter(record["candidate_index"] for record in records) == {
        8: 18,
        18: 36,
        28: 18,
        38: 36,
    }
    assert Counter(
        record["automorphism_action"]["action_proof"] for record in records
    ) == {
        "exact equality on cover cocycles": 72,
        "exact quotient reduction modulo coboundaries": 36,
    }
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^9(Q(omega))"
        for record in records
    )
    assert all(record["exact"] is True for record in records)


def test_checked_action_frontier_closes_dimension_eighteen() -> None:
    """The ledger midpoint closes all 72 projective-seventeen quotients."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    records = [
        pairs[record["global_pair_index"]]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 18
    ]

    assert len(pairs) >= 720
    assert len(constituents) >= 120
    assert len(records) == 72
    assert Counter(record["candidate_index"] for record in records) == {
        9: 18,
        15: 18,
        29: 18,
        35: 18,
    }
    assert Counter(
        record["automorphism_action"]["action_proof"] for record in records
    ) == {
        "exact equality on cover cocycles": 36,
        "exact quotient reduction modulo coboundaries": 36,
    }
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^17(Q(omega))"
        for record in records
    )
    assert all(record["exact"] is True for record in records)


def test_checked_action_frontier_closes_dimension_twenty_two() -> None:
    """Both factor orientations close all projective-twenty-one quotients."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    records = [
        pairs[record["global_pair_index"]]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 22
    ]

    assert len(constituents) >= 144
    assert len(records) == 36
    assert Counter(record["candidate_index"] for record in records) == {17: 18, 37: 18}
    assert all(
        record["automorphism_action"]["action_proof"]
        == "exact equality on cover cocycles"
        for record in records
    )
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^21(Q(omega))"
        for record in records
    )
    assert all(record["exact"] is True for record in records)


def test_checked_action_frontier_closes_dimension_twenty_four() -> None:
    """Six character-split blocks close all projective-twenty-three quotients."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, _ = _read_partial(ACTION_CHECKPOINT, digest)
    records = [
        pairs[record["global_pair_index"]]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 24
    ]

    assert len(records) == 108
    assert Counter(record["candidate_index"] for record in records) == {
        9: 18,
        15: 18,
        17: 18,
        29: 18,
        35: 18,
        37: 18,
    }
    assert Counter(
        record["automorphism_action"]["action_proof"] for record in records
    ) == {
        "exact equality on cover cocycles": 72,
        "exact quotient reduction modulo coboundaries": 36,
    }
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^23(Q(omega))"
        for record in records
    )
    assert all(record["exact"] is True for record in records)


def test_checked_action_frontier_closes_dimension_thirty() -> None:
    """All thirty-dimensional actions become scalar only after reduction."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, constituents = _read_partial(ACTION_CHECKPOINT, digest)
    records = [
        pairs[record["global_pair_index"]]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 30
    ]

    assert len(pairs) >= 900
    assert len(constituents) >= 168
    assert len(records) == 36
    assert Counter(record["candidate_index"] for record in records) == {10: 18, 30: 18}
    assert all(
        record["automorphism_action"]["action_proof"]
        == "exact quotient reduction modulo coboundaries"
        for record in records
    )
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^29(Q(omega))"
        for record in records
    )
    assert all(record["exact"] is True for record in records)


def test_checked_action_frontier_closes_dimension_thirty_six() -> None:
    """Both factor orientations close directly in dimension thirty-six."""

    digest, invariant_records = _validated_invariant_records(
        DEFAULT_INVARIANT_ARTIFACT
    )
    pairs, _ = _read_partial(ACTION_CHECKPOINT, digest)
    records = [
        pairs[record["global_pair_index"]]
        for record in invariant_records
        if record["invariant_subcomplex"]["invariant_ext_one_dimension"] == 36
    ]

    assert len(records) == 36
    assert Counter(record["candidate_index"] for record in records) == {7: 18, 27: 18}
    assert all(
        record["automorphism_action"]["action_proof"]
        == "exact equality on cover cocycles"
        for record in records
    )
    assert all(
        record["automorphism_action"]["nonzero_orbit_space"]
        == "P^35(Q(omega))"
        for record in records
    )
    assert all(record["exact"] is True for record in records)


def test_checked_action_frontier_records_square_zero_unipotent_orbit() -> None:
    """Pair 217 stores a complete nonprojective canonical orbit algorithm."""

    digest, _ = _validated_invariant_records(DEFAULT_INVARIANT_ARTIFACT)
    pairs, _ = _read_partial(ACTION_CHECKPOINT, digest)
    record = pairs[217]
    action = record["automorphism_action"]

    assert record["invariant_ext_one_dimension"] == 38
    assert action["action_proof"] == "exact quotient reduction modulo coboundaries"
    assert action["nonzero_orbit_space"] == (
        "fixed-basis scalar-plus-square-zero-unipotent quotient"
    )
    assert action["radical_generator_count"] == 3
    assert action["radical_action_ranks"] == [2, 2, 2]
    assert action["unit_characters_exact"] is True
    assert action["radical_square_zero"] is True
    assert action["canonical_normal_form"]["implemented_by"] == (
        "canonical_square_zero_orbit_representative"
    )
    assert action["canonical_orbits_computed"] is True
    assert action["outer_extension_constructed"] is False
    assert record["exact"] is True
