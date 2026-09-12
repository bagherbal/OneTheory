"""Pair the two bottom V2 matter representatives into det(V2).

Owns:
    The shared-chart Pluecker contraction on the actual A-plus-F0 matter
    support and its hypersurface-quotient Cech--Koszul homotopy.

Depends on:
    Exact V2 matter lifts, certified affine constituent presentations,
    determinant-one overlap transitions, and local maximal-minor pairings.

Must not:
    Extend the map to unused F1 inputs without a derivation, omit the overlap
    homotopy, choose an extension point, or infer a Yukawa coefficient.

Phase 0:
    Research-only bottom-matter determinant pairing for the first higher product.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from onetheory.math.numbers import Eisenstein
from onetheory.math.sheaves import LaurentMatrix
from research.experiments.computable_carrier.generate_tier_b_schoen_outer_automorphisms import (
    _canonical_digest,
)
from research.experiments.computable_carrier.pencil import (
    BlowupChart,
    tier_a_pencil_model,
)

from .diagonal_schoen_line_actions import (
    Character,
    constituent_determinant_character,
    line_has_character,
    project_line_character,
)
from .diagonal_schoen_line_contraction import (
    exact_diagonal_ambient_line_primitive,
    projected_line_coordinates,
)
from .diagonal_schoen_lines import (
    LineDegree4,
    Monomial,
    _FullBasis,
    _FullCochain,
    _subtract_degrees,
)
from .mixed_schoen_determinant_pairing import (
    _pairing_hypersurface_quotient,
    plucker_pairing,
)
from .mixed_schoen_matter_representatives import (
    OUTPUT as MATTER_ARTIFACT,
)
from .mixed_schoen_matter_representatives import (
    mixed_schoen_matter_representatives,
)
from .mixed_schoen_matter_tensor import (
    IndependentMatterCochain,
    _cell_cup,
    lift_matter_cochain,
)
from .mixed_schoen_universal_matter_lifts import UP_MATTER_CHARACTERS
from .mixed_schoen_yukawa_trace import (
    _full_cochain_digest,
    scalar_full_differential,
)
from .published_constituent_full_cech import published_constituent_full_cech
from .published_constituent_overlap_transitions import (
    ConstituentOverlapTransition,
    _relation_columns,
    published_constituent_overlap_atlases,
)

DET_V2_AMBIENT_DEGREES: LineDegree4 = (2, 0, -2, 0)
ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "data/generated/scientific_genesis/mixed_schoen_v2_pluecker_chain_map.json"


def _chart_key(chart: BlowupChart) -> tuple[int, int]:
    """Return the base and fiber pivots of one certified blow-up chart."""

    return chart.base_pivot, 0 if chart.fiber_chart == "mu" else 1


def _middle_row(object_index: int) -> int:
    """Map A,F0 object indices to the local presentation row order."""

    if object_index == 0:
        return 4
    if 1 <= object_index <= 4:
        return object_index - 1
    raise ValueError("the certified V2 matter support contains only A and F0")


def _add_monomials(*values: Monomial) -> Monomial:
    """Add homogeneous Laurent exponent vectors in one factor."""

    return tuple(sum(entries) for entries in zip(*values, strict=True))


@cache
def _local_pairings() -> dict[tuple[int, int], LaurentMatrix]:
    """Return the six full local Pluecker matrices for V2."""

    constituent = published_constituent_full_cech()[1]
    return {
        _chart_key(chart): plucker_pairing(
            _relation_columns(constituent, chart)
        )
        for chart in tier_a_pencil_model().blowup_atlas.charts
    }


def _is_positive_adjacent(transition: ConstituentOverlapTransition) -> bool:
    """Select each adjacent product-cover edge in sorted orientation once."""

    source = _chart_key(transition.source)
    target = _chart_key(transition.target)
    return (
        source[0] < target[0] and source[1] == target[1]
    ) or (
        source[0] == target[0] and source[1] < target[1]
    )


@cache
def _overlap_quotients() -> tuple[
    tuple[tuple[int, int], tuple[int, int], LaurentMatrix],
    ...,
]:
    """Return exact Pluecker hypersurface quotients on adjacent V2 charts."""

    constituent = published_constituent_full_cech()[1]
    return tuple(
        (
            _chart_key(transition.source),
            _chart_key(transition.target),
            _pairing_hypersurface_quotient(
                _relation_columns(constituent, transition.source),
                transition,
            ),
        )
        for transition in published_constituent_overlap_atlases()[1].transitions
        if _is_positive_adjacent(transition)
    )


def _append_pairing_terms(
    terms: list[tuple[_FullBasis, Eisenstein]],
    left: IndependentMatterCochain,
    right: IndependentMatterCochain,
) -> None:
    """Append the shared-chart degree-zero Pluecker component."""

    pairings = _local_pairings()
    for left_basis, left_coefficient in left.terms:
        left_row = _middle_row(left_basis.object_index)
        left_cech_degree = sum(len(simplex) - 1 for simplex in left_basis.cell)
        for right_basis, right_coefficient in right.terms:
            right_row = _middle_row(right_basis.object_index)
            cell_product = _cell_cup(left_basis.cell, right_basis.cell)
            if cell_product is None:
                continue
            raw_subset = (*left_basis.subset, *right_basis.subset)
            if len(set(raw_subset)) != len(raw_subset):
                continue
            subset = tuple(sorted(raw_subset))
            cell_sign, cell = cell_product
            pairing = pairings[
                (left_basis.cell[2][-1], left_basis.cell[3][-1])
            ]
            value = pairing.rows[left_row][right_row]
            sign = cell_sign
            if left_cech_degree * len(right_basis.subset) % 2:
                sign *= -1
            if left_basis.object_index and right_basis.object_index:
                sign *= -1
            ambient_degrees = _subtract_degrees(
                DET_V2_AMBIENT_DEGREES,
                subset,
            )
            for exponents, scalar in value.terms:
                monomials = cast(
                    tuple[Monomial, Monomial, Monomial, Monomial],
                    (
                        _add_monomials(
                            left_basis.monomials[0],
                            right_basis.monomials[0],
                        ),
                        _add_monomials(
                            left_basis.monomials[1],
                            right_basis.monomials[1],
                        ),
                        _add_monomials(
                            left_basis.monomials[2],
                            right_basis.monomials[2],
                            cast(Monomial, exponents[:3]),
                        ),
                        _add_monomials(
                            left_basis.monomials[3],
                            right_basis.monomials[3],
                            cast(Monomial, exponents[3:]),
                        ),
                    ),
                )
                if tuple(sum(item) for item in monomials) != ambient_degrees:
                    raise ValueError("a local Pluecker term changed det(V2) degree")
                terms.append(
                    (
                        _FullBasis(subset, ambient_degrees, monomials, cell),
                        left_coefficient
                        * right_coefficient
                        * scalar
                        * sign,
                    )
                )


def _append_homotopy_terms(
    terms: list[tuple[_FullBasis, Eisenstein]],
    left: IndependentMatterCochain,
    right: IndependentMatterCochain,
) -> None:
    """Append the Cech-one hypersurface-quotient Pluecker component."""

    for left_basis, left_coefficient in left.terms:
        if left_basis.object_index == 0:
            continue
        left_row = _middle_row(left_basis.object_index)
        left_cech_degree = sum(len(simplex) - 1 for simplex in left_basis.cell)
        for right_basis, right_coefficient in right.terms:
            if right_basis.object_index == 0:
                continue
            right_row = _middle_row(right_basis.object_index)
            product = _cell_cup(left_basis.cell, right_basis.cell)
            if product is None:
                continue
            raw_subset = (*left_basis.subset, *right_basis.subset)
            if len(set(raw_subset)) != len(raw_subset) or 1 in raw_subset:
                continue
            product_sign, product_cell = product
            if left_cech_degree * len(right_basis.subset) % 2:
                product_sign *= -1
            for source, target, quotient in _overlap_quotients():
                if source[1] == target[1]:
                    map_cell = (
                        (product_cell[0][0],),
                        (product_cell[1][0],),
                        tuple(sorted((source[0], target[0]))),
                        (source[1],),
                    )
                else:
                    map_cell = (
                        (product_cell[0][0],),
                        (product_cell[1][0],),
                        (source[0],),
                        tuple(sorted((source[1], target[1]))),
                    )
                mapped_cell = _cell_cup(map_cell, product_cell)
                if mapped_cell is None:
                    continue
                map_sign, target_cell = mapped_cell
                subset = (1,)
                ambient_degrees = _subtract_degrees(
                    DET_V2_AMBIENT_DEGREES,
                    subset,
                )
                for exponents, scalar in quotient.rows[left_row][right_row].terms:
                    monomials = cast(
                        tuple[Monomial, Monomial, Monomial, Monomial],
                        (
                            _add_monomials(
                                left_basis.monomials[0],
                                right_basis.monomials[0],
                            ),
                            _add_monomials(
                                left_basis.monomials[1],
                                right_basis.monomials[1],
                            ),
                            _add_monomials(
                                left_basis.monomials[2],
                                right_basis.monomials[2],
                                cast(Monomial, exponents[:3]),
                            ),
                            _add_monomials(
                                left_basis.monomials[3],
                                right_basis.monomials[3],
                                cast(Monomial, exponents[3:]),
                            ),
                        ),
                    )
                    if tuple(sum(item) for item in monomials) != ambient_degrees:
                        raise ValueError("a Pluecker homotopy changed det(V2) degree")
                    terms.append(
                        (
                            _FullBasis(
                                subset,
                                ambient_degrees,
                                monomials,
                                target_cell,
                            ),
                            left_coefficient
                            * right_coefficient
                            * scalar
                            * product_sign
                            * map_sign,
                        )
                    )


def pair_v2_matter_representatives(
    left: IndependentMatterCochain,
    right: IndependentMatterCochain,
) -> _FullCochain:
    """Pair two degree-one V2 representatives into canonical det(V2)."""

    if left.factor != 2 or right.factor != 2:
        raise ValueError("the bottom Pluecker pairing requires two V2 cochains")
    if left.total_degree != 1 or right.total_degree != 1:
        raise ValueError("the bottom Pluecker pairing requires degree-one inputs")
    terms: list[tuple[_FullBasis, Eisenstein]] = []
    _append_pairing_terms(terms, left, right)
    _append_homotopy_terms(terms, left, right)
    return _FullCochain(tuple(terms))


@dataclass(frozen=True, slots=True)
class V2PlueckerPairingWitness:
    """One exact bottom-matter determinant pairing and closure evidence."""

    pairing: _FullCochain
    reverse_pairing: _FullCochain
    differential: _FullCochain
    reverse_differential: _FullCochain
    pairing_coordinates: tuple[tuple[int, Eisenstein], ...]
    reverse_coordinates: tuple[tuple[int, Eisenstein], ...]
    projection_depth: int
    reverse_projection_depth: int
    exchange_primitive: _FullCochain
    exchange_identity_exact: bool
    target_character: Character
    determinant_frame_character: Character
    equivariant_pairing: _FullCochain
    equivariant_differential: _FullCochain
    equivariant_character_exact: bool

    @property
    def exact(self) -> bool:
        """Return whether closure and degree-one exchange symmetry both hold."""

        return (
            self.differential.is_zero()
            and self.reverse_differential.is_zero()
            and self.pairing_coordinates == self.reverse_coordinates
            and self.exchange_identity_exact
            and self.equivariant_differential.is_zero()
            and self.equivariant_character_exact
        )

    def as_record(self) -> dict[str, object]:
        """Serialize closure, exchange, and exact equivariance evidence."""

        return {
            "determinant_ambient_degrees": list(DET_V2_AMBIENT_DEGREES),
            "target_character_exponents": list(self.target_character),
            "determinant_frame_character_exponents": list(
                self.determinant_frame_character
            ),
            "pairing_term_count": len(self.pairing.terms),
            "pairing_digest": _full_cochain_digest(self.pairing),
            "reverse_pairing_term_count": len(self.reverse_pairing.terms),
            "reverse_pairing_digest": _full_cochain_digest(
                self.reverse_pairing
            ),
            "pairing_is_cycle": self.differential.is_zero(),
            "reverse_pairing_is_cycle": self.reverse_differential.is_zero(),
            "pairing_reduced_coordinate_count": len(self.pairing_coordinates),
            "reverse_reduced_coordinate_count": len(self.reverse_coordinates),
            "projection_depth": self.projection_depth,
            "reverse_projection_depth": self.reverse_projection_depth,
            "exchange_primitive_term_count": len(self.exchange_primitive.terms),
            "exchange_identity_exact": self.exchange_identity_exact,
            "equivariant_pairing_term_count": len(
                self.equivariant_pairing.terms
            ),
            "equivariant_pairing_digest": _full_cochain_digest(
                self.equivariant_pairing
            ),
            "equivariant_pairing_is_cycle": (
                self.equivariant_differential.is_zero()
            ),
            "equivariant_character_exact": self.equivariant_character_exact,
            "exact": self.exact,
            "f1_extension_defined": False,
            "holomorphic_yukawa_entry_available": False,
            "extension_point_selected": False,
            "observational_inputs_used": False,
            "first_missing_input": (
                "an exact chain homotopy comparing the grouped HPL matter-leg "
                "contraction with the equivariant V2 determinant pairing"
            ),
        }


def v2_pluecker_pairing_witness(
    left: IndependentMatterCochain,
    right: IndependentMatterCochain,
    target_character: Character,
) -> V2PlueckerPairingWitness:
    """Construct one pairing together with exact closure and exchange checks."""

    pairing = pair_v2_matter_representatives(left, right)
    reverse = pair_v2_matter_representatives(right, left)
    pairing_coordinates, projection_depth = projected_line_coordinates(
        pairing,
        DET_V2_AMBIENT_DEGREES,
        2,
    )
    reverse_coordinates, reverse_projection_depth = projected_line_coordinates(
        reverse,
        DET_V2_AMBIENT_DEGREES,
        2,
    )
    exchange = _FullCochain(pairing.terms + reverse.scale(-1).terms)
    exchange_primitive = exact_diagonal_ambient_line_primitive(
        exchange,
        DET_V2_AMBIENT_DEGREES,
        2,
    ).primitive
    determinant_character = constituent_determinant_character(2)
    equivariant_pairing = project_line_character(
        pairing,
        target_character,
        determinant_character,
    )
    witness = V2PlueckerPairingWitness(
        pairing,
        reverse,
        scalar_full_differential(pairing),
        scalar_full_differential(reverse),
        pairing_coordinates,
        reverse_coordinates,
        projection_depth,
        reverse_projection_depth,
        exchange_primitive,
        scalar_full_differential(exchange_primitive) == exchange,
        target_character,
        determinant_character,
        equivariant_pairing,
        scalar_full_differential(equivariant_pairing),
        line_has_character(
            equivariant_pairing,
            target_character,
            determinant_character,
        ),
    )
    if not witness.exact:
        raise ValueError("the V2 Pluecker chain-map witness failed")
    return witness


@cache
def local_v2_pluecker_pairing_for_characters(
    row_character: Character,
    column_character: Character,
    row_local_family_index: int,
    column_local_family_index: int,
) -> V2PlueckerPairingWitness:
    """Pair indexed local classes from an ordered character pair."""

    if row_local_family_index not in (1, 2) or column_local_family_index not in (
        1,
        2,
    ):
        raise ValueError("local V2 family indices must be one or two")
    _first, second = mixed_schoen_matter_representatives()
    sectors = {sector.character: sector for sector in second.sectors}
    try:
        left_representative = sectors[row_character].full_representatives[
            row_local_family_index - 1
        ]
        right_representative = sectors[column_character].full_representatives[
            column_local_family_index - 1
        ]
    except IndexError as error:
        raise ValueError("the local V2 family index is unavailable") from error
    left = lift_matter_cochain(left_representative, 2)
    right = lift_matter_cochain(right_representative, 2)
    target_character = (
        (row_character[0] + column_character[0]) % 3,
        (row_character[1] + column_character[1]) % 3,
    )
    return v2_pluecker_pairing_witness(left, right, target_character)


@cache
def local_v2_pluecker_pairing(
    row_local_family_index: int,
    column_local_family_index: int,
) -> V2PlueckerPairingWitness:
    """Pair indexed local classes from the up-type matter characters."""

    return local_v2_pluecker_pairing_for_characters(
        *UP_MATTER_CHARACTERS,
        row_local_family_index,
        column_local_family_index,
    )


@cache
def first_v2_pluecker_pairing() -> V2PlueckerPairingWitness:
    """Pair the first local classes in the two required matter characters."""

    return local_v2_pluecker_pairing(1, 1)


def write_v2_pluecker_pairing(path: Path = OUTPUT) -> dict[str, object]:
    """Write the content-addressed first equivariant pairing certificate."""

    prerequisite = json.loads(MATTER_ARTIFACT.read_text(encoding="utf-8"))
    prerequisite_digest = prerequisite.pop("artifact_digest", None)
    if prerequisite_digest != _canonical_digest(prerequisite):
        raise ValueError("the strict matter prerequisite digest failed")
    payload: dict[str, object] = {
        "schema": "mixed-schoen-v2-pluecker-chain-map-v1",
        "coefficient_field": "Q(omega)",
        "matter_artifact_digest": prerequisite_digest,
        **first_v2_pluecker_pairing().as_record(),
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
    """Regenerate the first exact equivariant V2 Pluecker pairing."""

    payload = write_v2_pluecker_pairing()
    print(f"artifact_digest: {payload['artifact_digest']}")
    print(f"exact: {payload['exact']}")
    print(f"first_missing_input: {payload['first_missing_input']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "DET_V2_AMBIENT_DEGREES",
    "OUTPUT",
    "V2PlueckerPairingWitness",
    "first_v2_pluecker_pairing",
    "local_v2_pluecker_pairing",
    "local_v2_pluecker_pairing_for_characters",
    "pair_v2_matter_representatives",
    "v2_pluecker_pairing_witness",
    "write_v2_pluecker_pairing",
]
