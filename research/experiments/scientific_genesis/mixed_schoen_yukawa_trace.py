"""Contract the exact up-type product slice toward the scalar residue.

Owns:
    The global Hilbert--Burch determinant contraction selected by the strict
    A1-tensor-A2 Higgs cocycle and exact scalar HPL residue projection.

Depends on:
    Exact equivariant matter-product cycles, the strict lawful Higgs cocycle,
    constituent Hilbert--Burch resolutions, and diagonal line contraction.

Must not:
    Read generated cochains as source inputs, select an extension point, fit a
    coefficient, hide a trace normalization, or call a partial matrix physical.

Phase 0:
    Research-only evaluation of the first lawful holomorphic Yukawa slice.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.linear import Matrix
from onetheory.math.numbers import Eisenstein
from onetheory.math.polynomials import Polynomial, determinant
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)

from .diagonal_schoen_lines import (
    Cell4,
    Monomial,
    _FullBasis,
    _FullCochain,
    _homotopy,
    _perturbation,
    _projection_index,
    _reduced_entries,
    _subtract_degrees,
)
from .mixed_constituent_schoen_arrows import mixed_schoen_constituents
from .mixed_schoen_chain_actions import load_certified_higgs_representative
from .mixed_schoen_chain_diagonal import (
    ChainDiagonalBasis,
    ChainDiagonalCochain,
    chain_diagonal_objects,
)
from .mixed_schoen_matter_comparison import mixed_schoen_matter_comparison
from .mixed_schoen_matter_tensor import _cell_cup

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_yukawa_trace.json"

ALLOWED_SLOTS = ((0, 1), (0, 2), (1, 0), (2, 0))
FORBIDDEN_SLOTS = tuple(
    (row, column)
    for row in range(3)
    for column in range(3)
    if (row, column) not in ALLOWED_SLOTS
)


def _sum_monomials(*values: Monomial) -> Monomial:
    """Add equally based Laurent exponent vectors."""

    return tuple(sum(entries) for entries in zip(*values, strict=True))


@cache
def _complementary_minor_polynomials(factor: int) -> tuple[Polynomial, ...]:
    """Pair each F0 generator with A using signed Hilbert--Burch minors."""

    constituent = mixed_schoen_constituents()[factor - 1]
    matrix = constituent.full.alignment.action.derived.extension.scheme.resolution.matrix
    generator_count = len(matrix)
    relation_rank = len(matrix[0])
    if generator_count != relation_rank + 1:
        raise ValueError("a rank-two Serre presentation needs one excess generator")
    last = generator_count
    values = []
    for generator in range(generator_count):
        minor = tuple(
            tuple(matrix[row][column] for column in range(relation_rank))
            for row in range(generator_count)
            if row != generator
        )
        sign = -1 if (generator + last + 1) % 2 else 1
        values.append(determinant(minor).scale(sign))
    return tuple(values)


@cache
def _pairing_terms(
    first_index: int,
    second_index: int,
) -> tuple[
    tuple[tuple[Monomial, Monomial, Monomial, Monomial], Eisenstein],
    ...,
]:
    """Pair F0 with A and annihilate all other resolution degrees."""

    if first_index == 0 or second_index == 0:
        return ()
    first_minors = _complementary_minor_polynomials(1)
    second_minors = _complementary_minor_polynomials(2)
    if first_index > len(first_minors) or second_index > len(second_minors):
        return ()
    first = first_minors[first_index - 1]
    second = second_minors[second_index - 1]
    zero2 = (0, 0)
    return tuple(
        (
            (
                cast(Monomial, first_exponents),
                zero2,
                cast(Monomial, second_exponents),
                zero2,
            ),
            cast(Eisenstein, first_coefficient)
            * cast(Eisenstein, second_coefficient),
        )
        for first_exponents, first_coefficient in first.terms
        for second_exponents, second_coefficient in second.terms
    )


def _determinant_shift_sign(subset: tuple[int, ...]) -> int:
    """Return the unique relative orientation solving the chain-map equations."""

    first = int(0 in subset)
    second = int(1 in subset)
    diagonal = int(2 in subset)
    exponent = second + first * second + first * diagonal
    return -1 if exponent % 2 else 1


def contract_with_strict_higgs(
    matter_product: ChainDiagonalCochain,
    higgs: ChainDiagonalCochain,
) -> _FullCochain:
    """Apply the global determinant contraction to one matter/Higgs pair."""

    objects = chain_diagonal_objects()
    if any(
        (
            objects[basis.component.object_index].first_index,
            objects[basis.component.object_index].second_index,
        )
        != (0, 0)
        or any(equation != 2 for equation in basis.component.subset)
        for basis, _coefficient in higgs.terms
    ):
        raise ValueError(
            "the direct global contraction requires the strict A1*A2 Higgs "
            "with only diagonal Koszul corrections"
        )
    higgs_by_start: dict[
        tuple[int, int, int, int],
        list[tuple[ChainDiagonalBasis, Eisenstein]],
    ] = {}
    for higgs_basis, higgs_coefficient in higgs.terms:
        start = cast(
            tuple[int, int, int, int],
            tuple(simplex[0] for simplex in higgs_basis.cell),
        )
        higgs_by_start.setdefault(start, []).append(
            (higgs_basis, higgs_coefficient)
        )
    terms = []
    for matter_basis, matter_coefficient in matter_product.terms:
        matter_object = objects[matter_basis.component.object_index]
        pairing = _pairing_terms(
            matter_object.first_index,
            matter_object.second_index,
        )
        if not pairing:
            continue
        endpoint = cast(
            tuple[int, int, int, int],
            tuple(simplex[-1] for simplex in matter_basis.cell),
        )
        for higgs_basis, higgs_coefficient in higgs_by_start.get(endpoint, ()):
            cell_product = _cell_cup(matter_basis.cell, higgs_basis.cell)
            if cell_product is None:
                continue
            cell_sign, cell = cell_product
            if set(matter_basis.component.subset) & set(
                higgs_basis.component.subset
            ):
                continue
            subset = tuple(
                sorted(
                    (*matter_basis.component.subset, *higgs_basis.component.subset)
                )
            )
            koszul_inversions = sum(
                left > right
                for left in matter_basis.component.subset
                for right in higgs_basis.component.subset
            )
            matter_second_structural_degree = -int(
                1 in matter_basis.component.subset
            )
            higgs_first_cech_degree = sum(
                len(higgs_basis.cell[slot]) - 1 for slot in (0, 1)
            )
            constituent_crossing = (
                matter_second_structural_degree * higgs_first_cech_degree
            )
            determinant_shift = _determinant_shift_sign(subset)
            base_sign = (
                -1 if (koszul_inversions + constituent_crossing) % 2 else 1
            )
            product_sign = base_sign * determinant_shift
            ambient_degrees = _subtract_degrees((0, 0, 0, 0), subset)
            for polynomial_monomials, polynomial_coefficient in pairing:
                monomials = cast(
                    tuple[Monomial, Monomial, Monomial, Monomial],
                    tuple(
                        _sum_monomials(matter, higgs_value, polynomial)
                        for matter, higgs_value, polynomial in zip(
                            matter_basis.monomials,
                            higgs_basis.monomials,
                            polynomial_monomials,
                            strict=True,
                        )
                    ),
                )
                if tuple(sum(item) for item in monomials) != ambient_degrees:
                    raise ValueError("the determinant contraction changed scalar degree")
                terms.append(
                    (
                        _FullBasis(subset, ambient_degrees, monomials, cell),
                        matter_coefficient
                        * higgs_coefficient
                        * polynomial_coefficient
                        * cell_sign
                        * product_sign,
                    )
                )
    return _FullCochain(tuple(terms))


def _scalar_cech_differential(cochain: _FullCochain) -> _FullCochain:
    """Apply the signed four-factor Cech differential at fixed Koszul subset."""

    values: dict[_FullBasis, Eisenstein] = {}
    for basis, coefficient in cochain.terms:
        preceding_degree = 0
        for factor, (simplex, monomial) in enumerate(
            zip(basis.cell, basis.monomials, strict=True)
        ):
            tensor_sign = -1 if preceding_degree % 2 else 1
            for vertex in range(len(monomial)):
                if vertex in simplex:
                    continue
                target_simplex = tuple(sorted((*simplex, vertex)))
                local_sign = -1 if target_simplex.index(vertex) % 2 else 1
                cell = list(basis.cell)
                cell[factor] = target_simplex
                target = _FullBasis(
                    basis.subset,
                    basis.ambient_degrees,
                    basis.monomials,
                    cast(Cell4, tuple(cell)),
                )
                structural_sign = -1 if len(basis.subset) % 2 else 1
                updated = values.get(target, Eisenstein(0)) + (
                    coefficient
                    * tensor_sign
                    * local_sign
                    * structural_sign
                )
                if updated.is_zero():
                    values.pop(target, None)
                else:
                    values[target] = updated
            preceding_degree += len(simplex) - 1
    return _FullCochain(tuple(values.items()))


def scalar_full_differential(cochain: _FullCochain) -> _FullCochain:
    """Apply the full Cech--Koszul differential of the scalar complex."""

    cech = _scalar_cech_differential(cochain)
    koszul = _perturbation(cochain)
    return _FullCochain(cech.terms + koszul.terms)


def scalar_residue(cochain: _FullCochain) -> tuple[Eisenstein, int]:
    """Project one degree-three scalar cocycle to the ordered residue generator."""

    entries = _reduced_entries((0, 0, 0, 0), 3)
    if len(entries) != 1:
        raise ValueError("the scalar residue target is not one-dimensional")
    target_indices = {
        (entry.subset, entry.monomials): entry.index for entry in entries
    }
    value = Eisenstein(0)
    current = cochain
    depth = 0
    while not current.is_zero():
        for basis, coefficient in current.terms:
            if _projection_index(basis, target_indices) == 0:
                value += coefficient
        current = _perturbation(_homotopy(current)).scale(-1)
        depth += 1
        if depth > 12:
            raise ValueError("the scalar residue projection did not terminate")
    return value, depth


def scalar_primitive(cochain: _FullCochain) -> tuple[_FullCochain, int]:
    """Construct the exact perturbed-Cech primitive of a zero-residue cycle."""

    if not scalar_full_differential(cochain).is_zero():
        raise ValueError("a scalar primitive requires a full cocycle")
    residue, _projection_depth = scalar_residue(cochain)
    if not residue.is_zero():
        raise ValueError("a nonzero scalar residue has no global primitive")
    result = _FullCochain()
    current = cochain
    depth = 0
    while not current.is_zero():
        image = _homotopy(current)
        result = _FullCochain(result.terms + image.terms)
        current = _perturbation(image).scale(-1)
        depth += 1
        if depth > 12:
            raise ValueError("the scalar primitive series did not terminate")
    if scalar_full_differential(result) != cochain:
        raise ValueError("the scalar primitive failed exact reconstruction")
    return result, depth


def _full_cochain_digest(cochain: _FullCochain) -> str:
    """Hash one exact scalar Cech--Koszul cochain deterministically."""

    digest = hashlib.sha256()
    for basis, coefficient in cochain.terms:
        record = (
            basis.subset,
            basis.ambient_degrees,
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


@dataclass(frozen=True, slots=True)
class HolomorphicUpSlice:
    """Four exact split-family entries in the first holomorphic matrix slice."""

    entries: tuple[tuple[int, int, Eisenstein], ...]
    scalar_term_counts: tuple[int, ...]
    projection_depths: tuple[int, ...]
    scalar_products_are_cycles: bool
    primitive_term_counts: tuple[int, ...]
    primitive_depths: tuple[int, ...]
    primitive_reconstructions_exact: tuple[bool, ...]
    scalar_digests: tuple[str, ...]
    primitive_digests: tuple[str, ...]

    @property
    def matrix(self) -> Matrix:
        """Return the complete exact three-family tree-level matrix."""

        values = {
            (row, column): value for row, column, value in self.entries
        }
        return Matrix(
            tuple(
                tuple(values.get((row, column), Eisenstein(0)) for column in range(3))
                for row in range(3)
            ),
            scalar_type=Eisenstein,
        )

    @property
    def matrix_rank(self) -> int:
        """Return the exact tree-level matrix rank."""

        return self.matrix.rank()

    @property
    def exact(self) -> bool:
        """Return whether all four contractions close as scalar cocycles."""

        return (
            tuple((row, column) for row, column, _value in self.entries)
            == ALLOWED_SLOTS
            and all(self.scalar_term_counts)
            and self.scalar_products_are_cycles
            and self.projection_depths == (4, 4, 4, 4)
            and self.primitive_term_counts == (4086, 3771, 4086, 3771)
            and self.primitive_depths == (4, 4, 4, 4)
            and all(self.primitive_reconstructions_exact)
            and all(value.is_zero() for _row, _column, value in self.entries)
            and self.matrix_rank == 0
        )

    def as_record(self) -> dict[str, object]:
        """Serialize the complete exact tree matrix and vanishing certificates."""

        return {
            "character_allowed_slots": [list(slot) for slot in ALLOWED_SLOTS],
            "character_forbidden_slots": [list(slot) for slot in FORBIDDEN_SLOTS],
            "entries": [
                {"row": row, "column": column, "value": str(value)}
                for row, column, value in self.entries
            ],
            "matrix": [
                [str(self.matrix[row][column]) for column in range(3)]
                for row in range(3)
            ],
            "matrix_rank": self.matrix_rank,
            "scalar_term_counts": list(self.scalar_term_counts),
            "scalar_projection_depths": list(self.projection_depths),
            "scalar_products_are_cycles": self.scalar_products_are_cycles,
            "primitive_term_counts": list(self.primitive_term_counts),
            "primitive_depths": list(self.primitive_depths),
            "primitive_reconstructions_exact": list(
                self.primitive_reconstructions_exact
            ),
            "scalar_digests": list(self.scalar_digests),
            "primitive_digests": list(self.primitive_digests),
            "determinant_orientation_supports": [
                list(subset)
                for subset in (
                    (),
                    (0,),
                    (0, 1),
                    (0, 1, 2),
                    (0, 2),
                    (1,),
                    (1, 2),
                    (2,),
                )
            ],
            "determinant_orientation_vector": [
                _determinant_shift_sign(subset)
                for subset in (
                    (),
                    (0,),
                    (0, 1),
                    (0, 1, 2),
                    (0, 2),
                    (1,),
                    (1, 2),
                    (2,),
                )
            ],
            "tree_level_nontrivial": self.matrix_rank > 0,
            "exact": self.exact,
        }


@cache
def mixed_schoen_holomorphic_up_slice() -> HolomorphicUpSlice:
    """Evaluate the four lawful split-family determinant traces exactly."""

    higgs = load_certified_higgs_representative()
    entries = []
    counts = []
    depths = []
    primitive_counts = []
    primitive_depths = []
    primitive_checks = []
    scalar_digests = []
    primitive_digests = []
    cycles = True
    for witness in mixed_schoen_matter_comparison():
        scalar = contract_with_strict_higgs(
            witness.equivariant_representative,
            higgs,
        )
        cycles = cycles and scalar_full_differential(scalar).is_zero()
        value, depth = scalar_residue(scalar)
        primitive, primitive_depth = scalar_primitive(scalar)
        entries.append((witness.row, witness.column, value))
        counts.append(len(scalar.terms))
        depths.append(depth)
        primitive_counts.append(len(primitive.terms))
        primitive_depths.append(primitive_depth)
        primitive_checks.append(scalar_full_differential(primitive) == scalar)
        scalar_digests.append(_full_cochain_digest(scalar))
        primitive_digests.append(_full_cochain_digest(primitive))
    result = HolomorphicUpSlice(
        tuple(entries),
        tuple(counts),
        tuple(depths),
        cycles,
        tuple(primitive_counts),
        tuple(primitive_depths),
        tuple(primitive_checks),
        tuple(scalar_digests),
        tuple(primitive_digests),
    )
    if not result.exact:
        raise ValueError("the first holomorphic up-type trace slice failed")
    return result


def write_mixed_schoen_yukawa_trace(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the content-addressed exact tree-level up-matrix certificate."""

    result = mixed_schoen_holomorphic_up_slice()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-holomorphic-up-trace-v1",
        "coefficient_field": "Q(omega)",
        "trace_normalization": (
            "the ordered ambient canonical Laurent residue generator has trace one"
        ),
        "up_type_tree_matrix": result.as_record(),
        "classification": "SCOPED_TREE_LEVEL_NO_GO",
        "observational_inputs_used": False,
        "extension_point_selected": False,
        "complete_tree_level_up_matrix_available": True,
        "nontrivial_tree_level_up_matrix_available": False,
        "physical_yukawa_matrix_available": False,
        "next_required_object": (
            "the first exact deformation or higher product permitted by the "
            "lawful carrier DGA that can escape the certified tree-level zero"
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
    """Regenerate the exact tree-level up-type trace artifact."""

    payload = write_mixed_schoen_yukawa_trace()
    matrix = payload["up_type_tree_matrix"]
    if not isinstance(matrix, dict):
        raise TypeError("the serialized up-type matrix record is invalid")
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"matrix_rank: {matrix['matrix_rank']}")
    print(f"classification: {payload['classification']}")
    print(f"next_required_object: {payload['next_required_object']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "HolomorphicUpSlice",
    "OUTPUT",
    "contract_with_strict_higgs",
    "mixed_schoen_holomorphic_up_slice",
    "scalar_full_differential",
    "scalar_primitive",
    "scalar_residue",
    "write_mixed_schoen_yukawa_trace",
]
