"""Audit the exact inputs required for the two physical seed Pfaffians.

Owns:
    Deterministic presence and hash checks for ambient geometry, conic
    embeddings, bundle restrictions, relative duality, and line conventions.

Depends on:
    `pathlib`, SHA-256, and the production conic-Pfaffian boundary contract.

Must not:
    Treat orbit counts or witness quartics as input, create restriction maps,
    evaluate Pfaffians, assign phases, or promote an unresolved result.

Phase 0:
    Sufficiency audit only; reconstruction stops at the first absent object.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final

from onetheory.models.heterotic_schoen.instantons import (
    CONIC_PFAFFIAN_MISSING_CHAIN,
    conic_pfaffian_input_status,
)


@dataclass(frozen=True, slots=True)
class InputRecord:
    """One required object and the exact repository path inspected for it."""

    name: str
    relative_path: str
    present: bool


@dataclass(frozen=True, slots=True)
class PfaffianSufficiencyAudit:
    """Immutable inventory of available and missing seed-Pfaffian inputs."""

    records: tuple[InputRecord, ...]
    published_files: tuple[str, ...]
    source_hashes: tuple[tuple[str, str], ...]
    first_missing_input: str | None
    prerequisite_chain: tuple[str, ...]
    promotable: bool


REQUIRED_INPUTS: Final[tuple[tuple[str, str], ...]] = (
    (
        "ambient Cox ring and multigrading",
        "src/onetheory/models/heterotic_schoen/geometry.py",
    ),
    (
        "defining equations of the Schoen threefold",
        "src/onetheory/models/heterotic_schoen/geometry.py",
    ),
    (
        "explicit embeddings of the two seed conics in frozen Schoen Cox coordinates",
        "data/published/conic_pfaffians/seed_conic_embeddings.json",
    ),
    (
        "visible-bundle constituent resolutions",
        "data/published/conic_pfaffians/visible_constituent_resolutions.json",
    ),
    (
        "outer extension and Serre representatives",
        "data/published/conic_pfaffians/outer_serre_representatives.json",
    ),
    (
        "restriction matrices for both seed conics",
        "data/published/conic_pfaffians/restriction_matrices.json",
    ),
    (
        "basis, sign, duality, and normalization conventions",
        "data/published/conic_pfaffians/line_map_conventions.json",
    ),
)

SOURCE_HASHES: Final[tuple[tuple[str, str], ...]] = (
    (
        "src/onetheory/models/heterotic_schoen/geometry.py",
        "22bfdeb11cd2e33658d293a7e0df8ece07c5f82dcc29341727dbf8b0c3f76b11",
    ),
    (
        "src/onetheory/models/heterotic_schoen/visible.py",
        "4ad5f63e5078234707c4410d6b093589d3c1352f9dbf099024c6997dd2bcdc29",
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
    """Hash one declared artifact without interpreting it as a physical map."""

    return sha256(path.read_bytes()).hexdigest()


def audit_inputs(root: Path) -> PfaffianSufficiencyAudit:
    """Return the earliest absent input without constructing a replacement."""

    records = tuple(
        InputRecord(name, relative_path, (root / relative_path).is_file())
        for name, relative_path in REQUIRED_INPUTS
    )
    published_root = root / "data" / "published" / "conic_pfaffians"
    published_files = tuple(
        str(path.relative_to(root))
        for path in sorted(published_root.rglob("*"))
        if path.is_file() and path.name != "README.md"
    ) if published_root.is_dir() else ()
    source_hashes = tuple(
        (relative_path, _sha256(root / relative_path))
        for relative_path, _ in SOURCE_HASHES
        if (root / relative_path).is_file()
    )
    first_missing = next((record.name for record in records if not record.present), None)
    status = conic_pfaffian_input_status()
    if status.first_missing_input != CONIC_PFAFFIAN_MISSING_CHAIN[0]:
        raise ValueError("production and research conic boundaries disagree")
    return PfaffianSufficiencyAudit(
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
    print(f"physical_pfaffian_promotable: {audit.promotable}")
    print("prerequisite_chain:")
    for item in audit.prerequisite_chain:
        print(f"- {item}")
    return 0 if audit.first_missing_input is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
