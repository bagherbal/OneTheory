"""Generate the resumable Tier B invariant outer-cocycle artifact.

Owns:
    Cover-artifact validation, one-pair child-process scheduling, atomic
    checkpointing, and canonical serialization of the exhaustive invariant
    Ext-one cocycle screen.

Depends on:
    The content-addressed cover screen and exact pair-level quotient cocycle
    calculation. Execution is deliberately serialized for bounded memory.

Must not:
    Recompute certified cover ranks, schedule concurrent heavy workers,
    choose an extension orbit, or claim a rank-four descended bundle.

Phase 0:
    Resumable invariant-cocycle generation is available; the complete artifact
    and all rank-four gates remain unresolved until every pair is certified.
"""

from __future__ import annotations

import hashlib
import json
from multiprocessing import get_context
from pathlib import Path

from .tier_b_schoen_outer_full import declared_schoen_outer_pairs
from .tier_b_schoen_outer_invariants import (
    InvariantPairTask,
    audit_schoen_invariant_pair,
    declared_schoen_invariant_pair_tasks,
)

SCHEMA = "tier-b-schoen-invariant-outer-v2"
DEFAULT_COVER_ARTIFACT = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_full.json"
)
DEFAULT_PARTIAL = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_invariants.partial.json"
)
DEFAULT_ARTIFACT = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_invariants.json"
)


def _canonical_digest(payload: object) -> str:
    """Return the SHA-256 digest of canonical compact JSON."""

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_atomic(path: Path, payload: object) -> None:
    """Write one checkpoint through a same-directory temporary file."""

    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    temporary.replace(path)


def _validated_cover_dimensions(path: Path) -> tuple[str, tuple[int, ...]]:
    """Verify the frozen cover artifact and return its ordered dimensions."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str):
        raise ValueError("cover artifact has no digest")
    if payload.pop("content_addressed", None) is not True:
        raise ValueError("cover artifact is not content addressed")
    if payload.pop("digest_algorithm", None) != "sha256":
        raise ValueError("cover artifact uses an unsupported digest")
    if _canonical_digest(payload) != digest:
        raise ValueError("cover artifact digest does not verify")
    if payload.get("exact") is not True or payload.get("screened_count") != 1440:
        raise ValueError("cover artifact is not the complete exact screen")
    audits = payload.get("audits")
    if not isinstance(audits, list) or len(audits) != 1440:
        raise ValueError("cover artifact audits do not span the declared screen")
    pairs = declared_schoen_outer_pairs()
    dimensions = []
    for audit, pair in zip(audits, pairs, strict=True):
        if not isinstance(audit, dict):
            raise ValueError("cover audit records must be objects")
        candidate_index, _, left_ray, right_ray = pair
        identity = (
            audit.get("candidate_index"),
            audit.get("left_scheme"),
            audit.get("left_character_pair"),
            audit.get("right_scheme"),
            audit.get("right_character_pair"),
        )
        expected = (
            candidate_index,
            left_ray.cokernel.scheme.name,
            [str(value) for value in left_ray.character_pair],
            right_ray.cokernel.scheme.name,
            [str(value) for value in right_ray.character_pair],
        )
        if identity != expected or audit.get("exact") is not True:
            raise ValueError("cover audit identity or exact gate is incompatible")
        dimension = audit.get("cover_ext_one_dimension")
        if isinstance(dimension, bool) or not isinstance(dimension, int):
            raise ValueError("cover Ext dimensions must be integers")
        dimensions.append(dimension)
    return digest, tuple(dimensions)


def _verify_pair_record(record: dict[str, object]) -> None:
    """Verify one content-addressed pair certificate in place."""

    digest = record.get("certificate_digest")
    if not isinstance(digest, str):
        raise ValueError("invariant pair record has no certificate digest")
    payload = dict(record)
    del payload["certificate_digest"]
    if _canonical_digest(payload) != digest:
        raise ValueError("invariant pair certificate digest does not verify")
    if payload.get("exact") is not True:
        raise ValueError("invariant pair certificate failed its exact gate")


def _read_partial(
    path: Path,
    cover_digest: str,
) -> dict[int, dict[str, object]]:
    """Read and verify all completed invariant-pair checkpoints."""

    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise ValueError("invariant checkpoint schema is incompatible")
    if payload.get("cover_artifact_digest") != cover_digest:
        raise ValueError("invariant checkpoint uses another cover artifact")
    raw_records = payload.get("completed_pairs")
    if not isinstance(raw_records, dict):
        raise ValueError("invariant checkpoint records must be an object")
    records = {int(index): record for index, record in raw_records.items()}
    for index, record in records.items():
        if not isinstance(record, dict):
            raise ValueError("invariant pair checkpoints must be objects")
        if record.get("global_pair_index") != index:
            raise ValueError("invariant pair checkpoint index is inconsistent")
        _verify_pair_record(record)
    return records


def _write_partial(
    path: Path,
    cover_digest: str,
    records: dict[int, dict[str, object]],
) -> None:
    """Persist every completed pair after one bounded child exits."""

    _write_atomic(
        path,
        {
            "schema": SCHEMA,
            "cover_artifact_digest": cover_digest,
            "declared_pair_count": 1440,
            "completed_pair_count": len(records),
            "completed_pairs": {
                str(index): records[index] for index in sorted(records)
            },
        },
    )


def _audit_pair_record(task: InvariantPairTask) -> dict[str, object]:
    """Return one compact pair record from a disposable worker process."""

    record = audit_schoen_invariant_pair(task).as_record()
    record["certificate_digest"] = _canonical_digest(record)
    return record


def _pending_order(task: InvariantPairTask) -> tuple[bool, int, int]:
    """Prioritize the smallest nonzero cover spaces deterministically."""

    cover_dimension = task[-1]
    return cover_dimension == 0, cover_dimension, task[0]


def generate(
    max_pairs: int | None = None,
    workers: int = 1,
    cover_path: Path = DEFAULT_COVER_ARTIFACT,
    partial_path: Path = DEFAULT_PARTIAL,
    artifact_path: Path = DEFAULT_ARTIFACT,
) -> dict[str, object] | None:
    """Resume the exact screen with one disposable process per pair."""

    if workers != 1:
        raise ValueError("the invariant screen is restricted to one memory-bounded worker")
    if max_pairs is not None and (
        isinstance(max_pairs, bool)
        or not isinstance(max_pairs, int)
        or max_pairs < 1
    ):
        raise ValueError("max_pairs must be a positive integer or None")
    cover_digest, dimensions = _validated_cover_dimensions(cover_path)
    tasks = declared_schoen_invariant_pair_tasks(dimensions)
    records = _read_partial(partial_path, cover_digest)
    pending = sorted(
        (task for task in tasks if task[0] not in records),
        key=_pending_order,
    )
    selected = pending if max_pairs is None else pending[:max_pairs]
    partial_path.parent.mkdir(parents=True, exist_ok=True)
    if selected:
        with get_context("fork").Pool(processes=1, maxtasksperchild=1) as pool:
            for record in pool.imap(_audit_pair_record, selected, chunksize=1):
                index = record.get("global_pair_index")
                if isinstance(index, bool) or not isinstance(index, int):
                    raise ValueError("worker returned an invalid pair index")
                _verify_pair_record(record)
                records[index] = record
                _write_partial(partial_path, cover_digest, records)
                print(
                    f"completed invariant pair {index}/1440 "
                    f"({len(records)}/1440)",
                    flush=True,
                )
    if len(records) != len(tasks):
        return None
    ordered = [records[index] for index in range(1, len(tasks) + 1)]
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "cover_artifact_digest": cover_digest,
        "screened_count": len(ordered),
        "declared_pair_count": len(tasks),
        "complete_for_declared_category": True,
        "exact": all(record.get("exact") is True for record in ordered),
        "automorphism_actions_computed": False,
        "canonical_orbits_computed": False,
        "outer_extensions_constructed": False,
        "promotion_ready": False,
        "status": (
            "complete invariant Ext-one cocycle screen; automorphism orbits, "
            "rank-four construction, and physical gates remain unresolved"
        ),
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
        raise SystemExit("invariant checkpoint incomplete")
    print(
        f"screened {generated['screened_count']} invariant pairs; "
        f"exact={generated['exact']}",
    )
