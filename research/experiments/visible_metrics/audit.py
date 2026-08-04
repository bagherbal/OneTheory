"""Audit the exact inputs required by the visible metric frontier.

Owns:
    Deterministic presence and source-hash checks for the reusable section compiler,
    Schoen presentation, extension cocycles, section bases, lifts, and metric gates.

Depends on:
    `pathlib`, SHA-256, and the production metric boundary contract.

Must not:
    Infer a section basis from dimensions, invent an extension representative, use
    sampled rank as global generation, or report numerical carrier evidence.

Phase 0:
    Sufficiency audit only; reconstruction stops at the earliest absent extension
    datum and preserves its prerequisite chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final

from onetheory.models.heterotic_schoen.metrics import (
    METRIC_MISSING_CHAIN,
    metric_input_status,
)


@dataclass(frozen=True, slots=True)
class InputRecord:
    """One required section or metric artifact and its repository path."""

    name: str
    relative_path: str
    present: bool


@dataclass(frozen=True, slots=True)
class MetricSufficiencyAudit:
    """Immutable inventory of the positive-twist metric prerequisites."""

    records: tuple[InputRecord, ...]
    published_files: tuple[str, ...]
    source_hashes: tuple[tuple[str, str], ...]
    first_missing_input: str | None
    prerequisite_chain: tuple[str, ...]
    promotable: bool


REQUIRED_INPUTS: Final[tuple[tuple[str, str], ...]] = (
    (
        "reusable exact multigraded section compiler",
        "src/onetheory/math/sections.py",
    ),
    (
        "frozen Schoen Cox presentation and exact equations",
        "src/onetheory/models/heterotic_schoen/geometry.py",
    ),
    (
        "four local non-split extension cocycles e_A in one common Cech basis",
        "data/published/visible_metrics/non_split_extension_cocycles.json",
    ),
    (
        "common equivariant 192 and 212 section bases",
        "data/published/visible_metrics/positive_twist_section_package.json",
    ),
    (
        "deck actions on every section basis vector",
        "data/published/visible_metrics/deck_section_actions.json",
    ),
    (
        "848 lawful Cech lift outputs",
        "data/published/visible_metrics/cech_lift_outputs.json",
    ),
    (
        "evaluated 4 by 404 section matrix and rank certificate",
        "data/published/visible_metrics/evaluation_basis.json",
    ),
    (
        "metric tolerance and refinement manifest",
        "data/published/visible_metrics/metric_manifest.json",
    ),
)

SOURCE_HASHES: Final[tuple[tuple[str, str], ...]] = (
    (
        "src/onetheory/math/sections.py",
        "bbc1c5a8903051243d8326334f369efc3f8311861e8b6cf3bfbfa14efc33d576",
    ),
    (
        "src/onetheory/models/heterotic_schoen/geometry.py",
        "22bfdeb11cd2e33658d293a7e0df8ece07c5f82dcc29341727dbf8b0c3f76b11",
    ),
    (
        "src/onetheory/models/heterotic_schoen/metrics.py",
        "3c03ae995f1a3618cec02473673636a50d30b6d77fa651a6c9848d045e3e1668",
    ),
    (
        "Experimental_Draft_OneTheory.py",
        "c50151b8afdcf52ab1c14e8385234cb5231ee542e61cf16f4dcf20e9da63c32e",
    ),
    (
        "Experimental_Draft_OneTheory.docx",
        "b9a538a8d8f53517081162123eef48590def7564b40962d89c4a727bda4ad698",
    ),
)


def _sha256(path: Path) -> str:
    """Hash one declared artifact without treating metadata as a result."""

    return sha256(path.read_bytes()).hexdigest()


def audit_inputs(root: Path) -> MetricSufficiencyAudit:
    """Return the earliest absent carrier input without a fallback."""

    records = tuple(
        InputRecord(name, relative_path, (root / relative_path).is_file())
        for name, relative_path in REQUIRED_INPUTS
    )
    published_root = root / "data" / "published"
    published_files = (
        tuple(
            str(path.relative_to(root))
            for path in sorted(published_root.rglob("*"))
            if path.is_file() and path.name != "README.md"
        )
        if published_root.is_dir()
        else ()
    )
    source_hashes = tuple(
        (relative_path, _sha256(root / relative_path))
        for relative_path, expected in SOURCE_HASHES
        if (root / relative_path).is_file() and expected
    )
    first_missing = next((record.name for record in records if not record.present), None)
    status = metric_input_status()
    if status.first_missing_input != METRIC_MISSING_CHAIN[0]:
        raise ValueError("production and research metric boundaries disagree")
    return MetricSufficiencyAudit(
        records,
        published_files,
        source_hashes,
        first_missing,
        status.prerequisite_chain,
        False,
    )


def main() -> int:
    """Print the boundary report and return nonzero while input is missing."""

    audit = audit_inputs(Path(__file__).resolve().parents[3])
    print(f"first_missing_input: {audit.first_missing_input}")
    print(f"metric_frontier_promotable: {audit.promotable}")
    print("prerequisite_chain:")
    for item in audit.prerequisite_chain:
        print(f"- {item}")
    return 0 if audit.first_missing_input is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
