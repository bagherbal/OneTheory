"""Audit exact inputs for the bounded hidden-bundle objective-(28) search.

Owns:
    Deterministic presence and hash checks for support records, candidate maps,
    multigraded charts, equivariance, curve restrictions, and stability data.

Depends on:
    `pathlib`, SHA-256, and the production hidden-bundle boundary contract.

Must not:
    Infer maps from ranks, prove global constant rank from samples, fabricate
    descent or stability, or report a hidden spectrum without a bundle.

Phase 0:
    Sufficiency audit only; reconstruction stops at the first absent input.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final

from onetheory.models.heterotic_schoen.hidden import (
    HIDDEN_BUNDLE_MISSING_CHAIN,
    hidden_bundle_input_status,
)


@dataclass(frozen=True, slots=True)
class InputRecord:
    """One required hidden-bundle object and its inspected repository path."""

    name: str
    relative_path: str
    present: bool


@dataclass(frozen=True, slots=True)
class HiddenSufficiencyAudit:
    """Immutable inventory of the hidden-bundle reconstruction inputs."""

    records: tuple[InputRecord, ...]
    published_files: tuple[str, ...]
    source_hashes: tuple[tuple[str, str], ...]
    first_missing_input: str | None
    prerequisite_chain: tuple[str, ...]
    promotable: bool


REQUIRED_INPUTS: Final[tuple[tuple[str, str], ...]] = (
    (
        "all 44 objective-(28) support-pattern records with exact map data",
        "data/published/hidden_bundle/objective28_supports.json",
    ),
    (
        "candidate 750 exact F and G polynomial matrices",
        "data/published/hidden_bundle/candidate750_F_G.json",
    ),
    (
        "line-bundle degrees and ordered bases",
        "data/published/hidden_bundle/multigraded_bases.json",
    ),
    (
        "irrelevant ideals and affine-chart presentations",
        "data/published/hidden_bundle/charts_and_ideals.json",
    ),
    (
        "Z3^2 actions and honest linearizations",
        "data/published/hidden_bundle/equivariant_actions.json",
    ),
    (
        "declared Chern target and normalization",
        "src/onetheory/models/heterotic_schoen/consistency.py",
    ),
    (
        "three retained curve seeds",
        "src/onetheory/models/heterotic_schoen/consistency.py",
    ),
)

SOURCE_HASHES: Final[tuple[tuple[str, str], ...]] = (
    (
        "src/onetheory/models/heterotic_schoen/hidden.py",
        "f6a97b773c6e4f13a2f870812972b1cfba6200ab850002bf4f66f1e4fac1d1b0",
    ),
    (
        "src/onetheory/models/heterotic_schoen/consistency.py",
        "5690787d2a66518525436ea9b7e2c48596194c11a3638c92c366277c120d4df3",
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
    """Hash one declared artifact without treating metadata as a bundle map."""

    return sha256(path.read_bytes()).hexdigest()


def audit_inputs(root: Path) -> HiddenSufficiencyAudit:
    """Return the earliest absent hidden input without a candidate fallback."""

    records = tuple(
        InputRecord(name, relative_path, (root / relative_path).is_file())
        for name, relative_path in REQUIRED_INPUTS
    )
    published_root = root / "data" / "published"
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
    status = hidden_bundle_input_status()
    if status.first_missing_input != HIDDEN_BUNDLE_MISSING_CHAIN[0]:
        raise ValueError("production and research hidden boundaries disagree")
    return HiddenSufficiencyAudit(
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
    print(f"hidden_bundle_promotable: {audit.promotable}")
    print("prerequisite_chain:")
    for item in audit.prerequisite_chain:
        print(f"- {item}")
    return 0 if audit.first_missing_input is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
