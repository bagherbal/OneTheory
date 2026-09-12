"""Derive the exact associated-graded Dirac-neutrino Yukawa matrix.

Owns:
    Four independently reconstructed split-family determinant contractions,
    their scalar residues, and exact boundary witnesses for every zero entry.

Depends on:
    Source-derived neutrino matter sectors, the strict up-Higgs cocycle, the
    grouped chain comparison, and the fixed ambient residue normalization.

Must not:
    Select an extension point, omit universal higher corrections, infer a
    nonzero coefficient, or call a holomorphic matrix physically normalized.

Phase 0:
    Research-only tree-level test on the Dirac-neutrino flavor path.
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

from .mixed_schoen_chain_actions import (
    OUTPUT as HIGGS_ARTIFACT,
)
from .mixed_schoen_chain_actions import load_certified_higgs_representative
from .mixed_schoen_matter_comparison import (
    _cochain_digest,
    mixed_schoen_matter_comparison_for_slot,
)
from .mixed_schoen_matter_representatives import (
    mixed_schoen_matter_representatives,
)
from .mixed_schoen_neutrino_matter_lifts import (
    NEUTRINO_MATTER_CHARACTERS,
)
from .mixed_schoen_neutrino_matter_lifts import (
    OUTPUT as MATTER_LIFTS_ARTIFACT,
)
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
    "mixed_schoen_neutrino_tree_matrix.json"
)


def _verified_digest(path: Path, gate: str) -> str:
    """Return an upstream digest only after its exact gate passes."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if not isinstance(digest, str) or digest != _canonical_digest(payload):
        raise ValueError(f"upstream artifact digest failed: {path.name}")
    if payload.get(gate) is not True:
        raise ValueError(f"upstream artifact gate failed: {path.name}")
    return digest


@dataclass(frozen=True, slots=True)
class NeutrinoTreeEntry:
    """One exact determinant residue and its global boundary certificate."""

    row: int
    column: int
    value: Eisenstein
    matter_term_count: int
    matter_digest: str
    scalar_term_count: int
    scalar_digest: str
    scalar_is_cycle: bool
    projection_depth: int
    primitive_term_count: int
    primitive_digest: str
    primitive_depth: int
    primitive_reconstruction_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether the zero residue has a reconstructed global boundary."""

        return (
            self.matter_term_count > 0
            and self.scalar_term_count > 0
            and self.scalar_is_cycle
            and self.projection_depth > 0
            and self.value.is_zero()
            and self.primitive_term_count > 0
            and self.primitive_depth > 0
            and self.primitive_reconstruction_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize one exact entry without treating zero as an assumption."""

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
            "primitive_term_count": self.primitive_term_count,
            "primitive_digest": self.primitive_digest,
            "primitive_depth": self.primitive_depth,
            "primitive_reconstruction_exact": (
                self.primitive_reconstruction_exact
            ),
            "exact": self.exact,
        }


def _trace_slot(slot: tuple[int, int]) -> NeutrinoTreeEntry:
    """Reconstruct and contract one ordered family slot in isolation."""

    row, column = slot
    row_character, column_character = NEUTRINO_MATTER_CHARACTERS
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
    primitive, primitive_depth = scalar_primitive(scalar)
    result = NeutrinoTreeEntry(
        row,
        column,
        value,
        len(witness.equivariant_representative.terms),
        _cochain_digest(witness.equivariant_representative),
        len(scalar.terms),
        _full_cochain_digest(scalar),
        scalar_is_cycle,
        projection_depth,
        len(primitive.terms),
        _full_cochain_digest(primitive),
        primitive_depth,
        scalar_full_differential(primitive) == scalar,
    )
    if not result.exact:
        raise ValueError(
            "the Dirac-neutrino tree entry failed: "
            f"slot=({row}, {column})"
        )
    return result


@dataclass(frozen=True, slots=True)
class HolomorphicNeutrinoTreeMatrix:
    """The complete exact associated-graded Dirac-neutrino matrix."""

    entries: tuple[NeutrinoTreeEntry, ...]

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
            and self.matrix_rank == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the complete matrix and its scoped no-go evidence."""

        return {
            "row_matter_character_exponents": list(
                NEUTRINO_MATTER_CHARACTERS[0]
            ),
            "column_matter_character_exponents": list(
                NEUTRINO_MATTER_CHARACTERS[1]
            ),
            "higgs_character_exponents": [0, 1],
            "family_basis": ["V1", "V2:1", "V2:2"],
            "character_allowed_slots": [list(slot) for slot in ALLOWED_SLOTS],
            "structural_zero_slots": [list(slot) for slot in FORBIDDEN_SLOTS],
            "entries": [entry.as_record() for entry in self.entries],
            "matrix": [
                [str(self.matrix[row][column]) for column in range(3)]
                for row in range(3)
            ],
            "matrix_rank": self.matrix_rank,
            "all_zero_entries_have_exact_primitives": all(
                entry.primitive_reconstruction_exact for entry in self.entries
            ),
            "tree_level_nontrivial": self.matrix_rank > 0,
            "exact": self.exact,
        }


@cache
def mixed_schoen_holomorphic_neutrino_tree_matrix(
) -> HolomorphicNeutrinoTreeMatrix:
    """Evaluate all four allowed Dirac-neutrino entries independently."""

    mixed_schoen_matter_representatives()
    load_certified_higgs_representative()
    with ProcessPoolExecutor(max_workers=len(ALLOWED_SLOTS)) as executor:
        entries = tuple(executor.map(_trace_slot, ALLOWED_SLOTS))
    result = HolomorphicNeutrinoTreeMatrix(entries)
    if not result.exact:
        raise ValueError("the complete Dirac-neutrino tree matrix failed")
    return result


def write_neutrino_tree_matrix(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed Dirac-neutrino tree no-go certificate."""

    result = mixed_schoen_holomorphic_neutrino_tree_matrix()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-holomorphic-neutrino-tree-matrix-v1",
        "coefficient_field": "Q(omega)",
        "trace_normalization": (
            "the ordered ambient canonical Laurent residue generator has trace one"
        ),
        "prerequisite_artifact_digests": {
            "neutrino_matter_lifts": _verified_digest(
                MATTER_LIFTS_ARTIFACT,
                "all_neutrino_matter_lifts_exact",
            ),
            "strict_up_higgs": _verified_digest(
                HIGGS_ARTIFACT,
                "full_representative_has_strict_character",
            ),
        },
        "dirac_neutrino_tree_matrix": result.as_record(),
        "classification": "SCOPED_TREE_LEVEL_NO_GO",
        "scope": (
            "the associated-graded split-family product with the strict up-Higgs "
            "class; universal parameter corrections remain to be evaluated"
        ),
        "complete_tree_level_neutrino_matrix_available": True,
        "nontrivial_holomorphic_neutrino_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "the complete first mathematically allowed universal Dirac-neutrino "
            "coefficient matrix"
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
    """Regenerate the exact neutrino tree matrix and print its next gate."""

    payload = write_neutrino_tree_matrix()
    matrix = payload["dirac_neutrino_tree_matrix"]
    if not isinstance(matrix, dict):
        raise TypeError("the serialized neutrino matrix record is invalid")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"matrix_rank: {matrix['matrix_rank']}")
    print(f"classification: {payload['classification']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "HolomorphicNeutrinoTreeMatrix",
    "NeutrinoTreeEntry",
    "OUTPUT",
    "mixed_schoen_holomorphic_neutrino_tree_matrix",
    "write_neutrino_tree_matrix",
]
