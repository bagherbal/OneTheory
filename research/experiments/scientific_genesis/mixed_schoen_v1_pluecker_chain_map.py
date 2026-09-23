"""Pair strict V1 matter classes into their determinant line.

Owns:
    The first-constituent local Pluecker contraction and its exact overlap
    hypersurface homotopy on the actual A-plus-F0 matter support.

Depends on:
    Certified first-constituent charts, exact local determinant pairings,
    independently lifted matter cocycles, and the signed four-factor cover.

Must not:
    Extend the map to unused F1 inputs, infer a reverse Yukawa coefficient,
    identify the two fiber factors, or select an extension point.

Phase 0:
    Research-only determinant pairing needed for the reverse central slot.
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
from research.experiments.computable_carrier.pencil import tier_a_pencil_model

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
from .mixed_schoen_reverse_down_matter_lifts import (
    FORWARD_MATTER_CHARACTERS,
)
from .mixed_schoen_reverse_down_matter_lifts import (
    OUTPUT as REVERSE_MATTER_ARTIFACT,
)
from .mixed_schoen_v2_pluecker_chain_map import (
    _chart_key,
    _is_positive_adjacent,
)
from .mixed_schoen_yukawa_trace import (
    _full_cochain_digest,
    scalar_full_differential,
)
from .published_constituent_full_cech import published_constituent_full_cech
from .published_constituent_overlap_transitions import (
    _relation_columns,
    published_constituent_overlap_atlases,
)

DET_V1_AMBIENT_DEGREES: LineDegree4 = (-2, 0, 2, 0)
ROOT = Path(__file__).resolve().parents[3]
OUTPUT = (
    ROOT
    / "data/generated/scientific_genesis/"
    "mixed_schoen_v1_pluecker_chain_map.json"
)


def _middle_row(object_index: int) -> int:
    """Map A and first-constituent F0 indices to local presentation rows."""

    if object_index == 0:
        return 3
    if 1 <= object_index <= 3:
        return object_index - 1
    raise ValueError("the certified V1 matter support contains only A and F0")


def _add_monomials(*values: Monomial) -> Monomial:
    """Add Laurent exponent vectors on one named ambient factor."""

    return tuple(sum(entries) for entries in zip(*values, strict=True))


@cache
def _local_pairings() -> dict[tuple[int, int], LaurentMatrix]:
    """Construct the six exact first-constituent Pluecker matrices."""

    constituent = published_constituent_full_cech()[0]
    return {
        _chart_key(chart): plucker_pairing(_relation_columns(constituent, chart))
        for chart in tier_a_pencil_model().blowup_atlas.charts
    }


@cache
def _overlap_quotients() -> tuple[
    tuple[tuple[int, int], tuple[int, int], LaurentMatrix], ...
]:
    """Return exact hypersurface quotients on first-factor adjacent charts."""

    constituent = published_constituent_full_cech()[0]
    return tuple(
        (
            _chart_key(transition.source),
            _chart_key(transition.target),
            _pairing_hypersurface_quotient(
                _relation_columns(constituent, transition.source),
                transition,
            ),
        )
        for transition in published_constituent_overlap_atlases()[0].transitions
        if _is_positive_adjacent(transition)
    )


def _pairing_terms(
    left: IndependentMatterCochain,
    right: IndependentMatterCochain,
) -> list[tuple[_FullBasis, Eisenstein]]:
    """Evaluate the degree-zero local pairing on shared first-factor charts."""

    pairings = _local_pairings()
    terms: list[tuple[_FullBasis, Eisenstein]] = []
    for left_basis, left_coefficient in left.terms:
        left_row = _middle_row(left_basis.object_index)
        left_cech_degree = sum(len(simplex) - 1 for simplex in left_basis.cell)
        for right_basis, right_coefficient in right.terms:
            right_row = _middle_row(right_basis.object_index)
            product = _cell_cup(left_basis.cell, right_basis.cell)
            if product is None:
                continue
            raw_subset = (*left_basis.subset, *right_basis.subset)
            if len(set(raw_subset)) != len(raw_subset):
                continue
            cell_sign, cell = product
            subset = tuple(sorted(raw_subset))
            sign = cell_sign
            if left_cech_degree * len(right_basis.subset) % 2:
                sign *= -1
            if left_basis.object_index and right_basis.object_index:
                sign *= -1
            pairing = pairings[(left_basis.cell[0][-1], left_basis.cell[1][-1])]
            value = pairing.rows[left_row][right_row]
            ambient_degrees = _subtract_degrees(DET_V1_AMBIENT_DEGREES, subset)
            for exponents, scalar in value.terms:
                monomials = cast(
                    tuple[Monomial, Monomial, Monomial, Monomial],
                    (
                        _add_monomials(
                            left_basis.monomials[0],
                            right_basis.monomials[0],
                            cast(Monomial, exponents[:3]),
                        ),
                        _add_monomials(
                            left_basis.monomials[1],
                            right_basis.monomials[1],
                            cast(Monomial, exponents[3:]),
                        ),
                        _add_monomials(
                            left_basis.monomials[2], right_basis.monomials[2]
                        ),
                        _add_monomials(
                            left_basis.monomials[3], right_basis.monomials[3]
                        ),
                    ),
                )
                if tuple(sum(item) for item in monomials) != ambient_degrees:
                    raise ValueError("a local V1 pairing changed determinant degree")
                terms.append(
                    (
                        _FullBasis(subset, ambient_degrees, monomials, cell),
                        left_coefficient * right_coefficient * scalar * sign,
                    )
                )
    return terms


def _homotopy_terms(
    left: IndependentMatterCochain,
    right: IndependentMatterCochain,
) -> list[tuple[_FullBasis, Eisenstein]]:
    """Insert the Čech-one correction for hypersurface-dependent overlaps."""

    terms: list[tuple[_FullBasis, Eisenstein]] = []
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
            if len(set(raw_subset)) != len(raw_subset) or 0 in raw_subset:
                continue
            product_sign, product_cell = product
            if left_cech_degree * len(right_basis.subset) % 2:
                product_sign *= -1
            for source, target, quotient in _overlap_quotients():
                if source[1] == target[1]:
                    map_cell = (
                        tuple(sorted((source[0], target[0]))),
                        (source[1],),
                        (product_cell[2][0],),
                        (product_cell[3][0],),
                    )
                else:
                    map_cell = (
                        (source[0],),
                        tuple(sorted((source[1], target[1]))),
                        (product_cell[2][0],),
                        (product_cell[3][0],),
                    )
                mapped = _cell_cup(map_cell, product_cell)
                if mapped is None:
                    continue
                map_sign, cell = mapped
                subset = (0,)
                ambient_degrees = _subtract_degrees(DET_V1_AMBIENT_DEGREES, subset)
                for exponents, scalar in quotient.rows[left_row][right_row].terms:
                    monomials = cast(
                        tuple[Monomial, Monomial, Monomial, Monomial],
                        (
                            _add_monomials(
                                left_basis.monomials[0],
                                right_basis.monomials[0],
                                cast(Monomial, exponents[:3]),
                            ),
                            _add_monomials(
                                left_basis.monomials[1],
                                right_basis.monomials[1],
                                cast(Monomial, exponents[3:]),
                            ),
                            _add_monomials(
                                left_basis.monomials[2], right_basis.monomials[2]
                            ),
                            _add_monomials(
                                left_basis.monomials[3], right_basis.monomials[3]
                            ),
                        ),
                    )
                    if tuple(sum(item) for item in monomials) != ambient_degrees:
                        raise ValueError("a V1 homotopy changed determinant degree")
                    terms.append(
                        (
                            _FullBasis(subset, ambient_degrees, monomials, cell),
                            left_coefficient
                            * right_coefficient
                            * scalar
                            * product_sign
                            * map_sign,
                        )
                    )
    return terms


def pair_v1_matter_representatives(
    left: IndependentMatterCochain,
    right: IndependentMatterCochain,
) -> _FullCochain:
    """Pair two degree-one first-constituent classes into det(V1)."""

    if left.factor != 1 or right.factor != 1:
        raise ValueError("the first Pluecker pairing requires two V1 cochains")
    if left.total_degree != 1 or right.total_degree != 1:
        raise ValueError("the first Pluecker pairing requires degree-one inputs")
    return _FullCochain(
        tuple(_pairing_terms(left, right) + _homotopy_terms(left, right))
    )


@dataclass(frozen=True, slots=True)
class V1PlueckerPairingWitness:
    """Exact physical-character V1 determinant pairing and exchange proof."""

    pairing: _FullCochain
    reverse_pairing: _FullCochain
    pairing_coordinates: tuple[tuple[int, Eisenstein], ...]
    reverse_coordinates: tuple[tuple[int, Eisenstein], ...]
    projection_depth: int
    reverse_projection_depth: int
    exchange_primitive: _FullCochain
    exchange_depth: int
    equivariant_pairing: _FullCochain
    target_character: Character
    determinant_frame_character: Character
    pairing_is_cycle: bool
    reverse_pairing_is_cycle: bool
    exchange_identity_exact: bool
    equivariant_pairing_is_cycle: bool
    equivariant_character_exact: bool

    @property
    def exact(self) -> bool:
        """Require closure, graded exchange, and strict character routing."""

        return (
            bool(self.pairing.terms)
            and self.pairing_is_cycle
            and self.reverse_pairing_is_cycle
            and self.pairing_coordinates == self.reverse_coordinates
            and self.exchange_identity_exact
            and self.equivariant_pairing_is_cycle
            and self.equivariant_character_exact
            and self.target_character == (0, 2)
        )

    def as_record(self) -> dict[str, object]:
        """Serialize exact gates without assigning a Yukawa value."""

        return {
            "determinant_ambient_degrees": list(DET_V1_AMBIENT_DEGREES),
            "target_character_exponents": list(self.target_character),
            "determinant_frame_character_exponents": list(
                self.determinant_frame_character
            ),
            "pairing_term_count": len(self.pairing.terms),
            "pairing_digest": _full_cochain_digest(self.pairing),
            "reverse_pairing_term_count": len(self.reverse_pairing.terms),
            "reverse_pairing_digest": _full_cochain_digest(self.reverse_pairing),
            "pairing_is_cycle": self.pairing_is_cycle,
            "reverse_pairing_is_cycle": self.reverse_pairing_is_cycle,
            "pairing_reduced_coordinate_count": len(self.pairing_coordinates),
            "reverse_reduced_coordinate_count": len(self.reverse_coordinates),
            "projection_depth": self.projection_depth,
            "reverse_projection_depth": self.reverse_projection_depth,
            "exchange_primitive_term_count": len(self.exchange_primitive.terms),
            "exchange_primitive_digest": _full_cochain_digest(
                self.exchange_primitive
            ),
            "exchange_depth": self.exchange_depth,
            "exchange_identity_exact": self.exchange_identity_exact,
            "equivariant_pairing_term_count": len(self.equivariant_pairing.terms),
            "equivariant_pairing_digest": _full_cochain_digest(
                self.equivariant_pairing
            ),
            "equivariant_pairing_is_cycle": self.equivariant_pairing_is_cycle,
            "equivariant_character_exact": self.equivariant_character_exact,
            "exact": self.exact,
        }


@cache
def physical_v1_pluecker_pairing() -> V1PlueckerPairingWitness:
    """Certify the unique V1-V1 physical down-sector matter pair."""

    first, _second = mixed_schoen_matter_representatives()
    sectors = {sector.character: sector for sector in first.sectors}
    row_character, column_character = FORWARD_MATTER_CHARACTERS
    row_representatives = sectors[row_character].full_representatives
    column_representatives = sectors[column_character].full_representatives
    if len(row_representatives) != 1 or len(column_representatives) != 1:
        raise ValueError("the physical V1 sectors must each contain one class")
    left = lift_matter_cochain(row_representatives[0], 1)
    right = lift_matter_cochain(column_representatives[0], 1)
    pairing = pair_v1_matter_representatives(left, right)
    reverse = pair_v1_matter_representatives(right, left)
    pairing_coordinates, projection_depth = projected_line_coordinates(
        pairing, DET_V1_AMBIENT_DEGREES, 2
    )
    reverse_coordinates, reverse_projection_depth = projected_line_coordinates(
        reverse, DET_V1_AMBIENT_DEGREES, 2
    )
    exchange = _FullCochain(pairing.terms + reverse.scale(-1).terms)
    exchange_certificate = exact_diagonal_ambient_line_primitive(
        exchange, DET_V1_AMBIENT_DEGREES, 2
    )
    frame_character = constituent_determinant_character(1)
    target_character: Character = (
        (row_character[0] + column_character[0]) % 3,
        (row_character[1] + column_character[1]) % 3,
    )
    equivariant = project_line_character(
        pairing, target_character, frame_character
    )
    witness = V1PlueckerPairingWitness(
        pairing,
        reverse,
        pairing_coordinates,
        reverse_coordinates,
        projection_depth,
        reverse_projection_depth,
        exchange_certificate.primitive,
        exchange_certificate.homotopy_depth,
        equivariant,
        target_character,
        frame_character,
        scalar_full_differential(pairing).is_zero(),
        scalar_full_differential(reverse).is_zero(),
        scalar_full_differential(exchange_certificate.primitive) == exchange,
        scalar_full_differential(equivariant).is_zero(),
        line_has_character(equivariant, target_character, frame_character),
    )
    if not witness.exact:
        raise ValueError("the physical V1 Pluecker pairing failed")
    return witness


def _verified_input(path: Path, schema: str, gate: str) -> str:
    """Validate one prerequisite and return its content digest."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.pop("artifact_digest", None)
    if (
        not isinstance(digest, str)
        or digest != _canonical_digest(payload)
        or payload.get("schema") != schema
        or payload.get(gate) is not True
    ):
        raise ValueError(f"V1 pairing prerequisite failed: {path.name}")
    return digest


def write_physical_v1_pluecker_pairing(
    path: Path = OUTPUT,
) -> dict[str, object]:
    """Write the exact source-derived V1 pairing certificate."""

    witness = physical_v1_pluecker_pairing()
    payload: dict[str, object] = {
        "schema": "mixed-schoen-v1-pluecker-chain-map-v1",
        "coefficient_field": "Q(omega)",
        "forward_matter_character_exponents": [
            list(character) for character in FORWARD_MATTER_CHARACTERS
        ],
        "prerequisite_artifact_digests": {
            "strict_matter": _verified_input(
                MATTER_ARTIFACT,
                "mixed-schoen-matter-representatives-v1",
                "all_strict_character_representatives_exact",
            ),
            "reverse_matter": _verified_input(
                REVERSE_MATTER_ARTIFACT,
                "mixed-schoen-reverse-down-matter-lifts-v1",
                "exact",
            ),
        },
        **witness.as_record(),
        "holomorphic_yukawa_entry_available": False,
        "extension_point_selected": False,
        "observational_inputs_used": False,
        "next_required_object": (
            "common-chain comparison of V1-V1 matter pairing against the "
            "reverse central Higgs determinant-two correction"
        ),
    }
    payload["artifact_digest"] = _canonical_digest(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)
    return payload


if __name__ == "__main__":
    result = write_physical_v1_pluecker_pairing()
    print(f"artifact_digest: {result['artifact_digest']}")
    print(f"pairing_term_count: {result['pairing_term_count']}")
    print(f"next_required_object: {result['next_required_object']}")


__all__ = [
    "DET_V1_AMBIENT_DEGREES",
    "V1PlueckerPairingWitness",
    "pair_v1_matter_representatives",
    "physical_v1_pluecker_pairing",
    "write_physical_v1_pluecker_pairing",
]
