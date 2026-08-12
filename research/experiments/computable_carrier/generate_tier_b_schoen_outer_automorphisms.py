"""Generate the resumable Tier B outer-automorphism artifact.

Owns:
    Validation of the frozen invariant artifact, serialized disposable workers,
    atomic checkpoints, constituent deduplication, and canonical pair ordering.

Depends on:
    Exact invariant pair certificates and cover-level automorphism action audits.

Must not:
    Recompute invariant cohomology, run concurrent heavy workers, select an
    extension class, or claim that any rank-four bundle exists.

Phase 0:
    Research-only resumable action generation is available; completion requires
    every declared pair certificate and no rank-four gate is implied.
"""

from __future__ import annotations

import json
from multiprocessing import get_context
from pathlib import Path

from .generate_tier_b_schoen_outer_invariants import (
    DEFAULT_ARTIFACT as DEFAULT_INVARIANT_ARTIFACT,
)
from .generate_tier_b_schoen_outer_invariants import (
    _canonical_digest,
    _validated_cover_dimensions,
    _verify_pair_record,
    _write_atomic,
)
from .tier_b_schoen_outer_automorphisms import (
    audit_schoen_outer_automorphism_pair,
    constituent_presentation_identity,
    constituent_presentation_key,
)
from .tier_b_schoen_outer_full import declared_schoen_outer_pairs
from .tier_b_schoen_outer_invariants import (
    InvariantPairTask,
    declared_schoen_invariant_pair_tasks,
)

SCHEMA = "tier-b-schoen-outer-automorphisms-v2"
DEFAULT_COVER_ARTIFACT = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_full.json"
)
DEFAULT_PARTIAL = Path(
    "data/generated/computable_carrier/"
    "tier_b_schoen_outer_automorphisms.partial.json"
)
DEFAULT_ARTIFACT = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_automorphisms.json"
)


def _validated_invariant_records(
    path: Path,
) -> tuple[str, tuple[dict[str, object], ...]]:
    """Verify the complete invariant artifact and every pair certificate."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str):
        raise ValueError("invariant artifact has no digest")
    if payload.pop("content_addressed", None) is not True:
        raise ValueError("invariant artifact is not content addressed")
    if payload.pop("digest_algorithm", None) != "sha256":
        raise ValueError("invariant artifact uses an unsupported digest")
    if _canonical_digest(payload) != digest:
        raise ValueError("invariant artifact digest does not verify")
    if (
        payload.get("schema") != "tier-b-schoen-invariant-outer-v2"
        or payload.get("exact") is not True
        or payload.get("screened_count") != 1440
    ):
        raise ValueError("invariant artifact is not the complete exact screen")
    raw_records = payload.get("audits")
    if not isinstance(raw_records, list) or len(raw_records) != 1440:
        raise ValueError("invariant artifact records do not span the pair category")
    records = []
    for index, record in enumerate(raw_records, 1):
        if not isinstance(record, dict) or record.get("global_pair_index") != index:
            raise ValueError("invariant artifact pair order is inconsistent")
        _verify_pair_record(record)
        records.append(record)
    return digest, tuple(records)


def _verify_action_record(record: dict[str, object]) -> None:
    """Verify one content-addressed pair action certificate in place."""

    digest = record.get("certificate_digest")
    if not isinstance(digest, str):
        raise ValueError("automorphism pair record has no certificate digest")
    payload = dict(record)
    del payload["certificate_digest"]
    if _canonical_digest(payload) != digest:
        raise ValueError("automorphism pair certificate digest does not verify")
    if payload.get("exact") is not True:
        raise ValueError("automorphism pair certificate failed its exact gate")


def _verify_constituent_record(record: dict[str, object]) -> None:
    """Verify one content-addressed constituent algebra certificate in place."""

    digest = record.get("certificate_digest")
    key = record.get("key")
    if not isinstance(digest, str) or not isinstance(key, str):
        raise ValueError("constituent algebra record lacks a key or digest")
    payload = dict(record)
    del payload["certificate_digest"]
    if _canonical_digest(payload) != digest:
        raise ValueError("constituent algebra certificate digest does not verify")
    if payload.get("exact") is not True:
        raise ValueError("constituent algebra certificate failed its exact gate")


def _read_partial(
    path: Path,
    invariant_digest: str,
) -> tuple[dict[int, dict[str, object]], dict[str, dict[str, object]]]:
    """Read and verify every completed pair and constituent checkpoint."""

    if not path.exists():
        return {}, {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") == "tier-b-schoen-outer-automorphisms-v1":
        payload = _migrate_v1(payload)
    if payload.get("schema") != SCHEMA:
        raise ValueError("automorphism checkpoint schema is incompatible")
    if payload.get("invariant_artifact_digest") != invariant_digest:
        raise ValueError("automorphism checkpoint uses another invariant artifact")
    raw_pairs = payload.get("completed_pairs")
    raw_constituents = payload.get("constituents")
    if not isinstance(raw_pairs, dict) or not isinstance(raw_constituents, dict):
        raise ValueError("automorphism checkpoint ledgers must be objects")
    pairs = {int(index): record for index, record in raw_pairs.items()}
    constituents = dict(raw_constituents)
    for index, record in pairs.items():
        if not isinstance(record, dict) or record.get("global_pair_index") != index:
            raise ValueError("automorphism pair checkpoint index is inconsistent")
        _verify_action_record(record)
    for key, record in constituents.items():
        if not isinstance(record, dict) or record.get("key") != key:
            raise ValueError("constituent checkpoint key is inconsistent")
        _verify_constituent_record(record)
    return pairs, constituents


def _compact_legacy_action(action: dict[str, object]) -> dict[str, object]:
    """Compact expanded projective charts without changing their exact rule."""

    compact = dict(action)
    charts = compact.pop("canonical_normal_form_charts", None)
    dimension = compact.get("extension_dimension")
    if charts is None:
        return compact
    if (
        isinstance(dimension, bool)
        or not isinstance(dimension, int)
        or not isinstance(charts, list)
        or len(charts) != dimension
    ):
        raise ValueError("legacy projective charts are inconsistent")
    compact["canonical_normal_form"] = {
        "rule": "normalize the first nonzero coordinate to one",
        "pivot_index_range": [0, dimension - 1],
        "coordinates_before_pivot": "zero",
        "coordinates_after_pivot": "free",
        "chart_count": dimension,
    }
    compact["action_proof"] = "exact equality on cover cocycles"
    compact["quotient_action_exact"] = True
    return compact


def _migrate_v1(payload: dict[str, object]) -> dict[str, object]:
    """Losslessly rebind unambiguous legacy keys to full presentation digests."""

    raw_pairs = payload.get("completed_pairs")
    raw_constituents = payload.get("constituents")
    if not isinstance(raw_pairs, dict) or not isinstance(raw_constituents, dict):
        raise ValueError("legacy automorphism ledgers must be objects")
    declared = declared_schoen_outer_pairs()
    identities: dict[str, dict[str, object]] = {}
    pair_bindings: dict[int, tuple[str, str] | None] = {}
    for text_index, raw_record in raw_pairs.items():
        if not isinstance(raw_record, dict):
            raise ValueError("legacy pair records must be objects")
        index = int(text_index)
        _, candidate, left_ray, right_ray = declared[index - 1]
        keys = []
        for field, ray, factor, twist in (
            ("left_constituent_key", left_ray, candidate.left_factor, candidate.left_twist),
            (
                "right_constituent_key",
                right_ray,
                candidate.right_factor,
                candidate.right_twist,
            ),
        ):
            old_key = raw_record.get(field)
            if old_key is None:
                keys = []
                break
            if not isinstance(old_key, str):
                raise ValueError("legacy constituent keys must be text")
            identity = constituent_presentation_identity(ray, factor, twist)
            existing = identities.get(old_key)
            if existing is not None and existing != identity:
                raise ValueError("legacy constituent key is ambiguous")
            identities[old_key] = identity
            keys.append(old_key)
        pair_bindings[index] = tuple(keys) if keys else None
    if set(identities) != set(raw_constituents):
        raise ValueError("legacy constituent ledger contains unbound records")
    migrated_constituents: dict[str, dict[str, object]] = {}
    replacement: dict[str, str] = {}
    for old_key, identity in identities.items():
        raw = raw_constituents[old_key]
        if not isinstance(raw, dict):
            raise ValueError("legacy constituent records must be objects")
        _verify_constituent_record(raw)
        record = {
            key: value
            for key, value in raw.items()
            if key
            not in {
                "certificate_digest",
                "scheme",
                "factor",
                "twist",
                "character_pair",
                "key",
            }
        }
        new_key = constituent_presentation_key(identity)
        record["key"] = new_key
        record["presentation_identity"] = identity
        record["certificate_digest"] = _canonical_digest(record)
        existing = migrated_constituents.get(new_key)
        if existing is not None and existing != record:
            raise ValueError("migrated constituent address collision")
        migrated_constituents[new_key] = record
        replacement[old_key] = new_key
    migrated_pairs: dict[str, dict[str, object]] = {}
    for text_index, raw in raw_pairs.items():
        if not isinstance(raw, dict):
            raise ValueError("legacy pair records must be objects")
        index = int(text_index)
        _verify_action_record(raw)
        record = dict(raw)
        del record["certificate_digest"]
        binding = pair_bindings[index]
        if binding is not None:
            left_key, right_key = binding
            record["left_constituent_key"] = replacement[left_key]
            record["right_constituent_key"] = replacement[right_key]
            action = record.get("automorphism_action")
            if not isinstance(action, dict):
                raise ValueError("legacy positive pair lacks its action record")
            record["automorphism_action"] = _compact_legacy_action(action)
        record["certificate_digest"] = _canonical_digest(record)
        migrated_pairs[text_index] = record
    return {
        "schema": SCHEMA,
        "invariant_artifact_digest": payload.get("invariant_artifact_digest"),
        "declared_pair_count": payload.get("declared_pair_count"),
        "completed_pair_count": len(migrated_pairs),
        "completed_pairs": migrated_pairs,
        "constituent_count": len(migrated_constituents),
        "constituents": migrated_constituents,
    }


def _write_partial(
    path: Path,
    invariant_digest: str,
    pairs: dict[int, dict[str, object]],
    constituents: dict[str, dict[str, object]],
) -> None:
    """Atomically persist all exact action progress after one pair."""

    _write_atomic(
        path,
        {
            "schema": SCHEMA,
            "invariant_artifact_digest": invariant_digest,
            "declared_pair_count": 1440,
            "completed_pair_count": len(pairs),
            "completed_pairs": {
                str(index): pairs[index] for index in sorted(pairs)
            },
            "constituent_count": len(constituents),
            "constituents": {
                key: constituents[key] for key in sorted(constituents)
            },
        },
    )


def _audit_pair_record(
    payload: tuple[InvariantPairTask, dict[str, object]],
) -> tuple[dict[str, object], tuple[dict[str, object], ...]]:
    """Return one pair certificate and any exact constituent certificates."""

    task, invariant_record = payload
    audit = audit_schoen_outer_automorphism_pair(task, invariant_record)
    record = audit.as_record()
    record["certificate_digest"] = _canonical_digest(record)
    constituents = tuple(
        constituent
        for constituent in (audit.left_constituent, audit.right_constituent)
        if constituent is not None
    )
    certified = []
    for constituent in constituents:
        copy = dict(constituent)
        copy["certificate_digest"] = _canonical_digest(copy)
        certified.append(copy)
    return record, tuple(certified)


def _merge_constituent(
    constituents: dict[str, dict[str, object]],
    record: dict[str, object],
) -> None:
    """Merge one exact duplicate only when its full certificate agrees."""

    _verify_constituent_record(record)
    key = record.get("key")
    if not isinstance(key, str):
        raise ValueError("constituent key must be text")
    existing = constituents.get(key)
    if existing is not None and existing != record:
        raise ValueError("one constituent key produced conflicting certificates")
    constituents[key] = record


def _pending_order(
    payload: tuple[InvariantPairTask, dict[str, object]],
) -> tuple[bool, int, int]:
    """Close zero spaces first, then increase invariant dimension exactly."""

    task, record = payload
    subcomplex = record.get("invariant_subcomplex")
    if not isinstance(subcomplex, dict):
        raise ValueError("invariant record lacks its subcomplex")
    dimension = subcomplex.get("invariant_ext_one_dimension")
    if isinstance(dimension, bool) or not isinstance(dimension, int):
        raise ValueError("invariant dimension must be an integer")
    return dimension != 0, dimension, task[0]


def _store_result(
    result: tuple[dict[str, object], tuple[dict[str, object], ...]],
    partial_path: Path,
    invariant_digest: str,
    pairs: dict[int, dict[str, object]],
    constituents: dict[str, dict[str, object]],
) -> None:
    """Verify and checkpoint one completed worker or zero-space result."""

    record, constituent_records = result
    index = record.get("global_pair_index")
    if isinstance(index, bool) or not isinstance(index, int):
        raise ValueError("worker returned an invalid pair index")
    _verify_action_record(record)
    for constituent in constituent_records:
        _merge_constituent(constituents, constituent)
    pairs[index] = record
    _write_partial(
        partial_path,
        invariant_digest,
        pairs,
        constituents,
    )
    print(
        f"completed automorphism pair {index}/1440 ({len(pairs)}/1440)",
        flush=True,
    )


def generate(
    max_pairs: int | None = None,
    workers: int = 1,
    cover_path: Path = DEFAULT_COVER_ARTIFACT,
    invariant_path: Path = DEFAULT_INVARIANT_ARTIFACT,
    partial_path: Path = DEFAULT_PARTIAL,
    artifact_path: Path = DEFAULT_ARTIFACT,
) -> dict[str, object] | None:
    """Resume the exact pair-action screen with one disposable worker."""

    if workers != 1:
        raise ValueError("the action screen is restricted to one bounded worker")
    if max_pairs is not None and (
        isinstance(max_pairs, bool)
        or not isinstance(max_pairs, int)
        or max_pairs < 1
    ):
        raise ValueError("max_pairs must be a positive integer or None")
    _, cover_dimensions = _validated_cover_dimensions(cover_path)
    invariant_digest, invariant_records = _validated_invariant_records(invariant_path)
    tasks = declared_schoen_invariant_pair_tasks(cover_dimensions)
    pairs, constituents = _read_partial(partial_path, invariant_digest)
    pending = sorted(
        (
            (task, record)
            for task, record in zip(tasks, invariant_records, strict=True)
            if task[0] not in pairs
        ),
        key=_pending_order,
    )
    selected = pending if max_pairs is None else pending[:max_pairs]
    partial_path.parent.mkdir(parents=True, exist_ok=True)
    positive_spaces: list[tuple[InvariantPairTask, dict[str, object]]] = []
    if selected:
        zero_spaces = [
            payload for payload in selected if _pending_order(payload)[1] == 0
        ]
        positive_spaces = [
            payload for payload in selected if _pending_order(payload)[1] > 0
        ]
        for payload in zero_spaces:
            _store_result(
                _audit_pair_record(payload),
                partial_path,
                invariant_digest,
                pairs,
                constituents,
            )
    if positive_spaces:
        with get_context("fork").Pool(processes=1, maxtasksperchild=1) as pool:
            for result in pool.imap(
                _audit_pair_record,
                positive_spaces,
                chunksize=1,
            ):
                _store_result(
                    result,
                    partial_path,
                    invariant_digest,
                    pairs,
                    constituents,
                )
    if len(pairs) != len(tasks):
        return None
    ordered = [pairs[index] for index in range(1, len(tasks) + 1)]
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "invariant_artifact_digest": invariant_digest,
        "screened_count": len(ordered),
        "declared_pair_count": len(tasks),
        "constituent_count": len(constituents),
        "complete_for_declared_category": True,
        "exact": all(record.get("exact") is True for record in ordered),
        "automorphism_actions_computed": True,
        "canonical_orbits_computed": True,
        "outer_extensions_constructed": False,
        "promotion_ready": False,
        "status": (
            "complete exact automorphism quotient; no extension point is selected "
            "and rank-four construction remains unresolved"
        ),
        "constituents": [constituents[key] for key in sorted(constituents)],
        "audits": ordered,
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    payload["content_addressed"] = True
    payload["digest_algorithm"] = "sha256"
    _write_atomic(artifact_path, payload)
    return payload


if __name__ == "__main__":
    generated = generate()
    if generated is None:
        raise SystemExit("automorphism checkpoint incomplete")
    print(
        f"screened {generated['screened_count']} automorphism pairs; "
        f"exact={generated['exact']}",
    )
