"""Derive the convention-corrected associated-graded down Yukawa matrix.

Owns:
    Four independently reconstructed down-sector determinant contractions,
    their exact scalar residues, and boundary witnesses for every zero entry.

Depends on:
    Convention-corrected down matter sectors, the physical down-Higgs cocycle,
    the grouped chain comparison, and the fixed ambient residue normalization.

Must not:
    Select an extension point, assume a zero residue, omit later universal
    corrections, or call a holomorphic matrix physically normalized.

Phase 0:
    Research-only tree-level calculation on the physical down-flavor path.
"""

from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .mixed_schoen_chain_actions import OUTPUT as HIGGS_ARTIFACT
from .mixed_schoen_chain_actions import load_certified_higgs_representative
from .mixed_schoen_character_convention import OUTPUT as CONVENTION_ARTIFACT
from .mixed_schoen_down_matter_lifts import (
    FORWARD_DOWN_HIGGS_CHARACTER,
    FORWARD_MATTER_CHARACTERS,
    SOURCE_DOWN_HIGGS_CHARACTER,
    SOURCE_MATTER_CHARACTERS,
)
from .mixed_schoen_down_matter_lifts import OUTPUT as DOWN_LIFTS_ARTIFACT
from .mixed_schoen_matter_comparison import (
    _cochain_digest,
    mixed_schoen_matter_comparison_for_slot,
)
from .mixed_schoen_matter_representatives import mixed_schoen_matter_representatives
from .mixed_schoen_yukawa_trace import (
    ALLOWED_SLOTS,
    FORBIDDEN_SLOTS,
    _full_cochain_digest,
    contract_with_strict_higgs,
    scalar_full_differential,
    scalar_primitive,
    scalar_residue,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_down_tree_matrix.json"
)


def _verified_digest(path: Path, gate: str) -> str:
    """Return an upstream digest only after its declared exact gate passes."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest


def _verified_down_inputs() -> tuple[str, str]:
    """Verify both physical labels and their source-to-forward convention."""

    payload = json.loads(DOWN_LIFTS_ARTIFACT.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    physical_slice = payload.get("physical_slice")
    prerequisites = payload.get("prerequisite_artifact_digests")
    convention_digest = _verified_digest(CONVENTION_ARTIFACT, "exact")
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("exact") is not True
        or not isinstance(physical_slice, dict)
        or not isinstance(prerequisites, dict)
        or physical_slice.get("source_matter_character_exponents")
        != [list(character) for character in SOURCE_MATTER_CHARACTERS]
        or physical_slice.get("forward_matter_character_exponents")
        != [list(character) for character in FORWARD_MATTER_CHARACTERS]
        or physical_slice.get("source_higgs_character_exponents")
        != list(SOURCE_DOWN_HIGGS_CHARACTER)
        or physical_slice.get("forward_higgs_character_exponents")
        != list(FORWARD_DOWN_HIGGS_CHARACTER)
        or prerequisites.get("character_convention") != convention_digest
    ):
        raise ValueError("the convention-corrected down input certificate failed")
    return digest, convention_digest


@dataclass(frozen=True, slots=True)
class DownTreeEntry:
    """One exact determinant residue with a boundary witness when it vanishes."""

    row: int
    column: int
    value: Eisenstein
    matter_term_count: int
    matter_digest: str
    scalar_term_count: int
    scalar_digest: str
    scalar_is_cycle: bool
    projection_depth: int
    primitive_term_count: int | None
    primitive_digest: str | None
    primitive_depth: int | None
    primitive_reconstruction_exact: bool | None

    @property
    def zero_boundary_certificate_exact(self) -> bool:
        """Require a primitive exactly when the residue is zero."""

        if not self.value.is_zero():
            return (
                self.primitive_term_count is None
                and self.primitive_digest is None
                and self.primitive_depth is None
                and self.primitive_reconstruction_exact is None
            )
        return (
            self.primitive_term_count is not None
            and self.primitive_term_count > 0
            and self.primitive_digest is not None
            and self.primitive_depth is not None
            and self.primitive_depth > 0
            and self.primitive_reconstruction_exact is True
        )

    @property
    def exact(self) -> bool:
        """Return whether the residue or its zero-boundary proof is complete."""

        return (
            self.matter_term_count > 0
            and self.scalar_term_count > 0
            and self.scalar_is_cycle
            and self.projection_depth > 0
            and self.zero_boundary_certificate_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one entry without presuming whether its residue vanishes."""

        boundary = None
        if self.value.is_zero():
            boundary = {
                "primitive_term_count": self.primitive_term_count,
                "primitive_digest": self.primitive_digest,
                "primitive_depth": self.primitive_depth,
                "primitive_reconstruction_exact": (
                    self.primitive_reconstruction_exact
                ),
            }
        return {
            "row": self.row,
            "column": self.column,
            "value": str(self.value),
            "matter_term_count": self.matter_term_count,
            "matter_digest": self.matter_digest,
            "scalar_term_count": self.scalar_term_count,
            "scalar_digest": self.scalar_digest,
            "scalar_is_cycle": self.scalar_is_cycle,
            "projection_depth": self.projection_depth,
            "zero_boundary_witness": boundary,
            "exact": self.exact,
        }


def _trace_slot(slot: tuple[int, int]) -> DownTreeEntry:
    """Reconstruct and contract one ordered physical down-family slot."""

    row, column = slot
    row_character, column_character = FORWARD_MATTER_CHARACTERS
    witness = mixed_schoen_matter_comparison_for_slot(
        row_character,
        column_character,
        row,
        column,
    )
    higgs = load_certified_higgs_representative()
    scalar = contract_with_strict_higgs(
        witness.equivariant_representative,
        higgs,
    )
    scalar_is_cycle = scalar_full_differential(scalar).is_zero()
    value, projection_depth = scalar_residue(scalar)
    primitive_term_count = None
    primitive_digest = None
    primitive_depth = None
    primitive_reconstruction_exact = None
    if value.is_zero():
        primitive, primitive_depth = scalar_primitive(scalar)
        primitive_term_count = len(primitive.terms)
        primitive_digest = _full_cochain_digest(primitive)
        primitive_reconstruction_exact = (
            scalar_full_differential(primitive) == scalar
        )
    result = DownTreeEntry(
        row,
        column,
        value,
        len(witness.equivariant_representative.terms),
        _cochain_digest(witness.equivariant_representative),
        len(scalar.terms),
        _full_cochain_digest(scalar),
        scalar_is_cycle,
        projection_depth,
        primitive_term_count,
        primitive_digest,
        primitive_depth,
        primitive_reconstruction_exact,
    )
    if not result.exact:
        raise ValueError(
            "the convention-corrected down tree entry failed: "
            f"slot=({row}, {column})"
        )
    return result


@dataclass(frozen=True, slots=True)
class HolomorphicDownTreeMatrix:
    """The complete exact associated-graded physical down matrix."""

    entries: tuple[DownTreeEntry, ...]

    @property
    def matrix(self) -> Matrix:
        """Return the exact three-family matrix in the declared family bases."""

        values = {
            (entry.row, entry.column): entry.value for entry in self.entries
        }
        return Matrix(
            tuple(
                tuple(
                    values.get((row, column), Eisenstein(0))
                    for column in range(3)
                )
                for row in range(3)
            ),
            scalar_type=Eisenstein,
        )

    @property
    def matrix_rank(self) -> int:
        """Return the exact associated-graded matrix rank."""

        return self.matrix.rank()

    @property
    def exact(self) -> bool:
        """Return whether every allowed slot and structural zero is certified."""

        return (
            tuple((entry.row, entry.column) for entry in self.entries)
            == ALLOWED_SLOTS
            and all(entry.exact for entry in self.entries)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the complete exact tree matrix without a rank assumption."""

        return {
            "source_row_matter_character_exponents": list(
                SOURCE_MATTER_CHARACTERS[0]
            ),
            "source_column_matter_character_exponents": list(
                SOURCE_MATTER_CHARACTERS[1]
            ),
            "forward_row_matter_character_exponents": list(
                FORWARD_MATTER_CHARACTERS[0]
            ),
            "forward_column_matter_character_exponents": list(
                FORWARD_MATTER_CHARACTERS[1]
            ),
            "source_higgs_character_exponents": list(
                SOURCE_DOWN_HIGGS_CHARACTER
            ),
            "forward_higgs_character_exponents": list(
                FORWARD_DOWN_HIGGS_CHARACTER
            ),
            "family_basis": ["V1", "V2:1", "V2:2"],
            "character_allowed_slots": [list(slot) for slot in ALLOWED_SLOTS],
            "structural_zero_slots": [list(slot) for slot in FORBIDDEN_SLOTS],
            "entries": [entry.as_record() for entry in self.entries],
            "matrix": [
                [str(self.matrix[row][column]) for column in range(3)]
                for row in range(3)
            ],
            "matrix_rank": self.matrix_rank,
            "zero_entries_have_exact_primitives": all(
                entry.zero_boundary_certificate_exact
                for entry in self.entries
                if entry.value.is_zero()
            ),
            "tree_level_nontrivial": self.matrix_rank > 0,
            "exact": self.exact,
        }


@cache
def mixed_schoen_holomorphic_down_tree_matrix() -> HolomorphicDownTreeMatrix:
    """Evaluate all four character-allowed physical down entries independently."""

    mixed_schoen_matter_representatives()
    load_certified_higgs_representative()
    with ProcessPoolExecutor(max_workers=len(ALLOWED_SLOTS)) as executor:
        entries = tuple(executor.map(_trace_slot, ALLOWED_SLOTS))
    result = HolomorphicDownTreeMatrix(entries)
    if not result.exact:
        raise ValueError("the complete convention-corrected down tree matrix failed")
    return result


def write_down_tree_matrix(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed physical down tree certificate."""

    result = mixed_schoen_holomorphic_down_tree_matrix()
    down_lifts_digest, convention_digest = _verified_down_inputs()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-holomorphic-down-tree-matrix-v1",
        "coefficient_field": "Q(omega)",
        "trace_normalization": (
            "the ordered ambient canonical Laurent residue generator has trace one"
        ),
        "prerequisite_artifact_digests": {
            "character_convention": convention_digest,
            "down_matter_lifts": down_lifts_digest,
            "strict_forward_higgs": _verified_digest(
                HIGGS_ARTIFACT,
                "full_representative_has_strict_character",
            ),
        },
        "down_tree_matrix": result.as_record(),
        "classification": (
            "EXACT_NONTRIVIAL_TREE_MATRIX"
            if result.matrix_rank > 0
            else "SCOPED_TREE_LEVEL_NO_GO"
        ),
        "scope": (
            "the associated-graded split-family product with the physical "
            "down-Higgs class; universal parameter corrections remain to be "
            "evaluated"
        ),
        "complete_tree_level_down_matrix_available": True,
        "nontrivial_holomorphic_down_matrix_available": result.matrix_rank > 0,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "exact": result.exact,
        "next_required_object": (
            "every exterior-allowed universal down-matrix coefficient"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return payload


def main() -> int:
    """Regenerate the exact down tree matrix and print its next gate."""

    payload = write_down_tree_matrix()
    matrix = payload["down_tree_matrix"]
    if not isinstance(matrix, dict):
        raise TypeError("the serialized down matrix record is invalid")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"matrix_rank: {matrix['matrix_rank']}")
    print(f"classification: {payload['classification']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DownTreeEntry",
    "HolomorphicDownTreeMatrix",
    "OUTPUT",
    "mixed_schoen_holomorphic_down_tree_matrix",
    "write_down_tree_matrix",
]
