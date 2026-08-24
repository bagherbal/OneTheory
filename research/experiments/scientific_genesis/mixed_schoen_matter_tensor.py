"""Tensor strict constituent matter cocycles in the lawful diagonal complex.

Owns:
    Exact insertion of independent degree-zero fiber-cover units and the
    candidate tensor products needed to test the split matter-product slice.

Depends on:
    Strict mixed-Schoen matter representatives, the lawful four-factor chain
    diagonal, and exact deck actions over the Eisenstein field.

Must not:
    Identify shared fiber covers by substitution, choose an extension point,
    normalize a cyclic trace, or report a holomorphic Yukawa coefficient.

Phase 0:
    Research-only audit of matter products in the diagonal presentation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import OMEGA, Eisenstein
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.schoen_serre_outer_transfer import (
    SparseOuterCechCochain,
)
from research.experiments.computable_carrier.schoen_sparse_actions import (
    schoen_sparse_deck_actions,
)

from .diagonal_schoen_lines import Cell4, Monomial
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_chain_actions import _full_action
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalBasis,
    ChainDiagonalCochain,
    _object_indices,
    _simplex_cup,
    _target_component,
    full_chain_diagonal_differential,
)
from .mixed_schoen_matter_representatives import (
    MatterCharacterSector,
    mixed_schoen_matter_representatives,
)
from .mixed_schoen_universal_matter_lifts import (
    UP_HIGGS_CHARACTER,
    UP_MATTER_CHARACTERS,
)

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_matter_tensor_audit.json"

Character = tuple[int, int]


@dataclass(frozen=True, slots=True, order=True)
class IndependentMatterBasis:
    """One constituent matter term after inserting its new fiber-cover unit."""

    factor: int
    object_index: int
    subset: tuple[int, ...]
    object_degree: int
    monomials: tuple[Monomial, Monomial, Monomial, Monomial]
    cell: Cell4

    @property
    def cech_degree(self) -> int:
        """Return the four-factor product-cover degree."""

        return sum(len(simplex) - 1 for simplex in self.cell)

    @property
    def structural_degree(self) -> int:
        """Return object degree minus the owned Koszul degree."""

        return self.object_degree - len(self.subset)


@dataclass(frozen=True, slots=True)
class IndependentMatterCochain:
    """One exact constituent cochain lifted to the independent-cover ambient."""

    factor: int
    total_degree: int
    terms: tuple[tuple[IndependentMatterBasis, Eisenstein], ...]

    def __post_init__(self) -> None:
        if self.factor not in {1, 2}:
            raise ValueError("independent matter factors are one and two")
        if not self.terms:
            raise ValueError("a strict independent matter cochain cannot be zero")
        if any(basis.factor != self.factor for basis, _coefficient in self.terms):
            raise ValueError("independent matter support mixes constituent factors")


def _factor_subset(factor: int, summand: str) -> tuple[int, ...]:
    """Translate one factor-pure Schoen Koszul summand to diagonal indices."""

    allowed = (
        {"k0": (), "k1_x": (0,)}
        if factor == 1
        else {"k0": (), "k1_u": (1,)}
    )
    try:
        return allowed[summand]
    except KeyError as error:
        raise ValueError(
            "a matter cocycle uses a Koszul equation owned by the other factor"
        ) from error


def lift_matter_cochain(
    cochain: SparseOuterCechCochain,
    factor: int,
) -> IndependentMatterCochain:
    """Insert the missing independent fiber factor as the exact Cech unit."""

    degrees = {basis.total_degree for basis, _coefficient in cochain.terms}
    if len(degrees) != 1:
        raise ValueError("a strict matter cochain must be homogeneous")
    terms: list[tuple[IndependentMatterBasis, Eisenstein]] = []
    for basis, coefficient in cochain.terms:
        component = basis.component
        if component.right_index != 0:
            raise ValueError("matter representatives must be maps from the unit object")
        subset = _factor_subset(factor, component.koszul_summand)
        for vertex in range(2):
            if factor == 1:
                monomials = (
                    basis.x_monomial,
                    basis.p_monomial,
                    basis.u_monomial,
                    (0, 0),
                )
                cell: Cell4 = (
                    basis.cell[0],
                    basis.cell[2],
                    basis.cell[1],
                    (vertex,),
                )
            elif factor == 2:
                monomials = (
                    basis.x_monomial,
                    (0, 0),
                    basis.u_monomial,
                    basis.p_monomial,
                )
                cell = (
                    basis.cell[0],
                    (vertex,),
                    basis.cell[1],
                    basis.cell[2],
                )
            else:
                raise ValueError("independent matter factors are one and two")
            terms.append(
                (
                    IndependentMatterBasis(
                        factor,
                        component.left_index,
                        subset,
                        component.object_degree,
                        monomials,
                        cell,
                    ),
                    coefficient,
                )
            )
    return IndependentMatterCochain(factor, next(iter(degrees)), tuple(terms))


def _sum_monomials(left: Monomial, right: Monomial) -> Monomial:
    """Add one pair of exact Laurent exponent vectors."""

    return tuple(a + b for a, b in zip(left, right, strict=True))


def _cell_cup(left: Cell4, right: Cell4) -> tuple[int, Cell4] | None:
    """Cup two four-factor cells with the product-totalization sign."""

    products = tuple(
        _simplex_cup(left_simplex, right_simplex)
        for left_simplex, right_simplex in zip(left, right, strict=True)
    )
    if any(product is None for product in products):
        return None
    left_degrees = tuple(len(simplex) - 1 for simplex in left)
    right_degrees = tuple(len(simplex) - 1 for simplex in right)
    crossings = sum(
        left_degrees[right_slot] * right_degrees[left_slot]
        for left_slot in range(4)
        for right_slot in range(left_slot + 1, 4)
    )
    return (-1 if crossings % 2 else 1), cast(Cell4, products)


def external_matter_tensor(
    first: SparseOuterCechCochain,
    second: SparseOuterCechCochain,
) -> ChainDiagonalCochain:
    """Tensor one V1 and one V2 matter cochain on independent fiber covers."""

    left = lift_matter_cochain(first, 1)
    right = lift_matter_cochain(second, 2)
    objects = _object_indices()
    terms = []
    for left_basis, left_coefficient in left.terms:
        for right_basis, right_coefficient in right.terms:
            cell_product = _cell_cup(left_basis.cell, right_basis.cell)
            if cell_product is None:
                continue
            cell_sign, cell = cell_product
            subset = tuple(sorted((*left_basis.subset, *right_basis.subset)))
            if len(subset) != len(left_basis.subset) + len(right_basis.subset):
                continue
            target = _target_component(
                objects[(left_basis.object_index, right_basis.object_index)],
                subset,
            )
            monomials = cast(
                tuple[Monomial, Monomial, Monomial, Monomial],
                tuple(
                    _sum_monomials(left_monomial, right_monomial)
                    for left_monomial, right_monomial in zip(
                        left_basis.monomials,
                        right_basis.monomials,
                        strict=True,
                    )
                ),
            )
            internal_crossing = (
                -len(left_basis.subset) * right_basis.object_degree
                + left_basis.cech_degree * right_basis.structural_degree
            )
            first_cover_reordering = (
                (len(left_basis.cell[1]) - 1)
                * (len(left_basis.cell[2]) - 1)
            )
            second_cech_degree = sum(
                len(simplex) - 1 for simplex in cell[2:]
            )
            grouped_conjugation = (
                right_basis.structural_degree * second_cech_degree
            )
            sign_exponent = (
                internal_crossing
                + first_cover_reordering
                + grouped_conjugation
            )
            sign = cell_sign * (-1 if sign_exponent % 2 else 1)
            terms.append(
                (
                    ChainDiagonalBasis(target, monomials, cell),
                    left_coefficient * right_coefficient * sign,
                )
            )
    result = ChainDiagonalCochain(tuple(terms))
    expected_degree = left.total_degree + right.total_degree
    if any(basis.total_degree != expected_degree for basis, _coefficient in result.terms):
        raise ValueError("the external matter tensor changed total degree")
    return result


def _sector(
    sectors: tuple[MatterCharacterSector, ...],
    character: Character,
) -> MatterCharacterSector:
    """Return one uniquely identified strict matter character sector."""

    matches = tuple(item for item in sectors if item.character == character)
    if len(matches) != 1:
        raise ValueError("the requested matter character sector is not unique")
    return matches[0]


def _sum_character(left: Character, right: Character) -> Character:
    """Add two deck-character exponent pairs modulo three."""

    return ((left[0] + right[0]) % 3, (left[1] + right[1]) % 3)


@dataclass(frozen=True, slots=True)
class SplitMatterTensorAudit:
    """The exact direct-tensor audit for one three-family split slice."""

    row_character: Character
    column_character: Character
    products: tuple[tuple[int, int, ChainDiagonalCochain], ...]
    products_are_cycles: bool
    products_have_required_character: bool
    inserted_units_exact: bool

    @property
    def product_character(self) -> Character:
        """Return the deck character shared by every nonzero product."""

        return _sum_character(self.row_character, self.column_character)

    @property
    def total_character_is_invariant(self) -> bool:
        """Return whether product and required Higgs characters sum to zero."""

        return _sum_character(self.product_character, UP_HIGGS_CHARACTER) == (0, 0)

    @property
    def support(self) -> tuple[tuple[int, int], ...]:
        """Return the derived nonzero family-slot support."""

        return tuple((row, column) for row, column, _product in self.products)

    @property
    def direct_product_hull_available(self) -> bool:
        """Return whether the candidates are lawful cohomology products."""

        return (
            len(self.products) == 4
            and self.products_are_cycles
            and self.products_have_required_character
            and self.inserted_units_exact
            and self.total_character_is_invariant
        )

    @property
    def audit_exact(self) -> bool:
        """Return whether every prerequisite and obstruction gate was evaluated."""

        return (
            len(self.products) == 4
            and all(product.terms for _row, _column, product in self.products)
            and self.products_have_required_character
            and self.inserted_units_exact
            and self.total_character_is_invariant
            and not self.products_are_cycles
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact support without inventing the unresolved trace."""

        return {
            "schema": "mixed-schoen-matter-tensor-audit-v1",
            "coefficient_field": "Q(omega)",
            "row_character_exponents": list(self.row_character),
            "column_character_exponents": list(self.column_character),
            "product_character_exponents": list(self.product_character),
            "required_higgs_character_exponents": list(UP_HIGGS_CHARACTER),
            "family_basis": ["V1", "V2:1", "V2:2"],
            "candidate_nonzero_split_support": [list(item) for item in self.support],
            "candidate_products": [
                {
                    "row": row,
                    "column": column,
                    "term_count": len(product.terms),
                }
                for row, column, product in self.products
            ],
            "inserted_degree_zero_fiber_units_exact": self.inserted_units_exact,
            "all_products_are_full_chain_cycles": self.products_are_cycles,
            "all_products_have_required_character": (
                self.products_have_required_character
            ),
            "product_plus_higgs_character_is_invariant": (
                self.total_character_is_invariant
            ),
            "external_cover_substitution_used": False,
            "extension_point_selected": False,
            "direct_product_hull_available": self.direct_product_hull_available,
            "cyclic_trace_available": False,
            "holomorphic_yukawa_matrix_available": False,
            "next_required_object": (
                "an exact equivariant chain comparison lifting the strict matter "
                "cocycles into the four-factor grouped Higgs complex"
            ),
            "status": (
                "the canonical signed direct tensor preserves the required deck "
                "character but is not closed in the grouped Higgs differential"
            ),
            "audit_exact": self.audit_exact,
        }


@cache
def split_matter_tensor_audit() -> SplitMatterTensorAudit:
    """Audit the canonical direct tensor for the minimum up-type split slice."""

    first, second = mixed_schoen_matter_representatives()
    row_character, column_character = UP_MATTER_CHARACTERS
    first_row = _sector(first.sectors, row_character)
    first_column = _sector(first.sectors, column_character)
    second_row = _sector(second.sectors, row_character)
    second_column = _sector(second.sectors, column_character)
    if first_row.dimension != 1 or first_column.dimension != 1:
        raise ValueError("the selected V1 matter sectors must be one-dimensional")
    if second_row.dimension != 2 or second_column.dimension != 2:
        raise ValueError("the selected V2 matter sectors must be two-dimensional")
    row_v1 = first_row.full_representatives[0]
    column_v1 = first_column.full_representatives[0]
    products = tuple(
        (0, index, external_matter_tensor(row_v1, representative))
        for index, representative in enumerate(
            second_column.full_representatives,
            start=1,
        )
    ) + tuple(
        (index, 0, external_matter_tensor(column_v1, representative))
        for index, representative in enumerate(
            second_row.full_representatives,
            start=1,
        )
    )
    actions = {action.name: action for action in schoen_sparse_deck_actions()}
    character = _sum_character(row_character, column_character)
    products_are_cycles = all(
        full_chain_diagonal_differential(product).is_zero()
        for _row, _column, product in products
    )
    products_have_character = all(
        all(
            _full_action(product, actions[name])
            == product.scale(OMEGA ** character[index])
            for index, name in enumerate(("P", "T"))
        )
        for _row, _column, product in products
    )
    lifted = (
        lift_matter_cochain(row_v1, 1),
        lift_matter_cochain(column_v1, 1),
        *(
            lift_matter_cochain(representative, 2)
            for representative in (
                *second_row.full_representatives,
                *second_column.full_representatives,
            )
        ),
    )
    constituents = mixed_schoen_constituents()
    inserted_units_exact = all(
        local.factor == factor
        and all(
            constituents[factor - 1].objects[basis.object_index].position
            - len(basis.subset)
            + sum(len(simplex) - 1 for simplex in basis.cell)
            == local.total_degree
            for basis, _coefficient in local.terms
        )
        and all(
            (
                basis.monomials[3] == (0, 0)
                and len(basis.cell[3]) == 1
            )
            if factor == 1
            else (
                basis.monomials[1] == (0, 0)
                and len(basis.cell[1]) == 1
            )
            for basis, _coefficient in local.terms
        )
        for local in lifted
        for factor in (local.factor,)
    )
    result = SplitMatterTensorAudit(
        row_character,
        column_character,
        products,
        products_are_cycles,
        products_have_character,
        inserted_units_exact,
    )
    if not result.audit_exact:
        raise ValueError(
            "the split matter tensor audit is incomplete: "
            f"cycles={result.products_are_cycles}, "
            f"characters={result.products_have_required_character}, "
            f"units={result.inserted_units_exact}, "
            f"invariant={result.total_character_is_invariant}"
        )
    return result


def write_split_matter_tensor_audit(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed direct matter-tensor obstruction."""

    payload = split_matter_tensor_audit().as_record()
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
    """Regenerate the direct matter-tensor obstruction artifact."""

    payload = write_split_matter_tensor_audit()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"direct_product_hull_available: {payload['direct_product_hull_available']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "IndependentMatterBasis",
    "IndependentMatterCochain",
    "OUTPUT",
    "SplitMatterTensorAudit",
    "external_matter_tensor",
    "lift_matter_cochain",
    "split_matter_tensor_audit",
    "write_split_matter_tensor_audit",
]
