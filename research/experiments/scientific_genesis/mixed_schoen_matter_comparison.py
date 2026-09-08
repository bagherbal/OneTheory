"""Compare direct matter tensors through the lawful grouped contraction.

Owns:
    Exact homological-perturbation projection, strict re-inclusion, and
    equivariant Reynolds projection of the four split matter products.

Depends on:
    The strict mixed-Schoen matter tensors, the certified four-factor Cech
    contraction, exact deck actions, and Eisenstein arithmetic.

Must not:
    Fit correction coefficients, identify fiber covers by substitution,
    choose an extension point, normalize a trace, or report a Yukawa coupling.

Phase 0:
    Research-only chain comparison at the flavor frontier.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .mixed_schoen_chain_actions import (
    _full_action,
    _perturbed_inclusion,
)
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalCochain,
    chain_diagonal_perturbation,
    full_chain_diagonal_differential,
)
from .mixed_schoen_chain_transfer import (
    _homotopy,
    _include,
    _projected_coordinates,
    _reduced_entries,
)
from .mixed_schoen_matter_tensor import split_matter_tensor_audit

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_matter_comparison.json"

Character = tuple[int, int]


def _cochain_digest(cochain: ChainDiagonalCochain) -> str:
    """Hash one exact sparse chain-diagonal cochain deterministically."""

    digest = hashlib.sha256()
    for basis, coefficient in cochain.terms:
        component = basis.component
        record = (
            component.object_index,
            component.subset,
            basis.monomials,
            basis.cell,
            coefficient.a.numerator,
            coefficient.a.denominator,
            coefficient.b.numerator,
            coefficient.b.denominator,
        )
        digest.update(repr(record).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _perturbed_projection_inclusion(
    cochain: ChainDiagonalCochain,
    degree: int,
) -> tuple[ChainDiagonalCochain, int]:
    """Apply ``p (1 + Delta h)^-1`` and include its reduced coordinates."""

    values: dict[int, Eisenstein] = {}
    current = cochain
    depth = 0
    while not current.is_zero():
        for index, coefficient in _projected_coordinates(current, degree).items():
            values[index] = values.get(index, Eisenstein(0)) + coefficient
        current = chain_diagonal_perturbation(_homotopy(current)).scale(-1)
        depth += 1
        if depth > 24:
            raise ValueError("the matter comparison projection did not terminate")
    entries = _reduced_entries(degree)
    result = ChainDiagonalCochain()
    for index, coefficient in sorted(values.items()):
        if not coefficient.is_zero():
            result = result + _include(entries[index]).scale(coefficient)
    return result, depth


def _character_project(
    cochain: ChainDiagonalCochain,
    character: Character,
) -> ChainDiagonalCochain:
    """Apply the normalized exact joint-character Reynolds projector."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    total = ChainDiagonalCochain()
    p_power = cochain
    for p_exponent in range(3):
        term = p_power
        for t_exponent in range(3):
            weight = OMEGA ** (-character[0] * p_exponent - character[1] * t_exponent)
            total = total + term.scale(weight)
            term = _full_action(term, actions["T"])
        p_power = _full_action(p_power, actions["P"])
    return total.scale(Eisenstein(1) / 9)


def _has_character(
    cochain: ChainDiagonalCochain,
    character: Character,
) -> bool:
    """Check both exact deck-generator eigenvalue equations."""

    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    return all(
        _full_action(cochain, actions[name]) == cochain.scale(OMEGA ** character[index])
        for index, name in enumerate(("P", "T"))
    )


@dataclass(frozen=True, slots=True)
class MatterComparisonWitness:
    """One exact equivariant comparison for a split family slot."""

    row: int
    column: int
    character: Character
    direct_product: ChainDiagonalCochain
    direct_residual: ChainDiagonalCochain
    reduced_representative: ChainDiagonalCochain
    strict_representative: ChainDiagonalCochain
    equivariant_representative: ChainDiagonalCochain
    correction: ChainDiagonalCochain
    projection_depth: int
    inclusion_depth: int
    projection_idempotent: bool
    strict_representative_is_cycle: bool
    equivariant_representative_is_cycle: bool
    correction_closes_direct_residual: bool
    character_exact: bool

    @property
    def exact(self) -> bool:
        """Return every chain, character, and nonzero comparison gate."""

        return (
            bool(self.reduced_representative.terms)
            and bool(self.equivariant_representative.terms)
            and self.projection_idempotent
            and self.strict_representative_is_cycle
            and self.equivariant_representative_is_cycle
            and self.correction_closes_direct_residual
            and self.character_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact comparison gates and content digests."""

        return {
            "row": self.row,
            "column": self.column,
            "character_exponents": list(self.character),
            "direct_product_term_count": len(self.direct_product.terms),
            "direct_residual_term_count": len(self.direct_residual.terms),
            "reduced_representative_term_count": len(self.reduced_representative.terms),
            "strict_representative_term_count": len(self.strict_representative.terms),
            "equivariant_representative_term_count": len(self.equivariant_representative.terms),
            "correction_term_count": len(self.correction.terms),
            "projection_depth": self.projection_depth,
            "inclusion_depth": self.inclusion_depth,
            "direct_product_digest": _cochain_digest(self.direct_product),
            "direct_residual_digest": _cochain_digest(self.direct_residual),
            "reduced_representative_digest": _cochain_digest(self.reduced_representative),
            "strict_representative_digest": _cochain_digest(self.strict_representative),
            "equivariant_representative_digest": _cochain_digest(self.equivariant_representative),
            "correction_digest": _cochain_digest(self.correction),
            "projection_idempotent": self.projection_idempotent,
            "strict_representative_is_cycle": self.strict_representative_is_cycle,
            "equivariant_representative_is_cycle": (self.equivariant_representative_is_cycle),
            "correction_closes_direct_residual": (self.correction_closes_direct_residual),
            "character_exact": self.character_exact,
            "exact": self.exact,
        }


@cache
def mixed_schoen_matter_comparison() -> tuple[MatterComparisonWitness, ...]:
    """Construct exact equivariant comparisons for all split matter products."""

    audit = split_matter_tensor_audit()
    residuals = {(row, column): residual for row, column, residual in audit.residuals}
    witnesses = []
    for row, column, product in audit.products:
        reduced, projection_depth = _perturbed_projection_inclusion(product, 2)
        strict, inclusion_depth = _perturbed_inclusion(reduced)
        equivariant = _character_project(strict, audit.product_character)
        projected_again, _depth = _perturbed_projection_inclusion(strict, 2)
        correction = equivariant + product.scale(-1)
        witness = MatterComparisonWitness(
            row,
            column,
            audit.product_character,
            product,
            residuals[(row, column)],
            reduced,
            strict,
            equivariant,
            correction,
            projection_depth,
            inclusion_depth,
            projected_again == reduced,
            full_chain_diagonal_differential(strict).is_zero(),
            full_chain_diagonal_differential(equivariant).is_zero(),
            full_chain_diagonal_differential(correction) == residuals[(row, column)].scale(-1),
            _has_character(equivariant, audit.product_character),
        )
        if not witness.exact:
            raise ValueError(
                f"the exact equivariant matter chain comparison failed: slot=({row}, {column})"
            )
        witnesses.append(witness)
    return tuple(witnesses)


def write_mixed_schoen_matter_comparison(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed exact matter comparison audit."""

    witnesses = mixed_schoen_matter_comparison()
    digests = tuple(_cochain_digest(witness.equivariant_representative) for witness in witnesses)
    payload: dict[str, object] = {
        "schema": "mixed-schoen-matter-comparison-v1",
        "coefficient_field": "Q(omega)",
        "comparison": (
            "finite HPL projection, strict HPL inclusion, and normalized "
            "joint-character Reynolds projection"
        ),
        "family_slots": [[witness.row, witness.column] for witness in witnesses],
        "witnesses": [witness.as_record() for witness in witnesses],
        "all_comparisons_exact": all(witness.exact for witness in witnesses),
        "equivariant_representatives_are_distinct": len(set(digests)) == 4,
        "direct_product_hull_available": True,
        "fiber_cover_substitution_used": False,
        "extension_point_selected": False,
        "cyclic_trace_available": False,
        "holomorphic_yukawa_matrix_available": False,
        "next_required_object": (
            "the determinant pairing and cyclic trace on the exact restricted matter-product hull"
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
    """Regenerate the exact matter chain-comparison artifact."""

    payload = write_mixed_schoen_matter_comparison()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"all_comparisons_exact: {payload['all_comparisons_exact']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "MatterComparisonWitness",
    "OUTPUT",
    "mixed_schoen_matter_comparison",
    "write_mixed_schoen_matter_comparison",
]
