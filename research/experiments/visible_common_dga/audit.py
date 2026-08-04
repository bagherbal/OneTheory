"""Audit the serialized inputs required for the physical common-DGA package.

Owns:
    Deterministic presence checks for the carrier-specific input manifest and
    the first missing prerequisite report.

Depends on:
    `pathlib`, exact source hashes, and the production common-DGA contract.

Must not:
    Infer representatives from dimensions, synthesize matrices, evaluate
    physical traces, or promote research results into production.

Phase 0:
    Sufficiency audit only; reconstruction halts at the first absent input.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final

from onetheory.models.heterotic_schoen.flavor import (
    COMMON_DGA_MISSING_CHAIN,
    f3_common_cyclic_contract,
)


@dataclass(frozen=True, slots=True)
class InputRecord:
    """One required carrier input and its observed repository status."""

    name: str
    relative_path: str
    present: bool


@dataclass(frozen=True, slots=True)
class SufficiencyAudit:
    """Immutable result of the common-DGA input sufficiency audit."""

    records: tuple[InputRecord, ...]
    published_files: tuple[str, ...]
    source_hashes: tuple[tuple[str, str], ...]
    first_missing_input: str | None
    prerequisite_chain: tuple[str, ...]
    promotable: bool


REQUIRED_INPUTS: Final[tuple[tuple[str, str], ...]] = (
    (
        "carrier-specific V1/V2 resolutions in a synchronized common Cech-Koszul basis",
        "data/published/visible_common_dga/v1_v2_resolutions.json",
    ),
    (
        "common Cech cover and Koszul ordering",
        "data/published/visible_common_dga/common_cech_koszul_ordering.json",
    ),
    (
        "forward hypercocycles",
        "data/published/visible_common_dga/forward_hypercocycles.json",
    ),
    (
        "reverse hypercocycles",
        "data/published/visible_common_dga/reverse_hypercocycles.json",
    ),
    (
        "matter and Higgs character data",
        "data/published/visible_common_dga/matter_higgs_character_data.json",
    ),
    (
        "deck action on every graded component",
        "data/published/visible_common_dga/deck_action_on_complex.json",
    ),
    (
        "sign, basis, and trace conventions",
        "data/published/visible_common_dga/sign_basis_trace_conventions.json",
    ),
)

SOURCE_HASHES: Final[tuple[tuple[str, str], ...]] = (
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
    """Hash one source artifact without interpreting it as a physical input."""

    return sha256(path.read_bytes()).hexdigest()


def audit_inputs(root: Path) -> SufficiencyAudit:
    """Return the first absent required object without constructing a fallback."""

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
    contract = f3_common_cyclic_contract()
    physical_available = contract["physical_carrier_package_available"] is True
    if physical_available:
        raise ValueError("the physical contract cannot be available without a promoted package")
    return SufficiencyAudit(
        records,
        published_files,
        source_hashes,
        first_missing,
        COMMON_DGA_MISSING_CHAIN,
        first_missing is None and physical_available,
    )


def main() -> int:
    """Print a deterministic audit summary and return a shell status."""

    audit = audit_inputs(Path(__file__).resolve().parents[4])
    print(f"first_missing_input: {audit.first_missing_input}")
    print(f"physical_package_promotable: {audit.promotable}")
    print("prerequisite_chain:")
    for item in audit.prerequisite_chain:
        print(f"- {item}")
    return 0 if audit.first_missing_input is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
