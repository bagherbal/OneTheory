"""Generate the resumable Tier B Schoen-cover outer artifact.

Owns:
    Atomic checkpointing, candidate-level worker scheduling, and canonical
    serialization of the complete sparse cover outer-Hom screen.

Depends on:
    The exact Tier B candidate tasks and sparse cover audits in the adjacent
    research modules.

Must not:
    Read observations, choose extension classes, infer quotient invariants,
    or turn a cover-level vanishing result into a carrier claim.

Phase 0:
    This generator produces only a resumable research artifact; quotient
    descent, rank-four construction, stability, spectrum, and physics remain.
"""

from __future__ import annotations

import hashlib
import json
from multiprocessing import get_context
from pathlib import Path

from .tier_b_schoen_outer_full import (
    SchoenCoverOuterAudit,
    SchoenCoverOuterFullScreen,
    _audit_candidate,
    declared_schoen_outer_candidate_data,
)

SCHEMA = "tier-b-schoen-cover-outer-v1"
DEFAULT_PARTIAL = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_full.partial.json"
)
DEFAULT_ARTIFACT = Path(
    "data/generated/computable_carrier/tier_b_schoen_outer_full.json"
)


def _write_atomic(path: Path, payload: object) -> None:
    """Write one JSON payload through a same-directory temporary file."""

    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _audit_from_record(record: dict[str, object]) -> SchoenCoverOuterAudit:
    """Restore one immutable audit from its canonical checkpoint record."""

    left_pair = record["left_character_pair"]
    right_pair = record["right_character_pair"]
    if not isinstance(left_pair, list) or not isinstance(right_pair, list):
        raise ValueError("checkpoint character pairs must be JSON lists")
    return SchoenCoverOuterAudit(
        int(record["candidate_index"]),
        str(record["left_scheme"]),
        (str(left_pair[0]), str(left_pair[1])),
        str(record["right_scheme"]),
        (str(right_pair[0]), str(right_pair[1])),
        int(record["cover_ext_one_dimension"]),
        bool(record["squared_zero"]),
    )


def _read_records(path: Path) -> dict[int, list[dict[str, object]]]:
    """Read and validate a prior candidate checkpoint."""

    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise ValueError("checkpoint schema does not match this generator")
    raw_records = payload.get("completed_candidates", {})
    if not isinstance(raw_records, dict):
        raise ValueError("checkpoint candidate records must be an object")
    return {
        int(index): list(records)
        for index, records in raw_records.items()
    }


def _write_partial(
    path: Path,
    records: dict[int, list[dict[str, object]]],
) -> None:
    """Persist completed candidate groups for interruption-safe resumption."""

    _write_atomic(
        path,
        {
            "schema": SCHEMA,
            "declared_candidate_count": 40,
            "audits_per_candidate": 36,
            "completed_candidate_count": len(records),
            "completed_candidates": {
                str(index): records[index]
                for index in sorted(records)
            },
        },
    )


def generate(
    workers: int = 4,
    partial_path: Path = DEFAULT_PARTIAL,
    artifact_path: Path = DEFAULT_ARTIFACT,
) -> SchoenCoverOuterFullScreen | None:
    """Resume or generate the complete deterministic cover-level artifact."""

    if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
        raise ValueError("workers must be a positive integer")
    candidate_data = declared_schoen_outer_candidate_data()
    records = _read_records(partial_path)
    pending = tuple(
        task for task in candidate_data if task[0] not in records
    )
    partial_path.parent.mkdir(parents=True, exist_ok=True)
    if pending:
        with get_context("fork").Pool(
            processes=workers,
            maxtasksperchild=1,
        ) as pool:
            for group in pool.imap_unordered(_audit_candidate, pending):
                if not group:
                    raise ValueError("candidate produced no outer audits")
                candidate_index = group[0].candidate_index
                if any(
                    audit.candidate_index != candidate_index
                    for audit in group
                ):
                    raise ValueError("candidate worker returned mixed indices")
                records[candidate_index] = [
                    audit.as_record() for audit in group
                ]
                _write_partial(partial_path, records)
                print(
                    f"completed candidate {candidate_index}/40 "
                    f"({len(records)}/40)",
                    flush=True,
                )
    if len(records) != 40:
        return None
    audits = tuple(
        _audit_from_record(record)
        for candidate_index in sorted(records)
        for record in records[candidate_index]
    )
    result = SchoenCoverOuterFullScreen(audits, 40, 1440)
    if not result.exact:
        raise ValueError("complete checkpoint failed exact cover gates")
    payload = result.as_record()
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["artifact_digest"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    payload["content_addressed"] = True
    payload["digest_algorithm"] = "sha256"
    _write_atomic(artifact_path, payload)
    return result


if __name__ == "__main__":
    generated = generate()
    if generated is None:
        raise SystemExit("checkpoint incomplete")
    print(
        f"screened {len(generated.audits)} audits; "
        f"all_zero={generated.all_zero}; exact={generated.exact}",
    )
